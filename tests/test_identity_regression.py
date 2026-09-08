import unittest
from unittest.mock import MagicMock

import psycopg2

from config import get_postgres_connection, PostgresConfig
from engine.data_migrator import DataMigrator
from engine.schema_extractor import SchemaExtractor
from models import Column, Table


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


class TestIdentityUnitRegression(unittest.TestCase):
    """
    Unit tests for IDENTITY DDL generation, sequence synchronization queries,
    and schema extraction error handling.
    """

    def test_identity_ddl_bounds_for_all_integer_types(self):
        # Smallint descending
        t_small = Table('TAB_SMALL')
        t_small.columns.append(
            Column('ID', 'SMALLINT', nullable=False, identity_type='ALWAYS', identity_increment=-2)
        )
        ddl_small = t_small.get_create_table_query()
        self.assertIn('MAXVALUE 32767', ddl_small)
        self.assertNotIn('9223372036854775807', ddl_small)

        # Integer descending
        t_int = Table('TAB_INT')
        t_int.columns.append(
            Column('ID', 'INTEGER', nullable=False, identity_type='ALWAYS', identity_increment=-2)
        )
        ddl_int = t_int.get_create_table_query()
        self.assertIn('MAXVALUE 2147483647', ddl_int)
        self.assertNotIn('9223372036854775807', ddl_int)

        # Bigint descending
        t_big = Table('TAB_BIG')
        t_big.columns.append(
            Column('ID', 'BIGINT', nullable=False, identity_type='BY DEFAULT', identity_increment=-2)
        )
        ddl_big = t_big.get_create_table_query()
        self.assertIn('MAXVALUE 9223372036854775807', ddl_big)

    def test_identity_ddl_custom_positive_increment(self):
        t = Table('TAB_INC10')
        t.columns.append(
            Column('ID', 'INTEGER', nullable=False, identity_type='ALWAYS', identity_increment=10)
        )
        ddl = t.get_create_table_query()
        self.assertIn('GENERATED ALWAYS AS IDENTITY (INCREMENT BY 10)', ddl)

    def test_schema_extractor_raises_when_generator_increment_fails(self):
        mock_fb_con = MagicMock()
        mock_fb_cur = MagicMock()
        mock_fb_con.cursor.return_value = mock_fb_cur

        # Mock table column query returning an identity column with generator GEN_T_ID
        columns_data = [
            (
                'ID',               # 0: column_name
                37,                 # 1: type_code (SMALLINT/INTEGER)
                0,                  # 2: sub_type
                4,                  # 3: length
                0,                  # 4: scale
                0,                  # 5: precision
                0,                  # 6: null_flag
                None,               # 7: default_source
                None,               # 8: domain_name
                None,               # 9: computed_source
                0,                  # 10: collation_id
                0,                  # 11: identity_type (0 = ALWAYS)
                'GEN_T_ID'          # 12: generator_name
            )
        ]
        mock_fb_cur.fetchall.return_value = columns_data

        import firebirdsql
        mock_fb_cur.execute.side_effect = [
            None,  # First query in _extract_columns (fetching columns)
            firebirdsql.OperationalError("Generator lookup failed"),
        ]

        with self.assertRaises(RuntimeError) as ctx:
            SchemaExtractor._extract_columns(mock_fb_cur, 'TEST_TABLE', {'TEST_TABLE'})
        self.assertIn("Failed to read generator increment", str(ctx.exception))

    def test_schema_extractor_raises_when_generator_current_state_fails(self):
        mock_fb_con = MagicMock()
        mock_fb_cur = MagicMock()
        mock_fb_con.cursor.return_value = mock_fb_cur

        columns_data = [
            (
                'ID', 37, 0, 4, 0, 0, 0, None, None, None, 0, 0, 'GEN_T_ID'
            )
        ]
        mock_fb_cur.fetchall.return_value = columns_data

        import firebirdsql
        mock_fb_cur.execute.side_effect = [
            None,  # columns query
            None,  # RDB$GENERATORS query
            firebirdsql.OperationalError("GEN_ID failure"),
        ]
        mock_fb_cur.fetchone.return_value = (1,)  # increment row

        with self.assertRaises(RuntimeError) as ctx:
            SchemaExtractor._extract_columns(mock_fb_cur, 'TEST_TABLE', {'TEST_TABLE'})
        self.assertIn("Failed to read current generator state", str(ctx.exception))

    def test_data_migrator_escapes_apostrophes_in_identity_sync_query(self):
        mock_fb_con = MagicMock()
        mock_pg_con = MagicMock()
        mock_fb_cur = MagicMock()
        mock_pg_cur = MagicMock()

        mock_fb_con.cursor.return_value = mock_fb_cur
        mock_pg_con.cursor.return_value = mock_pg_cur
        migrator = DataMigrator(mock_fb_con, mock_pg_con)

        t = Table("tbl'special")
        t.columns.append(Column("col'id", "INTEGER", nullable=False, identity_type="ALWAYS", identity_increment=1, identity_current=0))

        mock_fb_cur.fetchmany.return_value = []
        success = migrator.import_data([t], max_workers=1)
        self.assertTrue(success)

        executed_queries = [call[0][0] for call in mock_pg_cur.execute.call_args_list]
        sync_queries = [q for q in executed_queries if 'SELECT setval(' in q]
        self.assertEqual(len(sync_queries), 1)

        query = sync_queries[0]
        # Must escape single quote in string literal: "tbl''special"
        self.assertIn("pg_get_serial_sequence('\"tbl''special\"', 'col''id')", query)
        # Must properly double-quote identifier in SQL FROM / MAX clause
        self.assertIn('FROM "tbl\'special"', query)
        self.assertIn('SELECT MAX("col\'id")', query)


