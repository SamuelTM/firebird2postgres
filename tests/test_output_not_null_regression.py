import unittest
import psycopg2

from config import (
    get_postgres_connection,
    PostgresConfig,
    get_firebird_connection,
    FirebirdConfig,
)
from transpiler import FirebirdToPostgresVisitor


def check_live_postgres_available() -> bool:
    try:
        cfg = PostgresConfig()
        conn = get_postgres_connection(cfg)
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        res = cur.fetchone()
        conn.close()
        return bool(res and res[0] == 1)
    except Exception:
        return False


def check_live_firebird_available() -> bool:
    try:
        cfg = FirebirdConfig()
        conn = get_firebird_connection(cfg)
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM RDB$DATABASE;")
        res = cur.fetchone()
        conn.close()
        return bool(res and res[0] == 1)
    except Exception:
        return False


HAS_REAL_PG = check_live_postgres_available()
HAS_REAL_FB = check_live_firebird_available()


class TestOutputNotNullRegression(unittest.TestCase):
    """
    Regression test suite for:
    'NOT NULL de saída não é suportado'

    Covers:
    - RETURNS (R INTEGER NOT NULL) parsing & transpilation without error
    - Distinct handling for inputs vs outputs
    - Validation on assignment: R = NULL throws runtime error
    - Validation on SUSPEND in selectable procedures
    - Validation on EXIT & routine end in executable procedures
    - Early EXIT in selectable procedures yields empty set without error
    - Multiple rows validated individually
    - Execution first against live Firebird, then demanding equivalent behavior in PostgreSQL
    """

    def setUp(self):
        if HAS_REAL_PG:
            self.pg_con = get_postgres_connection()
            self.pg_con.autocommit = False
            self.pg_cur = self.pg_con.cursor()
        else:
            self.pg_con = None
            self.pg_cur = None

        if HAS_REAL_FB:
            self.fb_con = get_firebird_connection()
            self.fb_cur = self.fb_con.cursor()
        else:
            self.fb_con = None
            self.fb_cur = None

    def tearDown(self):
        if self.pg_cur:
            try:
                self.pg_con.rollback()
            except Exception:
                pass
            try:
                self.pg_con.close()
            except Exception:
                pass

        if self.fb_cur:
            try:
                self.fb_con.rollback()
            except Exception:
                pass
            try:
                self.fb_con.close()
            except Exception:
                pass

    def _cleanup_fb_proc(self, name: str):
        if not HAS_REAL_FB:
            return
        try:
            self.fb_cur.execute(f"DROP PROCEDURE {name}")
            self.fb_con.commit()
        except Exception:
            try:
                self.fb_con.rollback()
            except Exception:
                pass

    def test_transpile_returns_not_null_signature_and_guards(self):
        """
        Verify that RETURNS (R INTEGER NOT NULL) parses cleanly without syntax errors,
        produces valid OUT R INTEGER in function signature, and emits runtime guards.
        """
        fb_sql = """
        CREATE OR ALTER PROCEDURE P_TEST_SIG
        RETURNS (R INTEGER NOT NULL)
        AS
        BEGIN
            R = 100;
            SUSPEND;
        END
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn('CREATE FUNCTION "p_test_sig"(OUT R INTEGER) RETURNS SETOF INTEGER', pg_sql)
        self.assertIn("IF R IS NULL THEN", pg_sql)
        self.assertIn("RAISE EXCEPTION 'validation error for variable %, value null', 'R';", pg_sql)
        self.assertIn("RETURN NEXT;", pg_sql)

    def test_regression_valid_output_selectable(self):
        """
        Valid selectable procedure: returns rows successfully on both Firebird and PostgreSQL.
        """
        fb_sql = """
        CREATE OR ALTER PROCEDURE P_TEST_VALID_SEL
        RETURNS (R INTEGER NOT NULL)
        AS
        BEGIN
            R = 10;
            SUSPEND;
            R = 20;
            SUSPEND;
        END
        """
        # 1. Firebird verification
        if HAS_REAL_FB:
            self._cleanup_fb_proc("P_TEST_VALID_SEL")
            self.fb_cur.execute(fb_sql)
            self.fb_con.commit()
            self.fb_cur.execute("SELECT R FROM P_TEST_VALID_SEL")
            fb_rows = self.fb_cur.fetchall()
            self.assertEqual(fb_rows, [(10,), (20,)])
            self._cleanup_fb_proc("P_TEST_VALID_SEL")

        # 2. PostgreSQL verification
        if HAS_REAL_PG:
            pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
            self.pg_cur.execute(pg_sql)
            self.pg_cur.execute('SELECT * FROM "p_test_valid_sel"();')
            pg_rows = self.pg_cur.fetchall()
            self.assertEqual(pg_rows, [(10,), (20,)])

    def test_regression_valid_output_executable(self):
        """
        Valid executable procedure: returns scalar value successfully on both Firebird and PostgreSQL.
        """
        fb_sql = """
        CREATE OR ALTER PROCEDURE P_TEST_VALID_EXEC
        RETURNS (R INTEGER NOT NULL)
        AS
        BEGIN
            R = 42;
        END
        """
        # 1. Firebird verification
        if HAS_REAL_FB:
            self._cleanup_fb_proc("P_TEST_VALID_EXEC")
            self.fb_cur.execute(fb_sql)
            self.fb_con.commit()
            self.fb_cur.execute("EXECUTE PROCEDURE P_TEST_VALID_EXEC")
            fb_res = self.fb_cur.fetchone()
            self.assertEqual(fb_res[0], 42)
            self._cleanup_fb_proc("P_TEST_VALID_EXEC")

        # 2. PostgreSQL verification
        if HAS_REAL_PG:
            pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
            self.pg_cur.execute(pg_sql)
            self.pg_cur.execute('SELECT "p_test_valid_exec"();')
            pg_res = self.pg_cur.fetchone()
            self.assertEqual(pg_res[0], 42)

    def test_regression_uninitialized_output_selectable(self):
        """
        Uninitialized output in selectable procedure: fails on SUSPEND on both Firebird and PostgreSQL.
        """
        fb_sql = """
        CREATE OR ALTER PROCEDURE P_TEST_UNINIT_SEL
        RETURNS (R INTEGER NOT NULL)
        AS
        BEGIN
            SUSPEND;
        END
        """
        # 1. Firebird verification: error occurs at SUSPEND
        if HAS_REAL_FB:
            self._cleanup_fb_proc("P_TEST_UNINIT_SEL")
            self.fb_cur.execute(fb_sql)
            self.fb_con.commit()
            with self.assertRaises(Exception) as fb_cm:
                self.fb_cur.execute("SELECT * FROM P_TEST_UNINIT_SEL")
            self.assertIn("validation error for variable R", str(fb_cm.exception))
            self.fb_con.rollback()
            self._cleanup_fb_proc("P_TEST_UNINIT_SEL")

        # 2. PostgreSQL verification
        if HAS_REAL_PG:
            pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
            self.pg_cur.execute(pg_sql)
            with self.assertRaises(psycopg2.Error) as pg_cm:
                self.pg_cur.execute('SELECT * FROM "p_test_uninit_sel"();')
            self.assertIn("validation error for variable R, value null", str(pg_cm.exception))
            self.pg_con.rollback()

    def test_regression_uninitialized_output_executable(self):
        """
        Uninitialized output in executable procedure: fails at routine end on both Firebird and PostgreSQL.
        """
        fb_sql = """
        CREATE OR ALTER PROCEDURE P_TEST_UNINIT_EXEC
        RETURNS (R INTEGER NOT NULL)
        AS
        BEGIN
        END
        """
        # 1. Firebird verification: error occurs at routine end
        if HAS_REAL_FB:
            self._cleanup_fb_proc("P_TEST_UNINIT_EXEC")
            self.fb_cur.execute(fb_sql)
            self.fb_con.commit()
            with self.assertRaises(Exception) as fb_cm:
                self.fb_cur.execute("EXECUTE PROCEDURE P_TEST_UNINIT_EXEC")
            self.assertIn("validation error for variable R", str(fb_cm.exception))
            self.fb_con.rollback()
            self._cleanup_fb_proc("P_TEST_UNINIT_EXEC")

        # 2. PostgreSQL verification
        if HAS_REAL_PG:
            pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
            self.pg_cur.execute(pg_sql)
            with self.assertRaises(psycopg2.Error) as pg_cm:
                self.pg_cur.execute('SELECT "p_test_uninit_exec"();')
            self.assertIn("validation error for variable R, value null", str(pg_cm.exception))
            self.pg_con.rollback()

    def test_regression_assignment_of_null(self):
        """
        Explicit assignment of NULL to NOT NULL output parameter: fails at assignment on both.
        """
        fb_sql = """
        CREATE OR ALTER PROCEDURE P_TEST_ASSIGN_NULL
        RETURNS (R INTEGER NOT NULL)
        AS
        BEGIN
            R = NULL;
            SUSPEND;
        END
        """
        # 1. Firebird verification
        if HAS_REAL_FB:
            self._cleanup_fb_proc("P_TEST_ASSIGN_NULL")
            self.fb_cur.execute(fb_sql)
            self.fb_con.commit()
            with self.assertRaises(Exception) as fb_cm:
                self.fb_cur.execute("SELECT * FROM P_TEST_ASSIGN_NULL")
            self.assertIn("validation error for variable R", str(fb_cm.exception))
            self.fb_con.rollback()
            self._cleanup_fb_proc("P_TEST_ASSIGN_NULL")

        # 2. PostgreSQL verification
        if HAS_REAL_PG:
            pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
            self.pg_cur.execute(pg_sql)
            with self.assertRaises(psycopg2.Error) as pg_cm:
                self.pg_cur.execute('SELECT * FROM "p_test_assign_null"();')
            self.assertIn("validation error for variable R, value null", str(pg_cm.exception))
            self.pg_con.rollback()

    def test_regression_multiple_suspend_individual_rows(self):
        """
        Multiple rows respect the constraint individually:
        Row 1 is valid, row 2 assigns NULL and triggers validation error.
        """
        fb_sql = """
        CREATE OR ALTER PROCEDURE P_TEST_MULTI_SUSPEND
        RETURNS (R INTEGER NOT NULL)
        AS
        BEGIN
            R = 100;
            SUSPEND;
            R = NULL;
            SUSPEND;
        END
        """
        # 1. Firebird verification: row 1 emitted, row 2 fails on assignment of NULL
        if HAS_REAL_FB:
            self._cleanup_fb_proc("P_TEST_MULTI_SUSPEND")
            self.fb_cur.execute(fb_sql)
            self.fb_con.commit()
            with self.assertRaises(Exception):
                self.fb_cur.execute("SELECT * FROM P_TEST_MULTI_SUSPEND")
                self.fb_cur.fetchall()
            try:
                self.fb_con.close()
            except Exception:
                pass
            self.fb_con = get_firebird_connection()
            self.fb_cur = self.fb_con.cursor()
            self._cleanup_fb_proc("P_TEST_MULTI_SUSPEND")

        # 2. PostgreSQL verification
        if HAS_REAL_PG:
            pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
            self.pg_cur.execute(pg_sql)
            with self.assertRaises(psycopg2.Error) as pg_cm:
                self.pg_cur.execute('SELECT * FROM "p_test_multi_suspend"();')
                self.pg_cur.fetchall()
            self.assertIn("validation error for variable R, value null", str(pg_cm.exception))
            self.pg_con.rollback()

    def test_regression_select_into_null(self):
        """
        Singleton SELECT NULL INTO NOT NULL output parameter: fails at runtime.
        """
        fb_sql = """
        CREATE OR ALTER PROCEDURE P_TEST_SEL_NULL
        RETURNS (R INTEGER NOT NULL)
        AS
        BEGIN
            SELECT NULL FROM RDB$DATABASE INTO R;
            SUSPEND;
        END
        """
        # 1. Firebird verification
        if HAS_REAL_FB:
            self._cleanup_fb_proc("P_TEST_SEL_NULL")
            self.fb_cur.execute(fb_sql)
            self.fb_con.commit()
            with self.assertRaises(Exception) as fb_cm:
                self.fb_cur.execute("SELECT * FROM P_TEST_SEL_NULL")
            self.assertIn("validation error for variable R", str(fb_cm.exception))
            self.fb_con.rollback()
            self._cleanup_fb_proc("P_TEST_SEL_NULL")

        # 2. PostgreSQL verification
        if HAS_REAL_PG:
            pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
            self.pg_cur.execute(pg_sql)
            with self.assertRaises(psycopg2.Error) as pg_cm:
                self.pg_cur.execute('SELECT * FROM "p_test_sel_null"();')
            self.assertIn("validation error for variable R, value null", str(pg_cm.exception))
            self.pg_con.rollback()

    def test_regression_for_select_into_null(self):
        """
        FOR SELECT NULL INTO NOT NULL output parameter: fails on loop iteration.
        """
        fb_sql = """
        CREATE OR ALTER PROCEDURE P_TEST_FOR_NULL
        RETURNS (R INTEGER NOT NULL)
        AS
        BEGIN
            FOR SELECT NULL FROM RDB$DATABASE INTO R DO
            BEGIN
                SUSPEND;
            END
        END
        """
        # 1. Firebird verification
        if HAS_REAL_FB:
            self._cleanup_fb_proc("P_TEST_FOR_NULL")
            self.fb_cur.execute(fb_sql)
            self.fb_con.commit()
            with self.assertRaises(Exception) as fb_cm:
                self.fb_cur.execute("SELECT * FROM P_TEST_FOR_NULL")
            self.assertIn("validation error for variable R", str(fb_cm.exception))
            self.fb_con.rollback()
            self._cleanup_fb_proc("P_TEST_FOR_NULL")

        # 2. PostgreSQL verification
        if HAS_REAL_PG:
            pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
            self.pg_cur.execute(pg_sql)
            with self.assertRaises(psycopg2.Error) as pg_cm:
                self.pg_cur.execute('SELECT * FROM "p_test_for_null"();')
            self.assertIn("validation error for variable R, value null", str(pg_cm.exception))
            self.pg_con.rollback()

    def test_regression_early_exit_selectable(self):
        """
        Early EXIT in selectable procedure before any SUSPEND yields empty set without error.
        Firebird and PostgreSQL both return 0 rows.
        """
        fb_sql = """
        CREATE OR ALTER PROCEDURE P_TEST_EARLY_EXIT_SEL
        RETURNS (R INTEGER NOT NULL)
        AS
        BEGIN
            EXIT;
            R = 10;
            SUSPEND;
        END
        """
        # 1. Firebird verification
        if HAS_REAL_FB:
            self._cleanup_fb_proc("P_TEST_EARLY_EXIT_SEL")
            self.fb_cur.execute(fb_sql)
            self.fb_con.commit()
            self.fb_cur.execute("SELECT * FROM P_TEST_EARLY_EXIT_SEL")
            fb_rows = self.fb_cur.fetchall()
            self.assertEqual(fb_rows, [])
            self._cleanup_fb_proc("P_TEST_EARLY_EXIT_SEL")

        # 2. PostgreSQL verification
        if HAS_REAL_PG:
            pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
            self.pg_cur.execute(pg_sql)
            self.pg_cur.execute('SELECT * FROM "p_test_early_exit_sel"();')
            pg_rows = self.pg_cur.fetchall()
            self.assertEqual(pg_rows, [])

    def test_regression_early_exit_executable(self):
        """
        Early EXIT in executable procedure when NOT NULL output is uninitialized:
        Fails on EXIT in both Firebird and PostgreSQL.
        """
        fb_sql = """
        CREATE OR ALTER PROCEDURE P_TEST_EARLY_EXIT_EXEC
        RETURNS (R INTEGER NOT NULL)
        AS
        BEGIN
            EXIT;
            R = 10;
        END
        """
        # 1. Firebird verification
        if HAS_REAL_FB:
            self._cleanup_fb_proc("P_TEST_EARLY_EXIT_EXEC")
            self.fb_cur.execute(fb_sql)
            self.fb_con.commit()
            with self.assertRaises(Exception) as fb_cm:
                self.fb_cur.execute("EXECUTE PROCEDURE P_TEST_EARLY_EXIT_EXEC")
            self.assertIn("validation error for variable R", str(fb_cm.exception))
            self.fb_con.rollback()
            self._cleanup_fb_proc("P_TEST_EARLY_EXIT_EXEC")

        # 2. PostgreSQL verification
        if HAS_REAL_PG:
            pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
            self.pg_cur.execute(pg_sql)
            with self.assertRaises(psycopg2.Error) as pg_cm:
                self.pg_cur.execute('SELECT "p_test_early_exit_exec"();')
            self.assertIn("validation error for variable R, value null", str(pg_cm.exception))
            self.pg_con.rollback()

    def test_distinct_input_and_output_not_null_treatment(self):
        """
        Verify distinct treatment for input vs output NOT NULL:
        - Input parameter NULL check happens on routine entry.
        - Output parameter NULL check happens on assignment and emission.
        """
        fb_sql = """
        CREATE OR ALTER PROCEDURE P_TEST_IN_OUT_DISTINCT (
            P_IN INTEGER NOT NULL
        )
        RETURNS (
            P_OUT INTEGER NOT NULL
        )
        AS
        BEGIN
            P_OUT = P_IN * 2;
            SUSPEND;
        END
        """
        # Transpilation checks
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("IF P_IN IS NULL THEN RAISE EXCEPTION 'Parameter \"%\" cannot be NULL', 'P_IN'; END IF;", pg_sql)
        self.assertIn("IF P_OUT IS NULL THEN", pg_sql)

        # 1. Firebird verification
        if HAS_REAL_FB:
            self._cleanup_fb_proc("P_TEST_IN_OUT_DISTINCT")
            self.fb_cur.execute(fb_sql)
            self.fb_con.commit()

            # Valid call
            self.fb_cur.execute("SELECT P_OUT FROM P_TEST_IN_OUT_DISTINCT(5)")
            self.assertEqual(self.fb_cur.fetchall(), [(10,)])

            # NULL input rejected
            with self.assertRaises(Exception):
                self.fb_cur.execute("SELECT P_OUT FROM P_TEST_IN_OUT_DISTINCT(NULL)")
            self.fb_con.rollback()
            self._cleanup_fb_proc("P_TEST_IN_OUT_DISTINCT")

        # 2. PostgreSQL verification
        if HAS_REAL_PG:
            self.pg_cur.execute(pg_sql)

            # Valid call
            self.pg_cur.execute('SELECT * FROM "p_test_in_out_distinct"(5);')
            self.assertEqual(self.pg_cur.fetchall(), [(10,)])

            # NULL input rejected
            with self.assertRaises(psycopg2.Error) as pg_cm:
                self.pg_cur.execute('SELECT * FROM "p_test_in_out_distinct"(NULL);')
            self.assertIn('Parameter "P_IN" cannot be NULL', str(pg_cm.exception))
            self.pg_con.rollback()

    def test_mixed_not_null_and_nullable_outputs(self):
        """
        Verify that in procedures with multiple outputs, NOT NULL is enforced only on
        the specific parameter declared NOT NULL, and nullable output can be NULL.
        """
        fb_sql = """
        CREATE OR ALTER PROCEDURE P_TEST_MIXED_OUT
        RETURNS (
            R_MANDATORY INTEGER NOT NULL,
            R_OPTIONAL INTEGER
        )
        AS
        BEGIN
            R_MANDATORY = 99;
            R_OPTIONAL = NULL;
            SUSPEND;
        END
        """
        # 1. Firebird verification
        if HAS_REAL_FB:
            self._cleanup_fb_proc("P_TEST_MIXED_OUT")
            self.fb_cur.execute(fb_sql)
            self.fb_con.commit()
            self.fb_cur.execute("SELECT R_MANDATORY, R_OPTIONAL FROM P_TEST_MIXED_OUT")
            self.assertEqual(self.fb_cur.fetchall(), [(99, None)])
            self._cleanup_fb_proc("P_TEST_MIXED_OUT")

        # 2. PostgreSQL verification
        if HAS_REAL_PG:
            pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
            self.pg_cur.execute(pg_sql)
            self.pg_cur.execute('SELECT * FROM "p_test_mixed_out"();')
            self.assertEqual(self.pg_cur.fetchall(), [(99, None)])

    def test_returning_into_not_null_guard_transpile(self):
        """
        INSERT/UPDATE/DELETE ... RETURNING ... INTO :R must inject NOT NULL guard
        when R is a NOT NULL output parameter.
        """
        fb_insert = """
        CREATE OR ALTER PROCEDURE P_RET_INSERT
        RETURNS (R INTEGER NOT NULL)
        AS
        BEGIN
            INSERT INTO T(V) VALUES(NULL) RETURNING V INTO :R;
            R = 1;
            SUSPEND;
        END
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_insert)
        # Guard must appear after the INSERT RETURNING INTO
        self.assertIn("RETURNING V INTO R;", pg_sql)
        # NOT NULL guard right after the RETURNING INTO statement
        lines = pg_sql.split('\n')
        returning_idx = next(i for i, l in enumerate(lines) if 'RETURNING V INTO R;' in l)
        guard_after = lines[returning_idx + 1]
        self.assertIn("IF R IS NULL THEN RAISE EXCEPTION", guard_after)

        # UPDATE RETURNING INTO
        fb_update = """
        CREATE OR ALTER PROCEDURE P_RET_UPDATE
        RETURNS (R INTEGER NOT NULL)
        AS
        BEGIN
            UPDATE T SET V = NULL WHERE ID = 1 RETURNING V INTO :R;
            SUSPEND;
        END
        """
        pg_upd = FirebirdToPostgresVisitor.transpile(fb_update)
        self.assertIn("RETURNING V INTO R;", pg_upd)
        lines_upd = pg_upd.split('\n')
        ret_idx = next(i for i, l in enumerate(lines_upd) if 'RETURNING V INTO R;' in l)
        self.assertIn("IF R IS NULL THEN RAISE EXCEPTION", lines_upd[ret_idx + 1])

        # DELETE RETURNING INTO
        fb_delete = """
        CREATE OR ALTER PROCEDURE P_RET_DELETE
        RETURNS (R INTEGER NOT NULL)
        AS
        BEGIN
            DELETE FROM T WHERE ID = 1 RETURNING V INTO :R;
            SUSPEND;
        END
        """
        pg_del = FirebirdToPostgresVisitor.transpile(fb_delete)
        self.assertIn("RETURNING V INTO R;", pg_del)
        lines_del = pg_del.split('\n')
        ret_idx_d = next(i for i, l in enumerate(lines_del) if 'RETURNING V INTO R;' in l)
        self.assertIn("IF R IS NULL THEN RAISE EXCEPTION", lines_del[ret_idx_d + 1])

    def test_returning_into_nullable_output_no_guard(self):
        """
        RETURNING INTO a nullable output should NOT inject guards.
        """
        fb_sql = """
        CREATE OR ALTER PROCEDURE P_RET_NULLABLE
        RETURNS (R INTEGER)
        AS
        BEGIN
            INSERT INTO T(V) VALUES(NULL) RETURNING V INTO :R;
            SUSPEND;
        END
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        # No NOT NULL guard after RETURNING INTO for nullable output
        lines = pg_sql.split('\n')
        for i, line in enumerate(lines):
            if 'RETURNING V INTO R;' in line:
                if i + 1 < len(lines):
                    self.assertNotIn("RAISE EXCEPTION", lines[i + 1])

    @unittest.skipUnless(HAS_REAL_FB and HAS_REAL_PG, "Live Firebird and PostgreSQL required")
    def test_returning_into_not_null_live_equivalence(self):
        """
        Execute INSERT RETURNING INTO :R (NOT NULL output) with NULL value
        on both Firebird and PostgreSQL, demanding equivalent error.
        """
        fb_sql = """
        CREATE OR ALTER PROCEDURE P_RET_LIVE
        RETURNS (R INTEGER NOT NULL)
        AS
        BEGIN
            INSERT INTO T_RET_LIVE(V) VALUES(NULL) RETURNING V INTO :R;
            SUSPEND;
        END
        """
        # Setup table in Firebird
        self._cleanup_fb_proc("P_RET_LIVE")
        for ddl in ["DROP TRIGGER T_RET_LIVE_BI", "DROP TABLE T_RET_LIVE", "DROP SEQUENCE GEN_T_RET_LIVE"]:
            try:
                self.fb_cur.execute(ddl)
                self.fb_con.commit()
            except Exception:
                self.fb_con.rollback()
        self.fb_cur.execute("CREATE TABLE T_RET_LIVE (ID INTEGER NOT NULL PRIMARY KEY, V INTEGER)")
        self.fb_cur.execute("CREATE GENERATOR GEN_T_RET_LIVE")
        self.fb_cur.execute("""
            CREATE OR ALTER TRIGGER T_RET_LIVE_BI FOR T_RET_LIVE
            ACTIVE BEFORE INSERT POSITION 0 AS BEGIN
                IF (NEW.ID IS NULL) THEN NEW.ID = GEN_ID(GEN_T_RET_LIVE, 1);
            END
        """)
        self.fb_con.commit()

        self._cleanup_fb_proc("P_RET_LIVE")
        self.fb_cur.execute(fb_sql)
        self.fb_con.commit()

        # Firebird: should raise validation error
        with self.assertRaises(Exception) as fb_cm:
            self.fb_cur.execute("SELECT R FROM P_RET_LIVE")
            self.fb_cur.fetchall()
        self.assertIn("validation error for variable R", str(fb_cm.exception))
        self.fb_con.rollback()

        # PostgreSQL setup
        self.pg_cur.execute("DROP TABLE IF EXISTS t_ret_live CASCADE;")
        self.pg_cur.execute("CREATE TABLE t_ret_live (id SERIAL PRIMARY KEY, v INTEGER);")
        self.pg_con.commit()

        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.pg_cur.execute(pg_sql)

        with self.assertRaises(psycopg2.Error) as pg_cm:
            self.pg_cur.execute('SELECT * FROM "p_ret_live"();')
        self.assertIn("validation error for variable R, value null", str(pg_cm.exception))
        self.pg_con.rollback()

        # Cleanup
        self._cleanup_fb_proc("P_RET_LIVE")
        try:
            self.fb_cur.execute("DROP TABLE T_RET_LIVE")
            self.fb_con.commit()
        except Exception:
            self.fb_con.rollback()

        self.pg_cur.execute("DROP TABLE IF EXISTS t_ret_live CASCADE;")
        self.pg_con.commit()


if __name__ == '__main__':
    unittest.main()

