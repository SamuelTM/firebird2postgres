import unittest
import psycopg2
import firebirdsql

from config import (
    get_postgres_connection,
    get_firebird_connection,
    PostgresConfig,
    FirebirdConfig,
)
from engine.schema_extractor import SchemaExtractor
from models import Column, Table
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


class TestComputedColumnEscapedQuotesUnitRegression(unittest.TestCase):
    """
    Unit tests ensuring computed columns with escaped double quotes in names
    and references (e.g. "A""B") are recognized as dependencies and expanded.
    """

    def test_single_computed_column_dependency_with_escaped_quotes(self):
        col_id = Column("ID", "INTEGER", nullable=False)
        col_ab = Column('A"B', "INTEGER", nullable=True, computed_source="id + 1")
        col_c = Column("C", "INTEGER", nullable=True, computed_source='"A""B" + 1')

        cols = [col_id, col_ab, col_c]
        SchemaExtractor._expand_computed_column_dependencies(cols, "T")

        self.assertEqual(col_ab.computed_source, "id + 1")
        self.assertEqual(col_c.computed_source, "((id + 1)::integer) + 1")

    def test_lowercase_and_table_qualified_escaped_quote_references(self):
        col_id = Column("ID", "INTEGER", nullable=False)
        col_ab = Column('A"B', "INTEGER", nullable=True, computed_source="id + 1")
        col_c = Column("C", "INTEGER", nullable=True, computed_source='"a""b" + 1')
        col_d = Column("D", "INTEGER", nullable=True, computed_source='"T"."A""B" + 2')

        cols = [col_id, col_ab, col_c, col_d]
        SchemaExtractor._expand_computed_column_dependencies(cols, "T")

        self.assertEqual(col_c.computed_source, "((id + 1)::integer) + 1")
        self.assertEqual(col_d.computed_source, "((id + 1)::integer) + 2")

    def test_chain_of_computed_columns_with_escaped_quotes(self):
        col_id = Column("ID", "INTEGER", nullable=False)
        col_ab = Column('A"B', "INTEGER", nullable=True, computed_source="id + 1")
        col_c = Column("C", "INTEGER", nullable=True, computed_source='"A""B" + 1')
        col_de = Column('D"E', "INTEGER", nullable=True, computed_source='c * 2 + "a""b"')

        cols = [col_id, col_ab, col_c, col_de]
        SchemaExtractor._expand_computed_column_dependencies(cols, "T")

        self.assertEqual(col_ab.computed_source, "id + 1")
        self.assertEqual(col_c.computed_source, "((id + 1)::integer) + 1")
        self.assertEqual(
            col_de.computed_source,
            '((((id + 1)::integer) + 1)::integer) * 2 + ((id + 1)::integer)'
        )

        table = Table("T")
        table.columns = cols
        ddl = table.get_create_table_query()
        self.assertIn('"a""b" INTEGER GENERATED ALWAYS AS (id + 1) STORED', ddl)
        self.assertIn('"c" INTEGER GENERATED ALWAYS AS (((id + 1)::integer) + 1) STORED', ddl)
        self.assertIn('"d""e" INTEGER GENERATED ALWAYS AS (((((id + 1)::integer) + 1)::integer) * 2 + ((id + 1)::integer)) STORED', ddl)

    def test_string_literal_containing_escaped_quote_not_treated_as_col(self):
        col_id = Column("ID", "INTEGER", nullable=False)
        col_ab = Column('A"B', "INTEGER", nullable=True, computed_source="id + 1")
        col_c = Column("C", "VARCHAR(50)", nullable=True, computed_source="id || '\"A\"\"B\"'")

        cols = [col_id, col_ab, col_c]
        SchemaExtractor._expand_computed_column_dependencies(cols, "T")

        # String literal should remain intact and not replaced
        self.assertEqual(col_c.computed_source, "id || '\"A\"\"B\"'")


