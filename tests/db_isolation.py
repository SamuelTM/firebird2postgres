"""
Test isolation helpers for live-database regression tests.

Rules enforced by this module (see P2 test-isolation task):

1. No connection is ever opened at import/collection time. Availability is
   probed lazily, only when a test actually runs, and results are cached.
2. Live tests never touch the production databases from ``.env``. They use
   an explicit disposable configuration (``TEST_PG_*`` / ``TEST_FB_*``
   environment variables with ``*_test`` defaults) so fixtures cannot
   destroy real data.
3. Skips are explicit and lazy: ``requires_postgres`` / ``requires_firebird``
   evaluate availability at test runtime. When ``REQUIRE_INTEGRATION`` is
   set (mandatory CI integration stage), an unavailable database raises
   instead of skipping so a silent vacuous pass is impossible.
"""

import functools
import os
import socket
import uuid

from config import (
    FirebirdConfig,
    PostgresConfig,
    get_firebird_connection,
    get_postgres_connection,
)

STRICT_ENV_VAR = 'REQUIRE_INTEGRATION'

TEST_PG_DEFAULT_DB = 'firebird2postgres_test'
TEST_FB_DEFAULT_DB = '/firebird/data/firebird2postgres_test.fdb'


def is_strict_integration_mode() -> bool:
    """Returns True when live databases are mandatory (CI integration stage)."""
    return os.getenv(STRICT_ENV_VAR, '').lower() in ('1', 'true', 'yes', 't')


def get_test_postgres_config() -> PostgresConfig:
    """
    Returns the explicit disposable PostgreSQL configuration for tests.
    Never returns the production database: the default dbname is a
    dedicated ``*_test`` database, overridable via ``TEST_PG_*`` env vars.
    """
    return PostgresConfig(
        host=os.getenv('TEST_PG_HOST', os.getenv('POSTGRES_HOST', 'localhost')),
        port=int(os.getenv('TEST_PG_PORT', os.getenv('POSTGRES_PORT', '5432'))),
        dbname=os.getenv('TEST_PG_DB', TEST_PG_DEFAULT_DB),
        user=os.getenv('TEST_PG_USER', os.getenv('POSTGRES_USER', 'postgres')),
        password=os.getenv('TEST_PG_PASSWORD', os.getenv('POSTGRES_PASSWORD', 'mypassword')),
    )


def get_test_firebird_config() -> FirebirdConfig:
    """
    Returns the explicit disposable Firebird configuration for tests.
    Never returns the production database: the default path is a
    dedicated ``*_test.fdb`` file, overridable via ``TEST_FB_*`` env vars.
    """
    return FirebirdConfig(
        host=os.getenv('TEST_FB_HOST', os.getenv('FIREBIRD_HOST', 'localhost')),
        database=os.getenv('TEST_FB_DATABASE', TEST_FB_DEFAULT_DB),
        user=os.getenv('TEST_FB_USER', os.getenv('FIREBIRD_USER', 'sysdba')),
        password=os.getenv('TEST_FB_PASSWORD', os.getenv('FIREBIRD_PASSWORD', 'masterkey')),
        charset=os.getenv('TEST_FB_CHARSET', os.getenv('FIREBIRD_CHARSET', 'WIN1252')),
        port=int(os.getenv('TEST_FB_PORT', os.getenv('FIREBIRD_PORT', '3050'))),
    )


def get_test_postgres_connection():
    """Opens a connection to the disposable test PostgreSQL database."""
    return get_postgres_connection(get_test_postgres_config())


def get_test_firebird_connection():
    """Opens a connection to the disposable test Firebird database."""
    return get_firebird_connection(get_test_firebird_config())


