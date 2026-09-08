import unittest
import psycopg2
import firebirdsql

from config import (
    get_postgres_connection,
    get_firebird_connection,
    PostgresConfig,
    FirebirdConfig,
)
from transpiler import FirebirdToPostgresVisitor
from utils import split_sql_statements


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


class TestDateInferenceUnitRegression(unittest.TestCase):
    """
    Unit tests ensuring DATE metadata propagates to NEW/OLD trigger records
    and derived table (subquery) projections.
    """

    def test_trigger_new_record_date_inference(self):
        sql = """
        CREATE TRIGGER TR_TEST FOR T BEFORE INSERT AS
        BEGIN
            NEW.N = DATEADD(DAY, 1, NEW.D) - NEW.D;
        END
        """
        symbols = {"t.d": "DATE", "t.n": "INTEGER"}
        out = FirebirdToPostgresVisitor.transpile(sql, symbols=symbols)
        self.assertIn("((NEW.D + (1) * INTERVAL '1 day')::date) - NEW.D", out)

    def test_trigger_old_record_date_inference(self):
        sql = """
        CREATE TRIGGER TR_UPDATE FOR T BEFORE UPDATE AS
        BEGIN
            NEW.N = DATEADD(DAY, 1, OLD.D) - OLD.D;
        END
        """
        symbols = {"t.d": "DATE", "t.n": "INTEGER"}
        out = FirebirdToPostgresVisitor.transpile(sql, symbols=symbols)
        self.assertIn("((OLD.D + (1) * INTERVAL '1 day')::date) - OLD.D", out)

    def test_derived_table_date_inference(self):
        sql = """
        CREATE VIEW V_TEST AS
        SELECT DATEADD(DAY, 1, X.D) - X.D AS N FROM (SELECT D FROM T) X;
        """
        symbols = {"t.d": "DATE", "t.n": "INTEGER"}
        out = FirebirdToPostgresVisitor.transpile(sql, symbols=symbols)
        self.assertIn("((X.D + (1) * INTERVAL '1 day')::date) - X.D", out)

    def test_derived_table_with_aliased_date_column(self):
        sql = """
        CREATE VIEW V_TEST_ALIAS AS
        SELECT DATEADD(DAY, 2, X.MY_DATE) - X.MY_DATE AS N FROM (SELECT D AS MY_DATE FROM T) X;
        """
        symbols = {"t.d": "DATE", "t.n": "INTEGER"}
        out = FirebirdToPostgresVisitor.transpile(sql, symbols=symbols)
        self.assertIn("((X.MY_DATE + (2) * INTERVAL '1 day')::date) - X.MY_DATE", out)

    def test_nested_derived_table_date_inference(self):
        sql = """
        CREATE VIEW V_NESTED AS
        SELECT DATEADD(DAY, 1, Y.D) - Y.D AS N FROM (SELECT D FROM (SELECT D FROM T) X) Y;
        """
        symbols = {"t.d": "DATE", "t.n": "INTEGER"}
        out = FirebirdToPostgresVisitor.transpile(sql, symbols=symbols)
        self.assertIn("((Y.D + (1) * INTERVAL '1 day')::date) - Y.D", out)


@unittest.skipUnless(HAS_REAL_PG, "PostgreSQL not available")
class TestDateInferenceLivePostgresRegression(unittest.TestCase):
    """
    Live PostgreSQL regression verifying that the date subtraction transpilation
    yields integer 1 and type 'integer' instead of interval.
    """

    def setUp(self):
        self.conn = get_postgres_connection(PostgresConfig())
        self.conn.autocommit = True
        self.cur = self.conn.cursor()
        self.cur.execute("DROP TABLE IF EXISTS t CASCADE;")
        self.cur.execute("CREATE TABLE t (d DATE, n INTEGER);")

    def tearDown(self):
        try:
            self.cur.execute("DROP TABLE IF EXISTS t CASCADE;")
        finally:
            self.cur.close()
            self.conn.close()

    def test_live_pg_trigger_new_date_subtraction(self):
        sql = """
        CREATE TRIGGER TR_TEST FOR T BEFORE INSERT AS
        BEGIN
            NEW.N = DATEADD(DAY, 1, NEW.D) - NEW.D;
        END
        """
        symbols = {"t.d": "DATE", "t.n": "INTEGER"}
        pg_sql = FirebirdToPostgresVisitor.transpile(sql, symbols=symbols)

        for stmt, _ in split_sql_statements(pg_sql):
            stmt = stmt.strip()
            if stmt:
                self.cur.execute(stmt)

        self.cur.execute("INSERT INTO t (d) VALUES ('2026-09-08') RETURNING n;")
        row = self.cur.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], 1)

    def test_live_pg_derived_table_view(self):
        self.cur.execute("INSERT INTO t (d) VALUES ('2026-09-08');")

        sql = """
        CREATE VIEW V_TEST AS
        SELECT DATEADD(DAY, 1, X.D) - X.D AS N FROM (SELECT D FROM T) X;
        """
        symbols = {"t.d": "DATE", "t.n": "INTEGER"}
        pg_sql = FirebirdToPostgresVisitor.transpile(sql, symbols=symbols)

        for stmt, _ in split_sql_statements(pg_sql):
            stmt = stmt.strip()
            if stmt:
                self.cur.execute(stmt)

        self.cur.execute("SELECT n, pg_typeof(n)::text FROM v_test;")
        row = self.cur.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], 1)
        self.assertEqual(row[1], "integer")


@unittest.skipUnless(HAS_REAL_FB, "Firebird not available")
class TestDateInferenceLiveFirebirdRegression(unittest.TestCase):
    """
    Live Firebird regression verifying native behavior of trigger and derived table view.
    """

    def setUp(self):
        self.conn = get_firebird_connection(FirebirdConfig())
        self.cur = self.conn.cursor()
        self._cleanup()
        self.cur.execute("CREATE TABLE T_DATE (D DATE, N INTEGER);")
        self.conn.commit()

    def _cleanup(self):
        for stmt in [
            "DROP VIEW V_DATE_TEST;",
            "DROP TRIGGER TR_DATE_TEST;",
            "DROP TABLE T_DATE;",
        ]:
            try:
                self.cur.execute(stmt)
                self.conn.commit()
            except Exception:
                pass

    def tearDown(self):
        self._cleanup()
        self.cur.close()
        self.conn.close()

    def test_live_fb_trigger_and_view(self):
        self.cur.execute("""
        CREATE TRIGGER TR_DATE_TEST FOR T_DATE BEFORE INSERT AS
        BEGIN
            NEW.N = DATEADD(DAY, 1, NEW.D) - NEW.D;
        END
        """)
        self.conn.commit()

        self.cur.execute("INSERT INTO T_DATE (D) VALUES ('2026-09-08');")
        self.conn.commit()

        self.cur.execute("SELECT N FROM T_DATE;")
        row = self.cur.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], 1)

        self.cur.execute("""
        CREATE VIEW V_DATE_TEST AS
        SELECT DATEADD(DAY, 1, X.D) - X.D AS N FROM (SELECT D FROM T_DATE) X;
        """)
        self.conn.commit()

        self.cur.execute("SELECT N FROM V_DATE_TEST;")
        row = self.cur.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], 1)


if __name__ == "__main__":
    unittest.main()
