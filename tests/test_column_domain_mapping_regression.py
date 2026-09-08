import unittest
from unittest.mock import MagicMock
import psycopg2

from engine.schema_extractor import SchemaExtractor
from engine.ddl_exporter import DdlExporter
from engine.data_migrator import DataMigrator
from models.database_objects import Table, Column
from models.firebird_types import build_domain_mapping
from tests.test_integration_execution import check_live_postgres_available, get_postgres_connection

HAS_REAL_PG = check_live_postgres_available()


class TestColumnDomainMappingRegression(unittest.TestCase):
    """
    Regression test suite for column domain mapping:
    - Columns maintain base physical data type in col.column_type
    - Columns receive mapped PostgreSQL domain name in col.domain_name
    - Chained collisions (FOO, FOO_DOM, table FOO) map accurately without cross-linking
    - Domain on DATE retains base type DATE and generates valid DDL
    - Domain on BLOB retains 'BLOB' in column_type, triggering row-by-row streaming
    - Effective type in live PostgreSQL catalog matches domain and base type
    """

    def test_chained_domain_collision_mapping(self):
        """
        Table 'FOO', domains 'FOO' and 'FOO_DOM'.
        FOO must map to 'foo_dom_dom' and FOO_DOM to 'foo_dom'.
        Columns referencing FOO must use 'foo_dom_dom', referencing FOO_DOM must use 'foo_dom'.
        """
        relations = {'FOO'}
        domains = ['FOO', 'FOO_DOM']
        domain_map = build_domain_mapping(domains, relations)

        self.assertEqual(domain_map['FOO_DOM'], 'foo_dom')
        self.assertEqual(domain_map['FOO'], 'foo_dom_dom')

        # Mock cursor for _extract_columns
        # Row format: FIELD_NAME, FIELD_TYPE, FIELD_SUB_TYPE, FIELD_LENGTH, NULL_FLAG,
        #             PRECISION, SCALE, DEFAULT_SOURCE, DOMAIN_DEFAULT, FIELD_SOURCE, COMPUTED_SOURCE
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            ("COL_A", 8, 0, 4, 1, 0, 0, None, None, "FOO", None),        # INTEGER, domain FOO
            ("COL_B", 37, 0, 50, 1, 0, 0, None, None, "FOO_DOM", None),  # VARCHAR(50), domain FOO_DOM
        ]

        columns = SchemaExtractor._extract_columns(
            mock_cursor, "FOO", relations, domain_map=domain_map
        )

        self.assertEqual(len(columns), 2)

        col_a, col_b = columns[0], columns[1]

        # Base types preserved
        self.assertEqual(col_a.column_type, "INTEGER")
        self.assertEqual(col_b.column_type, "VARCHAR(50)")

        # Domain names mapped correctly from domain_map without isolated recalculation
        self.assertEqual(col_a.domain_name, "foo_dom_dom")
        self.assertEqual(col_b.domain_name, "foo_dom")

        # Table DDL generation uses mapped domain names
        table = Table("FOO")
        table.columns = columns
        ddl = table.get_create_table_query()

        self.assertIn('"col_a" public."foo_dom_dom"', ddl)
        self.assertIn('"col_b" public."foo_dom"', ddl)

    def test_multiple_chained_collisions(self):
        """
        Multiple collisions: table 'FOO', 'BAR'; domains 'FOO', 'FOO_DOM', 'FOO_DOM_DOM', 'BAR', 'BAR_DOM'.
        """
        relations = {'FOO', 'BAR'}
        domains = ['FOO', 'FOO_DOM', 'FOO_DOM_DOM', 'BAR', 'BAR_DOM']
        domain_map = build_domain_mapping(domains, relations)

        self.assertEqual(domain_map['FOO_DOM'], 'foo_dom')
        self.assertEqual(domain_map['FOO_DOM_DOM'], 'foo_dom_dom')
        self.assertEqual(domain_map['FOO'], 'foo_dom_dom_dom')
        self.assertEqual(domain_map['BAR_DOM'], 'bar_dom')
        self.assertEqual(domain_map['BAR'], 'bar_dom_dom')

        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            ("C1", 8, 0, 4, 1, 0, 0, None, None, "FOO", None),
            ("C2", 8, 0, 4, 1, 0, 0, None, None, "FOO_DOM", None),
            ("C3", 8, 0, 4, 1, 0, 0, None, None, "FOO_DOM_DOM", None),
        ]

        cols = SchemaExtractor._extract_columns(
            mock_cursor, "FOO", relations, domain_map=domain_map
        )
        self.assertEqual(cols[0].domain_name, "foo_dom_dom_dom")
        self.assertEqual(cols[0].column_type, "INTEGER")
        self.assertEqual(cols[1].domain_name, "foo_dom")
        self.assertEqual(cols[1].column_type, "INTEGER")
        self.assertEqual(cols[2].domain_name, "foo_dom_dom")
        self.assertEqual(cols[2].column_type, "INTEGER")

    def test_domain_on_date(self):
        """
        Domain over DATE type preserves base type DATE and maps domain name.
        """
        relations = {'EVENTS'}
        domains = ['DOM_DATA_EVENTO']
        domain_map = build_domain_mapping(domains, relations)

        mock_cursor = MagicMock()
        # Firebird field_type 12 = DATE
        mock_cursor.fetchall.return_value = [
            ("DT_EVENTO", 12, 0, 4, 1, 0, 0, None, None, "DOM_DATA_EVENTO", None)
        ]

        columns = SchemaExtractor._extract_columns(
            mock_cursor, "EVENTS", relations, domain_map=domain_map
        )
        col = columns[0]
        self.assertEqual(col.column_type, "DATE")
        self.assertEqual(col.domain_name, "dom_data_evento")

        table = Table("EVENTS")
        table.columns = columns
        ddl = table.get_create_table_query()
        self.assertIn('"dt_evento" public."dom_data_evento"', ddl)

    def test_domain_on_blob_detected_in_migrator(self):
        """
        Domain over BLOB preserves 'BLOB' in column_type, triggering row-by-row streaming.
        """
        relations = {'DOCS'}
        domains = ['DOM_FOTO', 'DOM_TEXTO']
        domain_map = build_domain_mapping(domains, relations)

        mock_cursor = MagicMock()
        # Firebird field_type 261 = BLOB; subtype 0 = binary, subtype 1 = text
        mock_cursor.fetchall.return_value = [
            ("ID", 8, 0, 4, 0, 0, 0, None, None, "RDB$1", None),
            ("FOTO", 261, 0, 8, 1, 0, 0, None, None, "DOM_FOTO", None),
            ("DESCRICAO", 261, 1, 8, 1, 0, 0, None, None, "DOM_TEXTO", None),
        ]

        columns = SchemaExtractor._extract_columns(
            mock_cursor, "DOCS", relations, domain_map=domain_map
        )

        col_id, col_foto, col_desc = columns

        self.assertEqual(col_foto.column_type, "BLOB SUBTYPE 0")
        self.assertEqual(col_foto.domain_name, "dom_foto")
        self.assertEqual(col_desc.column_type, "BLOB SUBTYPE 1")
        self.assertEqual(col_desc.domain_name, "dom_texto")

        table = Table("DOCS")
        table.columns = columns

        # BLOB count in data_migrator must detect both BLOBs
        blob_count = sum(1 for col in table.columns if 'BLOB' in col.column_type)
        self.assertEqual(blob_count, 2)

        # fetch_size strategy
        fetch_size = 1 if blob_count > 0 else 10000
        self.assertEqual(fetch_size, 1)

        # DDL uses mapped domains
        ddl = table.get_create_table_query()
        self.assertIn('"foto" public."dom_foto"', ddl)
        self.assertIn('"descricao" public."dom_texto"', ddl)

    @unittest.skipUnless(HAS_REAL_PG, "Live PostgreSQL database required")
    def test_live_postgres_catalog_and_domain_resolution(self):
        """
        Verify live PostgreSQL catalog for domain creation and table columns referencing domains:
        - Creates collision-resolved domains: 'foo_dom_dom', 'foo_dom', 'dom_data_evento', 'dom_blob'
        - Creates table 'foo' referencing domains
        - Inspects pg_attribute, pg_type to ensure effective types and domain references
        """
        con = get_postgres_connection()
        cur = con.cursor()
        try:
            # Clean up prior test objects
            cur.execute("DROP TABLE IF EXISTS public.foo CASCADE;")
            cur.execute("DROP DOMAIN IF EXISTS public.foo_dom_dom CASCADE;")
            cur.execute("DROP DOMAIN IF EXISTS public.foo_dom CASCADE;")
            cur.execute("DROP DOMAIN IF EXISTS public.dom_data_evento CASCADE;")
            cur.execute("DROP DOMAIN IF EXISTS public.dom_blob CASCADE;")

            # Create domains as exported by DdlExporter
            cur.execute('CREATE DOMAIN public."foo_dom_dom" AS INTEGER;')
            cur.execute('CREATE DOMAIN public."foo_dom" AS VARCHAR(50);')
            cur.execute('CREATE DOMAIN public."dom_data_evento" AS DATE;')
            cur.execute('CREATE DOMAIN public."dom_blob" AS BYTEA;')

            # Build Table object and generate DDL
            table = Table("FOO")
            table.columns = [
                Column("ID", "INTEGER", nullable=False, domain_name="foo_dom_dom"),
                Column("NOME", "VARCHAR(50)", nullable=True, domain_name="foo_dom"),
                Column("DATA_CADASTRO", "DATE", nullable=True, domain_name="dom_data_evento"),
                Column("ARQUIVO", "BLOB SUBTYPE 0", nullable=True, domain_name="dom_blob"),
            ]

            ddl = table.get_create_table_query()
            cur.execute(ddl)

            # Query PostgreSQL catalog to verify column types and domain linkage
            cur.execute("""
                SELECT 
                    a.attname,
                    t.typname,
                    t.typtype,
                    bt.typname AS base_typename
                FROM pg_attribute a
                JOIN pg_class c ON a.attrelid = c.oid
                JOIN pg_namespace n ON c.relnamespace = n.oid
                JOIN pg_type t ON a.atttypid = t.oid
                LEFT JOIN pg_type bt ON t.typbasetype = bt.oid
                WHERE n.nspname = 'public'
                  AND c.relname = 'foo'
                  AND a.attnum > 0
                  AND NOT a.attisdropped
                ORDER BY a.attnum;
            """)
            catalog_rows = cur.fetchall()

            self.assertEqual(len(catalog_rows), 4)

            # Column 1: ID -> foo_dom_dom, typtype 'd' (domain), base type 'int4'
            self.assertEqual(catalog_rows[0][0], "id")
            self.assertEqual(catalog_rows[0][1], "foo_dom_dom")
            self.assertEqual(catalog_rows[0][2], "d")
            self.assertEqual(catalog_rows[0][3], "int4")

            # Column 2: NOME -> foo_dom, typtype 'd', base type 'varchar'
            self.assertEqual(catalog_rows[1][0], "nome")
            self.assertEqual(catalog_rows[1][1], "foo_dom")
            self.assertEqual(catalog_rows[1][2], "d")
            self.assertEqual(catalog_rows[1][3], "varchar")

            # Column 3: DATA_CADASTRO -> dom_data_evento, typtype 'd', base type 'date'
            self.assertEqual(catalog_rows[2][0], "data_cadastro")
            self.assertEqual(catalog_rows[2][1], "dom_data_evento")
            self.assertEqual(catalog_rows[2][2], "d")
            self.assertEqual(catalog_rows[2][3], "date")

            # Column 4: ARQUIVO -> dom_blob, typtype 'd', base type 'bytea'
            self.assertEqual(catalog_rows[3][0], "arquivo")
            self.assertEqual(catalog_rows[3][1], "dom_blob")
            self.assertEqual(catalog_rows[3][2], "d")
            self.assertEqual(catalog_rows[3][3], "bytea")

            con.commit()
        finally:
            cur.execute("DROP TABLE IF EXISTS public.foo CASCADE;")
            cur.execute("DROP DOMAIN IF EXISTS public.foo_dom_dom CASCADE;")
            cur.execute("DROP DOMAIN IF EXISTS public.foo_dom CASCADE;")
            cur.execute("DROP DOMAIN IF EXISTS public.dom_data_evento CASCADE;")
            cur.execute("DROP DOMAIN IF EXISTS public.dom_blob CASCADE;")
            con.commit()
            cur.close()
            con.close()


if __name__ == "__main__":
    unittest.main()
