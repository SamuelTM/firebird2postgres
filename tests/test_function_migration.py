import os
import tempfile
import unittest
from unittest.mock import MagicMock

from engine.ddl_exporter import DdlExporter
from transpiler import FirebirdToPostgresVisitor
from utils.sql_runner import SqlRunner


class TestFunctionTranspilation(unittest.TestCase):
    def test_psql_function_returns_postgres_function(self):
        sql = """
        CREATE FUNCTION F_ADD(A INTEGER, B INTEGER) RETURNS INTEGER AS
        BEGIN
            RETURN A + B;
        END;
        """
        output = FirebirdToPostgresVisitor.transpile(sql)
        self.assertIn('CREATE OR REPLACE FUNCTION "f_add"(A INTEGER, B INTEGER) RETURNS INTEGER', output)
        self.assertIn('RETURN A + B;', output)
        self.assertIn('LANGUAGE plpgsql IMMUTABLE;', output)

    def test_function_header_variants_and_quoted_names(self):
        for sql in (
            'CREATE FUNCTION F() RETURNS INTEGER AS BEGIN RETURN 1; END;',
            'CREATE OR ALTER FUNCTION "MixedCase"(A INTEGER) RETURNS INTEGER AS BEGIN RETURN A; END;',
            'RECREATE FUNCTION F(A INTEGER NOT NULL) RETURNS INTEGER AS BEGIN RETURN A; END;',
        ):
            with self.subTest(sql=sql):
                output = FirebirdToPostgresVisitor.transpile(sql)
                self.assertIn('CREATE OR REPLACE FUNCTION', output)
                self.assertNotIn('DROP FUNCTION', output)

    def test_function_return_not_null_is_checked_once(self):
        output = FirebirdToPostgresVisitor.transpile(
            'CREATE FUNCTION F(A INTEGER) RETURNS INTEGER AS BEGIN RETURN A + 1; END;',
            function_return_not_null=True,
        )
        self.assertIn('__fb_return_value := A + 1;', output)
        self.assertIn("RAISE EXCEPTION 'Function return value cannot be NULL'", output)

    def test_function_map_rewrites_call_at_ast_node(self):
        output = FirebirdToPostgresVisitor.transpile(
            'CREATE FUNCTION F(A INTEGER) RETURNS INTEGER AS BEGIN RETURN CEIL(A); END;',
            function_map={'CEIL': 'floor'},
        )
        self.assertIn('RETURN floor(A);', output)
        self.assertNotIn("'CEIL'", output)


