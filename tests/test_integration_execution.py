import decimal
import unittest
from unittest.mock import MagicMock

import psycopg2
from config import get_postgres_connection, PostgresConfig
from transpiler import FirebirdToPostgresVisitor
from validate_postgres_ddl import check_plpgsql_runtime_validity


def check_live_postgres_available() -> bool:
    try:
        cfg = PostgresConfig()
        conn = get_postgres_connection(cfg)
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        res = cur.fetchone()
        conn.close()
        return bool(res and res[0] == 1)
    except psycopg2.Error:
        return False


HAS_REAL_PG = check_live_postgres_available()


class TestIntegrationExecution(unittest.TestCase):
    """
    Validates execution semantics of PL/pgSQL functions and triggers beyond mere DDL compilation.
    Validates runtime behavior against real PostgreSQL: creating objects, invoking functions,
    firing triggers, comparing returned values, data types, runtime error exceptions, and
    benchmarking query plans with EXPLAIN (ANALYZE, BUFFERS).
    """

    def setUp(self):
        if HAS_REAL_PG:
            self.pg_con = get_postgres_connection()
            self.pg_con.autocommit = False
            self.pg_cur = self.pg_con.cursor()
        else:
            self.pg_con = None
            self.pg_cur = None

    def tearDown(self):
        if self.pg_con:
            try:
                self.pg_con.rollback()
            except psycopg2.Error:
                pass
            try:
                self.pg_con.close()
            except psycopg2.Error:
                pass

    @unittest.skipUnless(HAS_REAL_PG, "Live PostgreSQL instance required for real execution test")
    def test_real_pg_late_binding_demonstrates_ddl_pass_vs_runtime_failure(self):
        """
        Validates real PostgreSQL late-binding: compiles a PL/pgSQL function referencing
        nonexistent tables/columns (succeeds at DDL time), but calling it fails at runtime
        with undefined_table (42P01).
        """
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
        # 1. DDL compilation succeeds in PostgreSQL
        self.pg_cur.execute(ddl_sql)

        # 2. Runtime execution triggers real PostgreSQL UndefinedTable exception
        with self.assertRaises(psycopg2.Error) as ctx:
            self.pg_cur.execute("SELECT sp_broken_late_binding();")

        # Confirm exact PostgreSQL SQLState code (42P01: undefined_table)
        self.assertEqual(ctx.exception.pgcode, '42P01')
        self.assertIn("nonexistent_table", str(ctx.exception))

    @unittest.skipUnless(HAS_REAL_PG, "Live PostgreSQL instance required for real execution test")
    def test_real_pg_transpiled_selectable_procedure_execution_and_values(self):
        """
        Transpiles a Firebird selectable procedure, executes the DDL against PostgreSQL,
        and invokes the function to verify returned types, decimal precision, and parameter branch logic.
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
        self.pg_cur.execute(pg_sql)

        # VIP branch: 100.00 * 0.80 = 80.00
        self.pg_cur.execute('SELECT * FROM "sp_calc_desconto"(100.00, 1);')
        row_vip = self.pg_cur.fetchone()
        self.assertIsNotNone(row_vip)
        self.assertIsInstance(row_vip[0], decimal.Decimal)
        self.assertEqual(row_vip[0], decimal.Decimal('80.00'))

        # Non-VIP branch: 100.00 * 0.95 = 95.00
        self.pg_cur.execute('SELECT * FROM "sp_calc_desconto"(100.00, 0);')
        row_reg = self.pg_cur.fetchone()
        self.assertIsNotNone(row_reg)
        self.assertIsInstance(row_reg[0], decimal.Decimal)
        self.assertEqual(row_reg[0], decimal.Decimal('95.00'))

    @unittest.skipUnless(HAS_REAL_PG, "Live PostgreSQL instance required for real execution test")
    def test_real_pg_transpiled_trigger_fires_and_mutates_data(self):
        """
        Creates a table in PostgreSQL, transpiles and creates a BEFORE INSERT trigger,
        and performs DML to prove the trigger fires and executes the transpiled logic.
        """
        self.pg_cur.execute("""
            CREATE TABLE test_real_audit (
                id SERIAL PRIMARY KEY,
                valor NUMERIC(15,2),
                desconto NUMERIC(15,2),
                status VARCHAR(20)
            );
        """)

        fb_trg = """
        CREATE TRIGGER TRG_AUDIT_BI FOR test_real_audit BEFORE INSERT
        AS
        BEGIN
            IF (NEW.valor > 100) THEN
                NEW.desconto = NEW.valor * 0.10;
            ELSE
                NEW.desconto = 0;
            NEW.status = 'PROCESSADO';
        END
        """
        pg_trg = FirebirdToPostgresVisitor.transpile(fb_trg)
        self.pg_cur.execute(pg_trg)

        # Insert valor > 100: trigger calculates 10% discount
        self.pg_cur.execute("INSERT INTO test_real_audit (valor) VALUES (200.00) RETURNING desconto, status;")
        row1 = self.pg_cur.fetchone()
        self.assertEqual(row1[0], decimal.Decimal('20.00'))
        self.assertEqual(row1[1], 'PROCESSADO')

        # Insert valor <= 100: trigger calculates 0 discount
        self.pg_cur.execute("INSERT INTO test_real_audit (valor) VALUES (50.00) RETURNING desconto, status;")
        row2 = self.pg_cur.fetchone()
        self.assertEqual(row2[0], decimal.Decimal('0.00'))
        self.assertEqual(row2[1], 'PROCESSADO')

    @unittest.skipUnless(HAS_REAL_PG, "Live PostgreSQL instance required for real execution test")
    def test_real_pg_explain_analyze_buffers_benchmark(self):
        """
        Validates performance by executing EXPLAIN (ANALYZE, BUFFERS) on representative
        functions and statements, confirming measured query plans, buffer hits, and execution times.
        """
        fb_sql = """
        CREATE OR ALTER PROCEDURE SP_BENCHMARK_FUNC (
            P_INPUT INTEGER
        )
        RETURNS (R_OUTPUT INTEGER)
        AS
        BEGIN
            R_OUTPUT = P_INPUT * 2 + 10;
            SUSPEND;
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.pg_cur.execute(pg_sql)

        # Run EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
        self.pg_cur.execute('EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) SELECT * FROM "sp_benchmark_func"(42);')
        plan_data = self.pg_cur.fetchone()[0]
        plan_root = plan_data[0]

        # Verify real execution metrics from PostgreSQL engine
        self.assertIn('Execution Time', plan_root)
        self.assertIn('Planning Time', plan_root)
        self.assertIsInstance(plan_root['Execution Time'], (int, float))
        self.assertGreater(plan_root['Execution Time'], 0.0)

        # Verify plan tree contains node details
        plan_tree = plan_root.get('Plan', {})
        self.assertIn('Node Type', plan_tree)

    def test_check_plpgsql_runtime_validity_finds_warnings(self):
        """
        Tests that check_plpgsql_runtime_validity inspects functions with OIDs and generates ValidationResult failures when plpgsql_check reports errors.
        """
        mock_cursor = MagicMock()
        # 1. plpgsql_check extension check
        mock_cursor.fetchone.return_value = (1,)
        # 2. pg_proc query, 3. pg_trigger query, 4. plpgsql_check_function_tb query
        mock_cursor.fetchall.side_effect = [
            [(12345, 'sp_broken_func', 'public', '')],  # pg_proc (oid, proname, nspname, identity_args)
            [],                                          # pg_trigger
            [("column 'bad_col' does not exist", 'error', '42703', 10, 'SELECT bad_col;')]  # check tb
        ]

        val_results, issues, status = check_plpgsql_runtime_validity(mock_cursor, ['sp_broken_func'])
        self.assertEqual(len(val_results), 1)
        self.assertFalse(val_results[0].success)
        self.assertEqual(val_results[0].statement.object_name, 'sp_broken_func')
        self.assertIn("column 'bad_col' does not exist", val_results[0].error_message)
        self.assertEqual(len(issues), 1)
        self.assertIn("column 'bad_col' does not exist", issues[0][1])
        self.assertEqual(status, "ISSUES_FOUND")

    def test_check_plpgsql_runtime_validity_graceful_when_extension_absent(self):
        """
        Tests that check_plpgsql_runtime_validity returns empty lists when plpgsql_check is not installed.
        """
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None  # Extension not found

        val_results, issues, status = check_plpgsql_runtime_validity(mock_cursor, ['sp_any_func'])
        self.assertEqual(val_results, [])
        self.assertEqual(len(issues), 1)
        self.assertIn("verificação não realizada", issues[0][1])
        self.assertEqual(status, "NOT_PERFORMED")


    def test_regression_disambiguation_runtime_execution_v_increment_and_assignment(self):
        """
        Regression test:
        - Parameter V=100; table with V=1 and V=2; UPDATE T SET V=V+1 must produce 2 and 3.
        - UPDATE T SET V=:V must produce 100.
        - WHERE ID=:ID.
        - Global precedence directive does not alter results.
        """
        if not HAS_REAL_PG or not self.pg_cur:
            self.skipTest("Real PostgreSQL database connection not available")

        # 1. Setup disposable table
        self.pg_cur.execute("""
            DROP TABLE IF EXISTS reg_t_disambig CASCADE;
            CREATE TABLE reg_t_disambig (id INT PRIMARY KEY, v INT);
            INSERT INTO reg_t_disambig (id, v) VALUES (1, 1), (2, 2);
        """)

        # 2. Transpile and create procedure with UPDATE T SET V = V + 1
        fb_inc = """
        CREATE OR ALTER PROCEDURE SP_REG_INC (V INTEGER)
        AS
        BEGIN
            UPDATE REG_T_DISAMBIG SET V = V + 1;
        END;
        """
        symbols = {'reg_t_disambig.id': 'INTEGER', 'reg_t_disambig.v': 'INTEGER'}
        pg_inc = FirebirdToPostgresVisitor.transpile(fb_inc, symbols=symbols)
        self.pg_cur.execute(pg_inc)

        # Execute with V=100 -> Must produce 2 and 3 (NOT 101, 101!)
        self.pg_cur.execute('SELECT "sp_reg_inc"(100);')
        self.pg_cur.execute('SELECT id, v FROM reg_t_disambig ORDER BY id;')
        rows_inc = self.pg_cur.fetchall()
        self.assertEqual(rows_inc, [(1, 2), (2, 3)])

        # 3. Transpile and create procedure with UPDATE T SET V = :V
        fb_set_var = """
        CREATE OR ALTER PROCEDURE SP_REG_SET_VAR (V INTEGER)
        AS
        BEGIN
            UPDATE REG_T_DISAMBIG SET V = :V;
        END;
        """
        pg_set_var = FirebirdToPostgresVisitor.transpile(fb_set_var, symbols=symbols)
        self.pg_cur.execute(pg_set_var)

        # Execute with V=100 -> Must produce 100 for both rows
        self.pg_cur.execute('SELECT "sp_reg_set_var"(100);')
        self.pg_cur.execute('SELECT id, v FROM reg_t_disambig ORDER BY id;')
        rows_set = self.pg_cur.fetchall()
        self.assertEqual(rows_set, [(1, 100), (2, 100)])

        # 4. Transpile and create procedure with WHERE ID = :ID
        fb_where = """
        CREATE OR ALTER PROCEDURE SP_REG_WHERE (ID INTEGER, V INTEGER)
        AS
        BEGIN
            UPDATE REG_T_DISAMBIG SET V = :V WHERE ID = :ID;
        END;
        """
        pg_where = FirebirdToPostgresVisitor.transpile(fb_where, symbols=symbols)
        self.pg_cur.execute(pg_where)

        # Execute with ID=1, V=999 -> Only row 1 should become 999, row 2 stays 100
        self.pg_cur.execute('SELECT "sp_reg_where"(1, 999);')
        self.pg_cur.execute('SELECT id, v FROM reg_t_disambig ORDER BY id;')
        rows_where = self.pg_cur.fetchall()
        self.assertEqual(rows_where, [(1, 999), (2, 100)])

    @unittest.skipUnless(HAS_REAL_PG, "Live PostgreSQL instance required for real execution test")
    def test_real_pg_volatility_classification_and_execution_semantics(self):
        """
        Validates Item D:
        - Procedures with DML following string '--' are classified as VOLATILE and persist changes.
        - Procedures with comments containing DML are classified as STABLE.
        - Mutating procedures called by other procedures execute and persist changes under VOLATILE.
        - Verifies PostgreSQL catalog attributes (pg_proc.provolatile).
        """
        if not HAS_REAL_PG or not self.pg_cur:
            self.skipTest("Real PostgreSQL database connection not available")

        # 1. Disposable fixtures
        self.pg_cur.execute("""
            DROP TABLE IF EXISTS reg_volatility_audit CASCADE;
            DROP TABLE IF EXISTS reg_volatility_data CASCADE;
            CREATE TABLE reg_volatility_audit (id SERIAL PRIMARY KEY, note TEXT);
            CREATE TABLE reg_volatility_data (id INT PRIMARY KEY, val TEXT);
            INSERT INTO reg_volatility_data (id, val) VALUES (1, 'initial');
        """)

        # 2. Case 1: String '--' followed by INSERT -> VOLATILE, executes and writes data
        fb_dash = """
        CREATE OR ALTER PROCEDURE SP_VOL_STR_DASH (MSG VARCHAR(50))
        AS
        DECLARE VARIABLE V_TEMP VARCHAR(50);
        BEGIN
            V_TEMP = '--';
            INSERT INTO REG_VOLATILITY_AUDIT (NOTE) VALUES (:MSG);
        END;
        """
        pg_dash = FirebirdToPostgresVisitor.transpile(fb_dash)
        self.assertIn("LANGUAGE plpgsql VOLATILE;", pg_dash)
        self.pg_cur.execute(pg_dash)

        # Check pg_proc catalog: 'v' = VOLATILE
        self.pg_cur.execute("SELECT provolatile FROM pg_proc WHERE proname = 'sp_vol_str_dash';")
        self.assertEqual(self.pg_cur.fetchone()[0], 'v')

        # Execute write and confirm row inserted
        self.pg_cur.execute('SELECT "sp_vol_str_dash"(\'inserted_via_dash\');')
        self.pg_cur.execute("SELECT note FROM reg_volatility_audit WHERE note = 'inserted_via_dash';")
        self.assertEqual(self.pg_cur.fetchone()[0], 'inserted_via_dash')

        # 3. Case 2: Read-only query with comment containing DML -> STABLE ('s')
        fb_readonly = """
        CREATE OR ALTER PROCEDURE SP_VOL_READONLY (P_ID INTEGER)
        RETURNS (VAL TEXT)
        AS
        BEGIN
            -- INSERT INTO REG_VOLATILITY_AUDIT (NOTE) VALUES ('should_not_run');
            /* UPDATE REG_VOLATILITY_DATA SET VAL = 'broken'; */
            SELECT VAL FROM REG_VOLATILITY_DATA WHERE ID = :P_ID INTO :VAL;
            SUSPEND;
        END;
        """
        pg_readonly = FirebirdToPostgresVisitor.transpile(fb_readonly)
        self.assertIn("LANGUAGE plpgsql STABLE;", pg_readonly)
        self.pg_cur.execute(pg_readonly)

        # Check pg_proc catalog: 's' = STABLE
        self.pg_cur.execute("SELECT provolatile FROM pg_proc WHERE proname = 'sp_vol_readonly';")
        self.assertEqual(self.pg_cur.fetchone()[0], 's')

        # Execute read and verify output and that no DML occurred
        self.pg_cur.execute('SELECT "val" FROM "sp_vol_readonly"(1);')
        self.assertEqual(self.pg_cur.fetchone()[0], 'initial')
        self.pg_cur.execute("SELECT COUNT(*) FROM reg_volatility_audit WHERE note = 'should_not_run';")
        self.assertEqual(self.pg_cur.fetchone()[0], 0)

        # 4. Case 3: Mutating procedure calling another modifying procedure -> VOLATILE
        fb_mutate = """
        CREATE OR ALTER PROCEDURE SP_VOL_MUTATE (P_ID INTEGER, P_NEW_VAL VARCHAR(50))
        AS
        BEGIN
            UPDATE REG_VOLATILITY_DATA SET VAL = :P_NEW_VAL WHERE ID = :P_ID;
        END;
        """
        fb_caller = """
        CREATE OR ALTER PROCEDURE SP_VOL_CALLER (P_ID INTEGER, P_NEW_VAL VARCHAR(50))
        AS
        BEGIN
            EXECUTE PROCEDURE SP_VOL_MUTATE(:P_ID, :P_NEW_VAL);
        END;
        """
        pg_mutate = FirebirdToPostgresVisitor.transpile(fb_mutate)
        pg_caller = FirebirdToPostgresVisitor.transpile(fb_caller)
        self.assertIn("LANGUAGE plpgsql VOLATILE;", pg_mutate)
        self.assertIn("LANGUAGE plpgsql VOLATILE;", pg_caller)
        self.pg_cur.execute(pg_mutate)
        self.pg_cur.execute(pg_caller)

        # Check catalog
        self.pg_cur.execute("SELECT provolatile FROM pg_proc WHERE proname = 'sp_vol_caller';")
        self.assertEqual(self.pg_cur.fetchone()[0], 'v')

        # Execute caller and confirm mutation persisted
        self.pg_cur.execute('SELECT "sp_vol_caller"(1, \'modified_via_caller\');')
        self.pg_cur.execute("SELECT val FROM reg_volatility_data WHERE id = 1;")
        self.assertEqual(self.pg_cur.fetchone()[0], 'modified_via_caller')

    @unittest.skipUnless(HAS_REAL_PG, "Live PostgreSQL instance required for real execution test")
    def test_real_pg_computed_columns_expansion_and_execution(self):
        """
        Validates Item F on a live PostgreSQL database:
        - Creates a table with base column X and computed columns:
          - "ABS": ABS(X)
          - A: X + 1 (INT128)
          - B: A * 2 (NUMERIC(15,2))
          - C: B + 10 (NUMERIC(15,2))
          - S: X || 'A' (VARCHAR(50))
        - Expands computed column dependencies and generates valid PostgreSQL DDL
        - Executes CREATE TABLE on PostgreSQL (verifying DDL syntax & cast validity)
        - Inserts rows with positive and negative X values
        - Verifies computed results in PostgreSQL match expected values
        """
        from models import Table, Column
        from engine.schema_extractor import SchemaExtractor
        from transpiler import FirebirdToPostgresVisitor

        table = Table("REG_COMPUTED_TEST")
        raw_cols = [
            Column("X", "INTEGER", nullable=False),
            Column("ABS", "INTEGER", nullable=True, computed_source=FirebirdToPostgresVisitor.transpile_expression("ABS(X)")),
            Column("A", "INT128", nullable=True, computed_source=FirebirdToPostgresVisitor.transpile_expression('"X" + 1')),
            Column("B", "NUMERIC(15,2)", nullable=True, computed_source=FirebirdToPostgresVisitor.transpile_expression("A * 2")),
            Column("C", "NUMERIC(15,2)", nullable=True, computed_source=FirebirdToPostgresVisitor.transpile_expression("B + 10")),
            Column("S", "VARCHAR(50)", nullable=True, computed_source=FirebirdToPostgresVisitor.transpile_expression("X || 'A'")),
        ]
        table.columns = raw_cols

        SchemaExtractor._expand_computed_column_dependencies(table.columns, table.name)
        create_sql = table.get_create_table_query()

        self.pg_cur.execute("DROP TABLE IF EXISTS reg_computed_test CASCADE;")
        self.pg_cur.execute(create_sql)

        self.pg_cur.execute("INSERT INTO reg_computed_test (x) VALUES (-42), (10);")
        self.pg_cur.execute('SELECT x, "abs", a, b, c, s FROM reg_computed_test ORDER BY x;')
        rows = self.pg_cur.fetchall()

        # Row 1: X = -42
        self.assertEqual(rows[0][0], -42)
        self.assertEqual(rows[0][1], 42)  # abs(-42)
        self.assertEqual(rows[0][2], decimal.Decimal('-41'))  # -42 + 1
        self.assertEqual(rows[0][3], decimal.Decimal('-82.00'))  # -41 * 2
        self.assertEqual(rows[0][4], decimal.Decimal('-72.00'))  # -82 + 10
        self.assertEqual(rows[0][5], '-42A')

        # Row 2: X = 10
        self.assertEqual(rows[1][0], 10)
        self.assertEqual(rows[1][1], 10)  # abs(10)
        self.assertEqual(rows[1][2], decimal.Decimal('11'))  # 10 + 1
        self.assertEqual(rows[1][3], decimal.Decimal('22.00'))  # 11 * 2
        self.assertEqual(rows[1][4], decimal.Decimal('32.00'))  # 22 + 10
        self.assertEqual(rows[1][5], '10A')

        self.pg_cur.execute("DROP TABLE IF EXISTS reg_computed_test CASCADE;")


if __name__ == '__main__':
    unittest.main()

