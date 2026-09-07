import unittest
from unittest.mock import MagicMock
from transpiler import FirebirdToPostgresVisitor
from engine import DatabaseMigrator, DdlExporter, SchemaExtractor


class TestFirstSkipSequenceRegression(unittest.TestCase):
    """
    Regression tests for FIRST/SKIP limit expressions, sequence increment metadata,
    and rejection before destructive DROP execution.
    """

    # 1. FIRST(IIF(...))
    def test_first_with_iif_expression(self):
        fb_sql = "CREATE VIEW V AS SELECT FIRST (IIF(X > 0, 10, 20)) COL FROM T;"
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("LIMIT (CASE WHEN X > 0 THEN 10 ELSE 20 END)", pg_sql)

    def test_first_with_iif_expression_without_outer_parens(self):
        fb_sql = "CREATE VIEW V AS SELECT FIRST IIF(X > 0, 10, 20) COL FROM T;"
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("LIMIT (CASE WHEN X > 0 THEN 10 ELSE 20 END)", pg_sql)

    # 2. SKIP with variable
    def test_skip_with_variable_prefixed_by_colon(self):
        fb_sql = "CREATE PROCEDURE P (V_SKIP INTEGER) AS BEGIN FOR SELECT SKIP :V_SKIP COL FROM T INTO :COL DO SUSPEND; END;"
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("OFFSET V_SKIP", pg_sql)

    def test_skip_with_variable_without_colon(self):
        fb_sql = "CREATE PROCEDURE P (V_SKIP INTEGER) AS BEGIN FOR SELECT SKIP V_SKIP COL FROM T INTO :COL DO SUSPEND; END;"
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("OFFSET V_SKIP", pg_sql)

    def test_first_and_skip_with_variables(self):
        fb_sql = "CREATE PROCEDURE P (V_FIRST INTEGER, V_SKIP INTEGER) AS BEGIN FOR SELECT FIRST V_FIRST SKIP V_SKIP COL FROM T INTO :COL DO SUSPEND; END;"
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("LIMIT V_FIRST OFFSET V_SKIP", pg_sql)

    # 3. Nested expressions
    def test_first_with_nested_arithmetic_expressions(self):
        fb_sql = "CREATE VIEW V AS SELECT FIRST ((X + 1) * 2) COL FROM T;"
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("LIMIT ((X + 1) * 2)", pg_sql)

    def test_first_with_nested_iif_expressions(self):
        fb_sql = "CREATE VIEW V AS SELECT FIRST (IIF(A > 0, (B + 1), (C - 1))) COL FROM T;"
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("LIMIT (CASE WHEN A > 0 THEN (B + 1) ELSE (C - 1) END)", pg_sql)

    # 4. GEN_ID(G,1) with increment 10
    def test_first_gen_id_incompatible_increment_rejected_without_fallback(self):
        fb_sql = "CREATE VIEW V AS SELECT FIRST (GEN_ID(G, 1)) COL FROM T;"
        with self.assertRaises(RuntimeError) as cm:
            FirebirdToPostgresVisitor.transpile(fb_sql, sequence_increments={'g': 10})
        # Verify rejection mentions sequence configured increment
        self.assertIn("sequence configured increment is 10", str(cm.exception))
        # Ensure it NEVER falls back to generating invalid PostgreSQL LIMIT (GEN_ID(G,1))
        self.assertNotIn("LIMIT (GEN_ID(G, 1))", str(cm.exception))

    def test_schema_computed_column_incompatible_increment_rejected(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            ("COMP_COL", 16, 0, 8, 1, 0, 0, None, None, "RDB$1", "GEN_ID(G, 1)"),
        ]
        with self.assertRaises(RuntimeError) as cm:
            SchemaExtractor._extract_columns(
                mock_cursor, "SALES", {"SALES"}, sequence_increments={'g': 10}
            )
        err_msg = str(cm.exception)
        self.assertIn("Failed to transpile computed column 'COMP_COL' in table 'SALES'", err_msg)
        self.assertIn("GEN_ID(G, 1)", err_msg)
        self.assertIn("sequence configured increment is 10", err_msg)

    def test_domain_default_incompatible_increment_rejected(self):
        with self.assertRaises(RuntimeError) as cm:
            DdlExporter._format_domain_postgres_ddl(
                "dom_id", "integer", default_source="DEFAULT GEN_ID(G, 1)",
                not_null=False, validation_source=None, sequence_increments={'g': 10}
            )
        self.assertIn("sequence configured increment is 10", str(cm.exception))

    # 5. Compatible step
    def test_first_gen_id_compatible_step_advances_sequence(self):
        # Configured increment 10 with step 10 -> nextval
        fb_sql10 = "CREATE VIEW V AS SELECT FIRST (GEN_ID(G, 10)) COL FROM T;"
        pg_sql10 = FirebirdToPostgresVisitor.transpile(fb_sql10, sequence_increments={'g': 10})
        self.assertIn("LIMIT (nextval('G'))", pg_sql10)

        # Configured increment 1 with step 1 -> nextval
        fb_sql1 = "CREATE VIEW V AS SELECT FIRST (GEN_ID(G, 1)) COL FROM T;"
        pg_sql1 = FirebirdToPostgresVisitor.transpile(fb_sql1, sequence_increments={'g': 1})
        self.assertIn("LIMIT (nextval('G'))", pg_sql1)

        # Without outer parentheses
        fb_sql_no_parens = "CREATE VIEW V AS SELECT FIRST GEN_ID(G, 10) COL FROM T;"
        pg_sql_no_parens = FirebirdToPostgresVisitor.transpile(fb_sql_no_parens, sequence_increments={'g': 10})
        self.assertIn("LIMIT nextval('G')", pg_sql_no_parens)

    # 6. State inspection with step zero
    def test_first_gen_id_step_zero_inspects_current_value(self):
        fb_sql = "CREATE VIEW V AS SELECT FIRST (GEN_ID(G, 0)) COL FROM T;"
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql, sequence_increments={'g': 10})
        self.assertIn('LIMIT ((SELECT CASE WHEN is_called THEN last_value ELSE last_value - 10 END FROM "g"))', pg_sql)

        fb_sql_no_parens = "CREATE VIEW V AS SELECT FIRST GEN_ID(G, 0) COL FROM T;"
        pg_sql_no_parens = FirebirdToPostgresVisitor.transpile(fb_sql_no_parens, sequence_increments={'g': 10})
        self.assertIn('LIMIT (SELECT CASE WHEN is_called THEN last_value ELSE last_value - 10 END FROM "g")', pg_sql_no_parens)

    # 7. Missing sequence metadata is not confused with increment proven equal to 1
    def test_missing_sequence_metadata_is_rejected_not_defaulted_to_one(self):
        # Metadata dictionary provided, but G is not present in it (unproven increment)
        fb_sql = "CREATE VIEW V AS SELECT FIRST (GEN_ID(G, 1)) COL FROM T;"
        with self.assertRaises(RuntimeError) as cm:
            FirebirdToPostgresVisitor.transpile(fb_sql, sequence_increments={'other_seq': 1})
        self.assertIn("sequence increment metadata is missing", str(cm.exception))

    def test_empty_sequence_metadata_is_rejected_not_defaulted_to_one(self):
        fb_sql = "CREATE VIEW V AS SELECT FIRST (GEN_ID(G, 1)) COL FROM T;"
        with self.assertRaises(RuntimeError) as cm:
            FirebirdToPostgresVisitor.transpile(fb_sql, sequence_increments={})
        self.assertIn("sequence increment metadata is missing", str(cm.exception))

    # 8. Metadata retrieval failure: verify rejection and absence of DROP
    def test_metadata_fetch_failure_aborts_migration_without_drop(self):
        mock_fb_con = MagicMock()
        mock_fb_cursor = MagicMock()
        mock_fb_con.cursor.return_value = mock_fb_cursor

        # Simulate catalog query failure when fetching sequence increments
        def execute_side_effect(sql, *args, **kwargs):
            if "RDB$GENERATORS" in sql:
                raise Exception("Catalog query failed: connection broken")
            return []

        mock_fb_cursor.execute.side_effect = execute_side_effect
        mock_fb_cursor.fetchall.return_value = []

        mock_pg_con = MagicMock()
        mock_pg_cursor = MagicMock()
        mock_pg_con.cursor.return_value = mock_pg_cursor

        import tempfile
        with tempfile.TemporaryDirectory() as tmp_dir:
            migrator = DatabaseMigrator(mock_fb_con, mock_pg_con)

            # Step 1: export_all_firebird_ddl must fail immediately
            with self.assertRaises(RuntimeError) as cm:
                migrator.export_all_firebird_ddl(output_dir=tmp_dir)
            self.assertIn("Failed to fetch sequence increments from Firebird", str(cm.exception))

        # Verify no DROP statement was EVER executed on the PostgreSQL connection
        for call_args in mock_pg_cursor.execute.call_args_list:
            executed_sql = call_args[0][0]
            self.assertNotIn("DROP TABLE", executed_sql.upper())
            self.assertNotIn("DROP SEQUENCE", executed_sql.upper())
            self.assertNotIn("DROP DOMAIN", executed_sql.upper())

    def test_metadata_fetch_failure_in_drop_schema_aborts_without_drop(self):
        mock_fb_con = MagicMock()
        mock_fb_cursor = MagicMock()
        mock_fb_con.cursor.return_value = mock_fb_cursor

        # Simulate catalog query failure when fetching sequence increments during schema extraction
        def execute_side_effect(sql, *args, **kwargs):
            if "RDB$GENERATORS" in sql:
                raise Exception("Catalog query failed: connection broken")
            return []

        mock_fb_cursor.execute.side_effect = execute_side_effect
        mock_fb_cursor.fetchall.return_value = []

        mock_pg_con = MagicMock()
        mock_pg_cursor = MagicMock()
        mock_pg_con.cursor.return_value = mock_pg_cursor

        migrator = DatabaseMigrator(mock_fb_con, mock_pg_con)

        with self.assertRaises(RuntimeError) as cm:
            migrator.drop_schema()
        self.assertIn("Failed to fetch sequence increments from Firebird", str(cm.exception))

        # Absolutely NO drop query should have been sent to PostgreSQL
        for call_args in mock_pg_cursor.execute.call_args_list:
            executed_sql = call_args[0][0]
            self.assertNotIn("DROP TABLE", executed_sql.upper())
            self.assertNotIn("DROP SEQUENCE", executed_sql.upper())
            self.assertNotIn("DROP DOMAIN", executed_sql.upper())


if __name__ == '__main__':
    unittest.main()
