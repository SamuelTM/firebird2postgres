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


class TestJoinUsingTranspiler(unittest.TestCase):
    """
    Unit tests ensuring JOIN ... USING syntax and combined column semantics
    are fully preserved without losing the join, dropping clauses, or erroneously
    qualifying combined columns with table aliases.
    """

    def test_reproduced_bug_select_id_join_using(self):
        # Original issue: SELECT ID FROM TA JOIN TB USING (ID) -> SELECT JOIN.ID FROM TA JOIN
        sql = "SELECT ID FROM TA JOIN TB USING (ID);"
        symbols = {"TA.ID": "INTEGER", "TB.ID": "INTEGER"}
        res = FirebirdToPostgresVisitor.transpile(sql, symbols=symbols)
        self.assertIn("SELECT ID FROM TA JOIN TB USING (ID)", res)
        self.assertNotIn("JOIN.ID", res)
        self.assertNotIn("TA.ID", res)

    def test_reproduced_bug_create_view_join_using(self):
        sql = "CREATE VIEW V AS SELECT ID FROM TA JOIN TB USING (ID);"
        symbols = {"TA.ID": "INTEGER", "TB.ID": "INTEGER"}
        res = FirebirdToPostgresVisitor.transpile(sql, symbols=symbols)
        self.assertIn('DROP VIEW IF EXISTS "v" CASCADE;', res)
        self.assertIn('CREATE VIEW "v" AS SELECT ID FROM TA JOIN TB USING (ID);', res)
        self.assertNotIn("JOIN.ID", res)

    def test_inner_join_using(self):
        sql = "CREATE VIEW V AS SELECT ID FROM TA INNER JOIN TB USING (ID);"
        symbols = {"TA.ID": "INTEGER", "TB.ID": "INTEGER"}
        res = FirebirdToPostgresVisitor.transpile(sql, symbols=symbols)
        self.assertIn('CREATE VIEW "v" AS SELECT ID FROM TA INNER JOIN TB USING (ID);', res)

    def test_left_join_using(self):
        sql = "CREATE VIEW V AS SELECT ID FROM TA LEFT JOIN TB USING (ID);"
        symbols = {"TA.ID": "INTEGER", "TB.ID": "INTEGER"}
        res = FirebirdToPostgresVisitor.transpile(sql, symbols=symbols)
        self.assertIn('CREATE VIEW "v" AS SELECT ID FROM TA LEFT JOIN TB USING (ID);', res)

    def test_left_outer_join_using(self):
        sql = "CREATE VIEW V AS SELECT ID FROM TA LEFT OUTER JOIN TB USING (ID);"
        symbols = {"TA.ID": "INTEGER", "TB.ID": "INTEGER"}
        res = FirebirdToPostgresVisitor.transpile(sql, symbols=symbols)
        self.assertIn('CREATE VIEW "v" AS SELECT ID FROM TA LEFT OUTER JOIN TB USING (ID);', res)

    def test_full_join_using(self):
        sql = "CREATE VIEW V AS SELECT ID FROM TA FULL JOIN TB USING (ID);"
        symbols = {"TA.ID": "INTEGER", "TB.ID": "INTEGER"}
        res = FirebirdToPostgresVisitor.transpile(sql, symbols=symbols)
        self.assertIn('CREATE VIEW "v" AS SELECT ID FROM TA FULL JOIN TB USING (ID);', res)

    def test_full_outer_join_using(self):
        sql = "CREATE VIEW V AS SELECT ID FROM TA FULL OUTER JOIN TB USING (ID);"
        symbols = {"TA.ID": "INTEGER", "TB.ID": "INTEGER"}
        res = FirebirdToPostgresVisitor.transpile(sql, symbols=symbols)
        self.assertIn('CREATE VIEW "v" AS SELECT ID FROM TA FULL OUTER JOIN TB USING (ID);', res)

    def test_select_star_join_using(self):
        for join_clause in ["JOIN", "INNER JOIN", "LEFT JOIN", "FULL JOIN"]:
            sql = f"CREATE VIEW V AS SELECT * FROM TA {join_clause} TB USING (ID);"
            res = FirebirdToPostgresVisitor.transpile(sql)
            self.assertIn(f"SELECT * FROM TA {join_clause} TB USING (ID);", res)

    def test_combined_column_and_other_columns_disambiguation(self):
        sql = "CREATE VIEW V AS SELECT ID, VAL_A, VAL_B FROM TA JOIN TB USING (ID);"
        symbols = {
            "TA.ID": "INTEGER", "TB.ID": "INTEGER",
            "TA.VAL_A": "VARCHAR", "TB.VAL_B": "VARCHAR"
        }
        res = FirebirdToPostgresVisitor.transpile(sql, symbols=symbols)
        # ID is combined (unqualified), VAL_A belongs to TA, VAL_B belongs to TB
        self.assertIn('SELECT ID, TA.VAL_A, TB.VAL_B FROM TA JOIN TB USING (ID);', res)

    def test_explicitly_qualified_columns_with_combined_column(self):
        sql = "CREATE VIEW V AS SELECT TA.ID, TB.ID, ID FROM TA FULL JOIN TB USING (ID);"
        symbols = {"TA.ID": "INTEGER", "TB.ID": "INTEGER"}
        res = FirebirdToPostgresVisitor.transpile(sql, symbols=symbols)
        self.assertIn('SELECT TA.ID, TB.ID, ID FROM TA FULL JOIN TB USING (ID);', res)

    def test_multiple_using_columns(self):
        sql = "CREATE VIEW V AS SELECT ID1, ID2 FROM TA JOIN TB USING (ID1, ID2);"
        symbols = {
            "TA.ID1": "INT", "TB.ID1": "INT",
            "TA.ID2": "INT", "TB.ID2": "INT",
        }
        res = FirebirdToPostgresVisitor.transpile(sql, symbols=symbols)
        self.assertIn('SELECT ID1, ID2 FROM TA JOIN TB USING (ID1, ID2);', res)

    def test_chained_joins_with_using(self):
        sql = "CREATE VIEW V AS SELECT ID FROM TA JOIN TB USING (ID) JOIN TC USING (ID);"
        symbols = {"TA.ID": "INTEGER", "TB.ID": "INTEGER", "TC.ID": "INTEGER"}
        res = FirebirdToPostgresVisitor.transpile(sql, symbols=symbols)
        self.assertIn('SELECT ID FROM TA JOIN TB USING (ID) JOIN TC USING (ID);', res)

    def test_procedure_with_for_select_using(self):
        fb_proc = """
        CREATE PROCEDURE SP_TEST AS
        DECLARE VARIABLE V_ID INTEGER;
        BEGIN
            FOR SELECT ID FROM TA FULL JOIN TB USING (ID) INTO :V_ID DO
            BEGIN
                V_ID = V_ID + 1;
            END
        END;
        """
        symbols = {"TA.ID": "INTEGER", "TB.ID": "INTEGER"}
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_proc, symbols=symbols)
        self.assertIn("FOR V_ID IN SELECT ID FROM TA FULL JOIN TB USING (ID) LOOP", pg_sql)


