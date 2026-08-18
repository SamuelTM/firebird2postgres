import sys
import logging
from config import get_firebird_connection, get_postgres_connection, get_dump_path, DumpFiles, setup_logging
from engine import DatabaseMigrator

logger = logging.getLogger('main')

if __name__ == '__main__':
    setup_logging()
    logger.info("Connecting to Firebird...")
    fb_connection = get_firebird_connection()

    logger.info("Connecting to PostgreSQL...")
    pg_connection = get_postgres_connection()

    migrator = DatabaseMigrator(fb_connection, pg_connection)

    try:
        # -------------------------------------------------------------
        # STEP 1: Export and transpile all Firebird DDLs
        # -------------------------------------------------------------
        logger.info("[STEP 1/8] Exporting and transpiling DDLs (Domains, Procedures, Views, Triggers)...")
        migrator.export_all_firebird_ddl()

        # -------------------------------------------------------------
        # STEP 2: Teardown - drop existing tables, sequences and domains
        # (tables must go first: DROP DOMAIN CASCADE would otherwise drop
        # the table columns that reference the domains)
        # -------------------------------------------------------------
        logger.info("[STEP 2/8] Dropping existing migrated objects in PostgreSQL...")
        migrator.drop_schema()

        # -------------------------------------------------------------
        # STEP 3: Apply Domains in PostgreSQL
        # -------------------------------------------------------------
        logger.info("[STEP 3/8] Applying Domains in PostgreSQL...")
        migrator.apply_sql_file(get_dump_path(DumpFiles.DOMAINS_PG))

        # -------------------------------------------------------------
        # STEP 4: Create Base Tables and Sequences (without constraints/indexes)
        # -------------------------------------------------------------
        logger.info("[STEP 4/8] Creating base Tables and Sequences in PostgreSQL...")
        migrator.create_tables()

        # -------------------------------------------------------------
        # STEP 5: Migrate Table Data and Synchronize Sequences
        # (Optimal speed: sequential raw inserts without index/FK overhead)
        # -------------------------------------------------------------
        logger.info("[STEP 5/8] Importing table data and synchronizing sequences...")
        data_success = migrator.import_data()
        if not data_success:
            logger.error("Migration halted due to data import errors.")
            sys.exit(1)

        # -------------------------------------------------------------
        # STEP 6: Create Constraints (PK, UK, FK) and Secondary Indexes
        # (Built in parallel sort / single pass after data load)
        # -------------------------------------------------------------
        logger.info("[STEP 6/8] Creating Constraints (PK, UK, FK) and Indexes in PostgreSQL...")
        migrator.create_constraints_and_indexes()

        # -------------------------------------------------------------
        # STEP 7: Apply Procedures and Views in PostgreSQL
        # -------------------------------------------------------------
        logger.info("[STEP 7/8] Applying Procedures and Views in PostgreSQL...")
        migrator.apply_sql_file(get_dump_path(DumpFiles.PROCEDURES_PG))
        migrator.apply_sql_file(get_dump_path(DumpFiles.VIEWS_PG))

        # -------------------------------------------------------------
        # STEP 8: Apply Triggers in PostgreSQL
        # -------------------------------------------------------------
        logger.info("[STEP 8/8] Applying Triggers in PostgreSQL...")
        migrator.apply_sql_file(get_dump_path(DumpFiles.TRIGGERS_PG))

        logger.info("Firebird to PostgreSQL migration completed successfully!")

    finally:
        fb_connection.close()
        pg_connection.close()
