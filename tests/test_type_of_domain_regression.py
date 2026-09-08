import unittest
import psycopg2

from transpiler import FirebirdToPostgresVisitor
from tests.db_isolation import (
    get_test_postgres_connection,
    is_postgres_available,
    requires_postgres,
)




class TestTypeOfDomainRegression(unittest.TestCase):
    """
    Regression test suite for 'TYPE OF domain' base type resolution vs direct domain declarations.
    Acceptance criteria:
    - 'TYPE OF' does not import default, CHECK, or NOT NULL from domain.
    - Precision, scale, and length of the base physical type are preserved.
    - Domain renaming (e.g. relation collisions) does not alter this distinction.
    - Unknown domain raises a contextualized error.
    - Tested for initialization, NULL assignment, and check constraint in procedure and trigger.
    """

    def test_type_of_resolves_base_type_and_discards_domain_constraints(self):
        fb_sql = """
        CREATE PROCEDURE SP_CALC
        AS
        DECLARE VARIABLE V_DIR DOM_POSITIVO;
        DECLARE VARIABLE V_TYPEOF TYPE OF DOM_POSITIVO;
        BEGIN
            V_TYPEOF = 10;
        END;
        """
        domain_map = {"DOM_POSITIVO": "dom_positivo"}
        domain_types = {"DOM_POSITIVO": "INTEGER"}
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql, domain_map=domain_map, domain_types=domain_types)

        self.assertIn("V_DIR dom_positivo;", pg_sql)
        self.assertIn("V_TYPEOF INTEGER;", pg_sql)
        self.assertNotIn("V_TYPEOF dom_positivo;", pg_sql)
        self.assertNotIn("TYPE OF", pg_sql)

    def test_precision_scale_and_length_preserved(self):
        fb_sql = """
        CREATE PROCEDURE SP_TYPES (
            P_TXT TYPE OF DOM_TEXTO,
            P_NUM TYPE OF DOM_DECIMAL,
            P_BIG TYPE OF DOM_BIG
        )
        AS
        DECLARE VARIABLE V_TXT TYPE OF DOM_TEXTO;
        DECLARE VARIABLE V_NUM TYPE OF DOM_DECIMAL;
        DECLARE VARIABLE V_BIG TYPE OF DOM_BIG;
        BEGIN
            V_BIG = 100;
        END;
        """
        domain_map = {
            "DOM_TEXTO": "dom_texto",
            "DOM_DECIMAL": "dom_decimal",
            "DOM_BIG": "dom_big",
        }
        domain_types = {
            "DOM_TEXTO": "VARCHAR(35)",
            "DOM_DECIMAL": "NUMERIC(12, 4)",
            "DOM_BIG": "BIGINT",
        }
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql, domain_map=domain_map, domain_types=domain_types)

        # Header parameters
        self.assertIn("P_TXT VARCHAR(35)", pg_sql)
        self.assertIn("P_NUM NUMERIC(12, 4)", pg_sql)
        self.assertIn("P_BIG BIGINT", pg_sql)

        # Local variables
        self.assertIn("V_TXT VARCHAR(35);", pg_sql)
        self.assertIn("V_NUM NUMERIC(12, 4);", pg_sql)
        self.assertIn("V_BIG BIGINT;", pg_sql)

    def test_domain_renaming_does_not_affect_type_of_resolution(self):
        # Domain CLIENTE collides with table CLIENTE, so domain is renamed to cliente_dom
        fb_sql = """
        CREATE PROCEDURE SP_CLIENTE
        AS
        DECLARE VARIABLE V_DIRECT CLIENTE;
        DECLARE VARIABLE V_BASE TYPE OF CLIENTE;
        BEGIN
            V_BASE = 1;
        END;
        """
        domain_map = {"CLIENTE": "cliente_dom"}
        domain_types = {"CLIENTE": "INTEGER"}
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql, domain_map=domain_map, domain_types=domain_types)

        # Direct declaration uses the renamed domain
        self.assertIn("V_DIRECT cliente_dom;", pg_sql)
        # TYPE OF declaration uses the base type, unaffected by renaming
        self.assertIn("V_BASE INTEGER;", pg_sql)

    def test_unknown_domain_raises_contextualized_error(self):
        fb_sql = """
        CREATE PROCEDURE SP_FAIL
        AS
        DECLARE VARIABLE V TYPE OF DOM_NONEXISTENT;
        BEGIN
            V = 1;
        END;
        """
        with self.assertRaises(ValueError) as ctx:
            FirebirdToPostgresVisitor.transpile(fb_sql, domain_types={"OTHER_DOM": "INTEGER"})

        err_msg = str(ctx.exception)
        self.assertIn("Unknown domain", err_msg)
        self.assertIn("DOM_NONEXISTENT", err_msg)
        self.assertIn("TYPE OF", err_msg)

    def test_trigger_with_direct_domain_and_type_of(self):
        fb_sql = """
        CREATE TRIGGER TRG_TEST FOR PEDIDOS
        BEFORE INSERT
        AS
        DECLARE VARIABLE V_DIR DOM_POSITIVO;
        DECLARE VARIABLE V_TYPEOF TYPE OF DOM_POSITIVO;
        BEGIN
            V_TYPEOF = 1;
        END;
        """
        domain_map = {"DOM_POSITIVO": "dom_positivo"}
        domain_types = {"DOM_POSITIVO": "INTEGER"}
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql, domain_map=domain_map, domain_types=domain_types)

        self.assertIn("V_DIR dom_positivo;", pg_sql)
        self.assertIn("V_TYPEOF INTEGER;", pg_sql)
        self.assertNotIn("TYPE OF", pg_sql)


