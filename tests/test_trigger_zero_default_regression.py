import unittest
from unittest.mock import MagicMock
import psycopg2
import firebirdsql

from tests.db_isolation import (
    get_test_firebird_connection,
    get_test_postgres_connection,
    require_live_databases,
    requires_live_databases_class,
)
from engine.schema_extractor import SchemaExtractor
from models import Column, Table
from transpiler import FirebirdToPostgresVisitor
from utils import split_sql_statements


class TestTriggerZeroDefaultUnitRegression(unittest.TestCase):
    """
    Unit tests ensuring isolated NEW.ID = 0 (and similar zero-only conditions)
    are NOT treated as equivalent to column defaults, while genuine absent conditions
    (with IS NULL or COALESCE) continue to be promoted.
    """

    def test_isolated_zero_conditions_not_promoted(self):
        # Conditions without null coverage must NOT be considered equivalent absent conditions
        self.assertFalse(SchemaExtractor._is_equivalent_absent_condition("NEW.ID = 0", "ID"))
        self.assertFalse(SchemaExtractor._is_equivalent_absent_condition("NEW.ID <= 0", "ID"))
        self.assertFalse(SchemaExtractor._is_equivalent_absent_condition("NEW.ID < 1", "ID"))
        self.assertFalse(SchemaExtractor._is_equivalent_absent_condition("NEW.ID = 0 OR NEW.ID <= 0", "ID"))

        table = Table("T_ZERO")
        col_id = Column("ID", "INTEGER", nullable=True)
        col_id_le = Column("ID_LE", "INTEGER", nullable=True)
        col_id_lt = Column("ID_LT", "INTEGER", nullable=True)
        table.columns.extend([col_id, col_id_le, col_id_lt])

        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            ("T_ZERO", "AS BEGIN IF (NEW.ID = 0) THEN NEW.ID = GEN_ID(G_ZERO, 1); END;", 1),
            ("T_ZERO", "AS BEGIN IF (NEW.ID_LE <= 0) THEN NEW.ID_LE = GEN_ID(G_LE, 1); END;", 1),
            ("T_ZERO", "AS BEGIN IF (NEW.ID_LT < 1) THEN NEW.ID_LT = GEN_ID(G_LT, 1); END;", 1),
        ]

        SchemaExtractor._bind_sequence_generators(mock_cursor, [table])

        self.assertIsNone(col_id.sequence_name)
        self.assertIsNone(col_id_le.sequence_name)
        self.assertIsNone(col_id_lt.sequence_name)

    def test_null_covered_conditions_still_promoted(self):
        self.assertTrue(SchemaExtractor._is_equivalent_absent_condition("NEW.ID IS NULL", "ID"))
        self.assertTrue(SchemaExtractor._is_equivalent_absent_condition("NEW.ID IS NULL OR NEW.ID = 0", "ID"))
        self.assertTrue(SchemaExtractor._is_equivalent_absent_condition("NEW.ID IS NULL OR NEW.ID <= 0", "ID"))
        self.assertTrue(SchemaExtractor._is_equivalent_absent_condition("COALESCE(NEW.ID, 0) <= 0", "ID"))
        self.assertTrue(SchemaExtractor._is_equivalent_absent_condition("COALESCE(NEW.ID, 0) = 0", "ID"))
        self.assertTrue(SchemaExtractor._is_equivalent_absent_condition("COALESCE(NEW.ID, 0) < 1", "ID"))

        table = Table("T_NULL")
        col_null = Column("ID_NULL", "INTEGER", nullable=True)
        col_null_zero = Column("ID_NZ", "INTEGER", nullable=True)
        col_coalesce = Column("ID_COAL", "INTEGER", nullable=True)
        table.columns.extend([col_null, col_null_zero, col_coalesce])

        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            ("T_NULL", "AS BEGIN IF (NEW.ID_NULL IS NULL) THEN NEW.ID_NULL = GEN_ID(G_NULL, 1); END;", 1),
            ("T_NULL", "AS BEGIN IF (NEW.ID_NZ IS NULL OR NEW.ID_NZ = 0) THEN NEW.ID_NZ = NEXT VALUE FOR G_NZ; END;", 1),
            ("T_NULL", "AS BEGIN IF (COALESCE(NEW.ID_COAL, 0) <= 0) THEN NEW.ID_COAL = GEN_ID(G_COAL, 1); END;", 1),
        ]

        SchemaExtractor._bind_sequence_generators(mock_cursor, [table])

        self.assertEqual(col_null.sequence_name, "g_null")
        self.assertEqual(col_null_zero.sequence_name, "g_nz")
        self.assertEqual(col_coalesce.sequence_name, "g_coal")


