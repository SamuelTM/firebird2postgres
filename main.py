import os
import firebirdsql
import psycopg2
from dotenv import load_dotenv

from database_migrator import DatabaseMigrator

load_dotenv()

if __name__ == '__main__':
    print('Connecting to Firebird...')
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

    # -------------------------------------------------------------
    # STEP 1: Export and transpile all Firebird DDLs
    # -------------------------------------------------------------
    print("\n[STEP 1/7] Exporting and transpiling DDLs (Domains, Procedures, Views, Triggers)...")
    migrator.export_all_firebird_ddl()

    # -------------------------------------------------------------
    # STEP 2: Teardown - drop existing tables, sequences and domains
    # (tables must go first: DROP DOMAIN CASCADE would otherwise drop
    # the table columns that reference the domains)
    # -------------------------------------------------------------
    print("\n[STEP 2/7] Dropping existing migrated objects in PostgreSQL...")
    migrator.drop_schema()

    # -------------------------------------------------------------
    # STEP 3: Apply Domains in PostgreSQL
    # -------------------------------------------------------------
    print("\n[STEP 3/7] Applying Domains in PostgreSQL...")
    migrator.apply_sql_file('postgres_domains_dump.sql')

    # -------------------------------------------------------------
    # STEP 4: Create Tables, Sequences, Foreign and Primary Keys schema
    # -------------------------------------------------------------
    print("\n[STEP 4/7] Creating Tables, Sequences, Foreign and Primary Keys schema in PostgreSQL...")
    migrator.migrate_schema(print_queries=False)

    # -------------------------------------------------------------
    # STEP 5: Migrate Table Data and Synchronize Sequences
    # -------------------------------------------------------------
    print("\n[STEP 5/7] Importing table data and synchronizing sequences...")
    migrator.import_data()

    # -------------------------------------------------------------
    # STEP 6: Apply Procedures and Views in PostgreSQL
    # -------------------------------------------------------------
    print("\n[STEP 6/7] Applying Procedures and Views in PostgreSQL...")
    migrator.apply_sql_file('postgres_procedures_dump.sql')
    migrator.apply_sql_file('postgres_views_dump.sql')

    # -------------------------------------------------------------
    # STEP 7: Apply Triggers in PostgreSQL
    # -------------------------------------------------------------
    print("\n[STEP 7/7] Applying Triggers in PostgreSQL...")
    migrator.apply_sql_file('postgres_triggers_dump.sql')

    print("\nFirebird to PostgreSQL migration completed successfully!")

    fb_connection.close()
    pg_connection.close()
