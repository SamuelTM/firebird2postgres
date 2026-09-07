import io
import logging
from concurrent.futures import ProcessPoolExecutor, as_completed, Executor
import firebirdsql
import psycopg2
import psycopg2.extras
from config import get_firebird_connection, get_postgres_connection
from models import Table, pg_quote_ident

logger = logging.getLogger(__name__)


def _import_single_table(table: Table, fb_cur, pg_cur, pg_con) -> int:
    """
    Imports data for a single table:
    1. Truncates table in PostgreSQL (no CASCADE)
    2. Queries Firebird and fetches rows in adaptive batches
    3. Streams rows into PostgreSQL using native COPY protocol (copy_expert)
    4. Commits table transaction in PostgreSQL
    Returns total rows imported.
    """
    logger.info(f"Importing data for '{table.name}'...")

    # Clean existing table data (no CASCADE: constraints don't exist at this pipeline stage,
    # and CASCADE would be dangerous with concurrent workers if they did)
    pg_cur.execute(f'TRUNCATE TABLE {pg_quote_ident(table.pg_name)};')

    blob_count = sum(1 for col in table.columns if 'BLOB' in col.column_type)
    batch_size = 10000
    if blob_count > 0:
        batch_size = max(1000, 10000 // (blob_count * 2))
        logger.debug(f"Found {blob_count} BLOB column(s) in '{table.name}'. Adjusted batch size to {batch_size}.")

    # Explicitly list columns to ensure it perfectly matches the postgres insert order.
    # Exclude computed (GENERATED ALWAYS) columns, as PostgreSQL forbids inserting into them directly.
    # Firebird-side keeps the original casing (quoted identifiers are case-sensitive there);
    # PostgreSQL-side uses the lowercase identifier.
    cols_to_import = [col for col in table.columns if not col.computed_source]
    fb_column_names = [pg_quote_ident(col.name) for col in cols_to_import]
    fb_columns_str = ", ".join(fb_column_names)

    pg_column_names = [pg_quote_ident(col.pg_name) for col in cols_to_import]
    pg_columns_str = ", ".join(pg_column_names)

    fb_cur.execute(f'SELECT {fb_columns_str} FROM {pg_quote_ident(table.name)}')
    copy_sql = f'COPY {pg_quote_ident(table.pg_name)} ({pg_columns_str}) FROM STDIN WITH (FORMAT text, NULL \'\\N\')'

    total_rows = 0
    while True:
        rows = fb_cur.fetchmany(batch_size)
        if not rows:
            break

        buf = io.StringIO()
        for row in rows:
            line = []
            for val in row:
                if val is None:
                    line.append(r'\N')
                elif isinstance(val, bytes):
                    line.append(r'\\x' + val.hex())
                elif isinstance(val, str):
                    line.append(val.replace('\x00', '').replace('\\', '\\\\')
                                   .replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t'))
                elif isinstance(val, bool):
                    line.append('t' if val else 'f')
                else:
                    line.append(str(val))
            buf.write('\t'.join(line) + '\n')

        buf.seek(0)
        pg_cur.copy_expert(copy_sql, buf)
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

    def _re_enable_triggers(self, table_objs: list[Table]):
        """
        Re-enables all triggers disabled for the data load. Executed from a finally block:
        an unexpected failure (e.g. a broken worker pool) must never leave the database
        with all triggers disabled. Errors are logged instead of raised so they do not
        mask the original exception.
        """
        pg_cur = self.pg_con.cursor()
        logger.info("Re-enabling triggers in PostgreSQL...")
        try:
            # Clear a possibly aborted transaction left over from a failure, otherwise
            # the ALTER TABLE statements below would fail with InFailedSqlTransaction
            self.pg_con.rollback()
            for table in table_objs:
                pg_cur.execute(f'ALTER TABLE {pg_quote_ident(table.pg_name)} ENABLE TRIGGER ALL;')
            self.pg_con.commit()
        except psycopg2.Error as e:
            logger.error(f"Failed to re-enable triggers: {e}. "
                         f"Re-enable them manually with ALTER TABLE ... ENABLE TRIGGER ALL.")
            raise

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
            pg_cur.execute(f'ALTER TABLE {pg_quote_ident(table.pg_name)} DISABLE TRIGGER ALL;')
        self.pg_con.commit()

        # Everything between DISABLE and the finally block is guarded: triggers are always
        # re-enabled, even when an unexpected exception escapes the import
        try:
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

            logger.info("Synchronizing sequences...")
            seq_to_targets: dict[str, list[tuple[str, str]]] = {}
            for table in table_objs:
                for col in table.columns:
                    if col.sequence_name:
                        seq_to_targets.setdefault(col.sequence_name, []).append((table.pg_name, col.pg_name))

            for seq_name, targets in seq_to_targets.items():
                max_selects = ", ".join(f'(SELECT MAX({pg_quote_ident(col)}) FROM {pg_quote_ident(tbl)})' for tbl, col in targets)
                greatest_expr = f'GREATEST({max_selects})' if len(targets) > 1 else max_selects
                quoted_seq = pg_quote_ident(seq_name)
                setval_arg = quoted_seq.replace("'", "''")
                sync_query = f"""
                    WITH max_calc AS MATERIALIZED (
                        SELECT {greatest_expr} AS max_val
                    )
                    SELECT setval(
                        '{setval_arg}',
                        GREATEST(s.last_value, m.max_val),
                        s.is_called OR (m.max_val IS NOT NULL AND m.max_val >= s.last_value)
                    )
                    FROM {quoted_seq} s, max_calc m;
                """
                logger.debug(sync_query.strip())
                pg_cur.execute(sync_query)
            self.pg_con.commit()
        finally:
            self._re_enable_triggers(table_objs)

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