def _tcp_reachable(host: str, port: int, timeout: float = 2.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


@functools.lru_cache(maxsize=1)
def is_postgres_available() -> bool:
    """
    Lazily probes the disposable test PostgreSQL database.
    No connection is opened at import time; call this at test runtime.
    """
    try:
        cfg = get_test_postgres_config()
        if not _tcp_reachable(cfg.host, int(cfg.port)):
            return False
        conn = get_postgres_connection(cfg)
        try:
            cur = conn.cursor()
            cur.execute("SELECT 1;")
            res = cur.fetchone()
            return bool(res and res[0] == 1)
        finally:
            try:
                conn.close()
            except Exception:
                pass
    except Exception:
        return False


@functools.lru_cache(maxsize=1)
def is_firebird_available() -> bool:
    """
    Lazily probes the disposable test Firebird database.
    No connection is opened at import time; call this at test runtime.
    """
    try:
        cfg = get_test_firebird_config()
        if not _tcp_reachable(cfg.host, int(cfg.port)):
            return False
        conn = get_firebird_connection(cfg)
        try:
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM RDB$DATABASE;")
            res = cur.fetchone()
            return bool(res and res[0] == 1)
        finally:
            try:
                conn.close()
            except Exception:
                pass
    except Exception:
        return False


def reset_availability_cache() -> None:
    """Clears cached availability probes (for tests of this module itself)."""
    is_postgres_available.cache_clear()
    is_firebird_available.cache_clear()


def _require_or_skip(testcase, available: bool, db_name: str) -> None:
    if available:
        return
    message = (
        f"Live {db_name} test database required but unavailable "
        f"(config: {get_test_postgres_config() if 'PostgreSQL' in db_name else get_test_firebird_config()})."
    )
    if is_strict_integration_mode():
        raise AssertionError(
            f"{message} {STRICT_ENV_VAR}=1 mandates live databases in the CI integration stage."
        )
    testcase.skipTest(message)


def require_live_postgres(testcase) -> None:
    """Skips (or fails in strict CI mode) when the test PG database is down."""
    _require_or_skip(testcase, is_postgres_available(), "PostgreSQL")


def require_live_firebird(testcase) -> None:
    """Skips (or fails in strict CI mode) when the test Firebird database is down."""
    _require_or_skip(testcase, is_firebird_available(), "Firebird")


def require_live_databases(testcase) -> None:
    """Skips (or fails in strict CI mode) unless both test databases are up."""
    require_live_firebird(testcase)
    require_live_postgres(testcase)


def _wrap_method(method, guard):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        guard(self)
        return method(self, *args, **kwargs)
    return wrapper


def requires_postgres(method):
    """Method decorator: lazy live-PostgreSQL gate evaluated at test runtime."""
    return _wrap_method(method, require_live_postgres)


def requires_firebird(method):
    """Method decorator: lazy live-Firebird gate evaluated at test runtime."""
    return _wrap_method(method, require_live_firebird)


def requires_live_databases(method):
    """Method decorator: lazy gate requiring both live test databases."""
    return _wrap_method(method, require_live_databases)


def requires_postgres_class(cls):
    """
    Class decorator: gates every ``test_*`` method on live PostgreSQL.
    Replaces ``@unittest.skipUnless(HAS_REAL_PG)`` evaluated at collection.
    """
    for name in list(vars(cls)):
        if name.startswith('test_') and callable(getattr(cls, name)):
            setattr(cls, name, requires_postgres(getattr(cls, name)))
    return cls


def requires_firebird_class(cls):
    """
    Class decorator: gates every ``test_*`` method on live Firebird.
    Replaces ``@unittest.skipUnless(HAS_REAL_FB)`` evaluated at collection.
    """
    for name in list(vars(cls)):
        if name.startswith('test_') and callable(getattr(cls, name)):
            setattr(cls, name, requires_firebird(getattr(cls, name)))
    return cls


def requires_live_databases_class(cls):
    """
    Class decorator: gates every ``test_*`` method on both live databases.
    Replaces ``@unittest.skipUnless(HAS_REAL_PG and HAS_REAL_FB)``.
    """
    for name in list(vars(cls)):
        if name.startswith('test_') and callable(getattr(cls, name)):
            setattr(cls, name, requires_live_databases(getattr(cls, name)))
    return cls


def unique_name(prefix: str) -> str:
    """
    Returns an isolated fixture name (``<prefix>_<8 hex chars>``) so parallel
    or repeated runs never collide on disposable test tables/schemas.
    """
    clean = ''.join(ch if (ch.isalnum() or ch == '_') else '_' for ch in prefix.lower())
    return f"{clean}_{uuid.uuid4().hex[:8]}"