@requires_live_databases_class
class TestTriggerZeroDefaultLiveComparisonRegression(unittest.TestCase):
    """
    Live regression comparing Firebird and PostgreSQL behavior for the trigger:
        IF (NEW.ID = 0) THEN NEW.ID = GEN_ID(GEN_T_ID, 1);
    Verifying that omitted ID, NULL, zero, and positive inputs behave identically:
    - Omitted: ID is NULL, generator does NOT advance.
    - NULL: ID is NULL, generator does NOT advance.
    - Zero: ID is assigned generator value, generator advances by 1.
    - Positive: ID retains positive value, generator does NOT advance.
    """

    def setUp(self):
        # Gated by @requires_live_databases: disposable test databases only.
        require_live_databases(self)
        self.fb_conn = get_test_firebird_connection()
        self.fb_cur = self.fb_conn.cursor()
        self.pg_conn = get_test_postgres_connection()
        self.pg_conn.autocommit = True
        self.pg_cur = self.pg_conn.cursor()
        self._cleanup()

    def _cleanup(self):
        try:
            self.fb_cur.execute("DROP TRIGGER TR_ZERO_REG;")
            self.fb_conn.commit()
        except Exception:
            pass
        try:
            self.fb_cur.execute("DROP TABLE T_ZERO_REG;")
            self.fb_conn.commit()
        except Exception:
            pass
        try:
            self.fb_cur.execute("DROP SEQUENCE GEN_ZERO_REG;")
            self.fb_conn.commit()
        except Exception:
            pass

        try:
            self.pg_cur.execute("DROP TABLE IF EXISTS t_zero_reg CASCADE;")
        except Exception:
            pass
        try:
            self.pg_cur.execute("DROP SEQUENCE IF EXISTS gen_zero_reg CASCADE;")
        except Exception:
            pass

    def tearDown(self):
        self._cleanup()
        self.fb_cur.close()
        self.fb_conn.close()
        self.pg_cur.close()
        self.pg_conn.close()

    def test_same_trigger_omitted_null_zero_positive_comparison(self):
        # 1. Setup Firebird objects
        self.fb_cur.execute("CREATE SEQUENCE GEN_ZERO_REG;")
        self.fb_conn.commit()
        self.fb_cur.execute("CREATE TABLE T_ZERO_REG (ID INT, VAL VARCHAR(20));")
        self.fb_conn.commit()
        self.fb_cur.execute("""
        CREATE TRIGGER TR_ZERO_REG FOR T_ZERO_REG BEFORE INSERT AS
        BEGIN
            IF (NEW.ID = 0) THEN
                NEW.ID = GEN_ID(GEN_ZERO_REG, 1);
        END
        """)
        self.fb_conn.commit()

        # 2. Extract schema and verify column.sequence_name is None (NOT promoted)
        extractor = SchemaExtractor(self.fb_conn)
        tables = extractor.extract_schema()
        table = next(t for t in tables if t.name == "T_ZERO_REG")
        col_id = next(c for c in table.columns if c.name == "ID")
        self.assertIsNone(col_id.sequence_name, "NEW.ID = 0 must not be promoted to a column default")

        # 3. Setup PostgreSQL objects: table DDL without default + transpiled trigger
        pg_ddl = table.get_create_table_query()
        self.assertNotIn("DEFAULT nextval", pg_ddl)
        self.pg_cur.execute("CREATE SEQUENCE gen_zero_reg START WITH 1;")
        self.pg_cur.execute(pg_ddl)

        fb_trg_sql = """
        CREATE TRIGGER TR_ZERO_REG FOR T_ZERO_REG BEFORE INSERT AS
        BEGIN
            IF (NEW.ID = 0) THEN
                NEW.ID = GEN_ID(GEN_ZERO_REG, 1);
        END
        """
        pg_trg_sql = FirebirdToPostgresVisitor.transpile(fb_trg_sql)
        for stmt, _ in split_sql_statements(pg_trg_sql):
            if stmt.strip():
                self.pg_cur.execute(stmt)

        def get_fb_gen():
            self.fb_cur.execute("SELECT GEN_ID(GEN_ZERO_REG, 0) FROM RDB$DATABASE;")
            return self.fb_cur.fetchone()[0]

        def get_pg_gen():
            self.pg_cur.execute("SELECT last_value, is_called FROM gen_zero_reg;")
            val, called = self.pg_cur.fetchone()
            return val if called else 0

        # Initial generator state: 0 in both
        self.assertEqual(get_fb_gen(), 0)
        self.assertEqual(get_pg_gen(), 0)

        # Case 1: ID OMITTED
        self.fb_cur.execute("INSERT INTO T_ZERO_REG (VAL) VALUES ('omitted');")
        self.fb_conn.commit()
        self.fb_cur.execute("SELECT ID FROM T_ZERO_REG WHERE VAL = 'omitted';")
        fb_id_omitted = self.fb_cur.fetchone()[0]
        fb_gen_omitted = get_fb_gen()

        self.pg_cur.execute("INSERT INTO t_zero_reg (val) VALUES ('omitted');")
        self.pg_cur.execute("SELECT id FROM t_zero_reg WHERE val = 'omitted';")
        pg_id_omitted = self.pg_cur.fetchone()[0]
        pg_gen_omitted = get_pg_gen()

        self.assertIsNone(fb_id_omitted)
        self.assertIsNone(pg_id_omitted)
        self.assertEqual(fb_gen_omitted, 0)
        self.assertEqual(pg_gen_omitted, 0)

        # Case 2: ID EXPLICIT NULL
        self.fb_cur.execute("INSERT INTO T_ZERO_REG (ID, VAL) VALUES (NULL, 'null');")
        self.fb_conn.commit()
        self.fb_cur.execute("SELECT ID FROM T_ZERO_REG WHERE VAL = 'null';")
        fb_id_null = self.fb_cur.fetchone()[0]
        fb_gen_null = get_fb_gen()

        self.pg_cur.execute("INSERT INTO t_zero_reg (id, val) VALUES (NULL, 'null');")
        self.pg_cur.execute("SELECT id FROM t_zero_reg WHERE val = 'null';")
        pg_id_null = self.pg_cur.fetchone()[0]
        pg_gen_null = get_pg_gen()

        self.assertIsNone(fb_id_null)
        self.assertIsNone(pg_id_null)
        self.assertEqual(fb_gen_null, 0)
        self.assertEqual(pg_gen_null, 0)

        # Case 3: ID EXPLICIT 0 (MUST TRIGGER GENERATOR)
        self.fb_cur.execute("INSERT INTO T_ZERO_REG (ID, VAL) VALUES (0, 'zero');")
        self.fb_conn.commit()
        self.fb_cur.execute("SELECT ID FROM T_ZERO_REG WHERE VAL = 'zero';")
        fb_id_zero = self.fb_cur.fetchone()[0]
        fb_gen_zero = get_fb_gen()

        self.pg_cur.execute("INSERT INTO t_zero_reg (id, val) VALUES (0, 'zero');")
        self.pg_cur.execute("SELECT id FROM t_zero_reg WHERE val = 'zero';")
        pg_id_zero = self.pg_cur.fetchone()[0]
        pg_gen_zero = get_pg_gen()

        self.assertEqual(fb_id_zero, 1)
        self.assertEqual(pg_id_zero, 1)
        self.assertEqual(fb_gen_zero, 1)
        self.assertEqual(pg_gen_zero, 1)

        # Case 4: ID EXPLICIT POSITIVE (42)
        self.fb_cur.execute("INSERT INTO T_ZERO_REG (ID, VAL) VALUES (42, 'pos');")
        self.fb_conn.commit()
        self.fb_cur.execute("SELECT ID FROM T_ZERO_REG WHERE VAL = 'pos';")
        fb_id_pos = self.fb_cur.fetchone()[0]
        fb_gen_pos = get_fb_gen()

        self.pg_cur.execute("INSERT INTO t_zero_reg (id, val) VALUES (42, 'pos');")
        self.pg_cur.execute("SELECT id FROM t_zero_reg WHERE val = 'pos';")
        pg_id_pos = self.pg_cur.fetchone()[0]
        pg_gen_pos = get_pg_gen()

        self.assertEqual(fb_id_pos, 42)
        self.assertEqual(pg_id_pos, 42)
        self.assertEqual(fb_gen_pos, 1)
        self.assertEqual(pg_gen_pos, 1)


if __name__ == "__main__":
    unittest.main()
