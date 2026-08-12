import firebirdsql
import psycopg2

from database_migrator import DatabaseMigrator

if __name__ == '__main__':
    fb_connection = firebirdsql.connect(
        host='localhost',
        database='/firebird/data/sample_database.fdb',
        user='sysdba',
        password='masterkey',
        charset='WIN1252'
    )

    print('Connecting to PostgreSQL...')
    pg_connection = psycopg2.connect(
        host='localhost',
        dbname='sample_database',
        user='postgres',
        password='mypassword'
    )

    migrator = DatabaseMigrator(fb_connection, pg_connection)

    migrator.migrate_schema(print_queries=True)

    migrator.import_data()

    migrator.export_firebird_triggers()
    migrator.export_firebird_procedures()
    migrator.export_firebird_views()

    fb_connection.close()
    pg_connection.close()
