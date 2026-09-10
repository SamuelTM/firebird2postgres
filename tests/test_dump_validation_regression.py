import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from config import DumpFiles
from engine.database_migrator import DatabaseMigrator
from engine.ddl_exporter import DdlExporter
from models.firebird_types import build_domain_mapping
from utils.sql_runner import SqlRunner, extract_defined_objects


class _RowsCursor:
    """Minimal cursor stub feeding catalog rows to the real mapping code."""

    def __init__(self, rows):
        self._rows = list(rows)

    def execute(self, *args, **kwargs):
        return None

    def fetchall(self):
        return list(self._rows)


class TestDumpValidationRegression(unittest.TestCase):
    """
    Regression tests verifying that DDL dumps are validated by object identity and type,
    that catalog query failures prevent approval, and that incomplete dumps are rejected
    before DROP of the destination database.
    """

    def setUp(self):
        self.mock_fb = MagicMock()
        self.mock_pg = MagicMock()
        self.mock_cur_pg = MagicMock()
        self.mock_pg.cursor.return_value = self.mock_cur_pg
        self.migrator = DatabaseMigrator(self.mock_fb, self.mock_pg)

    def test_extract_defined_objects_all_types(self):
        """extract_defined_objects correctly extracts names for procedures, views, triggers, and domains."""
        # Procedures / Functions
        proc_sql = """
        DROP FUNCTION IF EXISTS "sp_one" CASCADE;
        CREATE FUNCTION "sp_one"(id integer) RETURNS void AS $$ BEGIN END; $$ LANGUAGE plpgsql;
        DROP PROCEDURE IF EXISTS "sp_two";
        CREATE OR REPLACE PROCEDURE "sp_two"() AS $$ BEGIN END; $$ LANGUAGE plpgsql;
        """
        self.assertEqual(extract_defined_objects(proc_sql, 'PROCEDURE'), {'SP_ONE', 'SP_TWO'})

        # Views
        view_sql = """
        DROP VIEW IF EXISTS "vw_active" CASCADE;
        CREATE VIEW "vw_active" AS SELECT 1;
        CREATE OR REPLACE VIEW public."vw_summary" ("c1", "c2") AS SELECT 1, 2;
        """
        self.assertEqual(extract_defined_objects(view_sql, 'VIEW'), {'VW_ACTIVE', 'VW_SUMMARY'})

        # Triggers (with and without sequence prefixes)
        trig_sql = """
        CREATE OR REPLACE FUNCTION "trg_00000_bi_ped_func"() RETURNS trigger AS $$ BEGIN RETURN NEW; END; $$ LANGUAGE plpgsql;
        CREATE TRIGGER "trg_00000_bi_ped" BEFORE INSERT ON "pedidos" FOR EACH ROW EXECUTE FUNCTION "trg_00000_bi_ped_func"();
        CREATE TRIGGER "BI_CLIENTES" BEFORE INSERT ON "clientes" FOR EACH ROW EXECUTE FUNCTION "f"();
        """
        trig_objs = extract_defined_objects(trig_sql, 'TRIGGER')
        self.assertIn('TRG_00000_BI_PED', trig_objs)
        self.assertIn('BI_CLIENTES', trig_objs)
        self.assertNotIn('TRG_00000_BI_PED_FUNC', trig_objs)
        # No fuzzy trg_ sequence-prefix alias: one definition, one identity.
        self.assertNotIn('BI_PED', trig_objs)

        # Domains (in DO block)
        dom_sql = """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type t WHERE t.typname = 'status_dom') THEN
                EXECUTE 'CREATE DOMAIN public."status_dom" AS VARCHAR(10);';
            END IF;
        END $$;
        CREATE DOMAIN "int_code" AS INTEGER;
        """
        dom_objs = extract_defined_objects(dom_sql, 'DOMAIN')
        self.assertIn('STATUS_DOM', dom_objs)
        self.assertIn('INT_CODE', dom_objs)
        # No fuzzy _dom alias: one defined domain satisfies exactly one identity.
        self.assertNotIn('STATUS', dom_objs)

    def test_two_procedures_one_removed_leaving_drop_and_create_fails_before_drop(self):
        """
        Regression: Firebird has 2 procedures. Export produces DROP + CREATE for each.
        One procedure is removed completely, leaving DROP + CREATE (2 statements) of the other.
        Validation MUST reject before DROP (statement count 2 was falsely approved under old logic).
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # File has 2 statements: DROP and CREATE for PROC_ALPHA only
            proc_file = os.path.join(tmpdir, DumpFiles.PROCEDURES_PG)
            with open(proc_file, "w", encoding="utf-8") as f:
                f.write(
                    'DROP FUNCTION IF EXISTS "proc_alpha" CASCADE;\n'
                    'CREATE FUNCTION "proc_alpha"() RETURNS void AS $$ BEGIN END; $$ LANGUAGE plpgsql;\n'
                )

            # Other categories empty
            for cat in [DumpFiles.DOMAINS_PG, DumpFiles.VIEWS_PG, DumpFiles.TRIGGERS_PG]:
                with open(os.path.join(tmpdir, cat), "w", encoding="utf-8") as f:
                    f.write("/* EMPTY */\n")

            # Catalog reports 2 procedures expected: PROC_ALPHA and PROC_BETA
            self.migrator.ddl_exporter.get_source_objects = MagicMock(return_value={
                DumpFiles.DOMAINS_PG: [],
                DumpFiles.PROCEDURES_PG: ["PROC_ALPHA", "PROC_BETA"],
                DumpFiles.VIEWS_PG: [],
                DumpFiles.TRIGGERS_PG: [],
            })

            drop_called = []
            self.migrator.drop_schema = lambda: drop_called.append(True)

            with self.assertRaises(ValueError) as ctx:
                self.migrator.validate_artifacts(output_dir=tmpdir)

            self.assertIn("missing 1 expected PROCEDURE(s): PROC_BETA", str(ctx.exception))
            self.assertEqual(len(drop_called), 0, "drop_schema MUST NOT be called when an object is missing")

    def test_catalog_query_failure_prevents_drop(self):
        """
        Regression: Catalog query failure in get_source_objects / get_source_object_counts
        must NOT be swallowed as 0/empty; it must raise and prevent DROP.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            for cat in [DumpFiles.DOMAINS_PG, DumpFiles.PROCEDURES_PG, DumpFiles.VIEWS_PG, DumpFiles.TRIGGERS_PG]:
                with open(os.path.join(tmpdir, cat), "w", encoding="utf-8") as f:
                    f.write("/* EMPTY */\n")

            # Mock Firebird catalog query failing with an exception
            mock_cursor = MagicMock()
            self.mock_fb.cursor.return_value = mock_cursor
            mock_cursor.execute.side_effect = RuntimeError("Firebird connection lost or catalog error")

            drop_called = []
            self.migrator.drop_schema = lambda: drop_called.append(True)

            with self.assertRaises(RuntimeError) as ctx:
                self.migrator.validate_artifacts(output_dir=tmpdir)

            self.assertIn("Firebird connection lost or catalog error", str(ctx.exception))
            self.assertEqual(len(drop_called), 0, "drop_schema MUST NOT be called on catalog failure")

    def test_missing_file_when_objects_expected_prevents_drop(self):
        """
        Regression: Missing dump file when source objects are expected must raise
        FileNotFoundError and prevent DROP.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create only DOMAINS, VIEWS, TRIGGERS; PROCEDURES_PG is missing
            for cat in [DumpFiles.DOMAINS_PG, DumpFiles.VIEWS_PG, DumpFiles.TRIGGERS_PG]:
                with open(os.path.join(tmpdir, cat), "w", encoding="utf-8") as f:
                    f.write("/* EMPTY */\n")

            self.migrator.ddl_exporter.get_source_objects = MagicMock(return_value={
                DumpFiles.DOMAINS_PG: [],
                DumpFiles.PROCEDURES_PG: ["SP_CALCULATE"],
                DumpFiles.VIEWS_PG: [],
                DumpFiles.TRIGGERS_PG: [],
            })

            drop_called = []
            self.migrator.drop_schema = lambda: drop_called.append(True)

            with self.assertRaises(FileNotFoundError) as ctx:
                self.migrator.validate_artifacts(output_dir=tmpdir)

            self.assertIn(DumpFiles.PROCEDURES_PG, str(ctx.exception))
            self.assertEqual(len(drop_called), 0, "drop_schema MUST NOT be called when file is missing")

    def test_complete_dump_passes_validation_and_allows_drop(self):
        """When all expected objects are present in the dump files, validation succeeds."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Procedures file with both expected procedures
            proc_file = os.path.join(tmpdir, DumpFiles.PROCEDURES_PG)
            with open(proc_file, "w", encoding="utf-8") as f:
                f.write(
                    'DROP FUNCTION IF EXISTS "proc_alpha" CASCADE;\n'
                    'CREATE FUNCTION "proc_alpha"() RETURNS void AS $$ BEGIN END; $$ LANGUAGE plpgsql;\n'
                    'DROP FUNCTION IF EXISTS "proc_beta" CASCADE;\n'
                    'CREATE FUNCTION "proc_beta"() RETURNS void AS $$ BEGIN END; $$ LANGUAGE plpgsql;\n'
                )

            for cat in [DumpFiles.DOMAINS_PG, DumpFiles.VIEWS_PG, DumpFiles.TRIGGERS_PG]:
                with open(os.path.join(tmpdir, cat), "w", encoding="utf-8") as f:
                    f.write("/* EMPTY */\n")

            self.migrator.ddl_exporter.get_source_objects = MagicMock(return_value={
                DumpFiles.DOMAINS_PG: [],
                DumpFiles.PROCEDURES_PG: ["PROC_ALPHA", "PROC_BETA"],
                DumpFiles.VIEWS_PG: [],
                DumpFiles.TRIGGERS_PG: [],
            })

            drop_called = []
            self.migrator.drop_schema = lambda: drop_called.append(True)

            verified = self.migrator.validate_artifacts(output_dir=tmpdir)
            self.assertFalse(verified[DumpFiles.PROCEDURES_PG])
            self.assertTrue(verified[DumpFiles.DOMAINS_PG])
            self.assertTrue(verified[DumpFiles.VIEWS_PG])
            self.assertTrue(verified[DumpFiles.TRIGGERS_PG])

    def test_textual_mention_inside_function_is_not_a_definition(self):
        """
        P1 regression: a dump defining P1 whose body only MENTIONS P2 in a
        RAISE NOTICE string must identify {P1}, and validation expecting
        {P1, P2} must fail reporting P2 as missing.
        """
        dump = (
            'CREATE FUNCTION "p1"() RETURNS void AS $$\n'
            'BEGIN\n'
            "    RAISE NOTICE 'CREATE FUNCTION p2()';\n"
            'END;\n'
            '$$ LANGUAGE plpgsql;\n'
        )
        self.assertEqual(extract_defined_objects(dump, 'PROCEDURE'), {'P1'})

        with tempfile.TemporaryDirectory() as tmpdir:
            proc_file = os.path.join(tmpdir, DumpFiles.PROCEDURES_PG)
            with open(proc_file, "w", encoding="utf-8") as f:
                f.write(dump)
            for cat in [DumpFiles.DOMAINS_PG, DumpFiles.VIEWS_PG, DumpFiles.TRIGGERS_PG]:
                with open(os.path.join(tmpdir, cat), "w", encoding="utf-8") as f:
                    f.write("/* EMPTY */\n")

            self.migrator.ddl_exporter.get_source_objects = MagicMock(return_value={
                DumpFiles.DOMAINS_PG: [],
                DumpFiles.PROCEDURES_PG: ["P1", "P2"],
                DumpFiles.VIEWS_PG: [],
                DumpFiles.TRIGGERS_PG: [],
            })

            drop_called = []
            self.migrator.drop_schema = lambda: drop_called.append(True)

            with self.assertRaises(ValueError) as ctx:
                self.migrator.validate_artifacts(output_dir=tmpdir)

            self.assertIn("missing 1 expected PROCEDURE(s): P2", str(ctx.exception))
            self.assertEqual(drop_called, [])

    def test_escaped_quotes_in_identifiers(self):
        """
        P1 regression: "a""b" is a single identifier (a"b), not A.
        Applies to definitions and to EXECUTE literals in DO blocks.
        """
        dump = (
            'CREATE FUNCTION "a""b"() RETURNS void AS $$ BEGIN END; $$ LANGUAGE plpgsql;\n'
            'CREATE VIEW "v""x" AS SELECT 1;\n'
        )
        self.assertEqual(extract_defined_objects(dump, 'PROCEDURE'), {'A"B'})
        self.assertEqual(extract_defined_objects(dump, 'VIEW'), {'V"X'})

    def test_hostile_identifier_contents_create_no_extra_identities(self):
        """
        P1 regression: identifier CONTENT that looks like commands, comments
        or escaped quotes is one single name. Nothing inside quotes may
        fabricate a second identity of any category.
        """
        dump = (
            'CREATE FUNCTION "CREATE DOMAIN fake"() RETURNS void AS $$\n'
            'BEGIN\n'
            "    RAISE NOTICE 'CREATE FUNCTION ghost_fn()';\n"
            'END;\n'
            '$$ LANGUAGE plpgsql;\n'
            'CREATE VIEW "my -- view" AS SELECT 1;\n'
            'CREATE VIEW "x /* y */ z" AS SELECT 1;\n'
            'CREATE TRIGGER "CREATE FUNCTION ghost_trg" BEFORE INSERT ON "t" '
            'FOR EACH ROW EXECUTE FUNCTION "f"();\n'
        )
        self.assertEqual(
            extract_defined_objects(dump, 'PROCEDURE'), {'CREATE DOMAIN FAKE'})
        self.assertEqual(
            extract_defined_objects(dump, 'DOMAIN'), set())
        self.assertEqual(
            extract_defined_objects(dump, 'VIEW'), {'MY -- VIEW', 'X /* Y */ Z'})
        self.assertEqual(
            extract_defined_objects(dump, 'TRIGGER'),
            {'CREATE FUNCTION GHOST_TRG'})
        self.assertNotIn('GHOST_FN', extract_defined_objects(dump))
        self.assertNotIn('FAKE', extract_defined_objects(dump))

    def test_schema_qualified_names_with_spaces_and_comments(self):
        """
        P2 regression: public.d, "public"."d", "public" . "d" and qualifiers
        split by comments all recognize D (never the schema). A dump with
        only such a domain must NOT satisfy an expected PUBLIC domain.
        """
        variants = [
            'CREATE DOMAIN public.d AS integer;',
            'CREATE DOMAIN "public"."d" AS integer;',
            'CREATE DOMAIN "public" . "d" AS integer;',
            'CREATE DOMAIN "public" /* schema comment */ . "d" AS integer;',
            'CREATE DOMAIN public -- trailing comment\n. d AS integer;',
        ]
        for sql in variants:
            with self.subTest(sql=sql):
                self.assertEqual(extract_defined_objects(sql, 'DOMAIN'), {'D'})

        with tempfile.TemporaryDirectory() as tmpdir:
            dom_file = os.path.join(tmpdir, DumpFiles.DOMAINS_PG)
            with open(dom_file, "w", encoding="utf-8") as f:
                f.write('CREATE DOMAIN "public" . "d" AS integer;\n')
            for cat in [DumpFiles.PROCEDURES_PG, DumpFiles.VIEWS_PG, DumpFiles.TRIGGERS_PG]:
                with open(os.path.join(tmpdir, cat), "w", encoding="utf-8") as f:
                    f.write("/* EMPTY */\n")

            runner = SqlRunner(MagicMock())
            with self.assertRaises(ValueError) as ctx:
                runner.validate_file(
                    dom_file, expected_objects=["PUBLIC"], object_type='DOMAIN')
            self.assertIn("missing 1 expected DOMAIN(s): PUBLIC", str(ctx.exception))

    def test_comments_inside_strings_neither_hide_nor_create_objects(self):
        """
        P1 regression: -- and /* */ markers inside string literals are text,
        not comments: they must not fabricate objects, and stripping them must
        not corrupt the surrounding definition. Real comments stay ignored.
        """
        dump = (
            '-- CREATE FUNCTION ghost_in_line_comment() RETURNS void;\n'
            '/* CREATE FUNCTION ghost_in_block_comment() RETURNS void; */\n'
            'CREATE FUNCTION "p1"() RETURNS void AS $$\n'
            'BEGIN\n'
            "    RAISE NOTICE '-- CREATE FUNCTION px() /* CREATE FUNCTION py() */';\n"
            'END;\n'
            '$$ LANGUAGE plpgsql;\n'
        )
        defined = extract_defined_objects(dump, 'PROCEDURE')
        self.assertEqual(defined, {'P1'})

    def test_exporter_do_blocks_count_as_definitions(self):
        """
        P1 regression: DO blocks effectively emitted by DdlExporter
        (EXECUTE 'CREATE DOMAIN ...' with ''-escaped quotes) define their
        domain; validation expecting it must pass.
        """
        do_block = DdlExporter._format_domain_postgres_ddl(
            'status_dom', 'VARCHAR(10)', None, False, None
        )
        self.assertIn('EXECUTE', do_block)
        defined = extract_defined_objects(do_block, 'DOMAIN')
        self.assertIn('STATUS_DOM', defined)

        with tempfile.TemporaryDirectory() as tmpdir:
            dom_file = os.path.join(tmpdir, DumpFiles.DOMAINS_PG)
            with open(dom_file, "w", encoding="utf-8") as f:
                f.write(do_block)
            for cat in [DumpFiles.PROCEDURES_PG, DumpFiles.VIEWS_PG, DumpFiles.TRIGGERS_PG]:
                with open(os.path.join(tmpdir, cat), "w", encoding="utf-8") as f:
                    f.write("/* EMPTY */\n")

            self.migrator.ddl_exporter.get_source_objects = MagicMock(return_value={
                DumpFiles.DOMAINS_PG: ["STATUS_DOM"],
                DumpFiles.PROCEDURES_PG: [],
                DumpFiles.VIEWS_PG: [],
                DumpFiles.TRIGGERS_PG: [],
            })

            verified = self.migrator.validate_artifacts(output_dir=tmpdir)
            self.assertFalse(verified[DumpFiles.DOMAINS_PG])

    def _mock_foo_domain_catalog(self):
        """
        Table FOO with domains FOO and FOO_DOM. The exact computed mapping is
        FOO -> foo_dom_dom and FOO_DOM -> foo_dom. Mocks the source catalog
        for both expected objects and the domain map.
        """
        mapping = build_domain_mapping(['FOO', 'FOO_DOM'], {'FOO'})
        self.assertEqual(mapping, {'FOO': 'foo_dom_dom', 'FOO_DOM': 'foo_dom'})
        self.migrator.ddl_exporter.get_source_objects = MagicMock(return_value={
            DumpFiles.DOMAINS_PG: ["FOO", "FOO_DOM"],
            DumpFiles.PROCEDURES_PG: [],
            DumpFiles.VIEWS_PG: [],
            DumpFiles.TRIGGERS_PG: [],
        })
        patcher = patch.object(DdlExporter, '_fetch_domain_map', return_value=mapping)
        patcher.start()
        self.addCleanup(patcher.stop)
        return mapping

    @staticmethod
    def _write_dump_files(tmpdir, domains_sql):
        with open(os.path.join(tmpdir, DumpFiles.DOMAINS_PG), "w", encoding="utf-8") as f:
            f.write(domains_sql)
        for cat in [DumpFiles.PROCEDURES_PG, DumpFiles.VIEWS_PG, DumpFiles.TRIGGERS_PG]:
            with open(os.path.join(tmpdir, cat), "w", encoding="utf-8") as f:
                f.write("/* EMPTY */\n")

    def test_complete_renamed_domains_pass_validation(self):
        """Both mapped domains present: exact mapping approves the dump."""
        self._mock_foo_domain_catalog()
        with tempfile.TemporaryDirectory() as tmpdir:
            self._write_dump_files(
                tmpdir,
                'CREATE DOMAIN "foo_dom_dom" AS INTEGER;\n'
                'CREATE DOMAIN "foo_dom" AS VARCHAR(10);\n'
            )
            verified = self.migrator.validate_artifacts(output_dir=tmpdir)
            self.assertFalse(verified[DumpFiles.DOMAINS_PG])

    def test_removing_renamed_domain_fails_validation(self):
        """
        P1 acceptance: removing foo_dom_dom (the PG name of source FOO)
        from an otherwise complete dump MUST fail, reporting source FOO.
        """
        self._mock_foo_domain_catalog()
        with tempfile.TemporaryDirectory() as tmpdir:
            self._write_dump_files(
                tmpdir,
                'CREATE DOMAIN "foo_dom" AS VARCHAR(10);\n'
            )

            drop_called = []
            self.migrator.drop_schema = lambda: drop_called.append(True)

            with self.assertRaises(ValueError) as ctx:
                self.migrator.validate_artifacts(output_dir=tmpdir)

            self.assertIn("missing 1 expected DOMAIN(s): FOO", str(ctx.exception))
            self.assertEqual(drop_called, [])

    def test_single_domain_cannot_satisfy_two_identities(self):
        """
        P1 regression: a dump with only foo_dom_dom must NOT satisfy both
        FOO and FOO_DOM (the old _dom-stripping alias approved this).
        """
        self._mock_foo_domain_catalog()
        with tempfile.TemporaryDirectory() as tmpdir:
            self._write_dump_files(
                tmpdir,
                'CREATE DOMAIN "foo_dom_dom" AS INTEGER;\n'
            )

            with self.assertRaises(ValueError) as ctx:
                self.migrator.validate_artifacts(output_dir=tmpdir)

            self.assertIn("missing 1 expected DOMAIN(s): FOO_DOM", str(ctx.exception))

    @staticmethod
    def _trigger_ddl(pg_name, table='t'):
        return (
            f'CREATE OR REPLACE FUNCTION "{pg_name}_func"() RETURNS TRIGGER '
            f'AS $$ BEGIN RETURN NEW; END; $$ LANGUAGE plpgsql;\n'
            f'CREATE TRIGGER "{pg_name}" BEFORE INSERT ON "{table}" FOR EACH ROW '
            f'EXECUTE FUNCTION "{pg_name}_func"();\n'
        )

    def _mock_trigger_catalog(self, rows):
        """
        Mocks the source trigger catalog with (name, sequence) rows and lets
        the REAL _fetch_trigger_map compute the exact mapping. Returns it.
        """
        from engine.ddl_exporter import DdlExporter as _DdlExporter
        mapping = _DdlExporter._fetch_trigger_map(_RowsCursor(rows))
        self.migrator.ddl_exporter.get_source_objects = MagicMock(return_value={
            DumpFiles.DOMAINS_PG: [],
            DumpFiles.PROCEDURES_PG: [],
            DumpFiles.VIEWS_PG: [],
            DumpFiles.TRIGGERS_PG: [name for name, _ in rows],
        })
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = list(rows)
        self.mock_fb.cursor.return_value = mock_cursor
        return mapping

    @staticmethod
    def _write_trigger_dump(tmpdir, triggers_sql):
        with open(os.path.join(tmpdir, DumpFiles.TRIGGERS_PG), "w", encoding="utf-8") as f:
            f.write(triggers_sql)
        for cat in [DumpFiles.DOMAINS_PG, DumpFiles.PROCEDURES_PG, DumpFiles.VIEWS_PG]:
            with open(os.path.join(tmpdir, cat), "w", encoding="utf-8") as f:
                f.write("/* EMPTY */\n")

    def test_complete_prefixed_triggers_pass_validation(self):
        """Both position-prefixed definitions present: exact mapping approves."""
        mapping = self._mock_trigger_catalog([("BI", 0), ("TRG_00000_BI", 5)])
        self.assertEqual(mapping, {"BI": "trg_00000_bi", "TRG_00000_BI": "trg_00005_trg_00000_bi"})
        with tempfile.TemporaryDirectory() as tmpdir:
            self._write_trigger_dump(
                tmpdir,
                self._trigger_ddl("trg_00000_bi")
                + self._trigger_ddl("trg_00005_trg_00000_bi"),
            )
            verified = self.migrator.validate_artifacts(output_dir=tmpdir)
            self.assertFalse(verified[DumpFiles.TRIGGERS_PG])

    def test_removing_either_prefixed_trigger_definition_fails(self):
        """
        P1 acceptance: source triggers BI (seq 0) and TRG_00000_BI (seq 5).
        Removing EITHER definition must fail before DROP, reporting the
        source identity — one definition can no longer satisfy both.
        """
        self._mock_trigger_catalog([("BI", 0), ("TRG_00000_BI", 5)])
        cases = [
            (self._trigger_ddl("trg_00005_trg_00000_bi"), "BI"),
            (self._trigger_ddl("trg_00000_bi"), "TRG_00000_BI"),
        ]
        for dump_sql, missing in cases:
            with self.subTest(missing=missing), tempfile.TemporaryDirectory() as tmpdir:
                self._write_trigger_dump(tmpdir, dump_sql)

                drop_called = []
                self.migrator.drop_schema = lambda: drop_called.append(True)

                with self.assertRaises(ValueError) as ctx:
                    self.migrator.validate_artifacts(output_dir=tmpdir)

                self.assertIn(f"missing 1 expected TRIGGER(s): {missing}", str(ctx.exception))
                self.assertEqual(drop_called, [])

    def test_trigger_position_is_part_of_identity(self):
        """
        P1 regression: positions differ, so trg_00000_bi must NOT satisfy a
        BI whose sequence is 7 (exact pg name trg_00007_bi).
        """
        self._mock_trigger_catalog([("BI", 7)])
        with tempfile.TemporaryDirectory() as tmpdir:
            self._write_trigger_dump(tmpdir, self._trigger_ddl("trg_00000_bi"))
            with self.assertRaises(ValueError) as ctx:
                self.migrator.validate_artifacts(output_dir=tmpdir)
            self.assertIn("missing 1 expected TRIGGER(s): BI", str(ctx.exception))

    def test_trigger_name_with_trg_prefix_validates_by_mapping(self):
        """
        P1 regression: a source trigger already starting with trg_
        (TRG_TEST, seq 3 -> trg_00003_trg_test) validates through the exact
        mapping, while extraction alone holds no bare TRG_TEST alias.
        """
        mapping = self._mock_trigger_catalog([("TRG_TEST", 3)])
        self.assertEqual(mapping, {"TRG_TEST": "trg_00003_trg_test"})
        dump_sql = self._trigger_ddl("trg_00003_trg_test")
        defined = extract_defined_objects(dump_sql, 'TRIGGER')
        self.assertIn('TRG_00003_TRG_TEST', defined)
        self.assertNotIn('TRG_TEST', defined)
        with tempfile.TemporaryDirectory() as tmpdir:
            self._write_trigger_dump(tmpdir, dump_sql)
            verified = self.migrator.validate_artifacts(output_dir=tmpdir)
            self.assertFalse(verified[DumpFiles.TRIGGERS_PG])


if __name__ == "__main__":
    unittest.main()
