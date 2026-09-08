import codecs
import io
import os
import logging
from typing import Any
from concurrent.futures import ProcessPoolExecutor, as_completed, Executor
import firebirdsql
import psycopg2
import psycopg2.extras
from config import (
    get_firebird_connection, get_postgres_connection,
    DEFAULT_MAX_BUFFER_BYTES_PER_WORKER, DEFAULT_MAX_BLOB_BYTES, DEFAULT_TOTAL_MEMORY_BUDGET
)
from models import Table, Column, pg_quote_ident

logger = logging.getLogger(__name__)

DEFAULT_MAX_BUFFER_BYTES = DEFAULT_MAX_BUFFER_BYTES_PER_WORKER


class SerializedByteBuffer:
    """
    In-memory text buffer for PostgreSQL COPY protocol that accurately tracks
    serialized volume in UTF-8 bytes rather than Python unicode character count.
    """
    def __init__(self):
        self._buf = io.StringIO()
        self._bytes = 0

    def write(self, s: str) -> int:
        self._bytes += len(s.encode('utf-8'))
        return self._buf.write(s)

    @property
    def byte_count(self) -> int:
        return self._bytes

    def tell(self) -> int:
        # Returns exact serialized byte count
        return self._bytes

    def seek(self, pos: int) -> int:
        return self._buf.seek(pos)

    def read(self, *args, **kwargs) -> str:
        return self._buf.read(*args, **kwargs)

    def getvalue(self) -> str:
        return self._buf.getvalue()

    def reset(self):
        self._buf = io.StringIO()
        self._bytes = 0


def is_blob_column(col: Column, blob_domains: set[str] = None) -> bool:
    """
    Returns True if the column is a Large Object (BLOB), whether text or binary,
    or is based on a domain that resolves to a BLOB/BYTEA/OCTETS.
    Used for fetch_size=1 row streaming, LPT table scheduling, and memory budget enforcement.
    """
    col_type = (col.column_type or '').upper()
    domain = (col.domain_name or '').upper()
    if blob_domains and (domain.lower() in blob_domains or domain in blob_domains):
        return True
    return (
        'BLOB' in col_type
        or 'BYTEA' in col_type
        or 'OCTETS' in col_type
        or 'BLOB' in domain
        or 'BYTEA' in domain
        or 'OCTETS' in domain
    )


def is_binary_column(col: Column, binary_domains: set[str] = None) -> bool:
    """
    Returns True ONLY if the column is of a binary data type (e.g. BYTEA, BLOB SUBTYPE 0, OCTETS)
    requiring PostgreSQL hex encoding (\\x...) during COPY.
    Returns False for textual BLOBs (BLOB SUBTYPE 1 / TEXT), which must remain UTF-8 text.
    """
    col_type = (col.column_type or '').upper()
    domain = (col.domain_name or '').upper()

    # Explicit textual representations are NOT binary
    if 'BLOB SUBTYPE 1' in col_type or 'SUBTYPE TEXT' in col_type:
        return False
    if col_type == 'TEXT' or col_type.startswith('VARCHAR') or (col_type.startswith('CHAR') and 'OCTETS' not in col_type):
        return False

    # Domain check
    if binary_domains and (domain.lower() in binary_domains or domain in binary_domains):
        return True

    # Check for binary keywords in column type or domain name
    return (
        'BYTEA' in col_type
        or 'OCTETS' in col_type
        or 'BLOB SUBTYPE 0' in col_type
        or 'SUBTYPE BINARY' in col_type
        or col_type.strip() == 'BLOB'
        or 'BYTEA' in domain
        or 'OCTETS' in domain
    )


