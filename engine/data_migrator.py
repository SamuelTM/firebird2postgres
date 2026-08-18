import logging
from concurrent.futures import ProcessPoolExecutor, as_completed, Executor
import firebirdsql
import psycopg2
import psycopg2.extras
from config import get_firebird_connection, get_postgres_connection
from models import Table

logger = logging.getLogger(__name__)


def _import_single_table(table: Table, fb_cur, pg_cur, pg_con) -> int:
    """
    Imports data for a single table:
    1. Truncates table in PostgreSQL (no CASCADE)
    2. Queries Firebird and fetches rows in adaptive batches
    3. Sanitizes strings only when text columns exist and NUL bytes are detected
    4. Inserts into PostgreSQL via execute_values with page_size=batch_size
    5. Commits table transaction in PostgreSQL
    Returns total rows imported.
    """
    logger.info(f"Importing data for '{table.name}'...")

    # Clean existing table data (no CASCADE: constraints don't exist at this pipeline stage,
    # and CASCADE would be dangerous with concurrent workers if they did)
    pg_cur.execute(f'TRUNCATE TABLE "{table.name.lower()}";')

    blob_count = sum(1 for col in table.columns if 'BLOB' in col.column_type)
    batch_size = 10000
    if blob_count > 0:
        batch_size = max(1000, 10000 // (blob_count * 2))
        logger.debug(f"Found {blob_count} BLOB column(s) in '{table.name}'. Adjusted batch size to {batch_size}.")

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

    pg_con.commit()
    logger.info(f"  -> Successfully imported {total_rows} rows for '{table.name}'.")
    return total_rows


def _migrate_table_worker(table: Table) -> tuple[str, int, str | None]:
    """
    Top-level worker function for ProcessPoolExecutor: establishes isolated database
    connections in the worker process, sets session performance tuning, and imports the table.
    """
    fb_con = get_firebird_connection()
    pg_con = get_postgres_connection()
    try:
        pg_cur = pg_con.cursor()
        pg_cur.execute("SET synchronous_commit = OFF;")
        fb_cur = fb_con.cursor()

        rows_imported = _import_single_table(table, fb_cur, pg_cur, pg_con)
        return table.name, rows_imported, None
    except (psycopg2.Error, firebirdsql.Error, OSError, ValueError, TypeError) as e:
        try:
            pg_con.rollback()
        except (psycopg2.Error, OSError):
            pass
        logger.error(f"Failed to import table '{table.name}': {e}", exc_info=True)
        return table.name, 0, str(e)
    finally:
        try:
            fb_con.close()
        except (firebirdsql.Error, OSError):
            pass
        try:
            pg_con.close()
        except (psycopg2.Error, OSError):
            pass


class DataMigrator:
    """
    Handles streaming data from Firebird and bulk-inserting into PostgreSQL
    with string sanitization, adaptive batching, trigger toggling, sequence synchronization,
    multi-process parallel worker execution, and comprehensive failure tracking.
    """

    def __init__(self, fb_con, pg_con):
        self.fb_con = fb_con
        self.pg_con = pg_con

    def import_data(self, table_objs: list[Table], max_workers: int = 4, executor: Executor = None) -> bool:
        """
        Reads data from Firebird and bulk inserts into PostgreSQL using a multi-process worker pool.
        Tables are prioritized by complexity (LPT scheduling) so heavy BLOB tables run concurrently.
        Returns True if all tables were imported successfully, False if any table failed.
        """
        logger.info(f"Starting data migration for {len(table_objs)} tables (workers={max_workers})...")
        pg_cur = self.pg_con.cursor()

        logger.info("Disabling triggers in PostgreSQL for a clean import...")
        for table in table_objs:
            pg_cur.execute(f'ALTER TABLE "{table.name.lower()}" DISABLE TRIGGER ALL;')
        self.pg_con.commit()

        # Sort tables by estimated workload (LPT: Longest Processing Time first)
        # Tables with BLOBs and higher column count are scheduled first
        sorted_tables = sorted(
            table_objs,
            key=lambda t: (sum(1 for c in t.columns if 'BLOB' in c.column_type), len(t.columns)),
            reverse=True
        )

        results: list[tuple[str, int, str | None]] = []

        if max_workers <= 1 or len(sorted_tables) <= 1:
            # Sequential execution using caller connections
            logger.info("Executing sequential table import...")
            pg_cur.execute("SET synchronous_commit = OFF;")
            fb_cur = self.fb_con.cursor()
            try:
                for table in sorted_tables:
                    try:
                        rows_imported = _import_single_table(table, fb_cur, pg_cur, self.pg_con)
                        results.append((table.name, rows_imported, None))
                    except (psycopg2.Error, firebirdsql.Error, OSError, ValueError, TypeError) as e:
                        self.pg_con.rollback()
                        logger.error(f"Failed to import table '{table.name}': {e}", exc_info=True)
                        results.append((table.name, 0, str(e)))
            finally:
                try:
                    pg_cur.execute("RESET synchronous_commit;")
                    self.pg_con.commit()
                except (psycopg2.Error, OSError):
                    pass
        else:
            # Parallel execution with multi-process pool
            logger.info(f"Spawning {max_workers} worker processes for concurrent table migration...")
            owns_executor = executor is None
            if owns_executor:
                executor = ProcessPoolExecutor(max_workers=max_workers)

            try:
                futures = {executor.submit(_migrate_table_worker, table): table for table in sorted_tables}
                for future in as_completed(futures):
                    tbl_name, rows_imported, err = future.result()
                    results.append((tbl_name, rows_imported, err))
            finally:
                if owns_executor:
                    executor.shutdown()

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

        failed_tables = [(tbl, err) for tbl, _, err in results if err is not None]
        successful_tables = sum(1 for _, _, err in results if err is None)
        total_rows_imported = sum(rows for _, rows, err in results if err is None)

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

