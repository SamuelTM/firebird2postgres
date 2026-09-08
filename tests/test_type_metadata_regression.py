import unittest
from unittest.mock import MagicMock

import psycopg2
from config import get_postgres_connection, PostgresConfig
from engine.data_migrator import DataMigrator
from engine.ddl_exporter import DdlExporter
from engine.schema_extractor import SchemaExtractor
from models import Column, Table, resolve_firebird_type
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


HAS_REAL_PG = check_live_postgres_available()


class TestTypeMetadataRegression(unittest.TestCase):
    """
    Regression test suite for:
    'Conversão de tipos altera identificadores e omite metadados'
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

    def test_identifiers_and_literals_with_type_names_remain_intact(self):
        """
        Verify that identifiers ("INT128", INT128) and literals ('INT128')
        are not transformed into numeric(39), while type declarations (CAST AS INT128)
        are properly converted.
        """
        sql = 'CREATE VIEW V_TEST AS SELECT "INT128", INT128, \'INT128\' AS LIT, CAST(X AS INT128) AS C FROM T;'
        transpiled = FirebirdToPostgresVisitor.transpile(sql)

        # "INT128" (delimited identifier) should stay "int128" or "INT128"
        self.assertIn('"int128"', transpiled.lower())
        # Unquoted identifier INT128 should stay int128
        self.assertIn('int128,', transpiled.lower())
        # Literal 'INT128' must not be altered
        self.assertIn("'INT128'", transpiled)
        # CAST type spec must be converted to numeric(39)
        self.assertIn('CAST(X AS NUMERIC(39))', transpiled)
        self.assertNotIn('AS INT128', transpiled.upper())

    def test_decfloat_identifier_and_literal_preserved(self):
        """
        DECFLOAT in identifiers and literals must not turn into NUMERIC.
        """
        sql = 'CREATE VIEW V_DEC AS SELECT "DECFLOAT", \'DECFLOAT(16)\' AS L, CAST(Y AS DECFLOAT(16)) AS C FROM T;'
        transpiled = FirebirdToPostgresVisitor.transpile(sql)

        self.assertIn('"decfloat"', transpiled.lower())
        self.assertIn("'DECFLOAT(16)'", transpiled)
        self.assertIn('CAST(Y AS NUMERIC)', transpiled)

    def test_parameter_and_variable_modern_types(self):
        """
        Procedures with INT128, DECFLOAT(16), and VARCHAR(...) CHARACTER SET OCTETS
        parameters and local variables are transpiled to numeric(39), numeric, and bytea.
        """
        fb_proc = """
        CREATE OR ALTER PROCEDURE SP_MODERN_TYPES (
            P_INT INT128,
            P_OCT VARCHAR(32) CHARACTER SET OCTETS
        ) RETURNS (
            OUT_NUM DECFLOAT(16)
        ) AS
        DECLARE VARIABLE V_BIG INT128;
        DECLARE VARIABLE V_RAW CHAR(16) CHARACTER SET OCTETS;
        BEGIN
            V_BIG = P_INT;
            V_RAW = P_OCT;
            OUT_NUM = V_BIG;
            SUSPEND;
        END;
        """
        transpiled = FirebirdToPostgresVisitor.transpile(fb_proc)
        self.assertIn('P_INT NUMERIC(39)', transpiled)
        self.assertIn('P_OCT BYTEA', transpiled)
        self.assertIn('OUT OUT_NUM NUMERIC', transpiled)
        self.assertIn('V_BIG NUMERIC(39);', transpiled)
        self.assertIn('V_RAW BYTEA;', transpiled)

    def test_delimited_domain_with_type_name_not_corrupted(self):
        """
        A domain called "INT128" (delimited identifier, NOT the native type)
        must resolve to its domain_map entry, not be converted to NUMERIC(39).
        Same for "BLOB", "DECFLOAT", etc.
        """
        from transpiler.firebird_visitor import convert_firebird_type_declaration

        # Domain "INT128" mapped to int128_dom
        dm = {'INT128': 'int128_dom'}

        # Delimited domain reference: "INT128" -> should resolve to int128_dom
        self.assertEqual(convert_firebird_type_declaration('"INT128"', domain_map=dm), 'int128_dom')

        # Unquoted domain reference: INT128 -> should also resolve to int128_dom
        self.assertEqual(convert_firebird_type_declaration('INT128', domain_map=dm), 'int128_dom')

        # Without domain_map, INT128 is a native type -> NUMERIC(39)
        self.assertEqual(convert_firebird_type_declaration('INT128'), 'NUMERIC(39)')

        # Domain "BLOB" mapped to blob_dom
        dm2 = {'BLOB': 'blob_dom'}
        self.assertEqual(convert_firebird_type_declaration('"BLOB"', domain_map=dm2), 'blob_dom')
        self.assertEqual(convert_firebird_type_declaration('BLOB', domain_map=dm2), 'blob_dom')

        # Without domain_map, BLOB is a native type -> BYTEA
        self.assertEqual(convert_firebird_type_declaration('BLOB'), 'BYTEA')

    def test_delimited_domain_in_procedure_transpile(self):
        """
        End-to-end: procedure with parameter, variable, and return using
        a domain "INT128" must use the domain, not NUMERIC(39).
        """
        fb_proc = """
        CREATE OR ALTER PROCEDURE SP_TEST (
            X "INT128"
        ) RETURNS (
            Y "INT128"
        ) AS
        DECLARE VARIABLE Z "INT128";
        BEGIN
            Z = X;
            Y = Z;
            SUSPEND;
        END;
        """
        dm = {'INT128': 'int128_dom'}
        transpiled = FirebirdToPostgresVisitor.transpile(fb_proc, domain_map=dm)
        # All three usages must resolve to domain, not NUMERIC(39)
        self.assertIn('X int128_dom', transpiled)
        self.assertIn('OUT Y int128_dom', transpiled)
        self.assertIn('Z int128_dom;', transpiled)
        self.assertNotIn('NUMERIC(39)', transpiled)


    def test_octets_domain_and_column_metadata(self):
        """
        Verify export_firebird_domains, _fetch_domain_info, and schema_extractor
        resolve CHARACTER_SET_ID=1 (OCTETS) to BYTEA for domains and columns.
        """
        import tempfile
        mock_fb = MagicMock()
        mock_cur = MagicMock()
        mock_fb.cursor.return_value = mock_cur
        exporter = DdlExporter(mock_fb)

        # 1. Test _fetch_domain_info resolves charset_id=1 as BYTEA
        mock_cur.fetchall.side_effect = [
            [],  # relation names
            [('DOM_OCTETS', 37, 0, 64, None, None, 1, None)]  # fields
        ]
        _, domain_types = exporter._fetch_domain_info(mock_cur)
        self.assertEqual(domain_types.get('DOM_OCTETS'), 'BYTEA')

        # 2. Test export_firebird_domains produces CREATE DOMAIN ... AS bytea
        with tempfile.NamedTemporaryFile(mode='w+', delete=True) as f_fb, \
             tempfile.NamedTemporaryFile(mode='w+', delete=True) as f_pg:
            mock_cur.fetchall.side_effect = [
                [],  # sequence increments
                [('DOM_OCTETS', 37, 0, 64, None, None, None, 0, None, 1, None)],  # domain fields
                [],  # relation names
            ]
            exporter.export_firebird_domains(output_file=f_fb.name, converted_file=f_pg.name)
            f_pg.seek(0)
            pg_content = f_pg.read()
            self.assertIn('"dom_octets" AS BYTEA;', pg_content)

        # 3. Test schema_extractor: relation field with charset_id=1
        mock_cur.fetchall.side_effect = [
            [
                ('DATA_RAW', 37, 0, 32, None, None, None, None, None, 'RDB$1', None, None, None, 1, None)
            ]
        ]
        mock_cur.description = None
        cols = SchemaExtractor._extract_columns(mock_cur, 'T_OCTETS', set(), domain_map={}, sequence_increments={})
        self.assertEqual(len(cols), 1)
        self.assertEqual(cols[0].column_type, 'BYTEA')

    def test_array_rejections_uniform(self):
        """
        Arrays must be rejected with NotImplementedError across:
        - resolve_firebird_type
        - SchemaExtractor._extract_columns (direct and domain-based)
        - DdlExporter.export_firebird_domains
        - DdlExporter._fetch_domain_info
        - DdlExporter._fetch_procedure_parameters
        """
        # 1. Direct type resolution
        with self.assertRaises(NotImplementedError):
            resolve_firebird_type(field_type=8, dimensions=1)

        mock_fb = MagicMock()
        mock_cur = MagicMock()
        mock_fb.cursor.return_value = mock_cur

        # 2. Table column with array dimensions
        mock_cur.fetchall.side_effect = [
            [('ARR_COL', 8, 0, 4, None, None, None, None, None, 'RDB$2', None, None, None, None, 1)]
        ]
        with self.assertRaises(NotImplementedError) as ctx:
            SchemaExtractor._extract_columns(mock_cur, 'T_ARR', set(), domain_map={}, sequence_increments={})
        self.assertIn("array", str(ctx.exception).lower())

        # 3. Domain with array dimensions in export_firebird_domains
        exporter = DdlExporter(mock_fb)
        mock_cur.fetchall.side_effect = [
            [],  # sequence increments
            [('DOM_ARR', 8, 0, 4, None, None, None, 0, None, None, 1)],  # domain fields with dimensions=1
            [],  # relation names
        ]
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w+', delete=True) as f_fb, \
             tempfile.NamedTemporaryFile(mode='w+', delete=True) as f_pg:
            with self.assertRaises(NotImplementedError) as ctx:
                exporter.export_firebird_domains(output_file=f_fb.name, converted_file=f_pg.name)
            self.assertIn("array", str(ctx.exception).lower())

        # 4. _fetch_domain_info
        mock_cur.fetchall.side_effect = [
            [],  # relation names
            [('DOM_ARR', 8, 0, 4, None, None, None, 1)],  # fields with dimensions=1
        ]
        with self.assertRaises(NotImplementedError) as ctx:
            exporter._fetch_domain_info(mock_cur)
        self.assertIn("array", str(ctx.exception).lower())

        # 5. _fetch_procedure_parameters
        mock_cur.fetchall.side_effect = [
            [('P_ARR', 0, 0, 8, 0, 4, None, None, 'RDB$3', None, None, None, None, None, None, 1)]
        ]
        with self.assertRaises(NotImplementedError) as ctx:
            exporter._fetch_procedure_parameters(mock_cur, 'SP1')
        self.assertIn("array", str(ctx.exception).lower())

    @unittest.skipUnless(HAS_REAL_PG, "Live PostgreSQL instance required for exact binary load test")
    def test_binary_octets_migration_exact_bytes_roundtrip(self):
        """
        Verify exact binary migration into PostgreSQL BYTEA and domain on BYTEA:
        - Must preserve bytes 0x00 (NUL), 0x80, and 0xFF without corruption or stripping.
        - Must succeed both when driver returns bytes and when it returns string.
        """
        self.pg_cur.execute('DROP TABLE IF EXISTS t_binary_test CASCADE;')
        self.pg_cur.execute('DROP DOMAIN IF EXISTS dom_bin_test CASCADE;')
        self.pg_cur.execute('CREATE DOMAIN dom_bin_test AS bytea;')
        self.pg_cur.execute("""
            CREATE TABLE t_binary_test (
                id integer PRIMARY KEY,
                raw_bytes bytea,
                dom_bytes dom_bin_test
            );
        """)
        self.pg_con.commit()

        # Binary payload with 00, 80, FF, and repeated sequences
        payload_1 = bytes([0x00, 0x80, 0xFF, 0x00, 0xAA, 0x55, 0x00])
        # Payload passed as decoded latin1 str (which drivers sometimes return)
        payload_2_bytes = bytes([0x80, 0x00, 0xFF, 0x7F, 0x00, 0x00, 0xFF])
        payload_2_str = payload_2_bytes.decode('latin1')

        table = Table('T_BINARY_TEST')
        table.columns.append(Column('ID', 'INTEGER', nullable=False))
        table.columns.append(Column('RAW_BYTES', 'BYTEA', nullable=True))
        col_dom = Column('DOM_BYTES', 'BYTEA', nullable=True)
        col_dom.domain_name = 'dom_bin_test'
        table.columns.append(col_dom)

        mock_fb_con = MagicMock()
        mock_fb_cur = MagicMock()
        mock_fb_con.cursor.return_value = mock_fb_cur
        mock_fb_cur.fetchmany.side_effect = [
            [
                (1, payload_1, payload_1),
                (2, payload_2_str, payload_2_bytes),
            ],
            []
        ]

        migrator = DataMigrator(mock_fb_con, self.pg_con)
        success = migrator.import_data([table], max_workers=1)
        self.assertTrue(success)
        # NUL stats should be empty because binary columns preserve NUL
        self.assertEqual(migrator.last_nul_stats.get('T_BINARY_TEST', {}), {})

        # Verify exact binary roundtrip in PostgreSQL
        self.pg_cur.execute('SELECT id, raw_bytes, dom_bytes FROM t_binary_test ORDER BY id;')
        rows = self.pg_cur.fetchall()
        self.assertEqual(len(rows), 2)

        row1 = rows[0]
        self.assertEqual(row1[0], 1)
        self.assertEqual(bytes(row1[1]), payload_1)
        self.assertEqual(bytes(row1[2]), payload_1)

        row2 = rows[1]
        self.assertEqual(row2[0], 2)
        self.assertEqual(bytes(row2[1]), payload_2_bytes)
        self.assertEqual(bytes(row2[2]), payload_2_bytes)

        # Cleanup
        self.pg_cur.execute('DROP TABLE t_binary_test CASCADE;')
        self.pg_cur.execute('DROP DOMAIN dom_bin_test CASCADE;')
        self.pg_con.commit()


if __name__ == '__main__':
    unittest.main()