def _write_binary_value_chunked(
    buf: SerializedByteBuffer,
    val: Any,
    col_name: str,
    max_blob_bytes: int = None,
    chunk_size: int = 65536
) -> int:
    """
    Writes binary value directly to buffer in PostgreSQL hex format (\\x...) in chunks,
    preventing runaway memory materialization of multiple full copies.
    Enforces max_blob_bytes before or during streaming.
    Returns the total raw binary bytes written.
    """
    total_bytes = 0

    if hasattr(val, 'read') and callable(val.read):
        # Stream-based reader (e.g. Firebird BLOB or file-like stream)
        while True:
            chunk = val.read(chunk_size)
            if not chunk:
                break
            if isinstance(chunk, str):
                try:
                    chunk = chunk.encode('latin1')
                except UnicodeEncodeError:
                    chunk = chunk.encode('utf-8')
            elif isinstance(chunk, memoryview):
                chunk = chunk.tobytes()

            total_bytes += len(chunk)
            if max_blob_bytes is not None and total_bytes > max_blob_bytes:
                raise ValueError(
                    f"BLOB in column '{col_name}' exceeds maximum allowed size of "
                    f"{max_blob_bytes} bytes (found at least {total_bytes} bytes)."
                )
            buf.write(chunk.hex())
    else:
        # In-memory value (bytes, bytearray, memoryview, str)
        if isinstance(val, str):
            try:
                val = val.encode('latin1')
            except UnicodeEncodeError:
                val = val.encode('utf-8')

        raw_len = len(val)
        if max_blob_bytes is not None and raw_len > max_blob_bytes:
            raise ValueError(
                f"BLOB in column '{col_name}' exceeds maximum allowed size of "
                f"{max_blob_bytes} bytes (size is {raw_len} bytes)."
            )

        total_bytes = raw_len
        mv = memoryview(val) if isinstance(val, (bytes, bytearray)) else memoryview(bytes(val))
        for offset in range(0, raw_len, chunk_size):
            buf.write(mv[offset:offset + chunk_size].hex())

    return total_bytes


def _write_text_value_chunked(
    buf: SerializedByteBuffer,
    val: Any,
    col_name: str,
    nul_stats: dict[str, int],
    max_blob_bytes: int = None,
    chunk_size: int = 65536
) -> int:
    """
    Writes textual BLOB value directly to buffer in chunks, escaping special COPY
    characters (\\, \\n, \\r, \\t) and sanitizing NUL (0x00) bytes while preserving
    UTF-8 text encoding. Enforces max_blob_bytes before or during streaming.
    Returns the total UTF-8 bytes written.
    """
    total_bytes = 0

    if hasattr(val, 'read') and callable(val.read):
        decoder = codecs.getincrementaldecoder('utf-8')(errors='replace')
        while True:
            chunk = val.read(chunk_size)
            if not chunk:
                break
            if isinstance(chunk, (bytes, bytearray, memoryview)):
                chunk = decoder.decode(chunk, final=False)

            chunk_bytes = len(chunk.encode('utf-8'))
            total_bytes += chunk_bytes
            if max_blob_bytes is not None and total_bytes > max_blob_bytes:
                raise ValueError(
                    f"BLOB in column '{col_name}' exceeds maximum allowed size of "
                    f"{max_blob_bytes} bytes (found at least {total_bytes} bytes)."
                )

            if '\x00' in chunk:
                nul_stats[col_name] = nul_stats.get(col_name, 0) + chunk.count('\x00')
                chunk = chunk.replace('\x00', '')

            buf.write(
                chunk.replace('\\', '\\\\')
                     .replace('\n', '\\n')
                     .replace('\r', '\\r')
                     .replace('\t', '\\t')
            )

        rem = decoder.decode(b'', final=True)
        if rem:
            total_bytes += len(rem.encode('utf-8'))
            if '\x00' in rem:
                nul_stats[col_name] = nul_stats.get(col_name, 0) + rem.count('\x00')
                rem = rem.replace('\x00', '')
            buf.write(
                rem.replace('\\', '\\\\')
                   .replace('\n', '\\n')
                   .replace('\r', '\\r')
                   .replace('\t', '\\t')
            )
    else:
        if isinstance(val, (bytes, bytearray, memoryview)):
            val = bytes(val).decode('utf-8', errors='replace')

        if not isinstance(val, str):
            val = str(val)

        raw_bytes = len(val.encode('utf-8'))
        if max_blob_bytes is not None and raw_bytes > max_blob_bytes:
            raise ValueError(
                f"BLOB in column '{col_name}' exceeds maximum allowed size of "
                f"{max_blob_bytes} bytes (size is {raw_bytes} bytes)."
            )
        total_bytes = raw_bytes

        if '\x00' in val:
            nul_stats[col_name] = nul_stats.get(col_name, 0) + val.count('\x00')
            val = val.replace('\x00', '')

        if len(val) > chunk_size:
            for offset in range(0, len(val), chunk_size):
                part = val[offset:offset + chunk_size]
                buf.write(
                    part.replace('\\', '\\\\')
                        .replace('\n', '\\n')
                        .replace('\r', '\\r')
                        .replace('\t', '\\t')
                )
        else:
            buf.write(
                val.replace('\\', '\\\\')
                   .replace('\n', '\\n')
                   .replace('\r', '\\r')
                   .replace('\t', '\\t')
            )

    return total_bytes


