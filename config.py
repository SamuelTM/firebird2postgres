import os
import logging
from dataclasses import dataclass, field
from typing import Callable, TypeVar
from dotenv import load_dotenv
import firebirdsql
import psycopg2

load_dotenv()

DUMP_DIR: str = os.getenv('DUMP_DIR', 'dumps')


class DumpFiles:
    TRIGGERS_FB:   str = 'firebird_triggers_dump.sql'
    TRIGGERS_PG:   str = 'postgres_triggers_dump.sql'
    PROCEDURES_FB: str = 'firebird_procedures_dump.sql'
    PROCEDURES_PG: str = 'postgres_procedures_dump.sql'
    VIEWS_FB:      str = 'firebird_views_dump.sql'
    VIEWS_PG:      str = 'postgres_views_dump.sql'
    DOMAINS_FB:    str = 'firebird_domains_dump.sql'
    DOMAINS_PG:    str = 'postgres_domains_dump.sql'


def get_dump_path(filename: str, dump_dir: str = None) -> str:
    """
    Returns the resolved path for a SQL dump file inside the configured dump directory.
    """
    base_dir = dump_dir or DUMP_DIR
    return os.path.join(base_dir, filename)


def setup_logging(level: str = None, log_file: str = None) -> None:
    """
    Configures standard structured logging for the application with dual handlers:
    - Console output: formatted at the configured LOG_LEVEL (default INFO).
    - File output: saves full log trace (including DEBUG queries) to a log file (default migration.log).
    """
    log_level = level or os.getenv('LOG_LEVEL', 'INFO').upper()
    console_level = getattr(logging, log_level, logging.INFO)
    file_path = log_file or os.getenv('LOG_FILE', 'migration.log')

    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(console_level)

    handlers: list[logging.Handler] = [console_handler]

    if file_path:
        file_handler = logging.FileHandler(file_path, mode='w', encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        handlers.append(file_handler)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.handlers = handlers


T = TypeVar('T')


def env_default(env_var: str, default: T, converter: Callable[[str], T] = str) -> Callable[[], T]:
    """
    Builds a default_factory that reads an environment variable at instantiation time
    (instead of at module import), so late changes to os.environ are picked up and
    conversion errors surface where the config is actually created.
    """
    def factory() -> T:
        return converter(os.getenv(env_var, default))
    return factory


@dataclass(frozen=True)
class FirebirdConfig:
    host: str = field(default_factory=env_default('FIREBIRD_HOST', 'localhost'))
    database: str = field(default_factory=env_default('FIREBIRD_DATABASE', '/firebird/data/sample_database.fdb'))
    user: str = field(default_factory=env_default('FIREBIRD_USER', 'sysdba'))
    password: str = field(default_factory=env_default('FIREBIRD_PASSWORD', 'masterkey'))
    charset: str = field(default_factory=env_default('FIREBIRD_CHARSET', 'WIN1252'))
    port: int = field(default_factory=env_default('FIREBIRD_PORT', 3050, int))


@dataclass(frozen=True)
class PostgresConfig:
    host: str = field(default_factory=env_default('POSTGRES_HOST', 'localhost'))
    port: int = field(default_factory=env_default('POSTGRES_PORT', 5432, int))
    dbname: str = field(default_factory=env_default('POSTGRES_DB', 'sample_database'))
    user: str = field(default_factory=env_default('POSTGRES_USER', 'postgres'))
    password: str = field(default_factory=env_default('POSTGRES_PASSWORD', 'mypassword'))


def get_firebird_connection(config: FirebirdConfig = None):
    """
    Establishes and returns a live connection to the Firebird database.
    """
    cfg = config or FirebirdConfig()
    return firebirdsql.connect(
        host=cfg.host,
        database=cfg.database,
        user=cfg.user,
        password=cfg.password,
        charset=cfg.charset,
        port=cfg.port
    )


def get_postgres_connection(config: PostgresConfig = None):
    """
    Establishes and returns a live connection to the PostgreSQL database.
    """
    cfg = config or PostgresConfig()
    return psycopg2.connect(
        host=cfg.host,
        port=cfg.port,
        dbname=cfg.dbname,
        user=cfg.user,
        password=cfg.password
    )
