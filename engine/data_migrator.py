import io
import os
import logging
from concurrent.futures import ProcessPoolExecutor, as_completed, Executor
import firebirdsql
import psycopg2
import psycopg2.extras
from config import get_firebird_connection, get_postgres_connection
from models import Table, pg_quote_ident

logger = logging.getLogger(__name__)


DEFAULT_MAX_BUFFER_BYTES = 32 * 1024 * 1024  # 32 MB buffer budget per worker


def _import_single_table(table: Table, fb_cur, pg_cur, pg_con, max_buffer_bytes: int = DEFAULT_MAX_BUFFER_BYTES) -> tuple[int, dict[str, int]]:
    """
    Imports data for a single table:
    1. Truncates table in PostgreSQL (no CASCADE)
    2. Queries Firebird and fetches rows in adaptive slices
    3. Streams rows into PostgreSQL using native COPY protocol (copy_expert),
       flushing incrementally whenever memory volume reaches max_buffer_bytes
    4. Commits table transaction in PostgreSQL

    Data transformation policy:
    PostgreSQL text/varchar rejects 0x00 (NUL) bytes. Strings containing NUL bytes
    have them stripped during serialization; all occurrences are counted per table/column
    and returned in nul_stats for auditing and diagnostics.

    Returns (total_rows, nul_stats).
    """
    logger.info(f"Importing data for '{table.name}'...")

    # Clean existing table data (no CASCADE: constraints don't exist at this pipeline stage,
    # and CASCADE would be dangerous with concurrent workers if they did)
    pg_cur.execute(f'TRUNCATE TABLE {pg_quote_ident(table.pg_name)};')

    blob_count = sum(1 for col in table.columns if 'BLOB' in col.column_type)
    # Tables with BLOBs fetch in smaller row slices (100 rows) to prevent the Firebird client
    # and Python runtime from buffering gigabytes of binary data before serialization
    fetch_size = 100 if blob_count > 0 else 10000
    if blob_count > 0:
        logger.debug(f"Found {blob_count} BLOB column(s) in '{table.name}'. Adjusted fetch slice to {fetch_size} rows with {max_buffer_bytes // (1024 * 1024)}MB memory buffer budget.")

    # Explicitly list columns to ensure it perfectly matches the postgres insert order.
    # Exclude computed (GENERATED ALWAYS) columns, as PostgreSQL forbids inserting into them directly.
    # Firebird-side keeps the original casing (quoted identifiers are case-sensitive there);
    # PostgreSQL-side uses the lowercase identifier.
    cols_to_import = [col for col in table.columns if not col.computed_source]
    col_names = [col.name for col in cols_to_import]
    fb_column_names = [pg_quote_ident(col.name) for col in cols_to_import]
    fb_columns_str = ", ".join(fb_column_names)

    pg_column_names = [pg_quote_ident(col.pg_name) for col in cols_to_import]
    pg_columns_str = ", ".join(pg_column_names)

    fb_cur.execute(f'SELECT {fb_columns_str} FROM {pg_quote_ident(table.name)}')
    copy_sql = f'COPY {pg_quote_ident(table.pg_name)} ({pg_columns_str}) FROM STDIN WITH (FORMAT text, NULL \'\\N\')'

    total_rows = 0
    nul_stats: dict[str, int] = {}
    buf = io.StringIO()

    while True:
        rows = fb_cur.fetchmany(fetch_size)
        if not rows:
            break

        for row in rows:
            line = []
            for col_idx, val in enumerate(row):
                if val is None:
                    line.append(r'\N')
                elif isinstance(val, bytes):
                    line.append(r'\\x' + val.hex())
                elif isinstance(val, str):
                    if '\x00' in val:
                        col_name = col_names[col_idx]
                        nul_stats[col_name] = nul_stats.get(col_name, 0) + val.count('\x00')
                        val = val.replace('\x00', '')
                    line.append(val.replace('\\', '\\\\')
                                   .replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t'))
                elif isinstance(val, bool):
                    line.append('t' if val else 'f')
                else:
                    line.append(str(val))
            buf.write('\t'.join(line) + '\n')

            # Flush buffer incrementally via COPY as soon as accumulated text volume exceeds memory budget
            if buf.tell() >= max_buffer_bytes:
                buf.seek(0)
                pg_cur.copy_expert(copy_sql, buf)
                buf = io.StringIO()

        total_rows += len(rows)

    # Flush any remaining rows in buffer
    if buf.tell() > 0:
        buf.seek(0)
        pg_cur.copy_expert(copy_sql, buf)

    pg_con.commit()
    if nul_stats:
        logger.warning(f"  -> Table '{table.name}': stripped NUL (0x00) bytes from columns: {nul_stats}")
    logger.info(f"  -> Successfully imported {total_rows} rows for '{table.name}'.")
    return total_rows, nul_stats


def _migrate_table_worker(table: Table) -> tuple[str, int, str | None, dict[str, int]]:
    """
    Top-level worker function for ProcessPoolExecutor: establishes isolated database
    connections in the worker process, sets session performance tuning, and imports the table.
    Returns (table_name, rows_imported, error_message, nul_stats).
    """
    fb_con = get_firebird_connection()
    pg_con = get_postgres_connection()
    try:
        pg_cur = pg_con.cursor()
        pg_cur.execute("SET synchronous_commit = OFF;")
        fb_cur = fb_con.cursor()

        rows_imported, nul_stats = _import_single_table(table, fb_cur, pg_cur, pg_con)
        return table.name, rows_imported, None, nul_stats
    except (psycopg2.Error, firebirdsql.Error, OSError, ValueError, TypeError) as e:
        try:
            pg_con.rollback()
        except (psycopg2.Error, OSError):
            pass
        logger.error(f"Failed to import table '{table.name}': {e}", exc_info=True)
        return table.name, 0, str(e), {}
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
        self.last_nul_stats: dict[str, dict[str, int]] = {}

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

    def check_source_consistency(self, require_frozen: bool = False, allow_live_source: bool = False) -> dict:
        """
        Checks whether the source Firebird database is frozen (read-only or shutdown)
        or has active concurrent client attachments that could compromise snapshot
        consistency across parallel workers.
        Captures and reports catalog query errors instead of silently ignoring them.
        When require_frozen is True, raises RuntimeError if the source is not proven frozen.
        """
        info = {
            'is_read_only': False,
            'is_shutdown': False,
            'active_attachments': 0,
            'verified': False,
            'error': None
        }
        try:
            cur = self.fb_con.cursor()
            try:
                cur.execute("SELECT MON$READ_ONLY, MON$SHUTDOWN_MODE FROM MON$DATABASE;")
                row = cur.fetchone()
                if row:
                    info['is_read_only'] = bool(row[0])
                    info['is_shutdown'] = (row[1] is not None and row[1] > 0)
                info['verified'] = True
            except Exception as e:
                info['error'] = f"Failed to check MON$DATABASE: {e}"
                logger.warning(f"Could not check source database frozen state: {e}")

            try:
                cur.execute("SELECT COUNT(*) FROM MON$ATTACHMENTS WHERE MON$ATTACHMENT_ID <> CURRENT_CONNECTION AND (MON$SYSTEM_FLAG = 0 OR MON$SYSTEM_FLAG IS NULL);")
                row = cur.fetchone()
                if row and row[0] is not None:
                    info['active_attachments'] = int(row[0])
            except Exception as e:
                err_msg = f"Failed to check MON$ATTACHMENTS: {e}"
                info['error'] = f"{info['error']}; {err_msg}" if info['error'] else err_msg
                logger.warning(f"Could not check source database attachments: {e}")
        except Exception as e:
            info['error'] = f"Failed to access source catalog: {e}"
            logger.warning(f"Could not verify source consistency: {e}")

        is_frozen = info['is_read_only'] or info['is_shutdown']

        if not is_frozen and not allow_live_source:
            if require_frozen:
                if info['error'] and not info['verified']:
                    raise RuntimeError(
                        f"Cannot verify that source Firebird database is frozen ({info['error']}). "
                        f"Refusing destructive operations without verified static/frozen source. "
                        f"Use allow_live_source=True or set ALLOW_LIVE_SOURCE=true to override."
                    )
                raise RuntimeError(
                    f"Source Firebird database is LIVE (read-write mode with "
                    f"{info['active_attachments']} active attachment(s)). "
                    f"Parallel workers cannot share a single transactional snapshot; "
                    f"concurrent writes during migration may cause relational inconsistencies. "
                    f"Freeze the source database ('gfix -mode read_only') or migrate from a static copy. "
                    f"Use allow_live_source=True or set ALLOW_LIVE_SOURCE=true to override."
                )

        if not is_frozen:
            if info['active_attachments'] > 0:
                logger.warning(
                    f"Source Firebird database is LIVE (read-write) with {info['active_attachments']} active "
                    f"external attachment(s). Parallel table workers cannot share a single transactional snapshot; "
                    f"concurrent writes during migration may cause relational inconsistencies. "
                    f"For guaranteed consistency, freeze the source database ('gfix -mode read_only') or migrate from a backup copy."
                )
            else:
                logger.warning(
                    f"Source Firebird database is in read-write mode. While 0 external attachments were "
                    f"detected at inspection time, new writes may occur during migration. "
                    f"Parallel table workers have independent connections and cannot share a single transaction snapshot. "
                    f"For guaranteed consistency, freeze the source database ('gfix -mode read_only') or migrate from a backup copy."
                )

        return info

    def import_data(
        self,
        table_objs: list[Table],
        max_workers: int = 4,
        executor: Executor = None,
        require_frozen_source: bool = False,
        allow_live_source: bool = False
    ) -> bool:
        """
        Reads data from Firebird and bulk inserts into PostgreSQL using a multi-process worker pool.
        Tables are prioritized by complexity (LPT scheduling) so heavy BLOB tables run concurrently.
        Enforces source database consistency before destructive operations (DISABLE TRIGGER, TRUNCATE).
        Returns True if all tables were imported successfully, False if any table failed.
        """
        env_allow_live = os.getenv('ALLOW_LIVE_SOURCE', 'false').lower() in ('1', 'true', 'yes')
        allow_live = allow_live_source or env_allow_live

        self.check_source_consistency(require_frozen=require_frozen_source, allow_live_source=allow_live)
        self.last_nul_stats = {}
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

            results: list[tuple[str, int, str | None, dict[str, int]]] = []

            if max_workers <= 1 or len(sorted_tables) <= 1:
                # Sequential execution using caller connections
                logger.info("Executing sequential table import...")
                pg_cur.execute("SET synchronous_commit = OFF;")
                fb_cur = self.fb_con.cursor()
                try:
                    for table in sorted_tables:
                        try:
                            rows_imported, nul_stats = _import_single_table(table, fb_cur, pg_cur, self.pg_con)
                            results.append((table.name, rows_imported, None, nul_stats))
                        except (psycopg2.Error, firebirdsql.Error, OSError, ValueError, TypeError) as e:
                            self.pg_con.rollback()
                            logger.error(f"Failed to import table '{table.name}': {e}", exc_info=True)
                            results.append((table.name, 0, str(e), {}))
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
                        tbl_name, rows_imported, err, nul_stats = future.result()
                        results.append((tbl_name, rows_imported, err, nul_stats))
                finally:
                    if owns_executor:
                        executor.shutdown()

            logger.info("Synchronizing sequences...")
            seq_to_targets: dict[str, list[tuple[str, str]]] = {}
            identity_targets: list[tuple[str, str, Column]] = []
            for table in table_objs:
                for col in table.columns:
                    if col.identity_type:
                        identity_targets.append((table.pg_name, col.pg_name, col))
                    elif col.sequence_name:
                        seq_to_targets.setdefault(col.sequence_name, []).append((table.pg_name, col.pg_name))

            for tbl, col, col_obj in identity_targets:
                quoted_tbl = pg_quote_ident(tbl)
                quoted_col = pg_quote_ident(col)
                inc = col_obj.identity_increment if col_obj.identity_increment is not None else 1
                curr = col_obj.identity_current
                if inc < 0:
                    if curr is not None:
                        sync_query = f"""
                            SELECT setval(
                                pg_get_serial_sequence('{quoted_tbl}', '{col}'),
                                LEAST({curr}, COALESCE((SELECT MIN({quoted_col}) FROM {quoted_tbl}), {curr})),
                                true
                            );
                        """
                    else:
                        sync_query = f"""
                            SELECT setval(
                                pg_get_serial_sequence('{quoted_tbl}', '{col}'),
                                COALESCE((SELECT MIN({quoted_col}) FROM {quoted_tbl}), -1),
                                (SELECT MIN({quoted_col}) IS NOT NULL FROM {quoted_tbl})
                            );
                        """
                else:
                    if curr is not None:
                        sync_query = f"""
                            SELECT setval(
                                pg_get_serial_sequence('{quoted_tbl}', '{col}'),
                                GREATEST({curr}, COALESCE((SELECT MAX({quoted_col}) FROM {quoted_tbl}), {curr})),
                                true
                            );
                        """
                    else:
                        sync_query = f"""
                            SELECT setval(
                                pg_get_serial_sequence('{quoted_tbl}', '{col}'),
                                COALESCE((SELECT MAX({quoted_col}) FROM {quoted_tbl}), 1),
                                (SELECT MAX({quoted_col}) IS NOT NULL FROM {quoted_tbl})
                            );
                        """
                logger.debug(sync_query.strip())
                pg_cur.execute(sync_query)

            for seq_name, targets in seq_to_targets.items():
                quoted_seq = pg_quote_ident(seq_name)
                setval_arg = quoted_seq.replace("'", "''")

                # Check sequence direction from PostgreSQL catalog
                try:
                    pg_cur.execute(
                        "SELECT increment_by FROM pg_sequences WHERE schemaname = current_schema() AND sequencename = lower(%s);",
                        (seq_name,)
                    )
                    inc_row = pg_cur.fetchone()
                    seq_inc = int(inc_row[0]) if inc_row and inc_row[0] is not None else 1
                except Exception:
                    seq_inc = 1

                if seq_inc < 0:
                    min_selects = ", ".join(f'(SELECT MIN({pg_quote_ident(c)}) FROM {pg_quote_ident(t)})' for t, c in targets)
                    least_expr = f'LEAST({min_selects})' if len(targets) > 1 else min_selects
                    sync_query = f"""
                        WITH min_calc AS MATERIALIZED (
                            SELECT {least_expr} AS min_val
                        )
                        SELECT setval(
                            '{setval_arg}',
                            LEAST(s.last_value, m.min_val),
                            s.is_called OR (m.min_val IS NOT NULL AND m.min_val <= s.last_value)
                        )
                        FROM {quoted_seq} s, min_calc m;
                    """
                else:
                    max_selects = ", ".join(f'(SELECT MAX({pg_quote_ident(c)}) FROM {pg_quote_ident(t)})' for t, c in targets)
                    greatest_expr = f'GREATEST({max_selects})' if len(targets) > 1 else max_selects
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

        failed_tables = [(tbl, err) for tbl, _, err, _ in results if err is not None]
        successful_tables = sum(1 for _, _, err, _ in results if err is None)
        total_rows_imported = sum(rows for _, rows, err, _ in results if err is None)

        all_nul_stats = {tbl: nuls for tbl, _, err, nuls in results if err is None and nuls}
        self.last_nul_stats = all_nul_stats
        if all_nul_stats:
            logger.warning("=" * 80)
            logger.warning("DATA TRANSFORMATION NOTICE: NUL (0x00) bytes were stripped from text columns:")
            for tbl, col_map in sorted(all_nul_stats.items()):
                details = ", ".join(f"'{col}': {cnt} NUL byte(s)" for col, cnt in sorted(col_map.items()))
                logger.warning(f"  Table '{tbl}': {details}")
            logger.warning("PostgreSQL text/varchar rejects 0x00 bytes. Verify downstream applications if exact binary values were required.")
            logger.warning("=" * 80)

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

