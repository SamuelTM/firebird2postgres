import os
import logging
from dataclasses import dataclass
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
        file_handler = logging.FileHandler(file_path, mode='a', encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        handlers.append(file_handler)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.handlers = handlers


@dataclass(frozen=True)
class FirebirdConfig:
    host: str = os.getenv('FIREBIRD_HOST', 'localhost')
    database: str = os.getenv('FIREBIRD_DATABASE', '/firebird/data/sample_database.fdb')
    user: str = os.getenv('FIREBIRD_USER', 'sysdba')
    password: str = os.getenv('FIREBIRD_PASSWORD', 'masterkey')
    charset: str = os.getenv('FIREBIRD_CHARSET', 'WIN1252')
    port: int = int(os.getenv('FIREBIRD_PORT', '3050'))


@dataclass(frozen=True)
class PostgresConfig:
    host: str = os.getenv('POSTGRES_HOST', 'localhost')
    port: int = int(os.getenv('POSTGRES_PORT', '5432'))
    dbname: str = os.getenv('POSTGRES_DB', 'sample_database')
    user: str = os.getenv('POSTGRES_USER', 'postgres')
    password: str = os.getenv('POSTGRES_PASSWORD', 'mypassword')


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
