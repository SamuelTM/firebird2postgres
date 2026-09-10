import datetime
import unittest
import psycopg2
import firebirdsql

from tests.db_isolation import (
    get_test_firebird_connection,
    get_test_postgres_connection,
    require_live_databases,
    require_live_firebird,
    require_live_postgres,
    requires_firebird_class,
    requires_live_databases_class,
    requires_postgres_class,
)
from transpiler import FirebirdToPostgresVisitor
from utils import split_sql_statements


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

    def test_star_projection_restricted_to_real_scope(self):
        """
        P1 regression: SELECT * over (T JOIN U) must not import Z.D DATE
        from outside the subquery. T.D TIMESTAMP keeps timestamp arithmetic
        (no ::date cast discarding the time).
        """
        sql = "SELECT DATEADD(HOUR, 1, X.D) FROM (SELECT * FROM T JOIN U ON 1 = 1) X;"
        symbols = {"t.d": "TIMESTAMP", "u.k": "INTEGER", "z.d": "DATE"}
        out = FirebirdToPostgresVisitor.transpile(sql, symbols=symbols)
        self.assertNotIn("::date", out)
        self.assertIn("(X.D + (1) * INTERVAL '1 hour')", out)

    def test_star_projection_still_sees_participating_date_column(self):
        """
        P1 regression counterpart: SELECT * DOES propagate DATE from tables
        that really participate in the subquery.
        """
        sql = "SELECT DATEADD(DAY, 1, X.D) - X.D FROM (SELECT * FROM T JOIN U ON 1 = 1) X;"
        symbols = {"t.d": "DATE", "u.k": "INTEGER", "z.d": "TIMESTAMP"}
        out = FirebirdToPostgresVisitor.transpile(sql, symbols=symbols)
        self.assertIn("((X.D + (1) * INTERVAL '1 day')::date) - X.D", out)

    def test_cte_propagates_date_type(self):
        """
        P1 regression: WITH X AS (SELECT D FROM T) propagates D DATE, so
        DATEADD casts to ::date and date subtraction stays integer.
        """
        sql = "WITH X AS (SELECT D FROM T) SELECT DATEADD(DAY, 1, X.D) - X.D FROM X;"
        out = FirebirdToPostgresVisitor.transpile(sql, symbols={"t.d": "DATE"})
        self.assertIn("((X.D + (1) * INTERVAL '1 day')::date) - X.D", out)

    def test_cte_with_column_alias_propagates(self):
        """
        P1 regression: WITH X(dt) AS ... maps the inner projection positionally
        to the CTE column alias.
        """
        sql = "WITH X(dt) AS (SELECT D FROM T) SELECT DATEADD(DAY, 1, X.dt) - X.dt FROM X;"
        out = FirebirdToPostgresVisitor.transpile(sql, symbols={"t.d": "DATE"})
        self.assertIn("((X.dt + (1) * INTERVAL '1 day')::date) - X.dt", out)

    def test_nested_cte_propagates(self):
        """
        P1 regression: a CTE selecting from another CTE inherits its types.
        """
        sql = (
            "WITH A AS (SELECT D FROM T), "
            "B AS (SELECT D FROM A) "
            "SELECT DATEADD(DAY, 1, B.D) - B.D FROM B;"
        )
        out = FirebirdToPostgresVisitor.transpile(sql, symbols={"t.d": "DATE"})
        self.assertIn("((B.D + (1) * INTERVAL '1 day')::date) - B.D", out)

    def test_self_referencing_cte_terminates(self):
        """
        P1 regression guard: a self-referencing CTE must not hang inference.
        """
        sql = "WITH X AS (SELECT n FROM X) SELECT n FROM X;"
        out = FirebirdToPostgresVisitor.transpile(sql, symbols={})
        self.assertIn("X", out)

    def test_same_name_projections_keep_positions_regardless_of_order(self):
        """
        P1 regression: SELECT T.D, U.D yields two 'd' slots in written order
        instead of collapsing into one dict key. X(A,B) maps positionally,
        so B is always U.D's type no matter how metadata was inserted.
        """
        sql = ("WITH X(A,B) AS (SELECT T.D, U.D FROM T JOIN U ON 1 = 1) "
               "SELECT DATEADD(DAY, 1, X.B) - X.B FROM X;")
        for symbols in ({"t.d": "TIMESTAMP", "u.d": "DATE"},
                        {"u.d": "DATE", "t.d": "TIMESTAMP"}):
            out = FirebirdToPostgresVisitor.transpile(sql, symbols=dict(symbols))
            self.assertIn("((X.B + (1) * INTERVAL '1 day')::date) - X.B", out,
                          f"failed for insertion order {list(symbols)}")

    def test_star_cte_alias_follows_catalog_position_order(self):
        """
        P1 regression: WITH X(A,B) AS (SELECT * FROM T) pairs aliases with
        T's real column order (K, D). Catalog rows inverted by position
        still produce identical symbols, hence identical inference.
        """
        from unittest.mock import MagicMock
        from engine.ddl_exporter import DdlExporter
        rows_kd = [
            ('T', 'K', 8, 0, 4, None, None, None, None, 0),
            ('T', 'D', 12, 0, 4, None, None, None, None, 1),
        ]
        orders = []
        for rows in (rows_kd, list(reversed(rows_kd))):
            cur = MagicMock()
            cur.fetchall.return_value = rows
            symbols = DdlExporter._fetch_all_column_symbols(cur)
            orders.append([k for k in symbols if '.' in k])
            sql = ("WITH X(A,B) AS (SELECT * FROM T) "
                   "SELECT DATEADD(DAY, 1, X.B) - X.B FROM X;")
            out = FirebirdToPostgresVisitor.transpile(sql, symbols=dict(symbols))
            self.assertIn("((X.B + (1) * INTERVAL '1 day')::date) - X.B", out)
        self.assertEqual(orders[0], orders[1])
        self.assertEqual(orders[0], ['t.k', 't.d'])

    def test_explicit_aliased_same_name_projections(self):
        """
        P1 regression: SELECT T.D AS D1, U.D AS D2 keeps both identities
        with their own types.
        """
        sql = ("WITH X AS (SELECT T.D AS D1, U.D AS D2 FROM T JOIN U ON 1 = 1) "
               "SELECT DATEADD(DAY, 1, X.D2) - X.D2 FROM X;")
        for symbols in ({"t.d": "TIMESTAMP", "u.d": "DATE"},
                        {"u.d": "DATE", "t.d": "TIMESTAMP"}):
            out = FirebirdToPostgresVisitor.transpile(sql, symbols=dict(symbols))
            self.assertIn("((X.D2 + (1) * INTERVAL '1 day')::date) - X.D2", out)