class TestTypeOfDomainRealPostgresExecution(unittest.TestCase):
    """
    Validates runtime PostgreSQL PL/pgSQL semantics for direct domain vs TYPE OF domain:
    - DEFAULT initialization
    - NULL assignment (NOT NULL violation on direct domain)
    - CHECK constraint violation on direct domain
    - Success of NULL and out-of-bounds on TYPE OF base type
    - Tested for both procedure/function and trigger.
    """

    def setUp(self):
        if is_postgres_available():
            self.pg_con = get_test_postgres_connection()
            self.pg_con.autocommit = False
            self.pg_cur = self.pg_con.cursor()
            # Set up domain and helper table
            self.pg_cur.execute("""
                CREATE DOMAIN dom_positivo AS INTEGER
                    DEFAULT 42
                    NOT NULL
                    CHECK (VALUE > 0);
            """)
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

    @requires_postgres
    def test_real_pg_procedure_initialization_and_constraints(self):
        # 1. Transpile procedure comparing initialization
        fb_sql = """
        CREATE PROCEDURE SP_CHECK_INIT
        AS
        DECLARE VARIABLE V_DIR DOM_POSITIVO;
        DECLARE VARIABLE V_TYPEOF TYPE OF DOM_POSITIVO;
        BEGIN
            -- Return both values
        END;
        """
        domain_map = {"DOM_POSITIVO": "dom_positivo"}
        domain_types = {"DOM_POSITIVO": "INTEGER"}
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql, domain_map=domain_map, domain_types=domain_types)

        # Confirm transpilation mapping
        self.assertIn("V_DIR dom_positivo;", pg_sql)
        self.assertIn("V_TYPEOF INTEGER;", pg_sql)

        # Create table to capture runtime variable values
        self.pg_cur.execute("CREATE TABLE tbl_results (dir_val INT, typeof_val INT);")

        # Verification of uninitialized behavior:
        # v_typeof INTEGER starts as NULL without error (no NOT NULL from domain)
        self.pg_cur.execute("""
            DO $$
            DECLARE
                v_typeof INTEGER;
            BEGIN
                INSERT INTO tbl_results (typeof_val) VALUES (v_typeof);
            END $$;
        """)
        self.pg_cur.execute("SELECT typeof_val FROM tbl_results;")
        self.assertIsNone(self.pg_cur.fetchone()[0], "TYPE OF variable must start as NULL")

        # In contrast, direct domain declaration v_dir dom_positivo fails to initialize
        # because the domain's NOT NULL constraint prevents implicit NULL initialization
        with self.assertRaises(psycopg2.IntegrityError) as cm_init:
            self.pg_cur.execute("""
                DO $$
                DECLARE
                    v_dir dom_positivo;
                BEGIN
                    NULL;
                END $$;
            """)
        self.assertTrue(cm_init.exception.pgcode == '23502' or "null" in str(cm_init.exception).lower())
        self.pg_con.rollback()

        # Recreate domain after rollback
        self.pg_cur.execute("""
            CREATE DOMAIN dom_positivo AS INTEGER
                DEFAULT 42
                NOT NULL
                CHECK (VALUE > 0);
        """)

        # Verify assigning NULL to v_typeof succeeds
        self.pg_cur.execute("""
            DO $$
            DECLARE
                v_typeof INTEGER;
            BEGIN
                v_typeof := NULL;
            END $$;
        """)

        # Verify assigning NULL to direct domain variable raises NOT NULL violation
        with self.assertRaises(psycopg2.IntegrityError) as cm_null:
            self.pg_cur.execute("""
                DO $$
                DECLARE
                    v_dir dom_positivo := 42;
                BEGIN
                    v_dir := NULL;
                END $$;
            """)
        self.assertTrue(cm_null.exception.pgcode == '23502' or "null" in str(cm_null.exception).lower())
        self.pg_con.rollback()

        # Recreate domain after rollback
        self.pg_cur.execute("""
            CREATE DOMAIN dom_positivo AS INTEGER
                DEFAULT 42
                NOT NULL
                CHECK (VALUE > 0);
        """)

        # Verify assigning non-positive value to v_typeof succeeds (no CHECK constraint)
        self.pg_cur.execute("""
            DO $$
            DECLARE
                v_typeof INTEGER;
            BEGIN
                v_typeof := -10;
            END $$;
        """)

        # Verify assigning non-positive value to direct domain variable raises CHECK violation
        with self.assertRaises(psycopg2.IntegrityError) as cm_chk:
            self.pg_cur.execute("""
                DO $$
                DECLARE
                    v_dir dom_positivo := 42;
                BEGIN
                    v_dir := -10;
                END $$;
            """)
        self.assertTrue(cm_chk.exception.pgcode == '23514' or "check" in str(cm_chk.exception).lower())

    @requires_postgres
    def test_real_pg_trigger_initialization_and_constraints(self):
        # Create target table and logging table
        self.pg_cur.execute("CREATE TABLE orders (id INT, total INT);")
        self.pg_cur.execute("CREATE TABLE trg_log (dir_val INT, typeof_val INT);")

        fb_trg_sql = """
        CREATE TRIGGER TRG_ORDERS_BI FOR ORDERS
        BEFORE INSERT
        AS
        DECLARE VARIABLE V_DIR DOM_POSITIVO;
        DECLARE VARIABLE V_TYPEOF TYPE OF DOM_POSITIVO;
        BEGIN
            V_TYPEOF = -5;
        END;
        """
        domain_map = {"DOM_POSITIVO": "dom_positivo"}
        domain_types = {"DOM_POSITIVO": "INTEGER"}
        pg_trg_sql = FirebirdToPostgresVisitor.transpile(fb_trg_sql, domain_map=domain_map, domain_types=domain_types)

        self.assertIn("V_DIR dom_positivo;", pg_trg_sql)
        self.assertIn("V_TYPEOF INTEGER;", pg_trg_sql)

        # 1. Trigger with TYPE OF (INTEGER) succeeds with uninitialized NULL and negative values
        self.pg_cur.execute("""
            CREATE OR REPLACE FUNCTION trg_orders_typeof_func()
            RETURNS trigger AS $$
            DECLARE
                v_typeof INTEGER;
            BEGIN
                INSERT INTO trg_log (typeof_val) VALUES (v_typeof);
                v_typeof := -5; -- Allowed for INTEGER (outside domain check)
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER trg_orders_bi
            BEFORE INSERT ON orders
            FOR EACH ROW EXECUTE FUNCTION trg_orders_typeof_func();
        """)
        self.pg_cur.execute("INSERT INTO orders VALUES (1, 100);")
        self.pg_cur.execute("SELECT typeof_val FROM trg_log;")
        self.assertIsNone(self.pg_cur.fetchone()[0])

        # 2. Trigger with direct domain declaration fails implicit initialization due to NOT NULL
        self.pg_cur.execute("""
            CREATE OR REPLACE FUNCTION trg_orders_dir_func()
            RETURNS trigger AS $$
            DECLARE
                v_dir dom_positivo;
            BEGIN
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            DROP TRIGGER trg_orders_bi ON orders;
            CREATE TRIGGER trg_orders_bi
            BEFORE INSERT ON orders
            FOR EACH ROW EXECUTE FUNCTION trg_orders_dir_func();
        """)
        with self.assertRaises(psycopg2.IntegrityError) as cm_trg_init:
            self.pg_cur.execute("INSERT INTO orders VALUES (2, 200);")
        self.assertTrue(cm_trg_init.exception.pgcode == '23502' or "null" in str(cm_trg_init.exception).lower())
        self.pg_con.rollback()

        # Recreate domain and table after rollback
        self.pg_cur.execute("""
            CREATE DOMAIN dom_positivo AS INTEGER
                DEFAULT 42
                NOT NULL
                CHECK (VALUE > 0);
            CREATE TABLE orders (id INT, total INT);
        """)

        # 3. Trigger assigning non-positive value to direct domain variable raises check_violation
        self.pg_cur.execute("""
            CREATE OR REPLACE FUNCTION trg_orders_bad_check()
            RETURNS trigger AS $$
            DECLARE
                v_dir dom_positivo := 42;
            BEGIN
                v_dir := -100;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER trg_orders_bi
            BEFORE INSERT ON orders
            FOR EACH ROW EXECUTE FUNCTION trg_orders_bad_check();
        """)
        with self.assertRaises(psycopg2.IntegrityError) as cm_trg_chk:
            self.pg_cur.execute("INSERT INTO orders VALUES (3, 300);")
        self.assertTrue(cm_trg_chk.exception.pgcode == '23514' or "check" in str(cm_trg_chk.exception).lower())
