import unittest
from unittest.mock import MagicMock

from engine.data_migrator import DataMigrator
from models import Table, Column


class TestDataMigrator(unittest.TestCase):
    def setUp(self):
        self.mock_fb_con = MagicMock()
        self.mock_pg_con = MagicMock()
        self.mock_fb_cur = MagicMock()
        self.mock_pg_cur = MagicMock()

        self.mock_pg_con.encoding = 'UTF8'
        self.mock_pg_cur.connection.encoding = 'UTF8'
        self.mock_pg_cur.mogrify.return_value = b"(1, 'test')"

        self.mock_fb_con.cursor.return_value = self.mock_fb_cur
        self.mock_pg_con.cursor.return_value = self.mock_pg_cur

        self.migrator = DataMigrator(self.mock_fb_con, self.mock_pg_con)

    def test_data_migration_sanitizes_nul_bytes_only_when_present(self):
        table = Table('CLIENTES')
        table.columns.append(Column('ID', 'INTEGER', nullable=False, sequence_name='GEN_CLIENTES_ID'))
        table.columns.append(Column('NOME', 'VARCHAR(100)', nullable=False))
        table.columns.append(Column('OBS', 'TEXT', nullable=True))

        # Row 1 has NUL byte in NOME, Row 2 is clean
        raw_rows = [
            (1, 'JOAO\x00 SILVA', 'OBS NORMAL'),
            (2, 'MARIA SANTOS', 'SEM NUL')
        ]

        # fetchmany returns rows first time, empty list second time
        self.mock_fb_cur.fetchmany.side_effect = [raw_rows, []]

        success = self.migrator.import_data([table])
        self.assertTrue(success)

        # Check commit was called and COPY protocol was used with sanitized buffer
        self.mock_pg_con.commit.assert_called()
        self.mock_pg_cur.copy_expert.assert_called()
        copy_sql, buf = self.mock_pg_cur.copy_expert.call_args[0]
        self.assertIn('COPY "clientes"', copy_sql)
        buf_val = buf.getvalue()
        self.assertIn('JOAO SILVA', buf_val)
        self.assertNotIn('\x00', buf_val)
        # NUL stats must record table, column, and exact count of occurrences
        self.assertEqual(self.migrator.last_nul_stats, {'CLIENTES': {'NOME': 1}})

    def test_data_migration_zero_copy_for_numeric_tables(self):
        table = Table('ESTATISTICAS')
        table.columns.append(Column('ID', 'INTEGER', nullable=False))
        table.columns.append(Column('VALOR', 'NUMERIC(15,2)', nullable=False))
        table.columns.append(Column('QUANTIDADE', 'INTEGER', nullable=False))

        raw_rows = [
            (1, 150.50, 10),
            (2, 300.00, 20)
        ]

        self.mock_fb_cur.fetchmany.side_effect = [raw_rows, []]

        success = self.migrator.import_data([table])
        self.assertTrue(success)
        self.assertEqual(self.migrator.last_nul_stats, {})

    def test_data_migration_nul_stats_warns_on_stripped_bytes(self):
        table = Table('TAB_NUL')
        table.columns.append(Column('ID', 'INTEGER', nullable=False))
        table.columns.append(Column('DESCRICAO', 'VARCHAR(50)', nullable=False))

        raw_rows = [(1, 'A\x00B\x00C'), (2, 'XYZ')]
        self.mock_fb_cur.fetchmany.side_effect = [raw_rows, []]

        with self.assertLogs('engine.data_migrator', level='WARNING') as cm:
            success = self.migrator.import_data([table], max_workers=1)
            self.assertTrue(success)
            self.assertEqual(self.migrator.last_nul_stats, {'TAB_NUL': {'DESCRICAO': 2}})
            self.assertTrue(any('DATA TRANSFORMATION NOTICE' in msg for msg in cm.output))
            self.assertTrue(any("'DESCRICAO': 2 NUL byte(s)" in msg for msg in cm.output))

    def test_data_migration_handles_failure_and_rollback(self):
        table = Table('FALHA')
        table.columns.append(Column('ID', 'INTEGER', nullable=False))

        self.mock_fb_cur.fetchmany.side_effect = OSError("DB Connection dropped")

        success = self.migrator.import_data([table], max_workers=1)
        self.assertFalse(success)
        self.mock_pg_con.rollback.assert_called()

    def test_re_enable_triggers_propagates_psycopg2_error(self):
        import psycopg2
        table = Table('TABELA1')
        table.columns.append(Column('ID', 'INTEGER', nullable=False))

        self.mock_pg_cur.execute.side_effect = psycopg2.OperationalError("Trigger lock timeout")

        with self.assertRaises(psycopg2.OperationalError):
            self.migrator._re_enable_triggers([table])

    def test_parallel_data_migration_with_workers(self):
        from unittest.mock import patch, MagicMock

        t1 = Table('TABELA1')
        t1.columns.append(Column('ID', 'INTEGER', nullable=False))
        t2 = Table('TABELA2')
        t2.columns.append(Column('ID', 'INTEGER', nullable=False))

        created_fb_conns = []
        created_pg_conns = []

        class MockFbCursor:
            def __init__(self):
                self._fetched = False

            def execute(self, query):
                self._fetched = False

            def fetchmany(self, batch_size):
                if not self._fetched:
                    self._fetched = True
                    return [(1,), (2,)]
                return []

        def make_fb_con():
            fb_con = MagicMock()
            cur = MockFbCursor()
            fb_con.cursor.return_value = cur
            created_fb_conns.append(fb_con)
            return fb_con

        def make_pg_con():
            pg_con = MagicMock()
            pg_cur = MagicMock()
            pg_con.encoding = 'UTF8'
            pg_cur.connection.encoding = 'UTF8'
            pg_cur.mogrify.return_value = b"(1)"
            pg_con.cursor.return_value = pg_cur
            created_pg_conns.append(pg_con)
            return pg_con

        from concurrent.futures import ThreadPoolExecutor

        with patch('engine.data_migrator.get_firebird_connection', side_effect=make_fb_con), \
             patch('engine.data_migrator.get_postgres_connection', side_effect=make_pg_con), \
             ThreadPoolExecutor(max_workers=2) as test_executor:

            success = self.migrator.import_data([t1, t2], max_workers=2, executor=test_executor)
            self.assertTrue(success)

            # Each worker opened its own isolated connection
            self.assertEqual(len(created_fb_conns), 2)
            self.assertEqual(len(created_pg_conns), 2)

            # All worker connections were cleanly closed
            for fb_conn in created_fb_conns:
                fb_conn.close.assert_called_once()
            for pg_conn in created_pg_conns:
                pg_conn.close.assert_called_once()

            # Commits were executed across worker connections
            total_commits = sum(pg_conn.commit.call_count for pg_conn in created_pg_conns)
            self.assertGreaterEqual(total_commits, 2)

    def test_copy_formatting_various_types(self):
        import datetime
        table = Table('DADOS')
        table.columns.append(Column('ID', 'INTEGER', nullable=False))
        table.columns.append(Column('TEXTO', 'VARCHAR(50)', nullable=True))
        table.columns.append(Column('FOTO', 'BLOB SUBTYPE 0', nullable=True))
        table.columns.append(Column('ATIVO', 'BOOLEAN', nullable=True))
        table.columns.append(Column('CRIADO_EM', 'TIMESTAMP', nullable=True))

        raw_rows = [
            (1, 'Texto com \n newline e \t tab e \\ barra', b'\xde\xad\xbe\xef', True, datetime.datetime(2026, 1, 1, 12, 0, 0)),
            (2, None, None, False, None)
        ]
        self.mock_fb_cur.fetchmany.side_effect = [raw_rows, []]

        success = self.migrator.import_data([table], max_workers=1)
        self.assertTrue(success)

        self.mock_pg_cur.copy_expert.assert_called()
        copy_sql, buf = self.mock_pg_cur.copy_expert.call_args[0]
        self.assertIn('COPY "dados"', copy_sql)
        buf_val = buf.getvalue()
        # Escaping
        self.assertIn(r'Texto com \n newline e \t tab e \\ barra', buf_val)
        # Bytea hex
        self.assertIn(r'\\xdeadbeef', buf_val)
        # Booleans
        self.assertIn('\tt\t', buf_val)
        self.assertIn('\tf\t', buf_val)
        # NULLs
        self.assertIn(r'\N', buf_val)

    def test_sequence_synchronization_does_not_regress_and_groups_by_sequence(self):
        t1 = Table('TABELA1')
        t1.columns.append(Column('ID', 'INTEGER', nullable=False, sequence_name='GEN_SHARED_ID'))
        t2 = Table('TABELA2')
        t2.columns.append(Column('CODIGO', 'INTEGER', nullable=False, sequence_name='GEN_SHARED_ID'))

        self.mock_fb_cur.fetchmany.return_value = []
        success = self.migrator.import_data([t1, t2], max_workers=1)
        self.assertTrue(success)

        executed_queries = [call[0][0] for call in self.mock_pg_cur.execute.call_args_list]
        sync_queries = [q for q in executed_queries if 'SELECT setval(' in q]

        # Must execute exactly once for the shared sequence across both tables
        self.assertEqual(len(sync_queries), 1)
        query = sync_queries[0]
        self.assertIn('"gen_shared_id"', query)
        self.assertIn('WITH max_calc AS MATERIALIZED', query)
        self.assertIn('FROM "gen_shared_id" s, max_calc m', query)
        self.assertIn('(SELECT MAX("id") FROM "tabela1")', query)
        self.assertIn('(SELECT MAX("codigo") FROM "tabela2")', query)
        self.assertEqual(query.count('SELECT MAX("id")'), 1)
        self.assertEqual(query.count('SELECT MAX("codigo")'), 1)
        self.assertNotIn('COALESCE', query)
        self.assertIn('IS NOT NULL', query)
        self.assertIn('s.is_called', query)

    def test_identity_and_descending_sequence_synchronization(self):
        t = Table('TEST_TBL')
        col_id = Column('ID', 'BIGINT', nullable=False, identity_type='ALWAYS', identity_increment=1, identity_current=500)
        col_desc = Column('CODE', 'INTEGER', nullable=False, sequence_name='GEN_DESC')
        t.columns.extend([col_id, col_desc])

        self.mock_fb_cur.fetchmany.return_value = []
        # Return -2 for increment_by of gen_desc from pg_sequences
        self.mock_pg_cur.fetchone.return_value = (-2,)
        success = self.migrator.import_data([t], max_workers=1)
        self.assertTrue(success)

        executed_queries = [call[0][0] for call in self.mock_pg_cur.execute.call_args_list]
        sync_queries = [q for q in executed_queries if 'SELECT setval(' in q]
        self.assertEqual(len(sync_queries), 2)

        # 1. Identity column sync query must preserve original current value 500
        id_sync = sync_queries[0]
        self.assertIn('GREATEST(500,', id_sync)

        # 2. Descending sequence sync query must use LEAST and MIN
        desc_sync = sync_queries[1]
        self.assertIn('WITH min_calc AS MATERIALIZED', desc_sync)
        self.assertIn('LEAST(', desc_sync)
        self.assertIn('SELECT MIN("code")', desc_sync)

    def test_check_source_consistency_read_only(self):
        self.mock_fb_cur.fetchone.side_effect = [
            (1, 0),  # MON$READ_ONLY = 1, MON$SHUTDOWN_MODE = 0
            (0,),    # active_attachments = 0
        ]
        info = self.migrator.check_source_consistency()
        self.assertTrue(info['is_read_only'])
        self.assertFalse(info['is_shutdown'])
        self.assertEqual(info['active_attachments'], 0)

    def test_check_source_consistency_warns_on_live_source(self):
        self.mock_fb_cur.fetchone.side_effect = [
            (0, 0),  # MON$READ_ONLY = 0, MON$SHUTDOWN_MODE = 0
            (3,),    # active_attachments = 3
        ]
        with self.assertLogs('engine.data_migrator', level='WARNING') as cm:
            info = self.migrator.check_source_consistency()
            self.assertFalse(info['is_read_only'])
            self.assertEqual(info['active_attachments'], 3)
            self.assertTrue(any('Source Firebird database is LIVE' in msg for msg in cm.output))

    def test_blob_memory_budget_flushes_incrementally_by_bytes(self):
        from engine.data_migrator import _import_single_table

        table = Table('TAB_BLOB')
        table.columns.append(Column('ID', 'INTEGER', nullable=False))
        table.columns.append(Column('ARQUIVO', 'BLOB SUBTYPE 0', nullable=True))

        # 4 rows of 300 bytes each -> total serialized ~ 2400 hex chars + overhead
        raw_rows = [(i, b'X' * 300) for i in range(1, 5)]
        self.mock_fb_cur.fetchmany.side_effect = [raw_rows, []]

        # Set a small budget (400 bytes) so each row or two triggers a flush
        rows_imported, _ = _import_single_table(
            table, self.mock_fb_cur, self.mock_pg_cur, self.mock_pg_con, max_buffer_bytes=400
        )
        self.assertEqual(rows_imported, 4)
        # copy_expert should have been called multiple times (flushes) rather than once
        self.assertGreaterEqual(self.mock_pg_cur.copy_expert.call_count, 3)