@requires_postgres_class
class TestDateInferenceLivePostgresRegression(unittest.TestCase):
    """
    Live PostgreSQL regression verifying that the date subtraction transpilation
    yields integer 1 and type 'integer' instead of interval.
    """

    def setUp(self):
        require_live_postgres(self)
        self.conn = get_test_postgres_connection()
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

    def test_live_pg_timestamp_preserved_through_star_join_subquery(self):
        """
        P1 regression (value AND type): T.D TIMESTAMP with non-null time must
        survive DATEADD over (SELECT * FROM T JOIN U); a DATE-typed Z outside
        the subquery scope must not truncate it via ::date.
        """
        try:
            self.cur.execute("DROP TABLE IF EXISTS reg_ts_t CASCADE;")
            self.cur.execute("DROP TABLE IF EXISTS reg_ts_u CASCADE;")
            self.cur.execute("DROP TABLE IF EXISTS reg_ts_z CASCADE;")
            self.cur.execute("CREATE TABLE reg_ts_t (d TIMESTAMP, k INTEGER);")
            self.cur.execute("CREATE TABLE reg_ts_u (k INTEGER);")
            self.cur.execute("CREATE TABLE reg_ts_z (d DATE);")
            self.cur.execute("INSERT INTO reg_ts_t VALUES ('2026-09-08 15:30:45', 1);")
            self.cur.execute("INSERT INTO reg_ts_u VALUES (1);")
            self.cur.execute("INSERT INTO reg_ts_z VALUES ('2026-01-01');")

            fb_sql = ("SELECT DATEADD(HOUR, 1, X.D) FROM "
                      "(SELECT * FROM REG_TS_T JOIN REG_TS_U ON 1 = 1) X;")
            symbols = {"reg_ts_t.d": "TIMESTAMP", "reg_ts_u.k": "INTEGER",
                       "reg_ts_z.d": "DATE"}
            pg_sel = FirebirdToPostgresVisitor.transpile(fb_sql, symbols=symbols)
            self.assertNotIn("::date", pg_sel)

            self.cur.execute(
                f"SELECT v, pg_typeof(v)::text FROM ({pg_sel.rstrip().rstrip(';')}) s(v);"
            )
            row = self.cur.fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row[0], datetime.datetime(2026, 9, 8, 16, 30, 45))
            self.assertEqual(row[1], "timestamp without time zone")
        finally:
            self.cur.execute("DROP TABLE IF EXISTS reg_ts_t CASCADE;")
            self.cur.execute("DROP TABLE IF EXISTS reg_ts_u CASCADE;")
            self.cur.execute("DROP TABLE IF EXISTS reg_ts_z CASCADE;")

    def test_live_pg_cte_date_subtraction_yields_integer(self):
        """
        P1 regression (value AND type): a CTE projecting D DATE propagates
        the type, so DATEADD casts to ::date and date subtraction is integer.
        """
        try:
            self.cur.execute("DROP TABLE IF EXISTS reg_cte_t CASCADE;")
            self.cur.execute("CREATE TABLE reg_cte_t (d DATE);")
            self.cur.execute("INSERT INTO reg_cte_t VALUES ('2026-09-08');")

            fb_sql = ("WITH X AS (SELECT D FROM REG_CTE_T) "
                      "SELECT DATEADD(DAY, 1, X.D) - X.D FROM X;")
            pg_sel = FirebirdToPostgresVisitor.transpile(
                fb_sql, symbols={"reg_cte_t.d": "DATE"})
            self.assertIn("::date", pg_sel)

            self.cur.execute(
                f"SELECT v, pg_typeof(v)::text FROM ({pg_sel.rstrip().rstrip(';')}) s(v);"
            )
            row = self.cur.fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row[0], 1)
            self.assertEqual(row[1], "integer")
        finally:
            self.cur.execute("DROP TABLE IF EXISTS reg_cte_t CASCADE;")


