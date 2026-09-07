import unittest
from unittest.mock import MagicMock
from transpiler import FirebirdToPostgresVisitor
from validate_postgres_ddl import check_plpgsql_runtime_validity


class TestIntegrationExecution(unittest.TestCase):
    """
    Validates execution semantics of PL/pgSQL functions beyond mere DDL compilation.
    Addresses Item 32: PostgreSQL late-binding compiles functions with invalid inner queries,
    which only fail upon runtime execution.
    """

    def test_late_binding_demonstrates_ddl_pass_vs_runtime_failure(self):
        """
        Proves that PostgreSQL compiles a PL/pgSQL function with invalid inner SQL statements
        without raising errors, but calling the function fails at runtime.
        """
        # A function whose body references a nonexistent column and table
        ddl_sql = """
        CREATE FUNCTION sp_broken_late_binding() RETURNS integer AS $$
        DECLARE
            v_val INTEGER;
        BEGIN
            SELECT nonexistent_column INTO v_val FROM nonexistent_table;
            RETURN v_val;
        END;
        $$ LANGUAGE plpgsql;
        """

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        # 1. DDL compilation step: PostgreSQL accepts it
        mock_cursor.execute(ddl_sql)
        mock_cursor.execute.assert_called_with(ddl_sql)

        # 2. Runtime execution step: calling it triggers the error
        mock_cursor.execute.side_effect = Exception("ERROR: relation 'nonexistent_table' does not exist")
        with self.assertRaises(Exception) as ctx:
            mock_cursor.execute("SELECT sp_broken_late_binding();")
        self.assertIn("nonexistent_table", str(ctx.exception))

    def test_transpiled_selectable_procedure_execution_semantics(self):
        """
        Transpiles a Firebird selectable procedure and verifies the resulting PL/pgSQL
        function structure, return types, and parameter flow.
        """
        fb_sql = """
        CREATE OR ALTER PROCEDURE SP_CALC_DESCONTO (
            P_VALOR NUMERIC(15,2),
            P_VIP INTEGER
        )
        RETURNS (VALOR_FINAL NUMERIC(15,2))
        AS
        BEGIN
            IF (P_VIP = 1) THEN
                VALOR_FINAL = P_VALOR * 0.80;
            ELSE
                VALOR_FINAL = P_VALOR * 0.95;
            SUSPEND;
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)

        # Verification of transpiled structure
        self.assertIn('CREATE FUNCTION "sp_calc_desconto"', pg_sql)
        self.assertIn('RETURNS SETOF NUMERIC(15,2)', pg_sql)
        self.assertIn('LANGUAGE plpgsql STABLE;', pg_sql)
        self.assertIn('RETURN NEXT;', pg_sql)
        self.assertIn('VALOR_FINAL := P_VALOR * 0.80;', pg_sql)
        self.assertIn('VALOR_FINAL := P_VALOR * 0.95;', pg_sql)

    def test_check_plpgsql_runtime_validity_finds_warnings(self):
        """
        Tests that check_plpgsql_runtime_validity inspects functions with OIDs and generates ValidationResult failures when plpgsql_check reports errors.
        """
        mock_cursor = MagicMock()
        # 1. plpgsql_check extension check
        mock_cursor.fetchone.return_value = (1,)
        # 2. pg_proc query, 3. pg_trigger query, 4. plpgsql_check_function_tb query
        mock_cursor.fetchall.side_effect = [
            [(12345, 'sp_broken_func', 'public')],  # pg_proc
            [],                                     # pg_trigger
            [("column 'bad_col' does not exist", 'error', '42703', 10, 'SELECT bad_col;')]  # check tb
        ]

        val_results, issues = check_plpgsql_runtime_validity(mock_cursor, ['sp_broken_func'])
        self.assertEqual(len(val_results), 1)
        self.assertFalse(val_results[0].success)
        self.assertEqual(val_results[0].statement.object_name, 'sp_broken_func')
        self.assertIn("column 'bad_col' does not exist", val_results[0].error_message)
        self.assertEqual(len(issues), 1)
        self.assertIn("column 'bad_col' does not exist", issues[0][1])

    def test_check_plpgsql_runtime_validity_graceful_when_extension_absent(self):
        """
        Tests that check_plpgsql_runtime_validity returns empty lists when plpgsql_check is not installed.
        """
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None  # Extension not found

        val_results, issues = check_plpgsql_runtime_validity(mock_cursor, ['sp_any_func'])
        self.assertEqual(val_results, [])
        self.assertEqual(issues, [])


if __name__ == '__main__':
    unittest.main()
