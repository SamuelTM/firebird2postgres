import logging
import psycopg2.extras
from models import Table

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

        logger.info("Configuring PostgreSQL session for high-throughput bulk import...")
        pg_cur.execute("SET synchronous_commit = OFF;")

        failed_tables: list[tuple[str, str]] = []
        successful_tables = 0
        total_rows_imported = 0

        try:
            logger.info("Disabling triggers and clearing existing table data for a clean import...")
            for table in table_objs:
                pg_cur.execute(f'ALTER TABLE "{table.name.lower()}" DISABLE TRIGGER ALL;')
                pg_cur.execute(f'TRUNCATE TABLE "{table.name.lower()}" CASCADE;')
            self.pg_con.commit()

            for table in table_objs:
                logger.info(f"Importing data for '{table.name}'...")

                try:
                    blob_count = sum(1 for col in table.columns if 'BLOB' in col.column_type)
                    batch_size = 10000
                    if blob_count > 0:
                        batch_size = max(500, 10000 // (blob_count * 5))
                        logger.debug(f"Found {blob_count} BLOB column(s) in '{table.name}'. Adjusted batch size to "
                                     f"{batch_size}.")

                    # Explicitly list columns to ensure it perfectly matches the postgres insert order
                    fb_column_names = [f'"{col.name}"' for col in table.columns]
                    fb_columns_str = ", ".join(fb_column_names)

                    pg_column_names = [f'"{col.name.lower()}"' for col in table.columns]
                    pg_columns_str = ", ".join(pg_column_names)

                    fb_cur.execute(f'SELECT {fb_columns_str} FROM "{table.name}"')

                    insert_query = f'INSERT INTO "{table.name.lower()}" ({pg_columns_str}) VALUES %s'

                    # Identify column indices that can contain text/strings to avoid unnecessary checks on numeric/date columns
                    # Note: 'BLOB SUBTYPE 1' maps to TEXT (strings), while 'BLOB SUBTYPE 0' maps to BYTEA (binary)
                    str_col_indices = [
                        i for i, col in enumerate(table.columns)
                        if any(t in col.column_type.upper() for t in ('VARCHAR', 'CHAR', 'TEXT', 'BLOB SUBTYPE 1', 'CSTRING'))
                        or col.domain_name
                    ]

                    total_rows = 0
                    while True:
                        rows = fb_cur.fetchmany(batch_size)
                        if not rows:
                            break

                        # Sanitize strings only if table contains text/domain columns and a NUL byte is found
                        if not str_col_indices:
                            sanitized_rows = rows
                        else:
                            sanitized_rows = []
                            for row in rows:
                                has_nul = False
                                for idx in str_col_indices:
                                    val = row[idx]
                                    if isinstance(val, str) and '\x00' in val:
                                        has_nul = True
                                        break
                                if has_nul:
                                    row_list = list(row)
                                    for idx in str_col_indices:
                                        val = row_list[idx]
                                        if isinstance(val, str) and '\x00' in val:
                                            row_list[idx] = val.replace('\x00', '')
                                    sanitized_rows.append(tuple(row_list))
                                else:
                                    sanitized_rows.append(row)

                        psycopg2.extras.execute_values(pg_cur, insert_query, sanitized_rows, page_size=batch_size)
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
                pg_cur.execute(f'ALTER TABLE "{table.name.lower()}" ENABLE TRIGGER ALL;')
            self.pg_con.commit()

            logger.info("Synchronizing sequences...")
            for table in table_objs:
                for col in table.columns:
                    if col.sequence_name:
                        sync_query = f"""
                            SELECT setval('"{col.sequence_name.lower()}"', COALESCE(MAX("{col.name.lower()}"), 1))
                            FROM "{table.name.lower()}";
                        """
                        logger.debug(sync_query.strip())
                        pg_cur.execute(sync_query)
            self.pg_con.commit()

        finally:
            try:
                pg_cur.execute("RESET synchronous_commit;")
                self.pg_con.commit()
            except Exception:
                pass

        if failed_tables:
            logger.error("=" * 80)
            logger.error(
                f"DATA MIGRATION FAILED: {len(failed_tables)} of {len(table_objs)} table(s) encountered errors:")
            for tbl_name, err in failed_tables:
                logger.error(f"  Table '{tbl_name}': {err}")
            logger.error("=" * 80)
            return False

        logger.info(
            f"Data migration completed successfully! Total {total_rows_imported} rows across "
            f"{successful_tables} tables."
        )
        return True
