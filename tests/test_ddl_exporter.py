import os
import tempfile
import unittest
from unittest.mock import MagicMock

from engine.ddl_exporter import DdlExporter


class TestDdlExporterTriggers(unittest.TestCase):
    def test_export_firebird_triggers_preserves_execution_sequence(self):
        # Firebird trigger data:
        # Trigger 1: Z_CALCULA with sequence 0
        # Trigger 2: A_VALIDA with sequence 10
        # In Firebird, Z_CALCULA executes BEFORE A_VALIDA due to sequence (0 < 10).
        # In PostgreSQL, triggers execute alphabetically by trigger name.
        # Exporting with trg_{seq:05d}_{name} guarantees PostgreSQL executes them in sequence.
        mock_fb_con = MagicMock()
        mock_cursor = MagicMock()
        mock_fb_con.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            ("Z_CALCULA", "PEDIDOS", 1, "AS BEGIN NEW.TOTAL = 100; END;", 0),
            ("A_VALIDA", "PEDIDOS", 1, "AS BEGIN IF (NEW.TOTAL < 0) THEN EXCEPTION; END;", 10),
        ]

        exporter = DdlExporter(mock_fb_con)

        with tempfile.TemporaryDirectory() as tmpdir:
            fb_out = os.path.join(tmpdir, "fb_triggers.sql")
            pg_out = os.path.join(tmpdir, "pg_triggers.sql")

            exporter.export_firebird_triggers(output_file=fb_out, converted_file=pg_out)

            with open(fb_out, "r", encoding="utf-8") as f:
                fb_content = f.read()
            with open(pg_out, "r", encoding="utf-8") as f:
                pg_content = f.read()

            # Firebird dump retains original names
            self.assertIn("CREATE TRIGGER Z_CALCULA FOR PEDIDOS", fb_content)
            self.assertIn("CREATE TRIGGER A_VALIDA FOR PEDIDOS", fb_content)

            # PostgreSQL dump uses sequence-prefixed names
            self.assertIn('CREATE TRIGGER "trg_00000_z_calcula"', pg_content)
            self.assertIn('CREATE OR REPLACE FUNCTION "trg_00000_z_calcula_func"()', pg_content)
            self.assertIn('CREATE TRIGGER "trg_00010_a_valida"', pg_content)
            self.assertIn('CREATE OR REPLACE FUNCTION "trg_00010_a_valida_func"()', pg_content)

            # Alphabetical ordering in PostgreSQL matches execution order:
            # "trg_00000_z_calcula" < "trg_00010_a_valida"
            self.assertLess("trg_00000_z_calcula", "trg_00010_a_valida")

    def test_export_firebird_generators(self):
        mock_fb_con = MagicMock()
        mock_cursor = MagicMock()
        mock_fb_con.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            ("GEN_STANDALONE",),
            ("GEN_APAC_ID",),
        ]
        mock_cursor.fetchone.side_effect = [
            (0,),
            (300,),
        ]

        exporter = DdlExporter(mock_fb_con)

        with tempfile.TemporaryDirectory() as tmpdir:
            fb_out = os.path.join(tmpdir, "fb_generators.sql")
            pg_out = os.path.join(tmpdir, "pg_sequences.sql")

            exporter.export_firebird_generators(output_file=fb_out, converted_file=pg_out)

            with open(fb_out, "r", encoding="utf-8") as f:
                fb_content = f.read()
            with open(pg_out, "r", encoding="utf-8") as f:
                pg_content = f.read()

            self.assertIn("CREATE SEQUENCE GEN_STANDALONE;", fb_content)
            self.assertIn("SET GENERATOR GEN_STANDALONE TO 0;", fb_content)
            self.assertIn("CREATE SEQUENCE GEN_APAC_ID;", fb_content)
            self.assertIn("SET GENERATOR GEN_APAC_ID TO 300;", fb_content)

            self.assertIn('CREATE SEQUENCE "gen_standalone";', pg_content)
            self.assertIn('CREATE SEQUENCE "gen_apac_id" START WITH 301;', pg_content)

    def test_export_firebird_generators_raises_on_failure(self):
        mock_fb_con = MagicMock()
        mock_cursor = MagicMock()
        mock_fb_con.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [("GEN_FAIL",)]
        mock_cursor.fetchone.side_effect = Exception("Failed to query generator")

        exporter = DdlExporter(mock_fb_con)
        with tempfile.TemporaryDirectory() as tmpdir:
            fb_out = os.path.join(tmpdir, "fb.sql")
            pg_out = os.path.join(tmpdir, "pg.sql")
            with self.assertRaises(RuntimeError) as cm:
                exporter.export_firebird_generators(output_file=fb_out, converted_file=pg_out)
            self.assertIn("Failed to read current value for generator 'GEN_FAIL'", str(cm.exception))