@unittest.skipUnless(HAS_REAL_PG, "PostgreSQL not available")
class TestComputedColumnEscapedQuotesLivePostgres(unittest.TestCase):
    """
    Live PostgreSQL regression verifying that table DDL with chain of computed columns
    containing escaped double quotes is created successfully and evaluates accurately.
    """

    def setUp(self):
        self.conn = get_postgres_connection(PostgresConfig())
        self.conn.autocommit = True
        self.cur = self.conn.cursor()
        self.cur.execute("DROP TABLE IF EXISTS t_comp_pg_test CASCADE;")

    def tearDown(self):
        try:
            self.cur.execute("DROP TABLE IF EXISTS t_comp_pg_test CASCADE;")
        finally:
            self.cur.close()
            self.conn.close()

    def test_live_pg_computed_column_chain_ddl_and_execution(self):
        col_id = Column("ID", "INTEGER", nullable=False)
        col_ab = Column('A"B', "INTEGER", nullable=True, computed_source="id + 1")
        col_c = Column("C", "INTEGER", nullable=True, computed_source='"A""B" + 1')
        col_de = Column('D"E', "INTEGER", nullable=True, computed_source='c * 2 + "a""b"')

        cols = [col_id, col_ab, col_c, col_de]
        SchemaExtractor._expand_computed_column_dependencies(cols, "T_COMP_PG_TEST")

        table = Table("T_COMP_PG_TEST")
        table.columns = cols
        ddl = table.get_create_table_query()

        self.cur.execute(ddl)
        self.cur.execute('INSERT INTO "t_comp_pg_test" ("id") VALUES (5);')
        self.cur.execute('SELECT "id", "a""b", "c", "d""e" FROM "t_comp_pg_test";')
        row = self.cur.fetchone()

        self.assertIsNotNone(row)
        # ID=5, A"B=6, C=7, D"E=7*2 + 6 = 20
        self.assertEqual(row, (5, 6, 7, 20))


@unittest.skipUnless(HAS_REAL_FB and HAS_REAL_PG, "Both Firebird and PostgreSQL required")
class TestComputedColumnEscapedQuotesE2EComparison(unittest.TestCase):
    """
    End-to-end regression: create table in Firebird with chain of computed columns
    using escaped double quotes, extract schema, generate PostgreSQL DDL,
    and compare rows inserted in both databases.
    """

    def setUp(self):
        self.fb_conn = get_firebird_connection(FirebirdConfig())
        self.fb_cur = self.fb_conn.cursor()
        self.pg_conn = get_postgres_connection(PostgresConfig())
        self.pg_conn.autocommit = True
        self.pg_cur = self.pg_conn.cursor()
        self._cleanup()

    def _cleanup(self):
        try:
            self.fb_cur.execute("DROP TABLE T_COMP_E2E_REG;")
            self.fb_conn.commit()
        except Exception:
            pass
        try:
            self.pg_cur.execute("DROP TABLE IF EXISTS t_comp_e2e_reg CASCADE;")
        except Exception:
            pass

    def tearDown(self):
        self._cleanup()
        self.fb_cur.close()
        self.fb_conn.close()
        self.pg_cur.close()
        self.pg_conn.close()

    def test_e2e_schema_extraction_and_row_comparison(self):
        self.fb_cur.execute("""
        CREATE TABLE T_COMP_E2E_REG (
            ID INTEGER NOT NULL,
            "A\"\"B" COMPUTED BY (ID + 1),
            C COMPUTED BY ("A\"\"B" + 1),
            "D\"\"E" COMPUTED BY (C * 2 + "A\"\"B")
        );
        """)
        self.fb_conn.commit()

        self.fb_cur.execute("INSERT INTO T_COMP_E2E_REG (ID) VALUES (15);")
        self.fb_conn.commit()

        extractor = SchemaExtractor(self.fb_conn)
        tables = extractor.extract_schema()
        table = next(t for t in tables if t.name == "T_COMP_E2E_REG")
        pg_ddl = table.get_create_table_query()

        self.pg_cur.execute(pg_ddl)
        self.pg_cur.execute('INSERT INTO "t_comp_e2e_reg" ("id") VALUES (15);')

        self.fb_cur.execute('SELECT ID, "A""B", C, "D""E" FROM T_COMP_E2E_REG;')
        fb_row = self.fb_cur.fetchone()

        self.pg_cur.execute('SELECT "id", "a""b", "c", "d""e" FROM "t_comp_e2e_reg";')
        pg_row = self.pg_cur.fetchone()

        # ID=15, A"B=16, C=17, D"E=17*2 + 16 = 50
        self.assertEqual(fb_row, (15, 16, 17, 50))
        self.assertEqual(pg_row, (15, 16, 17, 50))
        self.assertEqual(fb_row, pg_row)


if __name__ == "__main__":
    unittest.main()