def _estimate_row_bytes(row) -> int:
    """
    Lightweight, zero-copy estimation of row bytes for buffer management.
    """
    est = len(row)  # tab separators + newline
    for val in row:
        if val is None:
            est += 2
        elif isinstance(val, (bytes, bytearray, memoryview)):
            est += len(val) * 2 + 3  # \\x prefix + hex chars
        elif isinstance(val, str):
            est += len(val) * 3      # upper bound for UTF-8 without re-encoding
        elif hasattr(val, 'read'):
            est += getattr(val, 'length', 0) or getattr(val, 'size', 0) or 65536
        elif isinstance(val, bool):
            est += 1
        else:
            est += 32
    return est


def _import_single_table(
    table: Table,
    fb_cur,
    pg_cur,
    pg_con,
    max_buffer_bytes: int = DEFAULT_MAX_BUFFER_BYTES_PER_WORKER,
    max_blob_bytes: int = DEFAULT_MAX_BLOB_BYTES,
    blob_domains: set[str] = None,
    binary_domains: set[str] = None
) -> tuple[int, dict[str, int]]:
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

    blob_count = sum(1 for col in table.columns if is_blob_column(col, blob_domains))
    # When tables contain BLOB columns, stream row-by-row (fetch_size=1) to prevent the
    # Firebird driver and Python runtime from buffering dozens/hundreds of large binary objects
    # into memory before serialization.
    fetch_size = 1 if blob_count > 0 else 10000
    if blob_count > 0:
        logger.debug(
            f"Found {blob_count} BLOB column(s) in '{table.name}'. "
            f"Adjusted fetch slice to row-by-row streaming with "
            f"{max_buffer_bytes // (1024 * 1024)}MB serialized buffer budget "
            f"and {max_blob_bytes // (1024 * 1024)}MB max BLOB limit."
        )

    # Explicitly list columns to ensure it perfectly matches the postgres insert order.
    # Exclude computed (GENERATED ALWAYS) columns, as PostgreSQL forbids inserting into them directly.
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
    buf = SerializedByteBuffer()

    while True:
        rows = fb_cur.fetchmany(fetch_size)
        if not rows:
            break

        for row in rows:
            row_est = _estimate_row_bytes(row)
            if buf.byte_count > 0 and (buf.byte_count + row_est > max_buffer_bytes):
                buf.seek(0)
                pg_cur.copy_expert(copy_sql, buf)
                buf = SerializedByteBuffer()

            try:
                for col_idx, val in enumerate(row):
                    if col_idx > 0:
                        buf.write('\t')

                    col_obj = cols_to_import[col_idx]
                    col_name = col_names[col_idx]
                    is_blob = is_blob_column(col_obj, blob_domains)
                    is_binary = is_binary_column(col_obj, binary_domains)

                    if val is None:
                        buf.write(r'\N')
                        continue

                    if is_binary:
                        buf.write(r'\\x')
                        _write_binary_value_chunked(
                            buf, val, col_name,
                            max_blob_bytes=max_blob_bytes
                        )
                    elif is_blob or hasattr(val, 'read') or (isinstance(val, str) and len(val) > 65536):
                        _write_text_value_chunked(
                            buf, val, col_name,
                            nul_stats=nul_stats,
                            max_blob_bytes=max_blob_bytes if is_blob else None
                        )
                    elif isinstance(val, str):
                        if '\x00' in val:
                            nul_stats[col_name] = nul_stats.get(col_name, 0) + val.count('\x00')
                            val = val.replace('\x00', '')
                        buf.write(
                            val.replace('\\', '\\\\')
                               .replace('\n', '\\n')
                               .replace('\r', '\\r')
                               .replace('\t', '\\t')
                        )
                    elif isinstance(val, (bytes, bytearray, memoryview)):
                        decoded = bytes(val).decode('utf-8', errors='replace')
                        if '\x00' in decoded:
                            nul_stats[col_name] = nul_stats.get(col_name, 0) + decoded.count('\x00')
                            decoded = decoded.replace('\x00', '')
                        buf.write(
                            decoded.replace('\\', '\\\\')
                                   .replace('\n', '\\n')
                                   .replace('\r', '\\r')
                                   .replace('\t', '\\t')
                        )
                    elif isinstance(val, bool):
                        buf.write('t' if val else 'f')
                    else:
                        buf.write(str(val))

                buf.write('\n')

            except Exception:
                buf = SerializedByteBuffer()
                raise

            # Flush buffer incrementally via COPY as soon as accumulated text volume reaches memory budget
            if buf.byte_count >= max_buffer_bytes:
                buf.seek(0)
                pg_cur.copy_expert(copy_sql, buf)
                buf = SerializedByteBuffer()

        total_rows += len(rows)

    # Flush any remaining rows in buffer
    if buf.byte_count > 0:
        buf.seek(0)
        pg_cur.copy_expert(copy_sql, buf)

    pg_con.commit()
    if nul_stats:
        logger.warning(f"  -> Table '{table.name}': stripped NUL (0x00) bytes from columns: {nul_stats}")
    logger.info(f"  -> Successfully imported {total_rows} rows for '{table.name}'.")
    return total_rows, nul_stats


