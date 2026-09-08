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
        logger.info("[STEP 1/9] Exporting and transpiling DDLs (Domains, Procedures, Views, Triggers)...")
        migrator.export_all_firebird_ddl()

        # -------------------------------------------------------------
        # Pre-flight Validation: Distinguish legitimately empty categories
        # from missing or incomplete exports BEFORE destructive DROP
        # -------------------------------------------------------------
        logger.info("Validating exported DDL artifacts before dropping target schema...")
        verified_empty = migrator.validate_artifacts()

        # -------------------------------------------------------------
        # STEP 2: Teardown - drop existing tables, sequences and domains
        # (tables must go first: DROP DOMAIN CASCADE would otherwise drop
        # the table columns that reference the domains)
        # -------------------------------------------------------------
        logger.info("[STEP 2/9] Dropping existing migrated objects in PostgreSQL...")
        migrator.drop_schema()

        # -------------------------------------------------------------
        # STEP 3: Apply Domains in PostgreSQL
        # -------------------------------------------------------------
        logger.info("[STEP 3/9] Applying Domains in PostgreSQL...")
        migrator.apply_sql_file(
            get_dump_path(DumpFiles.DOMAINS_PG),
            allow_empty=verified_empty.get(DumpFiles.DOMAINS_PG, False)
        )

        # -------------------------------------------------------------
        # STEP 4: Create Base Tables and Sequences (without constraints/indexes)
        # -------------------------------------------------------------
        logger.info("[STEP 4/9] Creating base Tables and Sequences in PostgreSQL...")
        migrator.create_tables()

        # -------------------------------------------------------------
        # STEP 5: Migrate Table Data and Synchronize Sequences
        # (Optimal speed: sequential raw inserts without index/FK overhead)
        # -------------------------------------------------------------
        logger.info("[STEP 5/9] Importing table data and synchronizing sequences...")
        data_success = migrator.import_data()
        if not data_success:
            logger.error("Migration halted due to data import errors.")
            sys.exit(1)

        # -------------------------------------------------------------
        # STEP 6: Create Constraints (PK, UK, FK) and Secondary Indexes
        # (Built in parallel sort / single pass after data load)
        # -------------------------------------------------------------
        logger.info("[STEP 6/9] Creating Constraints (PK, UK, FK) and Indexes in PostgreSQL...")
        migrator.create_constraints_and_indexes()

        # -------------------------------------------------------------
        # STEP 7: Apply Procedures and Views in PostgreSQL
        # -------------------------------------------------------------
        logger.info("[STEP 7/9] Applying Procedures and Views in PostgreSQL...")
        migrator.apply_sql_file(
            get_dump_path(DumpFiles.PROCEDURES_PG),
            allow_empty=verified_empty.get(DumpFiles.PROCEDURES_PG, False)
        )
        migrator.apply_sql_file(
            get_dump_path(DumpFiles.VIEWS_PG),
            allow_empty=verified_empty.get(DumpFiles.VIEWS_PG, False)
        )

        # -------------------------------------------------------------
        # STEP 8: Apply Triggers in PostgreSQL
        # -------------------------------------------------------------
        logger.info("[STEP 8/9] Applying Triggers in PostgreSQL...")
        migrator.apply_sql_file(
            get_dump_path(DumpFiles.TRIGGERS_PG),
            allow_empty=verified_empty.get(DumpFiles.TRIGGERS_PG, False)
        )

        # -------------------------------------------------------------
        # STEP 9: Update Optimizer Statistics (ANALYZE)
        # (Ensures query planner has up-to-date distribution and row statistics)
        # -------------------------------------------------------------
        logger.info("[STEP 9/9] Updating PostgreSQL optimizer statistics (ANALYZE)...")
        migrator.analyze_tables()

        logger.info("Firebird to PostgreSQL migration completed successfully!")

    finally:
        fb_connection.close()
        pg_connection.close()
