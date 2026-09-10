import unittest
from unittest.mock import MagicMock, patch

from config import MigrationConfig
from engine.database_migrator import DatabaseMigrator
from main import run_migration


class TestFrozenSourceProtectionRegression(unittest.TestCase):
    """
    Regression tests for frozen source database protection in the main migration flow.
    Ensures that source freeze is proven BEFORE any export or destructive target operations.
    """

    def setUp(self):
        self.mock_fb_con = MagicMock()
        self.mock_pg_con = MagicMock()
        self.mock_fb_cur = MagicMock()
        self.mock_pg_cur = MagicMock()

        self.mock_fb_con.cursor.return_value = self.mock_fb_cur
        self.mock_pg_con.cursor.return_value = self.mock_pg_cur

    def _setup_migrator_with_mocked_lifecycle(self, config=None):
        """Builds DatabaseMigrator with mocked lifecycle steps to trace execution sequence."""
        migrator = DatabaseMigrator(self.mock_fb_con, self.mock_pg_con, config=config)

        call_trace = []
        migrator.export_all_firebird_ddl = lambda *a, **k: call_trace.append('export_all_firebird_ddl')
        migrator.validate_artifacts = lambda *a, **k: call_trace.append('validate_artifacts') or {}
        migrator.drop_schema = lambda *a, **k: call_trace.append('drop_schema')
        migrator.create_tables = lambda *a, **k: call_trace.append('create_tables')
        migrator.create_constraints_and_indexes = lambda *a, **k: call_trace.append('create_constraints_and_indexes')
        migrator.apply_sql_file = lambda *a, **k: call_trace.append('apply_sql_file') or 0
        migrator.import_data = lambda *a, **k: call_trace.append('import_data') or True
        migrator.analyze_tables = lambda *a, **k: call_trace.append('analyze_tables')

        return migrator, call_trace

    def test_normal_path_triggers_protection_by_default(self):
        """Normal path must enable require_frozen_source=True and allow_live_source=False by default."""
        config = MigrationConfig()
        self.assertTrue(config.require_frozen_source)
        self.assertFalse(config.allow_live_source)

        migrator = DatabaseMigrator(self.mock_fb_con, self.mock_pg_con)
        self.assertTrue(migrator.config.require_frozen_source)
        self.assertFalse(migrator.config.allow_live_source)

    def test_read_only_source_approved_in_main_flow(self):
        """Firebird source set to read-only (MON$READ_ONLY=1) is approved and proceeds through main flow."""
        self.mock_fb_cur.fetchone.side_effect = [
            (1, 0),  # MON$READ_ONLY = 1, MON$SHUTDOWN_MODE = 0
            (0,),    # active_attachments = 0
        ]

        migrator, call_trace = self._setup_migrator_with_mocked_lifecycle()
        res = run_migration(migrator)

        self.assertTrue(res)
        self.assertIn('export_all_firebird_ddl', call_trace)
        self.assertIn('drop_schema', call_trace)
        self.assertIn('create_tables', call_trace)
        self.assertIn('import_data', call_trace)

    def test_read_write_without_connections_rejected_in_main_flow(self):
        """Read-write source is rejected when freezing is required, even with zero external connections."""
        self.mock_fb_cur.fetchone.side_effect = [
            (0, 0),  # MON$READ_ONLY = 0, MON$SHUTDOWN_MODE = 0
            (0,),    # active_attachments = 0 (zero external connections)
        ]

        migrator, call_trace = self._setup_migrator_with_mocked_lifecycle()

        with self.assertRaises(RuntimeError) as ctx:
            run_migration(migrator)

        self.assertIn("Source Firebird database is LIVE (read-write mode with 0 active attachment(s))",
                      str(ctx.exception))
        # Absolutely NO export, DROP, or schema modifications should have occurred
        self.assertEqual(call_trace, [], "No lifecycle operations should occur when source is rejected")

    def test_read_write_with_connections_rejected_in_main_flow(self):
        """Read-write source with active external attachments is rejected before any destructive action."""
        self.mock_fb_cur.fetchone.side_effect = [
            (0, 0),  # MON$READ_ONLY = 0, MON$SHUTDOWN_MODE = 0
            (4,),    # active_attachments = 4
        ]

        migrator, call_trace = self._setup_migrator_with_mocked_lifecycle()

        with self.assertRaises(RuntimeError) as ctx:
            run_migration(migrator)

        self.assertIn("Source Firebird database is LIVE (read-write mode with 4 active attachment(s))",
                      str(ctx.exception))
        self.assertEqual(call_trace, [])

    def test_shutdown_multi_rejected_as_proof_of_freeze(self):
        """Shutdown mode 'multi' (MON$SHUTDOWN_MODE=1) allows SYSDBA/owner writes and MUST be rejected."""
        self.mock_fb_cur.fetchone.side_effect = [
            (0, 1),  # MON$READ_ONLY = 0, MON$SHUTDOWN_MODE = 1 (multi)
            (0,),    # active_attachments = 0
        ]

        migrator, call_trace = self._setup_migrator_with_mocked_lifecycle()

        with self.assertRaises(RuntimeError) as ctx:
            run_migration(migrator)

        self.assertIn("multi-user maintenance shutdown mode (MON$SHUTDOWN_MODE=1)", str(ctx.exception))
        self.assertIn("Mode 'multi' allows connections from SYSDBA and database owner", str(ctx.exception))
        self.assertEqual(call_trace, [], "Destructive operations must be blocked for shutdown mode 'multi'")

    def test_catalog_query_failure_prevents_approval(self):
        """Catalog query failure prevents approval and blocks all destructive operations."""
        self.mock_fb_cur.execute.side_effect = Exception("Catalog access error: connection severed")

        migrator, call_trace = self._setup_migrator_with_mocked_lifecycle()

        with self.assertRaises(RuntimeError) as ctx:
            run_migration(migrator)

        self.assertIn("Cannot verify that source Firebird database is frozen", str(ctx.exception))
        self.assertIn("Catalog query failure prevents approval of migration operations", str(ctx.exception))
        self.assertEqual(call_trace, [], "No operations allowed when catalog cannot be verified")

    def test_explicit_override_allows_live_source_with_warning(self):
        """Explicit override allow_live_source=True allows migration with explicit warning that consistency is NOT guaranteed."""
        self.mock_fb_cur.fetchone.side_effect = [
            (0, 0),  # MON$READ_ONLY = 0, MON$SHUTDOWN_MODE = 0
            (2,),    # active_attachments = 2
        ]

        config = MigrationConfig(allow_live_source=True)
        migrator, call_trace = self._setup_migrator_with_mocked_lifecycle(config=config)

        with self.assertLogs('engine.data_migrator', level='WARNING') as cm:
            res = run_migration(migrator)

        self.assertTrue(res)
        self.assertIn('drop_schema', call_trace)
        self.assertTrue(any('EXPLICIT OVERRIDE' in msg for msg in cm.output))
        self.assertTrue(any('Data consistency across tables is NOT guaranteed' in msg for msg in cm.output))

    def test_verification_precedes_drop_truncate_and_disable_triggers(self):
        """Verification is confirmed to execute strictly before drop_schema, truncate, and trigger disabling."""
        # Spy on check_source_consistency and drop_schema
        events = []

        migrator = DatabaseMigrator(self.mock_fb_con, self.mock_pg_con)
        orig_check = migrator.check_source_consistency

        def wrapped_check(*a, **k):
            events.append('check_source_consistency')
            return orig_check(*a, **k)

        migrator.check_source_consistency = wrapped_check
        migrator.export_all_firebird_ddl = lambda *a, **k: events.append('export_all_firebird_ddl')
        migrator.validate_artifacts = lambda *a, **k: events.append('validate_artifacts') or {}
        migrator.drop_schema = lambda *a, **k: events.append('drop_schema')
        migrator.create_tables = lambda *a, **k: events.append('create_tables')
        migrator.create_constraints_and_indexes = lambda *a, **k: events.append('create_constraints_and_indexes')
        migrator.apply_sql_file = lambda *a, **k: events.append('apply_sql_file') or 0
        migrator.import_data = lambda *a, **k: events.append('import_data') or True
        migrator.analyze_tables = lambda *a, **k: events.append('analyze_tables')

        # Read-only source
        self.mock_fb_cur.fetchone.side_effect = [
            (1, 0),
            (0,),
        ]

        run_migration(migrator)

        self.assertEqual(events[0], 'check_source_consistency',
                         "check_source_consistency MUST be the very first step in the lifecycle")
        self.assertLess(events.index('check_source_consistency'), events.index('export_all_firebird_ddl'))
        self.assertLess(events.index('check_source_consistency'), events.index('drop_schema'))

    def test_validate_memory_budget_resolves_config_and_rejects_impossible(self):
        """Direct unit cover for the pre-flight memory gate."""
        migrator, _ = self._setup_migrator_with_mocked_lifecycle()
        total, worker, blob = migrator.validate_memory_budget()
        self.assertLessEqual(4 * worker, total)

        bad_config = MigrationConfig(
            total_memory_budget_bytes=64 * 1024 * 1024,
            max_buffer_bytes_per_worker=32 * 1024 * 1024,
            max_blob_bytes=8 * 1024 * 1024,
        )
        bad_migrator, _ = self._setup_migrator_with_mocked_lifecycle(config=bad_config)
        with self.assertRaises(ValueError) as ctx:
            bad_migrator.validate_memory_budget()
        self.assertIn("exceeds total budget", str(ctx.exception))

    def test_incompatible_memory_config_blocks_run_before_drop(self):
        """
        P1 regression: an impossible memory configuration (4 workers x 32MiB
        per worker > 64MiB total) must fail the full run_migration() BEFORE
        any export or destructive drop_schema(), never after wiping the target.
        """
        # Frozen source so the run reaches the memory gate.
        self.mock_fb_cur.fetchone.side_effect = [(1, 0), (0,)]

        bad_config = MigrationConfig(
            total_memory_budget_bytes=64 * 1024 * 1024,
            max_buffer_bytes_per_worker=32 * 1024 * 1024,
            max_blob_bytes=8 * 1024 * 1024,
        )
        migrator, call_trace = self._setup_migrator_with_mocked_lifecycle(config=bad_config)

        with self.assertRaises(ValueError) as ctx:
            run_migration(migrator)

        self.assertIn("exceeds total budget", str(ctx.exception))
        self.assertEqual(call_trace, [], "No lifecycle step may run on impossible memory config")
        self.assertNotIn('drop_schema', call_trace)

    def test_compatible_memory_config_passes_preflight(self):
        """A compatible configuration flows past the memory gate normally."""
        self.mock_fb_cur.fetchone.side_effect = [(1, 0), (0,)]

        migrator, call_trace = self._setup_migrator_with_mocked_lifecycle()
        res = run_migration(migrator)

        self.assertTrue(res)
        self.assertIn('export_all_firebird_ddl', call_trace)
        self.assertIn('drop_schema', call_trace)
        self.assertIn('import_data', call_trace)

    def test_single_user_valid_for_one_worker_passes_and_reuses_connection(self):
        """
        P2 acceptance: single-user source (MON$SHUTDOWN_MODE=2) with total
        32MiB / 32MiB per worker is valid for ONE effective worker. The full
        run_migration() must pass the preflight and execute sequentially,
        reusing the caller connections instead of opening worker ones.
        """
        from models import Column, Table

        # Frozen single-user source; three probes run
        # (preflight + upfront import check + inner import check).
        self.mock_fb_cur.fetchone.side_effect = [(0, 2), (0,)] * 3
        self.mock_fb_cur.fetchmany.return_value = []

        config = MigrationConfig(
            total_memory_budget_bytes=32 * 1024 * 1024,
            max_buffer_bytes_per_worker=32 * 1024 * 1024,
            max_blob_bytes=16 * 1024 * 1024,
        )
        migrator, call_trace = self._setup_migrator_with_mocked_lifecycle(config=config)
        # Keep the REAL import_data (still traced): only the surrounding
        # lifecycle steps stay mocked.
        real_import_data = DatabaseMigrator.import_data.__get__(migrator, DatabaseMigrator)
        migrator.import_data = lambda *a, **k: (
            call_trace.append('import_data'), real_import_data(*a, **k))[1]

        t1, t2 = Table('T_SEQ_A'), Table('T_SEQ_B')
        for table in (t1, t2):
            table.columns.append(Column('ID', 'INTEGER', nullable=False))
        migrator.table_objs = [t1, t2]

        with patch('engine.data_migrator.get_firebird_connection') as mock_new_fb, \
             patch('engine.data_migrator.get_postgres_connection') as mock_new_pg:
            res = run_migration(migrator)

        self.assertTrue(res)
        self.assertIn('export_all_firebird_ddl', call_trace)
        self.assertIn('drop_schema', call_trace)
        self.assertIn('import_data', call_trace)
        # Sequential single-user path: no worker connections opened.
        mock_new_fb.assert_not_called()
        mock_new_pg.assert_not_called()

    def test_same_config_with_four_effective_workers_fails_before_drop(self):
        """
        P2 acceptance: the same 32MiB/32MiB configuration with FOUR effective
        workers (frozen read-only source, no single-user reduction) must fail
        the full run_migration() before drop_schema().
        """
        self.mock_fb_cur.fetchone.side_effect = [(1, 0), (0,)]

        config = MigrationConfig(
            total_memory_budget_bytes=32 * 1024 * 1024,
            max_buffer_bytes_per_worker=32 * 1024 * 1024,
            max_blob_bytes=16 * 1024 * 1024,
        )
        migrator, call_trace = self._setup_migrator_with_mocked_lifecycle(config=config)

        with self.assertRaises(ValueError) as ctx:
            run_migration(migrator)

        self.assertIn("exceeds total budget", str(ctx.exception))
        self.assertEqual(call_trace, [], "No lifecycle step may run, especially drop_schema")
        self.assertNotIn('drop_schema', call_trace)


if __name__ == '__main__':
    unittest.main()