@unittest.skipUnless(HAS_REAL_PG, "Live PostgreSQL instance required for live identity regression tests")
class TestIdentityLivePostgresRegression(unittest.TestCase):
    """
    Live execution tests against PostgreSQL validating:
    - Empty table and unused generator (state 0) does not produce out-of-bounds setval.
    - Increment 10 and Increment -2 preservation.
    - SMALLINT, INTEGER, BIGINT type limits and execution.
    - Generator ahead of data does not regress.
    - Explicit IDs beyond generator advance sequence to avoid collisions.
    - Tables and columns with apostrophes execute properly.
    - First and second inserts yield expected values in all cases.
    """

    def setUp(self):
        self.pg_con = get_postgres_connection()
        self.pg_con.autocommit = False
        self.pg_cur = self.pg_con.cursor()

    def tearDown(self):
        try:
            self.pg_con.rollback()
        except psycopg2.Error:
            pass
        try:
            self.pg_con.close()
        except psycopg2.Error:
            pass

    def _run_migrator_sync(self, table: Table, fb_rows=None):
        """Run migrator import_data with mock Firebird. fb_rows fed through mock COPY."""
        mock_fb_con = MagicMock()
        mock_fb_cur = MagicMock()
        mock_fb_con.cursor.return_value = mock_fb_cur
        if fb_rows:
            mock_fb_cur.fetchmany.side_effect = [fb_rows, []]
        else:
            mock_fb_cur.fetchmany.return_value = []

        migrator = DataMigrator(mock_fb_con, self.pg_con)
        success = migrator.import_data([table], max_workers=1)
        self.assertTrue(success)

    def test_live_empty_table_state_zero_inc_1(self):
        t = Table('t_live_zero_inc1')
        t.columns.append(Column('id', 'INTEGER', nullable=False, identity_type='ALWAYS', identity_increment=1, identity_current=0))
        t.columns.append(Column('val', 'TEXT', nullable=True))

        self.pg_cur.execute(f"DROP TABLE IF EXISTS {t.pg_name} CASCADE;")
        self.pg_cur.execute(t.get_create_table_query())

        self._run_migrator_sync(t)

        self.pg_cur.execute(f"INSERT INTO {t.pg_name} (val) VALUES ('a') RETURNING id;")
        first_id = self.pg_cur.fetchone()[0]
        self.assertEqual(first_id, 1)

        self.pg_cur.execute(f"INSERT INTO {t.pg_name} (val) VALUES ('b') RETURNING id;")
        second_id = self.pg_cur.fetchone()[0]
        self.assertEqual(second_id, 2)

    def test_live_empty_table_state_zero_inc_10(self):
        t = Table('t_live_zero_inc10')
        t.columns.append(Column('id', 'INTEGER', nullable=False, identity_type='ALWAYS', identity_increment=10, identity_current=0))
        t.columns.append(Column('val', 'TEXT', nullable=True))

        self.pg_cur.execute(f"DROP TABLE IF EXISTS {t.pg_name} CASCADE;")
        self.pg_cur.execute(t.get_create_table_query())

        self._run_migrator_sync(t)

        self.pg_cur.execute(f"INSERT INTO {t.pg_name} (val) VALUES ('a') RETURNING id;")
        first_id = self.pg_cur.fetchone()[0]
        self.assertEqual(first_id, 10)

        self.pg_cur.execute(f"INSERT INTO {t.pg_name} (val) VALUES ('b') RETURNING id;")
        second_id = self.pg_cur.fetchone()[0]
        self.assertEqual(second_id, 20)

    def test_live_empty_table_descending_inc_neg2_all_integer_types(self):
        cases = [
            ('t_live_desc_small', 'SMALLINT'),
            ('t_live_desc_int', 'INTEGER'),
            ('t_live_desc_big', 'BIGINT'),
        ]

        for tbl_name, col_type in cases:
            with self.subTest(table=tbl_name, type=col_type):
                t = Table(tbl_name)
                t.columns.append(Column('id', col_type, nullable=False, identity_type='ALWAYS', identity_increment=-2, identity_current=0))
                t.columns.append(Column('val', 'TEXT', nullable=True))

                self.pg_cur.execute(f"DROP TABLE IF EXISTS {t.pg_name} CASCADE;")
                self.pg_cur.execute(t.get_create_table_query())

                self._run_migrator_sync(t)

                self.pg_cur.execute(f"INSERT INTO {t.pg_name} (val) VALUES ('first') RETURNING id;")
                first_id = self.pg_cur.fetchone()[0]
                self.assertEqual(first_id, -2)

                self.pg_cur.execute(f"INSERT INTO {t.pg_name} (val) VALUES ('second') RETURNING id;")
                second_id = self.pg_cur.fetchone()[0]
                self.assertEqual(second_id, -4)

    def test_live_generator_ahead_of_data_does_not_regress(self):
        t = Table('t_live_ahead')
        t.columns.append(Column('id', 'INTEGER', nullable=False, identity_type='ALWAYS', identity_increment=1, identity_current=20))
        t.columns.append(Column('val', 'TEXT', nullable=True))

        self.pg_cur.execute(f"DROP TABLE IF EXISTS {t.pg_name} CASCADE;")
        self.pg_cur.execute(t.get_create_table_query())

        # Data max is 5, but generator is at 20 — rows fed through mock Firebird to survive TRUNCATE
        self._run_migrator_sync(t, fb_rows=[(1, 'x'), (2, 'y'), (5, 'z')])

        self.pg_cur.execute(f"INSERT INTO {t.pg_name} (val) VALUES ('new1') RETURNING id;")
        first_id = self.pg_cur.fetchone()[0]
        self.assertEqual(first_id, 21)

        self.pg_cur.execute(f"INSERT INTO {t.pg_name} (val) VALUES ('new2') RETURNING id;")
        second_id = self.pg_cur.fetchone()[0]
        self.assertEqual(second_id, 22)

    def test_live_explicit_ids_beyond_generator_advances_sequence(self):
        t = Table('t_live_explicit_ids')
        t.columns.append(Column('id', 'INTEGER', nullable=False, identity_type='ALWAYS', identity_increment=1, identity_current=10))
        t.columns.append(Column('val', 'TEXT', nullable=True))

        self.pg_cur.execute(f"DROP TABLE IF EXISTS {t.pg_name} CASCADE;")
        self.pg_cur.execute(t.get_create_table_query())

        # Generator was at 10, but table has explicit IDs up to 50 — rows fed through mock Firebird
        self._run_migrator_sync(t, fb_rows=[(1, 'x'), (50, 'y')])

        self.pg_cur.execute(f"INSERT INTO {t.pg_name} (val) VALUES ('new1') RETURNING id;")
        first_id = self.pg_cur.fetchone()[0]
        self.assertEqual(first_id, 51)

        self.pg_cur.execute(f"INSERT INTO {t.pg_name} (val) VALUES ('new2') RETURNING id;")
        second_id = self.pg_cur.fetchone()[0]
        self.assertEqual(second_id, 52)

    def test_live_names_with_apostrophes_execute_and_insert(self):
        from models.database_objects import pg_quote_ident
        tbl_name = "t'special_tbl"
        col_name = "id'col"
        t = Table(tbl_name)
        t.columns.append(Column(col_name, 'INTEGER', nullable=False, identity_type='ALWAYS', identity_increment=1, identity_current=0))
        t.columns.append(Column('val', 'TEXT', nullable=True))

        quoted_tbl = pg_quote_ident(t.pg_name)
        quoted_col = pg_quote_ident(col_name.lower())

        self.pg_cur.execute(f"DROP TABLE IF EXISTS {quoted_tbl} CASCADE;")
        self.pg_cur.execute(t.get_create_table_query())

        self._run_migrator_sync(t)

        self.pg_cur.execute(f"INSERT INTO {quoted_tbl} (val) VALUES ('a') RETURNING {quoted_col};")
        first_id = self.pg_cur.fetchone()[0]
        self.assertEqual(first_id, 1)

        self.pg_cur.execute(f"INSERT INTO {quoted_tbl} (val) VALUES ('b') RETURNING {quoted_col};")
        second_id = self.pg_cur.fetchone()[0]
        self.assertEqual(second_id, 2)


if __name__ == '__main__':
    unittest.main()
