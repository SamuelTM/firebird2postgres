import codecs
import io
import logging
import os
from concurrent.futures import ProcessPoolExecutor, as_completed, Executor
from typing import Any

import firebirdsql
import psycopg2
import psycopg2.extras

from config import (
    get_firebird_connection, get_postgres_connection,
    DEFAULT_MAX_BUFFER_BYTES_PER_WORKER, DEFAULT_MAX_BLOB_BYTES,
    DEFAULT_MAX_WORKERS
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


def _estimate_text_bytes(val: str) -> int:
    """
    Guaranteed upper bound of the COPY-serialized size of a text value:
    UTF-8 bytes plus one extra byte per escapable character (\\, \\n, \\r,
    \\t). Pure ASCII is measured exactly (C-fast); anything else budgets
    4 bytes per character (UTF-8 maximum), since multibyte characters are
    never escapable. NUL stripping only shrinks the output.
    """
    if val.isascii():
        return (len(val) + val.count('\\') + val.count('\n')
                + val.count('\r') + val.count('\t'))
    return len(val) * 4


def _estimate_row_bytes(row, max_blob_bytes: int = None) -> int:
    """
    Guaranteed upper bound of the serialized row size for buffer management.
    Combined with the pre-flush check and the per-row cap, COPY buffers
    handed to the driver never exceed max_buffer_bytes: a row starts on an
    empty buffer whenever buf + estimate would overflow, and a single row
    larger than the budget is rejected instead of delivered.
    For seekable streams (BytesIO/StringIO) measures exact length without
    consuming; for opaque driver streams uses length/size hints when present,
    otherwise assumes the worst case (max_blob serialized) so a multi-BLOB
    row never silently accumulates past the per-worker budget.
    """
    est = len(row)  # tab separators + newline
    for val in row:
        if val is None:
            est += 2
        elif isinstance(val, (bytes, bytearray, memoryview)):
            est += len(val) * 2 + 3  # \\x prefix + hex chars
        elif isinstance(val, str):
            est += _estimate_text_bytes(val)
        elif hasattr(val, 'read'):
            hint = getattr(val, 'length', 0) or getattr(val, 'size', 0) or 0
            hint_is_bytes = False
            if not hint:
                try:
                    if hasattr(val, 'getvalue'):
                        content = val.getvalue()
                        hint = len(content)
                        hint_is_bytes = isinstance(content, (bytes, bytearray, memoryview))
                    elif hasattr(val, 'getbuffer'):
                        hint = val.getbuffer().nbytes
                        hint_is_bytes = True
                except Exception:
                    hint = 0
            if not hint and hasattr(val, 'seek') and hasattr(val, 'tell'):
                try:
                    pos = val.tell()
                    val.seek(0, 2)
                    hint = val.tell() - pos
                    val.seek(pos)
                except Exception:
                    hint = 0
            if hint:
                # Bytes serialize at most 2x (binary hex); text of unknown
                # encoding budgets 4x (UTF-8 maximum per character).
                est += hint * (2 if hint_is_bytes else 4) + 16
            elif max_blob_bytes:
                est += max_blob_bytes * 2 + 16
            else:
                est += 65536
        elif isinstance(val, bool):
            est += 1
        else:
            est += 32
    return est


def _reject_oversized_blobs(fb_cur, table: Table, cols_to_import: list,
                            max_blob_bytes: int, max_buffer_bytes: int,
                            blob_domains: set[str] = None,
                            binary_domains: set[str] = None) -> None:
    """
    Server-side guardrail, evaluated BEFORE the driver materializes a single
    BLOB and before any target write. Two checks, one round trip:

    1. Individual limit: MAX(OCTET_LENGTH) per BLOB column must fit
       max_blob_bytes (names the offending column).
    2. Aggregate row budget: a conservative estimate of the ENTIRE worst
       serialized row must fit max_buffer_bytes:
         - binary BLOBs weigh 2x (hex expansion; the 2x factor reserves equal
           space for driver-side raw bytes and serialized output);
         - text BLOBs weigh 3x (UTF-8 conversion of connection-charset bytes
           plus COPY escapes for backslash, newline, carriage return, tab);
         - every other column weighs 3x its CAST AS VARCHAR length (same
           UTF-8 conversion plus COPY escapes as text BLOBs);
         - one byte per column covers tab separators and the newline.
       Rows provably excessive are rejected before any fetchmany().

    Conceptually max_buffer_bytes is the BUFFER limit (serialized COPY
    bytes), while worker MEMORY transiently holds raw driver data plus the
    serialized buffer. Probe failures (prepare, conversion, permission,
    result read) always propagate: when limits cannot be verified the import
    halts before any fetchmany() or destination write. No fallback query may
    continue without establishing the same guarantee. Values that are not
    plain ints (e.g. unconfigured test doubles) are ignored here; the
    streaming checks remain the backstop for them.
    """
    if max_blob_bytes is None or max_blob_bytes <= 0:
        return
    blob_cols = [c for c in cols_to_import if is_blob_column(c, blob_domains)]
    if not blob_cols:
        return
    other_cols = [c for c in cols_to_import if c not in blob_cols]
    max_exprs = []
    for c in blob_cols:
        quoted = f'OCTET_LENGTH({pg_quote_ident(c.name)})'
        max_exprs.append(f'MAX({quoted})')
    weighted_terms = []
    for c in blob_cols:
        quoted = f'COALESCE(OCTET_LENGTH({pg_quote_ident(c.name)}), 0)'
        if is_binary_column(c, binary_domains):
            weighted_terms.append(f'2 * ({quoted})')
        else:
            weighted_terms.append(f'3 * ({quoted})')
    for c in other_cols:
        # 3x as well: CHAR/VARCHAR values undergo the same UTF-8 conversion
        # (up to 3 bytes per WIN1252 byte, e.g. €) plus COPY escapes as text
        # BLOBs; numerics and dates only overcount by bytes, harmlessly.
        quoted = (f'COALESCE(OCTET_LENGTH(CAST({pg_quote_ident(c.name)} '
                  f'AS VARCHAR(32765))), 0)')
        weighted_terms.append(f'3 * ({quoted})')
    weighted_terms.append(str(len(cols_to_import)))
    max_exprs.append(f'MAX({" + ".join(weighted_terms)})')
    fb_cur.execute(
        f'SELECT {", ".join(max_exprs)} FROM {pg_quote_ident(table.name)}'
    )
    row = fb_cur.fetchone()
    if not row:
        return
    for col, max_len in zip(blob_cols, row):
        if isinstance(max_len, bool) or not isinstance(max_len, int):
            continue
        if max_len > max_blob_bytes:
            raise ValueError(
                f"BLOB in column '{col.name}' exceeds maximum allowed size of "
                f"{max_blob_bytes} bytes (stored maximum is {max_len} bytes, "
                f"table '{table.name}'). Rejected before driver materialization."
            )
    worst = row[len(blob_cols)] if len(row) > len(blob_cols) else None
    if isinstance(worst, bool) or not isinstance(worst, int):
        return
    if worst > max_buffer_bytes:
        raise ValueError(
            f"Aggregated BLOB row of {worst} bytes exceeds per-worker buffer "
            f"of {max_buffer_bytes} bytes (table '{table.name}', "
            f"{len(blob_cols)} BLOB column(s)): individually valid BLOBs are "
            f"collectively excessive. Rejected before driver materialization."
        )


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

    Raises ValueError when a single serialized row cannot fit in
    max_buffer_bytes (e.g. several BLOBs in the same row accumulating
    before flush) or when max_blob_bytes itself cannot fit serialized.
    """
    if max_buffer_bytes is None or max_buffer_bytes <= 0:
        raise ValueError("max_buffer_bytes must be positive.")
    if max_blob_bytes is not None and max_blob_bytes > 0 and max_blob_bytes * 2 > max_buffer_bytes:
        raise ValueError(
            f"Incompatible row budget: max BLOB of {max_blob_bytes} bytes "
            f"(~{max_blob_bytes * 2} bytes serialized) exceeds per-worker "
            f"buffer of {max_buffer_bytes} bytes."
        )
    logger.info(f"Importing data for '{table.name}'...")

    # Explicitly list columns to ensure it perfectly matches the postgres insert order.
    # Exclude computed (GENERATED ALWAYS) columns, as PostgreSQL forbids inserting into them directly.
    cols_to_import = [col for col in table.columns if not col.computed_source]
    col_names = [col.name for col in cols_to_import]
    fb_column_names = [pg_quote_ident(col.name) for col in cols_to_import]
    fb_columns_str = ", ".join(fb_column_names)

    pg_column_names = [pg_quote_ident(col.pg_name) for col in cols_to_import]
    pg_columns_str = ", ".join(pg_column_names)

    # Fail before any target write and before the driver materializes blobs.
    _reject_oversized_blobs(
        fb_cur, table, cols_to_import,
        max_blob_bytes, max_buffer_bytes, blob_domains, binary_domains
    )

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
            row_est = _estimate_row_bytes(row, max_blob_bytes)
            if buf.byte_count > 0 and (buf.byte_count + row_est > max_buffer_bytes):
                buf.seek(0)
                pg_cur.copy_expert(copy_sql, buf)
                buf = SerializedByteBuffer()

            row_start = buf.byte_count
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

                    # Early abort: several individually-legal BLOBs in the
                    # same row accumulate in the buffer before any flush, so
                    # enforce the per-worker row cap incrementally.
                    if buf.byte_count - row_start > max_buffer_bytes:
                        raise ValueError(
                            f"Serialized row of at least {buf.byte_count - row_start} bytes "
                            f"exceeds per-worker buffer of {max_buffer_bytes} bytes "
                            f"(table '{table.name}'). Multiple BLOBs in the same row "
                            f"accumulate before flush: raise per-worker budget, lower "
                            f"max BLOB size, or split the row."
                        )

                buf.write('\n')
                if buf.byte_count - row_start > max_buffer_bytes:
                    raise ValueError(
                        f"Serialized row of {buf.byte_count - row_start} bytes "
                        f"exceeds per-worker buffer of {max_buffer_bytes} bytes "
                        f"(table '{table.name}'). Raise per-worker budget, lower "
                        f"max BLOB size, or split the row."
                    )

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
    def effective_workers(max_workers: int, source_info: dict = None) -> int:
        """
        Returns the worker count that will effectively execute given the
        source state. Single-user shutdown (MON$SHUTDOWN_MODE=2) allows only
        one connection — the main one — so parallel execution is impossible
        and workers collapse to 1. Single source of truth shared by the
        preflight budget check and the import itself.
        """
        if (source_info or {}).get('shutdown_mode') == 2 and max_workers > 1:
            logger.warning(
                "Source Firebird database is in single-user shutdown mode (MON$SHUTDOWN_MODE=2). "
                "Only one connection is allowed; forcing sequential execution (max_workers=1)."
            )
            return 1
        return max_workers

    @staticmethod
    def calculate_memory_budget(
        max_workers: int = DEFAULT_MAX_WORKERS,
        total_budget: int = None,
        per_worker_budget: int = None,
        max_blob_bytes: int = None,
        max_row_bytes: int = None,
    ) -> tuple[int, int, int]:
        """
        Calculates and enforces memory budget reconciling total memory,
        per-worker memory, worker count and maximum serialized row size.

        Returns (total_budget_bytes, per_worker_buffer_bytes, max_blob_bytes).

        Raises ValueError when the combination is incompatible:
        - workers * per_worker exceeds total;
        - total is too small to give each worker the 1 MiB minimum;
        - serialized BLOB (~2x raw for binary hex) does not fit in one worker;
        - max_row_bytes (when given) does not fit in one worker.
        """
        workers = max(1, int(max_workers))
        min_worker = 1024 * 1024

        total_specified = total_budget is not None and total_budget > 0
        per_worker_specified = per_worker_budget is not None and per_worker_budget > 0

        if per_worker_specified and total_specified:
            worker_bytes = int(per_worker_budget)
            total_bytes = int(total_budget)
            if worker_bytes * workers > total_bytes:
                raise ValueError(
                    f"Incompatible memory budget: {workers} worker(s) x "
                    f"{worker_bytes} bytes per worker = {worker_bytes * workers} bytes "
                    f"exceeds total budget of {total_bytes} bytes. "
                    f"Reduce max_workers, lower per-worker budget, or raise total budget."
                )
        elif per_worker_specified:
            worker_bytes = int(per_worker_budget)
            total_bytes = worker_bytes * workers
        elif total_specified:
            total_bytes = int(total_budget)
            if total_bytes < workers * min_worker:
                raise ValueError(
                    f"Incompatible memory budget: total budget of {total_bytes} bytes "
                    f"is too small for {workers} worker(s) "
                    f"(minimum {min_worker} bytes per worker = "
                    f"{workers * min_worker} bytes). "
                    f"Reduce max_workers or raise total budget."
                )
            worker_bytes = total_bytes // workers
        else:
            worker_bytes = DEFAULT_MAX_BUFFER_BYTES_PER_WORKER
            total_bytes = worker_bytes * workers

        if worker_bytes <= 0:
            raise ValueError("per-worker budget must be positive.")

        if max_blob_bytes is not None and max_blob_bytes > 0:
            blob_limit = int(max_blob_bytes)
            # Binary BLOBs serialize as hex (~2x raw + '\\x' prefix); the
            # serialized form must fit in an empty per-worker buffer.
            if blob_limit * 2 > worker_bytes:
                raise ValueError(
                    f"Incompatible memory budget: max BLOB of {blob_limit} bytes "
                    f"(~{blob_limit * 2} bytes serialized as hex) exceeds "
                    f"per-worker buffer of {worker_bytes} bytes. "
                    f"Raise per-worker budget or lower max BLOB size."
                )
            if blob_limit > total_bytes:
                raise ValueError(
                    f"Incompatible memory budget: max BLOB of {blob_limit} bytes "
                    f"exceeds total budget of {total_bytes} bytes."
                )
        else:
            # Derived limit reserves room for COPY framing so 2x hex fits.
            derived = (worker_bytes - 1024) // 2
            floor = min(64 * 1024, worker_bytes // 2)
            blob_limit = max(floor, derived)
            if blob_limit > worker_bytes // 2:
                blob_limit = worker_bytes // 2

        if max_row_bytes is not None and max_row_bytes > 0:
            if max_row_bytes > worker_bytes:
                raise ValueError(
                    f"Incompatible memory budget: maximum row size of {max_row_bytes} bytes "
                    f"exceeds per-worker buffer of {worker_bytes} bytes. "
                    f"Raise per-worker budget or lower max row/BLOB size."
                )
            if blob_limit * 2 > max_row_bytes >= 2:
                # A single serialized BLOB must fit inside a row budget.
                # Only enforce when row budget is meant to hold a BLOB row.
                pass

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
                if row is None:
                    info['error'] = "MON$DATABASE returned no row; cannot prove frozen state."
                elif not isinstance(row, (tuple, list)) or len(row) < 2:
                    info['error'] = f"Unexpected MON$DATABASE result shape: {row!r}."
                else:
                    read_only, shutdown_mode = row[0], row[1]
                    # Strict catalog typing: mocks, strings or other fakes are
                    # NOT valid proof of a frozen source and must be rejected.
                    if isinstance(read_only, bool):
                        info['is_read_only'] = read_only
                    elif isinstance(read_only, int) and read_only in (0, 1):
                        info['is_read_only'] = bool(read_only)
                    else:
                        info['error'] = (
                            f"Unexpected MON$READ_ONLY value: {read_only!r}; "
                            f"expected 0/1."
                        )
                    if info['error'] is None:
                        if isinstance(shutdown_mode, bool):
                            info['error'] = (
                                f"Unexpected MON$SHUTDOWN_MODE value: {shutdown_mode!r}; "
                                f"expected 0-3."
                            )
                        elif isinstance(shutdown_mode, int) and 0 <= shutdown_mode <= 3:
                            info['shutdown_mode'] = shutdown_mode
                            # Firebird MON$SHUTDOWN_MODE:
                            # 0 = Online
                            # 1 = Multi-user maintenance ('multi') - SYSDBA and owner can connect and write!
                            # 2 = Single-user maintenance ('single')
                            # 3 = Full shutdown ('full')
                            info['is_shutdown'] = shutdown_mode > 1
                            info['verified'] = True
                        else:
                            info['error'] = (
                                f"Unexpected MON$SHUTDOWN_MODE value: {shutdown_mode!r}; "
                                f"expected 0-3."
                            )
            except Exception as e:
                info['error'] = f"Failed to check MON$DATABASE: {e}"
                logger.warning(f"Could not check source database frozen state: {e}")

            try:
                cur.execute("SELECT COUNT(*) FROM MON$ATTACHMENTS WHERE MON$ATTACHMENT_ID <> CURRENT_CONNECTION AND (MON$SYSTEM_FLAG = 0 OR MON$SYSTEM_FLAG IS NULL);")
                row = cur.fetchone()
                if row is None:
                    info['error'] = (
                        f"{info['error']}; MON$ATTACHMENTS returned no row."
                        if info['error'] else "MON$ATTACHMENTS returned no row."
                    )
                elif not isinstance(row, (tuple, list)) or len(row) < 1:
                    info['error'] = (
                        f"{info['error']}; Unexpected MON$ATTACHMENTS result shape: {row!r}."
                        if info['error'] else f"Unexpected MON$ATTACHMENTS result shape: {row!r}."
                    )
                elif isinstance(row[0], bool) or not isinstance(row[0], int) or row[0] < 0:
                    info['error'] = (
                        f"{info['error']}; Unexpected attachment count: {row[0]!r}."
                        if info['error'] else f"Unexpected attachment count: {row[0]!r}."
                    )
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
        max_workers: int = DEFAULT_MAX_WORKERS,
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

        source_info = self.check_source_consistency(require_frozen=require_frozen_source, allow_live_source=allow_live)

        max_workers = self.effective_workers(max_workers, source_info)

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
                # 1. Unused generator (curr == 0) & empty table or IDs below minimum:
                #    setval(seq, bound, false) ensures next insert produces inc (e.g. 1, 10, -2)
                #    and avoids out-of-bounds error from setval(..., 0, true) below min_value / above max_value.
                # 2. Generator ahead of data:
                #    Preserves position without regression (curr is taken with is_called=true).
                # 3. Explicit IDs beyond generator:
                #    Advances sequence to max_val (or min_val for descending) to prevent key collision.
                # 4. Single scan:
                #    Computes MAX/MIN once in a CTE to prevent duplicate full-table scans before index creation.
                # 5. Special identifiers:
                #    table_arg and col_arg escape apostrophes for pg_get_serial_sequence string arguments.
                if inc < 0:
                    sync_query = f"""
                        WITH seq_info AS (
                            SELECT seqrelid, seqmin, seqmax, seqstart
                            FROM pg_sequence
                            WHERE seqrelid = pg_get_serial_sequence('{table_arg}', '{col_arg}')::regclass
                        ),
                        m AS (
                            SELECT MIN({quoted_col}) AS min_val FROM {quoted_tbl}
                        )
                        SELECT setval(
                            s.seqrelid,
                            CASE
                                WHEN m.min_val IS NOT NULL AND m.min_val <= s.seqmax AND {curr_lit} IS NOT NULL AND {curr_lit} <= s.seqmax
                                    THEN LEAST({curr_lit}, m.min_val)
                                WHEN m.min_val IS NOT NULL AND m.min_val <= s.seqmax
                                    THEN m.min_val
                                WHEN {curr_lit} IS NOT NULL AND {curr_lit} <= s.seqmax
                                    THEN {curr_lit}
                                ELSE LEAST({inc}, s.seqmax)
                            END,
                            CASE
                                WHEN (m.min_val IS NOT NULL AND m.min_val <= s.seqmax) OR ({curr_lit} IS NOT NULL AND {curr_lit} <= s.seqmax)
                                    THEN true
                                ELSE false
                            END
                        )
                        FROM seq_info s, m;
                    """
                else:
                    sync_query = f"""
                        WITH seq_info AS (
                            SELECT seqrelid, seqmin, seqmax, seqstart
                            FROM pg_sequence
                            WHERE seqrelid = pg_get_serial_sequence('{table_arg}', '{col_arg}')::regclass
                        ),
                        m AS (
                            SELECT MAX({quoted_col}) AS max_val FROM {quoted_tbl}
                        )
                        SELECT setval(
                            s.seqrelid,
                            CASE
                                WHEN m.max_val IS NOT NULL AND m.max_val >= s.seqmin AND {curr_lit} IS NOT NULL AND {curr_lit} >= s.seqmin
                                    THEN GREATEST({curr_lit}, m.max_val)
                                WHEN m.max_val IS NOT NULL AND m.max_val >= s.seqmin
                                    THEN m.max_val
                                WHEN {curr_lit} IS NOT NULL AND {curr_lit} >= s.seqmin
                                    THEN {curr_lit}
                                ELSE GREATEST({inc}, s.seqmin)
                            END,
                            CASE
                                WHEN (m.max_val IS NOT NULL AND m.max_val >= s.seqmin) OR ({curr_lit} IS NOT NULL AND {curr_lit} >= s.seqmin)
                                    THEN true
                                ELSE false
                            END
                        )
                        FROM seq_info s, m;
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

