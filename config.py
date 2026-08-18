import os
from dataclasses import dataclass
from dotenv import load_dotenv
import firebirdsql
import psycopg2

load_dotenv()


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
