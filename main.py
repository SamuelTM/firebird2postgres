import os
import firebirdsql
import psycopg2
from dotenv import load_dotenv

from database_migrator import DatabaseMigrator

load_dotenv()

if __name__ == '__main__':
    fb_connection = firebirdsql.connect(
        host=os.getenv('FIREBIRD_HOST', 'localhost'),
        database=os.getenv('FIREBIRD_DATABASE', '/firebird/data/sample_database.fdb'),
        user=os.getenv('FIREBIRD_USER', 'sysdba'),
        password=os.getenv('FIREBIRD_PASSWORD', 'masterkey'),
        charset='WIN1252'
    )

    print('Connecting to PostgreSQL...')
    pg_connection = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=int(os.getenv('POSTGRES_PORT', 5432)),
        dbname=os.getenv('POSTGRES_DB', 'sample_database'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', 'mypassword')
    )

    migrator = DatabaseMigrator(fb_connection, pg_connection)

    migrator.migrate_schema(print_queries=True)

    migrator.import_data()

    migrator.export_firebird_domains()
    migrator.export_firebird_triggers()
    migrator.export_firebird_procedures()
    migrator.export_firebird_views()

    fb_connection.close()
    pg_connection.close()
