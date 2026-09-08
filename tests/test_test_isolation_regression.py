"""
Regression suite for P2 test isolation:

1. Collection opens no database connections (structural AST check on every
   test module + collect-only smoke run against unroutable hosts).
2. With REQUIRE_INTEGRATION=1 (mandatory CI integration stage), unavailable
   live databases raise instead of silently skipping.
3. Live-test fixtures run against an explicit disposable configuration and
   use collision-free isolated names.
4. Absent/invalid source state is rejected by production code with no
   mock shortcuts.
"""

import ast
import os
import pathlib
import subprocess
import sys
import unittest
from unittest.mock import MagicMock

from engine.data_migrator import DataMigrator
from tests import db_isolation
from tests.db_isolation import (
    STRICT_ENV_VAR,
    get_test_firebird_config,
    get_test_postgres_config,
    is_firebird_available,
    is_postgres_available,
    requires_postgres,
    reset_availability_cache,
    unique_name,
)

TESTS_DIR = pathlib.Path(__file__).resolve().parent

# Calls that must never execute at module level (collection time).
FORBIDDEN_AT_COLLECTION = {
    'check_live_postgres_available',
    'check_live_firebird_available',
    'get_postgres_connection',
    'get_firebird_connection',
    'get_test_postgres_connection',
    'get_test_firebird_connection',
    'is_postgres_available',
    'is_firebird_available',
}


def _module_level_forbidden_calls(path: pathlib.Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
    found: list[str] = []

    class Visitor(ast.NodeVisitor):
        def visit_Call(self, node: ast.Call) -> None:  # noqa: N802
            func = node.func
            name = None
            if isinstance(func, ast.Name):
                name = func.id
            elif isinstance(func, ast.Attribute):
                name = func.attr
            if name in FORBIDDEN_AT_COLLECTION:
                found.append(f"{path.name}:{node.lineno}: {name}()")
            self.generic_visit(node)

    for node in tree.body:
        # Only module-level statements run at collection; defs/classes are lazy.
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef,
                             ast.Import, ast.ImportFrom)):
            continue
        Visitor().visit(node)
    return found


class TestCollectionOpensNoConnections(unittest.TestCase):
    """
    Accepts: coletar sem banco.
    No test module may open a database connection while it is imported
    (pytest collection imports every module).
    """

    def test_no_module_level_connection_calls(self):
        offenders: list[str] = []
        for path in sorted(TESTS_DIR.glob('test_*.py')):
            if path.name == 'test_test_isolation_regression.py':
                continue
            offenders.extend(_module_level_forbidden_calls(path))
        self.assertEqual(
            offenders, [],
            f"Connection calls at module level (collection time):\n" + "\n".join(offenders),
        )

    def test_no_has_real_constants_at_module_level(self):
        offenders = []
        for path in sorted(TESTS_DIR.glob('test_*.py')):
            if path.name == 'test_test_isolation_regression.py':
                continue
            tree = ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
            for node in tree.body:
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id.startswith('HAS_REAL'):
                            offenders.append(f"{path.name}:{node.lineno}: {target.id}")
        self.assertEqual(
            offenders, [],
            f"HAS_REAL_* constants evaluate connections at import:\n" + "\n".join(offenders),
        )

    def test_collect_only_succeeds_with_unreachable_databases(self):
        env = dict(os.environ)
        env['TEST_PG_HOST'] = '192.0.2.1'
        env['TEST_FB_HOST'] = '192.0.2.1'
        env['POSTGRES_HOST'] = '192.0.2.1'
        env['FIREBIRD_HOST'] = '192.0.2.1'
        proc = subprocess.run(
            [sys.executable, '-m', 'pytest', 'tests/', '--collect-only', '-q'],
            cwd=str(TESTS_DIR.parent),
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
        )
        self.assertEqual(
            proc.returncode, 0,
            f"Collection must succeed without databases.\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}",
        )
        self.assertIn('tests collected', proc.stdout)