@requires_live_databases_class
class TestDateInferenceCrossDatabaseRegression(unittest.TestCase):
    """
    P1 regression: the same CTE queries run natively in Firebird and
    transpiled in PostgreSQL must agree on VALUE and TYPE, with CTE column
    positions (not metadata order) driving inference.
    """

    def setUp(self):
        require_live_databases(self)
        self.pg_con = get_test_postgres_connection()
        self.pg_con.autocommit = True
        self.pg_cur = self.pg_con.cursor()
        self.fb_con = get_test_firebird_connection()
        self.fb_cur = self.fb_con.cursor()
        self._cleanup()
        self.fb_cur.execute("CREATE TABLE REG_DATEPOS_T (K INTEGER, D DATE);")
        self.fb_con.commit()
        self.fb_cur.execute("INSERT INTO REG_DATEPOS_T VALUES (5, '2026-09-08');")
        self.fb_con.commit()
        self.fb_cur.execute("CREATE TABLE REG_DATEPOS_U (D DATE);")
        self.fb_con.commit()
        self.fb_cur.execute("INSERT INTO REG_DATEPOS_U VALUES ('2026-09-08');")
        self.fb_con.commit()
        self.fb_cur.execute("CREATE TABLE REG_DATEPOS_T1 (D TIMESTAMP);")
        self.fb_con.commit()
        self.fb_cur.execute("INSERT INTO REG_DATEPOS_T1 VALUES ('2026-09-08 15:30:45');")
        self.fb_con.commit()
        self.fb_cur.execute("CREATE TABLE REG_DATEPOS_T2 (D DATE);")
        self.fb_con.commit()
        self.fb_cur.execute("INSERT INTO REG_DATEPOS_T2 VALUES ('2026-09-08');")
        self.fb_con.commit()
        self.pg_cur.execute("DROP TABLE IF EXISTS reg_datepos_t CASCADE;")
        self.pg_cur.execute("DROP TABLE IF EXISTS reg_datepos_u CASCADE;")
        self.pg_cur.execute("DROP TABLE IF EXISTS reg_datepos_t1 CASCADE;")
        self.pg_cur.execute("DROP TABLE IF EXISTS reg_datepos_t2 CASCADE;")
        self.pg_cur.execute("CREATE TABLE reg_datepos_t (k INTEGER, d DATE);")
        self.pg_cur.execute("CREATE TABLE reg_datepos_u (d DATE);")
        self.pg_cur.execute("CREATE TABLE reg_datepos_t1 (d TIMESTAMP);")
        self.pg_cur.execute("CREATE TABLE reg_datepos_t2 (d DATE);")
        self.pg_cur.execute("INSERT INTO reg_datepos_t VALUES (5, '2026-09-08');")
        self.pg_cur.execute("INSERT INTO reg_datepos_u VALUES ('2026-09-08');")
        self.pg_cur.execute("INSERT INTO reg_datepos_t1 VALUES ('2026-09-08 15:30:45');")
        self.pg_cur.execute("INSERT INTO reg_datepos_t2 VALUES ('2026-09-08');")

    def _cleanup(self):
        for stmt in ("DROP TABLE REG_DATEPOS_T;", "DROP TABLE REG_DATEPOS_U;",
                     "DROP TABLE REG_DATEPOS_T1;", "DROP TABLE REG_DATEPOS_T2;"):
            try:
                self.fb_cur.execute(stmt)
                self.fb_con.commit()
            except Exception:
                pass
        for stmt in ("DROP TABLE IF EXISTS reg_datepos_t CASCADE;",
                     "DROP TABLE IF EXISTS reg_datepos_u CASCADE;",
                     "DROP TABLE IF EXISTS reg_datepos_t1 CASCADE;",
                     "DROP TABLE IF EXISTS reg_datepos_t2 CASCADE;"):
            try:
                self.pg_cur.execute(stmt)
            except Exception:
                pass

    def tearDown(self):
        try:
            self._cleanup()
        finally:
            try:
                self.fb_cur.close()
            except Exception:
                pass
            try:
                self.fb_con.close()
            except Exception:
                pass
            try:
                self.pg_cur.close()
            except Exception:
                pass
            try:
                self.pg_con.close()
            except Exception:
                pass

    def test_star_cte_position_matches_in_both_databases(self):
        """
        WITH X(A,B) AS (SELECT * FROM T): B is DATE by position in both
        databases — value 1, PG type integer, FB native integer.
        """
        fb_sql = ("WITH X(A, B) AS (SELECT * FROM REG_DATEPOS_T) "
                  "SELECT DATEADD(DAY, 1, B) - B FROM X")
        self.fb_cur.execute(fb_sql)
        fb_rows = self.fb_cur.fetchall()
        self.assertEqual([(1,)], [(r[0],) for r in fb_rows])
        self.assertIsInstance(fb_rows[0][0], int)

        pg_sql = FirebirdToPostgresVisitor.transpile(
            fb_sql, symbols={"reg_datepos_t.k": "INTEGER", "reg_datepos_t.d": "DATE"})
        self.assertIn("::date", pg_sql)
        self.cur_execute_pg(pg_sql, fb_rows)

    def cur_execute_pg(self, pg_sql, fb_rows):
        inner = pg_sql.rstrip().rstrip(';')
        self.pg_cur.execute(
            f"SELECT v, pg_typeof(v)::text FROM ({inner}) s(v);")
        pg_row = self.pg_cur.fetchone()
        self.assertIsNotNone(pg_row)
        self.assertEqual(pg_row[0], fb_rows[0][0])
        self.assertEqual(pg_row[1], "integer")

    def test_same_name_projections_match_in_both_databases(self):
        """
        WITH X(A,B) AS (SELECT T1.D, T2.D ...) with T1.D TIMESTAMP and
        T2.D DATE: A keeps the time, B stays a date subtraction. Values and
        types agree across Firebird and PostgreSQL by position.
        """
        fb_sql = ("WITH X(A, B) AS (SELECT T1.D, T2.D FROM REG_DATEPOS_T1 T1 "
                  "JOIN REG_DATEPOS_T2 T2 ON 1 = 1) "
                  "SELECT DATEADD(HOUR, 1, A), DATEADD(DAY, 1, B) - B FROM X")
        self.fb_cur.execute(fb_sql)
        fb_rows = self.fb_cur.fetchall()
        self.assertEqual(len(fb_rows), 1)
        self.assertEqual(fb_rows[0][0], datetime.datetime(2026, 9, 8, 16, 30, 45))
        self.assertEqual(fb_rows[0][1], 1)
        self.assertIsInstance(fb_rows[0][1], int)

        symbols = {"reg_datepos_t1.d": "TIMESTAMP", "reg_datepos_t2.d": "DATE"}
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql, symbols=dict(symbols))
        self.assertIn("(X.A + (1) * INTERVAL '1 hour')", pg_sql)
        self.assertIn("::date", pg_sql)
        inner = pg_sql.rstrip().rstrip(';')
        self.pg_cur.execute(
            f"SELECT a, pg_typeof(a)::text, b, pg_typeof(b)::text FROM ({inner}) s(a, b);")
        pg_row = self.pg_cur.fetchone()
        self.assertIsNotNone(pg_row)
        self.assertEqual(pg_row[0], fb_rows[0][0])
        self.assertEqual(pg_row[1], "timestamp without time zone")
        self.assertEqual(pg_row[2], fb_rows[0][1])
        self.assertEqual(pg_row[3], "integer")


@requires_firebird_class
class TestDateInferenceLiveFirebirdRegression(unittest.TestCase):
    """
    Live Firebird regression verifying native behavior of trigger and derived table view.
    """

    def setUp(self):
        require_live_firebird(self)
        self.conn = get_test_firebird_connection()
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