class TestDdlExporterViews(unittest.TestCase):
    def test_fetch_view_columns_preserves_quotes_and_escapes(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            ("Order Total",),
            ("SELECT",),
            ('Col "Special"',),
            ("ID",),
        ]
        cols = DdlExporter._fetch_view_columns(mock_cursor, "V_TEST")
        self.assertEqual(cols, ['"Order Total"', '"SELECT"', '"Col ""Special"""', '"ID"'])

    def test_format_view_firebird_ddl(self):
        col_names = ['"Order Total"', '"SELECT"']
        source = "SELECT total, sel FROM orders"
        ddl = DdlExporter._format_view_firebird_ddl("V_ORDERS", col_names, source)
        expected = 'CREATE OR ALTER VIEW "V_ORDERS" ("Order Total", "SELECT") AS\nSELECT total, sel FROM orders\n\n'
        self.assertEqual(ddl, expected)

    def test_resolve_view_dependency_order_reverse_alphabetical(self):
        mock_cursor = MagicMock()
        # A_CHILD depends on Z_BASE (in Firebird RDB$DEPENDENCIES: dependent=A_CHILD, depended_on=Z_BASE)
        mock_cursor.fetchall.return_value = [
            ("A_CHILD", "Z_BASE"),
            ("A_CHILD", "SOME_TABLE"),  # Not in view_names, should be ignored
        ]
        ordered = DdlExporter._resolve_view_dependency_order(mock_cursor, {"A_CHILD", "Z_BASE"})
        self.assertEqual(ordered, ["Z_BASE", "A_CHILD"])

    def test_resolve_view_dependency_order_multilevel_chain(self):
        mock_cursor = MagicMock()
        # Chain: A_LEAF -> M_MID -> Z_ROOT
        mock_cursor.fetchall.return_value = [
            ("A_LEAF", "M_MID"),
            ("M_MID", "Z_ROOT"),
        ]
        ordered = DdlExporter._resolve_view_dependency_order(mock_cursor, {"A_LEAF", "M_MID", "Z_ROOT"})
        self.assertEqual(ordered, ["Z_ROOT", "M_MID", "A_LEAF"])

    def test_export_transpiled_ddl_raises_and_saves_diagnostics_on_failure(self):
        items = [
            ("PROC_GOOD", "CREATE PROCEDURE PROC_GOOD AS BEGIN DUMMY = 1; END;"),
            ("PROC_BAD", "CREATE PROCEDURE PROC_BAD AS BEGIN INVALID SYNTAX ???; END;"),
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = os.path.join(tmpdir, "out.sql")
            conv_file = os.path.join(tmpdir, "conv.sql")
            with self.assertRaises(RuntimeError) as cm:
                DdlExporter._export_transpiled_ddl(
                    items=items,
                    output_file=out_file,
                    converted_file=conv_file,
                    object_type="PROCEDURE",
                    firebird_header="-- FB HEADER\n",
                    postgres_header="-- PG HEADER\n",
                )
            self.assertIn("Transpilation failed for 1 procedure(s)", str(cm.exception))
            self.assertIn("PROC_BAD", str(cm.exception))
            with open(conv_file, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("[TRANSPILER FAILED] PROCEDURE PROC_BAD", content)

    def test_fetch_procedure_parameters_with_defaults_and_domains(self):
        mock_cursor = MagicMock()
        # Mock result for RDB$PROCEDURE_PARAMETERS joined with RDB$FIELDS
        # Tuple columns:
        # 0: pp.RDB$PARAMETER_NAME
        # 1: pp.RDB$PARAMETER_TYPE (0=in, 1=out)
        # 2: pp.RDB$PARAMETER_NUMBER
        # 3: f.RDB$FIELD_TYPE
        # 4: f.RDB$FIELD_SUB_TYPE
        # 5: f.RDB$FIELD_LENGTH
        # 6: f.RDB$FIELD_PRECISION
        # 7: f.RDB$FIELD_SCALE
        # 8: pp.RDB$FIELD_SOURCE (domain name or system domain)
        # 9: pp.RDB$DEFAULT_SOURCE
        # 10: pp.RDB$NULL_FLAG
        # 11: f.RDB$NULL_FLAG
        # 12: f.RDB$DEFAULT_SOURCE
        mock_cursor.fetchall.return_value = [
            ("P_ID", 0, 0, 8, 0, 4, 0, 0, "DM_ID", "= 1", 1, 0, None),
            ("P_NAME", 0, 1, 37, 0, 50, 0, 0, "RDB$123", "DEFAULT 'ANON'", 0, 0, None),
            ("OUT_STATUS", 1, 2, 37, 0, 10, 0, 0, "DM_STATUS", None, 0, 0, None),
        ]
        in_params, out_params = DdlExporter._fetch_procedure_parameters(mock_cursor, "SP_TEST")
        self.assertEqual(len(in_params), 2)
        self.assertEqual(len(out_params), 1)
        self.assertIn("P_ID DM_ID NOT NULL DEFAULT 1", in_params[0])
        self.assertIn("P_NAME VARCHAR(50) DEFAULT 'ANON'", in_params[1])
        self.assertIn("OUT_STATUS DM_STATUS", out_params[0])

    def test_format_domain_postgres_ddl_transpiles_check_and_default(self):
        pg_ddl = DdlExporter._format_domain_postgres_ddl(
            pg_domain_name="dm_test",
            pg_type="INTEGER",
            default_source="DEFAULT IIF(1=1, 1, 0)",
            not_null=False,
            validation_source="CHECK (IIF(VALUE > 0, 1, 0) = 1)",
        )
        self.assertIn("DEFAULT CASE WHEN 1=1 THEN 1 ELSE 0 END", pg_ddl)
        self.assertIn("CHECK (CASE WHEN VALUE > 0 THEN 1 ELSE 0 END = 1)", pg_ddl)
        self.assertNotIn("IIF", pg_ddl)


if __name__ == '__main__':
    unittest.main()


