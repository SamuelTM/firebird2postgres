import os
import tempfile
import unittest
from unittest.mock import MagicMock

from config import DumpFiles
from engine.database_migrator import DatabaseMigrator
from engine.ddl_exporter import DdlExporter
from utils.sql_runner import SqlRunner, extract_defined_objects


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
        self.assertIn('BI_PED', trig_objs)
        self.assertIn('TRG_00000_BI_PED', trig_objs)
        self.assertIn('BI_CLIENTES', trig_objs)
        self.assertNotIn('TRG_00000_BI_PED_FUNC', trig_objs)

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
        self.assertIn('STATUS', dom_objs)  # _dom stripped
        self.assertIn('INT_CODE', dom_objs)

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


if __name__ == "__main__":
    unittest.main()
