import logging
import psycopg2.extras
from database_objects import Table

logger = logging.getLogger(__name__)


class DataMigrator:
    """
    Handles streaming data from Firebird and bulk-inserting into PostgreSQL
    with string sanitization, adaptive batching, trigger toggling, sequence synchronization,
    and comprehensive failure tracking.
    """

    def __init__(self, fb_con, pg_con):
        self.fb_con = fb_con
        self.pg_con = pg_con

    def import_data(self, table_objs: list[Table]) -> bool:
        """
        Reads data from Firebird and bulk inserts into PostgreSQL.
        Returns True if all tables were imported successfully, False if any table failed.
        """
        logger.info(f"Starting data migration for {len(table_objs)} tables...")
        fb_cur = self.fb_con.cursor()
        pg_cur = self.pg_con.cursor()

        logger.info("Disabling triggers and clearing existing table data for a clean import...")
        for table in table_objs:
            pg_cur.execute(f'ALTER TABLE "{table.name}" DISABLE TRIGGER ALL;')
            pg_cur.execute(f'TRUNCATE TABLE "{table.name}" CASCADE;')
        self.pg_con.commit()

        failed_tables: list[tuple[str, str]] = []
        successful_tables = 0
        total_rows_imported = 0

        for table in table_objs:
            logger.info(f"Importing data for '{table.name}'...")

            try:
                blob_count = sum(1 for col in table.columns if 'BLOB' in col.column_type)
                batch_size = 10000
                if blob_count > 0:
                    batch_size = max(500, 10000 // (blob_count * 5))
                    logger.debug(f"Found {blob_count} BLOB column(s) in '{table.name}'. Adjusted batch size to {batch_size}.")

                # Explicitly list columns to ensure it perfectly matches the postgres insert order
                fb_column_names = [f'"{col.name}"' for col in table.columns]
                fb_columns_str = ", ".join(fb_column_names)

                fb_cur.execute(f'SELECT {fb_columns_str} FROM "{table.name}"')

                insert_query = f'INSERT INTO "{table.name}" ({fb_columns_str}) VALUES %s'

                total_rows = 0
                while True:
                    rows = fb_cur.fetchmany(batch_size)
                    if not rows:
                        break

                    # Sanitize strings because postgres does not allow NUL (\x00) bytes in TEXT/VARCHAR
                    sanitized_rows = []
                    for row in rows:
                        sanitized_row = []
                        for val in row:
                            if isinstance(val, str):
                                sanitized_row.append(val.replace('\x00', ''))
                            else:
                                sanitized_row.append(val)
                        sanitized_rows.append(tuple(sanitized_row))

                    psycopg2.extras.execute_values(pg_cur, insert_query, sanitized_rows)
                    total_rows += len(rows)

                self.pg_con.commit()
                successful_tables += 1
                total_rows_imported += total_rows
                logger.info(f"  -> Successfully imported {total_rows} rows for '{table.name}'.")

            except Exception as e:
                self.pg_con.rollback()
                logger.error(f"Failed to import table '{table.name}': {e}", exc_info=True)
                failed_tables.append((table.name, str(e)))

        logger.info("Re-enabling triggers in PostgreSQL...")
        for table in table_objs:
            pg_cur.execute(f'ALTER TABLE "{table.name}" ENABLE TRIGGER ALL;')
        self.pg_con.commit()

        logger.info("Synchronizing sequences...")
        for table in table_objs:
            for col in table.columns:
                if col.sequence_name:
                    sync_query = f"""
                        SELECT setval('"{col.sequence_name}"', COALESCE(MAX("{col.name}"), 1))
                        FROM "{table.name}";
                    """
                    logger.debug(sync_query.strip())
                    pg_cur.execute(sync_query)
        self.pg_con.commit()

        if failed_tables:
            logger.error("=" * 80)
            logger.error(f"DATA MIGRATION FAILED: {len(failed_tables)} of {len(table_objs)} table(s) encountered errors:")
            for tbl_name, err in failed_tables:
                logger.error(f"  Table '{tbl_name}': {err}")
            logger.error("=" * 80)
            return False

        logger.info(
            f"Data migration completed successfully! Total {total_rows_imported} rows across {successful_tables} tables."
        )
        return True