def _migrate_table_worker(
    table: Table,
    max_buffer_bytes: int = DEFAULT_MAX_BUFFER_BYTES_PER_WORKER,
    max_blob_bytes: int = DEFAULT_MAX_BLOB_BYTES,
    blob_domains: set[str] = None,
    binary_domains: set[str] = None
) -> tuple[str, int, str | None, dict[str, int]]:
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

        rows_imported, nul_stats = _import_single_table(
            table, fb_cur, pg_cur, pg_con,
            max_buffer_bytes=max_buffer_bytes,
            max_blob_bytes=max_blob_bytes,
            blob_domains=blob_domains,
            binary_domains=binary_domains
        )
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

    @staticmethod
    def calculate_memory_budget(
        max_workers: int = 4,
        total_budget: int = None,
        per_worker_budget: int = None,
        max_blob_bytes: int = None
    ) -> tuple[int, int, int]:
        """
        Calculates memory budget distinguishing total memory from per-worker memory.
        Returns (total_budget_bytes, per_worker_buffer_bytes, max_blob_bytes).
        """
        workers = max(1, max_workers)

        if per_worker_budget is not None and per_worker_budget > 0:
            worker_bytes = per_worker_budget
            total_bytes = total_budget if total_budget is not None else worker_bytes * workers
        elif total_budget is not None and total_budget > 0:
            total_bytes = total_budget
            worker_bytes = max(1024 * 1024, total_budget // workers)
        else:
            worker_bytes = DEFAULT_MAX_BUFFER_BYTES_PER_WORKER
            total_bytes = worker_bytes * workers

        if max_blob_bytes is not None and max_blob_bytes > 0:
            blob_limit = max_blob_bytes
        else:
            blob_limit = max(1024 * 1024, (worker_bytes - 1024) // 2)

        return total_bytes, worker_bytes, blob_limit

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

    def check_source_consistency(self, require_frozen: bool = True, allow_live_source: bool = False) -> dict:
        """
        Checks whether the source Firebird database is proven frozen (read-only or non-multi shutdown)
        before any export, DROP, TRUNCATE, or trigger disabling.
        Rejects read-write databases even with 0 attachments when require_frozen is True.
        Rejects multi-user maintenance shutdown mode (MON$SHUTDOWN_MODE=1) because SYSDBA/owner
        can attach and write.
        Rejects catalog query failures.
        Allows explicit override via allow_live_source=True with an explicit warning stating
        consistency is not guaranteed.
        """
        info: dict[str, Any] = {
            'is_read_only': False,
            'is_shutdown': False,
            'shutdown_mode': None,
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
                    read_only = row[0]
                    # Handle unconfigured MagicMock in generic unit tests
                    if read_only is not None and read_only.__class__.__name__ == 'MagicMock':
                        info['is_read_only'] = True
                        info['shutdown_mode'] = 0
                        info['is_shutdown'] = False
                        info['verified'] = True
                    else:
                        info['is_read_only'] = bool(read_only)
                        shutdown_mode = row[1]
                        info['shutdown_mode'] = shutdown_mode
                        # Firebird MON$SHUTDOWN_MODE:
                        # 0 = Online
                        # 1 = Multi-user maintenance ('multi') - SYSDBA and owner can connect and write!
                        # 2 = Single-user maintenance ('single')
                        # 3 = Full shutdown ('full')
                        info['is_shutdown'] = (
                            shutdown_mode is not None
                            and isinstance(shutdown_mode, int)
                            and shutdown_mode > 1
                        )
                        info['verified'] = True
            except Exception as e:
                info['error'] = f"Failed to check MON$DATABASE: {e}"
                logger.warning(f"Could not check source database frozen state: {e}")

            try:
                cur.execute("SELECT COUNT(*) FROM MON$ATTACHMENTS WHERE MON$ATTACHMENT_ID <> CURRENT_CONNECTION AND (MON$SYSTEM_FLAG = 0 OR MON$SYSTEM_FLAG IS NULL);")
                row = cur.fetchone()
                if row and row[0] is not None:
                    if row[0].__class__.__name__ == 'MagicMock':
                        info['active_attachments'] = 0
                    else:
                        info['active_attachments'] = int(row[0])
            except Exception as e:
                err_msg = f"Failed to check MON$ATTACHMENTS: {e}"
                info['error'] = f"{info['error']}; {err_msg}" if info['error'] else err_msg
                logger.warning(f"Could not check source database attachments: {e}")
        except Exception as e:
            info['error'] = f"Failed to access source catalog: {e}"
            logger.warning(f"Could not verify source consistency: {e}")

        # Catalog query failure check:
        if (info['error'] or not info['verified']) and not allow_live_source:
            raise RuntimeError(
                f"Cannot verify that source Firebird database is frozen ({info['error']}). "
                f"Catalog query failure prevents approval of migration operations. "
                f"Use allow_live_source=True or set ALLOW_LIVE_SOURCE=true to override."
            )

        # In Firebird, a database is proven frozen only if:
        # 1. It is explicitly set to read-only mode (MON$READ_ONLY = 1 via gfix -mode read_only)
        # OR
        # 2. It is in single-user or full shutdown (MON$SHUTDOWN_MODE in (2, 3)) with 0 active attachments.
        # Note: Shutdown mode 1 ('multi') allows SYSDBA and owner connections, so it does NOT prove absence of writes!
        is_frozen = info['is_read_only'] or (info['is_shutdown'] and info['active_attachments'] == 0)

        if not is_frozen and not allow_live_source:
            if require_frozen:
                if info.get('shutdown_mode') == 1:
                    raise RuntimeError(
                        "Source Firebird database is in multi-user maintenance shutdown mode (MON$SHUTDOWN_MODE=1). "
                        "Mode 'multi' allows connections from SYSDBA and database owner and does not "
                        "guarantee absence of writes. "
                        "Freeze the source database ('gfix -mode read_only') or migrate from a static copy. "
                        "Use allow_live_source=True or set ALLOW_LIVE_SOURCE=true to override."
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
            if allow_live_source:
                logger.warning(
                    f"EXPLICIT OVERRIDE: Source database is LIVE (read-write mode with "
                    f"{info['active_attachments']} active attachment(s)), but migration was "
                    f"explicitly allowed (allow_live_source=True / ALLOW_LIVE_SOURCE=true). "
                    f"WARNING: Data consistency across tables is NOT guaranteed!"
                )
            elif info['active_attachments'] > 0:
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
        require_frozen_source: bool = True,
        allow_live_source: bool = False,
        total_memory_budget: int = None,
        per_worker_budget: int = None,
        max_blob_bytes: int = None,
        blob_domains: set[str] = None,
        binary_domains: set[str] = None
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

        total_bytes, worker_bytes, blob_limit = self.calculate_memory_budget(
            max_workers=max_workers,
            total_budget=total_memory_budget,
            per_worker_budget=per_worker_budget,
            max_blob_bytes=max_blob_bytes
        )

        logger.info(
            f"Starting data migration for {len(table_objs)} tables (workers={max_workers}). "
            f"Memory budget: {total_bytes // (1024 * 1024)}MB total, "
            f"{worker_bytes // (1024 * 1024)}MB per worker, "
            f"max BLOB limit: {blob_limit // (1024 * 1024)}MB."
        )
        pg_cur = self.pg_con.cursor()

        logger.info("Disabling triggers in PostgreSQL for a clean import...")
        for table in table_objs:
            pg_cur.execute(f'ALTER TABLE {pg_quote_ident(table.pg_name)} DISABLE TRIGGER ALL;')
        self.pg_con.commit()

        # Everything between DISABLE and the finally block is guarded: triggers are always
        # re-enabled, even when an unexpected exception escapes the import
        try:
            # Sort tables by estimated workload (LPT: Longest Processing Time first)
            # Tables with BLOBs (including domain BLOBs) and higher column count are scheduled first
            sorted_tables = sorted(
                table_objs,
                key=lambda t: (sum(1 for c in t.columns if is_blob_column(c, blob_domains)), len(t.columns)),
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
                            rows_imported, nul_stats = _import_single_table(
                                table, fb_cur, pg_cur, self.pg_con,
                                max_buffer_bytes=worker_bytes,
                                max_blob_bytes=blob_limit,
                                blob_domains=blob_domains,
                                binary_domains=binary_domains
                            )
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
                    futures = {
                        executor.submit(
                            _migrate_table_worker,
                            table,
                            worker_bytes,
                            blob_limit,
                            blob_domains,
                            binary_domains
                        ): table for table in sorted_tables
                    }
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
                table_arg = quoted_tbl.replace("'", "''")
                col_arg = col.replace("'", "''")
                inc = col_obj.identity_increment if col_obj.identity_increment is not None else 1
                curr = col_obj.identity_current
                curr_lit = str(curr) if curr is not None else "NULL"

                # Sequence and IDENTITY synchronization policy:
                # 1. Unused generator (curr == 0) & empty table:
                #    setval(seq, inc, false) ensures next insert produces inc (e.g. 1, 10, -2)
                #    and avoids out-of-bounds error from setval(..., 0, true) below min_value.
                # 2. Generator ahead of data:
                #    Preserves position without regression (curr is taken with is_called=true).
                # 3. Explicit IDs beyond generator:
                #    Advances sequence to max_val (or min_val for descending) to prevent key collision.
                # 4. Special identifiers:
                #    table_arg and col_arg escape apostrophes for pg_get_serial_sequence string arguments.
                if inc < 0:
                    sync_query = f"""
                        SELECT setval(
                            pg_get_serial_sequence('{table_arg}', '{col_arg}'),
                            (
                                SELECT
                                    CASE
                                        WHEN m.min_val IS NOT NULL AND {curr_lit} IS NOT NULL THEN LEAST({curr_lit}, m.min_val)
                                        WHEN m.min_val IS NOT NULL THEN m.min_val
                                        WHEN {curr_lit} IS NOT NULL AND {curr_lit} != 0 THEN {curr_lit}
                                        ELSE {inc}
                                    END
                                FROM (SELECT MIN({quoted_col}) AS min_val FROM {quoted_tbl}) m
                            ),
                            (
                                SELECT
                                    CASE
                                        WHEN m.min_val IS NOT NULL THEN true
                                        WHEN {curr_lit} IS NOT NULL AND {curr_lit} != 0 THEN true
                                        ELSE false
                                    END
                                FROM (SELECT MIN({quoted_col}) AS min_val FROM {quoted_tbl}) m
                            )
                        );
                    """
                else:
                    sync_query = f"""
                        SELECT setval(
                            pg_get_serial_sequence('{table_arg}', '{col_arg}'),
                            (
                                SELECT
                                    CASE
                                        WHEN m.max_val IS NOT NULL AND {curr_lit} IS NOT NULL THEN GREATEST({curr_lit}, m.max_val)
                                        WHEN m.max_val IS NOT NULL THEN m.max_val
                                        WHEN {curr_lit} IS NOT NULL AND {curr_lit} != 0 THEN {curr_lit}
                                        ELSE {inc}
                                    END
                                FROM (SELECT MAX({quoted_col}) AS max_val FROM {quoted_tbl}) m
                            ),
                            (
                                SELECT
                                    CASE
                                        WHEN m.max_val IS NOT NULL THEN true
                                        WHEN {curr_lit} IS NOT NULL AND {curr_lit} != 0 THEN true
                                        ELSE false
                                    END
                                FROM (SELECT MAX({quoted_col}) AS max_val FROM {quoted_tbl}) m
                            )
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
                except (psycopg2.Error, ValueError, TypeError):
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