class TestDatabaseFunctionAnalysis(unittest.TestCase):
    def setUp(self):
        self.exporter = DdlExporter(MagicMock())
        self.exporter._fetch_function_catalog = lambda _cursor: [
            {'name': 'F_ROOT', 'source': 'BEGIN RETURN F_LEAF(X); END;',
             'module': '', 'entrypoint': '', 'deterministic': True},
            {'name': 'F_LEAF', 'source': 'BEGIN RETURN ABS(X); END;',
             'module': '', 'entrypoint': '', 'deterministic': True},
            {'name': 'ABS', 'source': '', 'module': 'ib_udf',
             'entrypoint': 'abs', 'deterministic': True},
            {'name': 'F_UNUSED', 'source': 'BEGIN RETURN 1; END;',
             'module': '', 'entrypoint': '', 'deterministic': True},
        ]
        self.exporter._stored_function_sources = lambda _cursor: [
            'SELECT F_ROOT(ID) FROM T'
        ]

    def test_analysis_closes_over_indirect_dependencies_and_excludes_unused(self):
        result = self.exporter.analyze_database_functions()
        self.assertEqual(result['F_ROOT']['classification'], 'PSQL')
        self.assertEqual(result['F_LEAF']['classification'], 'PSQL')
        self.assertEqual(result['ABS']['classification'], 'NATIVE_EQUIVALENT')
        self.assertNotIn('F_UNUSED', result)

    def test_function_calls_ignore_comments_and_literals(self):
        calls = self.exporter._function_calls(
            "SELECT F_REAL(X), 'F_FAKE(X)' /* F_BLOCK(Y) */ -- F_LINE(Z)\n FROM T"
        )
        self.assertEqual(calls, {'F_REAL'})

    def test_native_classification_requires_library_entrypoint(self):
        item = {'name': 'ABS', 'source': '', 'module': 'other_udf',
                'entrypoint': 'abs', 'deterministic': True}
        self.assertEqual(self.exporter._classify_function(item)[0], 'EXTERNAL_MANUAL')

    def test_standard_ib_udf_entrypoint_and_module_variants_are_recognized(self):
        item = {'name': 'ABS', 'source': '',
                'module': '/opt/firebird/UDF/ib_udf.so',
                'entrypoint': 'IB_UDF_abs', 'deterministic': True}
        classification, target, _reason = self.exporter._classify_function(item)
        self.assertEqual(classification, 'NATIVE_EQUIVALENT')
        self.assertEqual(target, 'abs')

    def test_runtime_dynamic_sql_does_not_promote_unused_functions(self):
        self.exporter._fetch_function_catalog = lambda _cursor: [
            {'name': 'ABS', 'source': '', 'module': 'ib_udf',
             'entrypoint': 'IB_UDF_abs', 'return_argument': 0},
            {'name': 'F_EXTERNAL', 'source': '', 'module': 'legacy_udf',
             'entrypoint': 'f_external', 'return_argument': 0},
        ]
        self.exporter._stored_function_sources = lambda _cursor: [
            'EXECUTE STATEMENT V_SQL;'
        ]
        self.assertEqual(self.exporter.analyze_database_functions(), {})

        audit = self.exporter.analyze_database_functions(include_unused=True)
        self.assertEqual(audit['ABS']['classification'], 'NATIVE_EQUIVALENT')
        self.assertEqual(audit['F_EXTERNAL']['classification'], 'EXTERNAL_MANUAL')
        self.assertEqual(audit['F_EXTERNAL']['status'], 'UNUSED')
        self.assertTrue(audit['F_EXTERNAL']['runtime_usage_unverified'])
        self.assertIn('possible use from runtime SQL', audit['F_EXTERNAL']['reason'])

    def test_external_udf_signature_uses_direct_argument_type_metadata(self):
        cursor = MagicMock()
        cursor.fetchall.return_value = [
            ('ARG0', 0, 'RDB$FIELD_1', 8, None, 4, None, 0,
             None, None, None, None, 0),
        ]
        signature = self.exporter._fetch_function_signature(
            cursor,
            {'name': 'ABS', 'return_argument': 0},
        )
        self.assertEqual(signature['fb_return'], 'INTEGER')
        self.assertEqual(signature['pg_return'], 'INTEGER')
        query = cursor.execute.call_args_list[0].args[0]
        self.assertIn('a.RDB$FIELD_TYPE', query)
        self.assertNotIn('a.RDB$DIMENSIONS', query)

    def test_external_udf_cstring_signature_maps_to_varchar(self):
        cursor = MagicMock()
        cursor.fetchall.return_value = [
            (None, 0, None, 40, 0, 255, None, 0,
             None, None, 0, None, None),
            (None, 1, None, 40, 0, 32767, None, 0,
             None, None, 0, None, None),
        ]
        signature = self.exporter._fetch_function_signature(
            cursor,
            {'name': 'LEGACY_TEXT', 'return_argument': 0},
        )
        self.assertEqual(signature['fb_return'], 'VARCHAR(255)')
        self.assertEqual(signature['pg_return'], 'VARCHAR(255)')
        self.assertEqual(signature['pg_params'], ['ARG1 VARCHAR(32767)'])

    def test_package_function_is_not_flattened_to_a_global_function(self):
        item = {'name': 'F_PACKAGED', 'source': 'BEGIN RETURN 1; END;',
                'module': '', 'entrypoint': '', 'package': 'PKG_API'}
        classification, _target, reason = self.exporter._classify_function(item)
        self.assertEqual(classification, 'PACKAGE_MANUAL')
        self.assertIn('PKG_API', reason)

    def test_overloaded_function_name_is_blocked(self):
        item = {'name': 'F_OVERLOADED', 'source': 'BEGIN RETURN 1; END;',
                'module': '', 'entrypoint': '', '_ambiguous_overload_count': 2}
        classification, _target, reason = self.exporter._classify_function(item)
        self.assertEqual(classification, 'AMBIGUOUS_SIGNATURE')
        self.assertIn('2 Firebird overloads', reason)

    def test_analysis_marks_duplicate_function_names_as_ambiguous(self):
        self.exporter._fetch_function_catalog = lambda _cursor: [
            {'name': 'F_DUP', 'source': 'BEGIN RETURN 1; END;',
             'module': '', 'entrypoint': '', 'return_argument': 0},
            {'name': 'F_DUP', 'source': 'BEGIN RETURN 2; END;',
             'module': '', 'entrypoint': '', 'return_argument': 0},
        ]
        self.exporter._stored_function_sources = lambda _cursor: ['SELECT F_DUP(ID) FROM T']
        result = self.exporter.analyze_database_functions()
        self.assertEqual(result['F_DUP']['status'], 'USED')
        self.assertEqual(result['F_DUP']['classification'], 'AMBIGUOUS_SIGNATURE')

    def test_constant_dynamic_sql_is_analyzed(self):
        self.exporter._fetch_function_catalog = lambda _cursor: [
            {'name': 'F_DYNAMIC', 'source': 'BEGIN RETURN 1; END;',
             'module': '', 'entrypoint': '', 'return_argument': 0},
            {'name': 'F_CALLED', 'source': 'BEGIN RETURN 2; END;',
             'module': '', 'entrypoint': '', 'return_argument': 0},
        ]
        self.exporter._stored_function_sources = lambda _cursor: [
            "EXECUTE STATEMENT 'SELECT F_CALLED(ID)';"
        ]
        result = self.exporter.analyze_database_functions(include_unused=True)
        self.assertEqual(result['F_CALLED']['status'], 'USED')
        self.assertEqual(result['F_DYNAMIC']['status'], 'UNUSED')

    def test_export_contains_psql_and_audits_native_choice(self):
        self.exporter._fetch_function_arguments = lambda _cursor, _name: (['A INTEGER'], 'INTEGER')
        with tempfile.TemporaryDirectory() as tmpdir:
            fb_path = os.path.join(tmpdir, 'functions_fb.sql')
            pg_path = os.path.join(tmpdir, 'functions_pg.sql')
            count = self.exporter.export_firebird_functions(fb_path, pg_path)
            self.assertEqual(count, 2)
            with open(pg_path, encoding='utf-8') as file:
                content = file.read()
            self.assertIn('CREATE OR REPLACE FUNCTION "f_root"', content)
            self.assertIn('CREATE OR REPLACE FUNCTION "f_leaf"', content)
            self.assertIn('Native PostgreSQL equivalents selected', content)
            self.assertIn('--   ABS', content)

    def test_required_external_function_blocks_export(self):
        self.exporter._fetch_function_catalog = lambda _cursor: [
            {'name': 'F_EXTERNAL', 'source': '', 'module': 'legacy.dll',
             'entrypoint': 'f_external', 'deterministic': False},
        ]
        self.exporter._stored_function_sources = lambda _cursor: ['SELECT F_EXTERNAL(ID) FROM T']
        with self.assertRaisesRegex(RuntimeError, 'F_EXTERNAL'):
            self.exporter.export_firebird_functions(
                os.path.join(tempfile.gettempdir(), 'functions_fb.sql'),
                os.path.join(tempfile.gettempdir(), 'functions_pg.sql'))

    def test_circular_psql_dependencies_block_export(self):
        self.exporter._fetch_function_catalog = lambda _cursor: [
            {'name': 'F_A', 'source': 'BEGIN RETURN F_B(X); END;',
             'module': '', 'entrypoint': '', 'deterministic': True},
            {'name': 'F_B', 'source': 'BEGIN RETURN F_A(X); END;',
             'module': '', 'entrypoint': '', 'deterministic': True},
        ]
        self.exporter._stored_function_sources = lambda _cursor: ['SELECT F_A(ID) FROM T']
        with self.assertRaisesRegex(RuntimeError, 'Circular dependency'):
            self.exporter.export_firebird_functions(
                os.path.join(tempfile.gettempdir(), 'functions_fb.sql'),
                os.path.join(tempfile.gettempdir(), 'functions_pg.sql'))


class TestFunctionArtifactValidation(unittest.TestCase):
    def test_function_validation_does_not_accept_a_procedure_with_same_name(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, 'functions.sql')
            with open(path, 'w', encoding='utf-8') as file:
                file.write('CREATE PROCEDURE f() AS $$ BEGIN NULL; END; $$;')
            with self.assertRaises(ValueError):
                SqlRunner(MagicMock()).validate_file(
                    path, expected_objects=['F'], object_type='FUNCTION'
                )


if __name__ == '__main__':
    unittest.main()