class TestStrictIntegrationMode(unittest.TestCase):
    """
    Accepts: executar integração indisponível exigindo falha.
    REQUIRE_INTEGRATION=1 turns a skip into a hard failure so CI cannot
    pass vacuously when the live stage is down.
    """

    def _run_strict(self, fn):
        old = os.environ.get(STRICT_ENV_VAR)
        os.environ[STRICT_ENV_VAR] = '1'
        reset_availability_cache()
        old_pg, old_fb = os.environ.get('TEST_PG_HOST'), os.environ.get('TEST_FB_HOST')
        os.environ['TEST_PG_HOST'] = '192.0.2.1'
        os.environ['TEST_FB_HOST'] = '192.0.2.1'
        try:
            return fn()
        finally:
            if old is None:
                os.environ.pop(STRICT_ENV_VAR, None)
            else:
                os.environ[STRICT_ENV_VAR] = old
            if old_pg is None:
                os.environ.pop('TEST_PG_HOST', None)
            else:
                os.environ['TEST_PG_HOST'] = old_pg
            if old_fb is None:
                os.environ.pop('TEST_FB_HOST', None)
            else:
                os.environ['TEST_FB_HOST'] = old_fb
            reset_availability_cache()

    def test_unavailable_postgres_fails_in_strict_mode(self):
        class Dummy:
            def skipTest(self, msg):
                raise AssertionError(f"skipTest must not be called in strict mode: {msg}")

        def run():
            with self.assertRaises(AssertionError) as ctx:
                requires_postgres(lambda self: None)(Dummy())
            self.assertIn(STRICT_ENV_VAR, str(ctx.exception))

        self._run_strict(run)

    def test_unavailable_databases_skip_outside_strict_mode(self):
        old = os.environ.pop(STRICT_ENV_VAR, None)
        reset_availability_cache()
        old_pg, old_fb = os.environ.get('TEST_PG_HOST'), os.environ.get('TEST_FB_HOST')
        os.environ['TEST_PG_HOST'] = '192.0.2.1'
        os.environ['TEST_FB_HOST'] = '192.0.2.1'
        try:
            self.assertFalse(is_postgres_available())
            self.assertFalse(is_firebird_available())

            class Dummy(unittest.TestCase):
                def runTest(self):
                    pass

            dummy = Dummy()
            with self.assertRaises(unittest.SkipTest):
                db_isolation.require_live_postgres(dummy)
            with self.assertRaises(unittest.SkipTest):
                db_isolation.require_live_firebird(dummy)
        finally:
            if old is not None:
                os.environ[STRICT_ENV_VAR] = old
            if old_pg is None:
                os.environ.pop('TEST_PG_HOST', None)
            else:
                os.environ['TEST_PG_HOST'] = old_pg
            if old_fb is None:
                os.environ.pop('TEST_FB_HOST', None)
            else:
                os.environ['TEST_FB_HOST'] = old_fb
            reset_availability_cache()


class TestDisposableFixtures(unittest.TestCase):
    """
    Accepts: rodar fixtures em ambiente isolado.
    Live tests must target explicit disposable databases — never the
    production ones — and use collision-free fixture names.
    """

    def test_disposable_postgres_config(self):
        cfg = get_test_postgres_config()
        self.assertEqual(cfg.dbname, os.getenv('TEST_PG_DB', 'firebird2postgres_test'))
        self.assertIn('test', cfg.dbname)
        # Must not point at the production database from .env by default.
        self.assertNotEqual(cfg.dbname, 'clini7')

    def test_disposable_firebird_config(self):
        cfg = get_test_firebird_config()
        self.assertEqual(cfg.database, os.getenv('TEST_FB_DATABASE', '/firebird/data/firebird2postgres_test.fdb'))
        self.assertIn('test', cfg.database)
        self.assertNotEqual(cfg.database, '/firebird/data/CLINI7.fdb')

    def test_unique_name_is_isolated(self):
        first, second = unique_name('reg_t'), unique_name('reg_t')
        self.assertNotEqual(first, second)
        for name in (first, second):
            self.assertTrue(name.startswith('reg_t_'))
            self.assertRegex(name, r'^[a-z0-9_]+$')

    def test_live_modules_use_disposable_connections(self):
        offenders = []
        for path in sorted(TESTS_DIR.glob('test_*.py')):
            if path.name == 'test_test_isolation_regression.py':
                continue
            text = path.read_text(encoding='utf-8')
            if 'get_postgres_connection(' in text or 'get_firebird_connection(' in text:
                offenders.append(path.name)
        self.assertEqual(
            offenders, [],
            f"Live tests must use get_test_*_connection, not production getters: {offenders}",
        )


class TestSourceStateRejectedWithoutShortcuts(unittest.TestCase):
    """
    Accepts: confirmar que estado ausente/inválido da origem é rejeitado
    sem atalhos. Production code contains no MagicMock special-casing.
    """

    def _migrator(self, fetchone_results=None, execute_error=None):
        fb_con, fb_cur = MagicMock(), MagicMock()
        fb_con.cursor.return_value = fb_cur
        if execute_error is not None:
            fb_cur.execute.side_effect = execute_error
        elif fetchone_results is not None:
            fb_cur.fetchone.side_effect = fetchone_results
        # else: bare MagicMock (no fetchone configuration at all)
        return DataMigrator(fb_con, MagicMock()), fb_cur

    def test_bare_mock_source_is_rejected(self):
        migrator, _ = self._migrator()
        with self.assertRaises(RuntimeError) as ctx:
            migrator.check_source_consistency()
        self.assertIn('Cannot verify', str(ctx.exception))

    def test_missing_catalog_row_is_rejected(self):
        migrator, _ = self._migrator(fetchone_results=[None, (0,)])
        with self.assertRaises(RuntimeError) as ctx:
            migrator.check_source_consistency()
        self.assertIn('Cannot verify', str(ctx.exception))

    def test_string_catalog_values_are_rejected(self):
        migrator, _ = self._migrator(fetchone_results=[('1', '0'), (0,)])
        with self.assertRaises(RuntimeError) as ctx:
            migrator.check_source_consistency()
        self.assertIn('Cannot verify', str(ctx.exception))

    def test_proven_frozen_source_still_approved(self):
        migrator, _ = self._migrator(fetchone_results=[(1, 0), (0,)])
        info = migrator.check_source_consistency()
        self.assertTrue(info['is_read_only'])
        self.assertTrue(info['verified'])

    def test_no_mock_shortcuts_remain_in_production(self):
        import engine.data_migrator as prod
        import inspect
        source = inspect.getsource(prod.DataMigrator.check_source_consistency)
        self.assertNotIn('MagicMock', source)


if __name__ == '__main__':
    unittest.main()