class TestJoinUsingExecution(unittest.TestCase):
    """
    Live regression test comparing query execution results and column metadata
    between Firebird and PostgreSQL for INNER, LEFT, and FULL JOIN ... USING,
    including unmatched rows, SELECT ID, and SELECT *.
    """

    def setUp(self):
        if HAS_REAL_PG and HAS_REAL_FB:
            self.pg_conn = get_postgres_connection(PostgresConfig())
            self.fb_conn = get_firebird_connection(FirebirdConfig())
            self.pg_cur = self.pg_conn.cursor()
            self.fb_cur = self.fb_conn.cursor()

            # Clean and setup test tables with unmatched rows
            self.pg_cur.execute("DROP TABLE IF EXISTS ta_reg_using, tb_reg_using CASCADE;")
            self.pg_cur.execute("CREATE TABLE ta_reg_using (id INT, val_a VARCHAR(20));")
            self.pg_cur.execute("CREATE TABLE tb_reg_using (id INT, val_b VARCHAR(20));")
            self.pg_cur.execute("INSERT INTO ta_reg_using VALUES (1, 'a1'), (2, 'a2');")
            self.pg_cur.execute("INSERT INTO tb_reg_using VALUES (2, 'b2'), (3, 'b3');")
            self.pg_conn.commit()

            self.fb_cur.execute("RECREATE TABLE TA_REG_USING (ID INT, VAL_A VARCHAR(20));")
            self.fb_cur.execute("RECREATE TABLE TB_REG_USING (ID INT, VAL_B VARCHAR(20));")
            self.fb_conn.commit()
            self.fb_cur.execute("INSERT INTO TA_REG_USING VALUES (1, 'a1');")
            self.fb_cur.execute("INSERT INTO TA_REG_USING VALUES (2, 'a2');")
            self.fb_cur.execute("INSERT INTO TB_REG_USING VALUES (2, 'b2');")
            self.fb_cur.execute("INSERT INTO TB_REG_USING VALUES (3, 'b3');")
            self.fb_conn.commit()
        else:
            self.pg_conn = None
            self.fb_conn = None

    def tearDown(self):
        if self.pg_conn:
            try:
                self.pg_cur.execute("DROP TABLE IF EXISTS ta_reg_using, tb_reg_using CASCADE;")
                self.pg_conn.commit()
            except Exception:
                pass
            self.pg_conn.close()
        if self.fb_conn:
            try:
                self.fb_cur.execute("DROP TABLE TA_REG_USING;")
                self.fb_cur.execute("DROP TABLE TB_REG_USING;")
                self.fb_conn.commit()
            except Exception:
                pass
            self.fb_conn.close()

    @staticmethod
    def _normalize_row(r):
        cleaned = []
        for val in r:
            if isinstance(val, str):
                cleaned.append(val.strip())
            else:
                cleaned.append(val)
        return tuple(cleaned)

    @unittest.skipUnless(HAS_REAL_PG and HAS_REAL_FB, "Live Firebird and PostgreSQL instances required")
    def test_inner_left_full_join_using_results_and_columns_match(self):
        """
        Compares results and column names between Firebird and PostgreSQL for:
        - INNER, LEFT, and FULL JOIN ... USING
        - Unmatched rows (ID=1 in TA only, ID=3 in TB only, ID=2 in both)
        - SELECT ID and SELECT *
        """
        for join_type in ["INNER", "LEFT", "FULL"]:
            for sel in ["SELECT ID", "SELECT *"]:
                fb_query = f"{sel} FROM TA_REG_USING {join_type} JOIN TB_REG_USING USING (ID) ORDER BY ID"
                pg_query = f"{sel} FROM ta_reg_using {join_type} JOIN tb_reg_using USING (id) ORDER BY id"

                self.fb_cur.execute(fb_query)
                fb_cols = [d[0].lower() for d in self.fb_cur.description]
                fb_rows = [self._normalize_row(r) for r in self.fb_cur.fetchall()]

                self.pg_cur.execute(pg_query)
                pg_cols = [d[0].lower() for d in self.pg_cur.description]
                pg_rows = [self._normalize_row(r) for r in self.pg_cur.fetchall()]

                # Compare columns
                self.assertEqual(
                    fb_cols, pg_cols,
                    f"Columns mismatch for {join_type} {sel}: Firebird={fb_cols} vs Postgres={pg_cols}"
                )

                # Compare row values
                self.assertEqual(
                    fb_rows, pg_rows,
                    f"Row results mismatch for {join_type} {sel}: Firebird={fb_rows} vs Postgres={pg_rows}"
                )

                # Specific check for combined column in FULL JOIN:
                # ID=3 (unmatched row from TB) must have ID=3, not NULL
                if join_type == "FULL":
                    if sel == "SELECT ID":
                        ids = [r[0] for r in pg_rows]
                        self.assertEqual(ids, [1, 2, 3], "FULL JOIN combined column must include [1, 2, 3]")
                    elif sel == "SELECT *":
                        # row 3: (3, None, 'b3')
                        self.assertEqual(pg_rows[2], (3, None, "b3"))

    @unittest.skipUnless(HAS_REAL_PG and HAS_REAL_FB, "Live Firebird and PostgreSQL instances required")
    def test_transpiled_view_execution_matches_firebird(self):
        """
        Creates a view in Firebird using FULL JOIN ... USING, transpiles it,
        creates the view in PostgreSQL, and verifies identical query results.
        """
        fb_view_ddl = "CREATE OR ALTER VIEW VW_REG_USING AS SELECT ID, VAL_A, VAL_B FROM TA_REG_USING FULL JOIN TB_REG_USING USING (ID);"
        symbols = {
            "TA_REG_USING.ID": "INTEGER", "TB_REG_USING.ID": "INTEGER",
            "TA_REG_USING.VAL_A": "VARCHAR", "TB_REG_USING.VAL_B": "VARCHAR",
        }
        pg_view_ddl = FirebirdToPostgresVisitor.transpile(fb_view_ddl, symbols=symbols)

        try:
            self.fb_cur.execute(fb_view_ddl)
            self.fb_conn.commit()

            self.pg_cur.execute(pg_view_ddl)
            self.pg_conn.commit()

            self.fb_cur.execute("SELECT ID, VAL_A, VAL_B FROM VW_REG_USING ORDER BY ID;")
            fb_rows = [self._normalize_row(r) for r in self.fb_cur.fetchall()]
            fb_cols = [d[0].lower() for d in self.fb_cur.description]

            self.pg_cur.execute('SELECT "id", "val_a", "val_b" FROM "vw_reg_using" ORDER BY "id";')
            pg_rows = [self._normalize_row(r) for r in self.pg_cur.fetchall()]
            pg_cols = [d[0].lower() for d in self.pg_cur.description]

            self.assertEqual(fb_cols, pg_cols)
            self.assertEqual(fb_rows, pg_rows)
            self.assertEqual(pg_rows, [(1, "a1", None), (2, "a2", "b2"), (3, None, "b3")])
        finally:
            try:
                self.pg_cur.execute('DROP VIEW IF EXISTS "vw_reg_using" CASCADE;')
                self.pg_conn.commit()
            except Exception:
                pass
            try:
                self.fb_cur.execute("DROP VIEW VW_REG_USING;")
                self.fb_conn.commit()
            except Exception:
                pass


if __name__ == "__main__":
    unittest.main()
