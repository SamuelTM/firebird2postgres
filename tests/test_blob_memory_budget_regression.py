import io
import multiprocessing
import os
import tracemalloc
import unittest
from unittest.mock import MagicMock

from config import MigrationConfig
from engine.data_migrator import (
    DataMigrator,
    SerializedByteBuffer,
    _estimate_row_bytes,
    _import_single_table,
    is_blob_column,
    is_binary_column,
)
from engine.database_migrator import DatabaseMigrator
from models import Column, Table
from tests.db_isolation import (
    get_test_firebird_connection,
    require_live_firebird,
    requires_firebird,
    unique_name,
)


def _worker_measure_peak_memory(queue, blob_size, max_buffer_bytes, max_blob_bytes):
    """
    Runs in a dedicated spawned process to measure true peak memory allocation
    during single-table streaming import, verifying that 5x monolithic memory copies
    do not occur.
    """
    tracemalloc.start()
    try:
        table = Table('TAB_PEAK_TEST')
        table.columns.append(Column('ID', 'INTEGER', nullable=False))
        table.columns.append(Column('PAYLOAD', 'BLOB SUBTYPE 0', nullable=True))

        # 5MB deterministic binary payload
        raw_blob = os.urandom(blob_size)

        mock_fb_cur = MagicMock()
        mock_pg_cur = MagicMock()
        mock_pg_con = MagicMock()

        # Provide raw_blob as an io.BytesIO stream to test chunked streaming
        mock_fb_cur.fetchmany.side_effect = [[(1, io.BytesIO(raw_blob))], []]

        # Reset peak before running import
        tracemalloc.reset_peak()
        before_current, before_peak = tracemalloc.get_traced_memory()

        total_rows, nul_stats = _import_single_table(
            table,
            mock_fb_cur,
            mock_pg_cur,
            mock_pg_con,
            max_buffer_bytes=max_buffer_bytes,
            max_blob_bytes=max_blob_bytes
        )

        after_current, after_peak = tracemalloc.get_traced_memory()
        peak_delta = after_peak - before_current

        # Extract copied buffer content
        mock_pg_cur.copy_expert.assert_called_once()
        copy_sql, buf = mock_pg_cur.copy_expert.call_args[0]
        buf_val = buf.getvalue()

        expected_hex = r'\x' + raw_blob.hex()
        is_exact = expected_hex in buf_val

        queue.put({
            'success': True,
            'peak_delta': peak_delta,
            'is_exact': is_exact,
            'total_rows': total_rows
        })
    except Exception as exc:
        queue.put({
            'success': False,
            'error': str(exc)
        })
    finally:
        tracemalloc.stop()


class TestBlobMemoryBudgetRegression(unittest.TestCase):
    """
    Regression suite for:
    'Buffer em bytes não limita BLOB individual'
    Verifies:
    1. Accurate serialized byte counting for multibyte text and binary hex.
    2. Domain-based BLOBs receive full BLOB streaming treatment and size limits.
    3. Memory budget clearly distinguishes worker budget from total budget.
    4. Object size limits reject oversized BLOBs before materializing copies and trigger rollback.
    5. Rows with multiple BLOBs stream correctly and maintain bit-exact content.
    6. Peak memory in separate process stays strictly bounded (preventing 5x materialization copies).
    """

    def test_serialized_byte_counting_with_multibyte_text(self):
        """
        Criteria: Contagem considera bytes serializados.
        Verifies SerializedByteBuffer tracks exact UTF-8 byte length across multibyte text and escapes.
        """
        buf = SerializedByteBuffer()
        self.assertEqual(buf.byte_count, 0)

        # ASCII string
        buf.write("Hello")
        self.assertEqual(buf.byte_count, 5)

        # 2-byte UTF-8 characters (Portuguese accents)
        buf.write("Ação e Atenção")
        expected_bytes = len("Hello".encode('utf-8')) + len("Ação e Atenção".encode('utf-8'))
        self.assertEqual(buf.byte_count, expected_bytes)

        # 4-byte UTF-8 emojis
        buf.write(" 🚀🔥🐘 ")
        expected_bytes += len(" 🚀🔥🐘 ".encode('utf-8'))
        self.assertEqual(buf.byte_count, expected_bytes)

        # PostgreSQL escapes
        buf.write(r"\n\t\\")
        expected_bytes += len(r"\n\t\\".encode('utf-8'))
        self.assertEqual(buf.byte_count, expected_bytes)

        # Read back and verify exact byte content
        buf.seek(0)
        content = buf.getvalue()
        self.assertEqual(content, "HelloAção e Atenção 🚀🔥🐘 \\n\\t\\\\")

    def test_blob_sizes_small_near_limit_and_exceeding_rejection(self):
        """
        Criteria:
        - Definir uma alternativa: leitura em partes ou limite de objeto com rejeição explícita.
        - Se houver rejeição por tamanho, ela precisa ocorrer antes de materializar cópias completas;
          se o driver impedir isso, declarar o limite real.
        - Conteúdo copiado permanece exato.
        """
        table = Table('TAB_BLOB_LIMITS')
        table.columns.append(Column('ID', 'INTEGER', nullable=False))
        table.columns.append(Column('DADOS', 'BLOB SUBTYPE 0', nullable=True))

        limit_bytes = 1000
        mock_fb_cur = MagicMock()
        mock_pg_cur = MagicMock()
        mock_pg_con = MagicMock()

        # 1. Small BLOB (< limit): 100 bytes -> Imported successfully with exact content
        small_payload = b'S' * 100
        mock_fb_cur.fetchmany.side_effect = [[(1, small_payload)], []]
        total_rows, _ = _import_single_table(
            table, mock_fb_cur, mock_pg_cur, mock_pg_con,
            max_buffer_bytes=4096, max_blob_bytes=limit_bytes
        )
        self.assertEqual(total_rows, 1)
        mock_pg_cur.copy_expert.assert_called_once()
        buf = mock_pg_cur.copy_expert.call_args[0][1]
        self.assertIn(r'\x' + small_payload.hex(), buf.getvalue())

        # 2. Near limit BLOB: exactly limit_bytes (1000 bytes) -> Imported successfully
        mock_pg_cur.reset_mock()
        near_limit_payload = b'N' * limit_bytes
        mock_fb_cur.fetchmany.side_effect = [[(2, near_limit_payload)], []]
        total_rows, _ = _import_single_table(
            table, mock_fb_cur, mock_pg_cur, mock_pg_con,
            max_buffer_bytes=4096, max_blob_bytes=limit_bytes
        )
        self.assertEqual(total_rows, 1)
        mock_pg_cur.copy_expert.assert_called_once()
        buf = mock_pg_cur.copy_expert.call_args[0][1]
        self.assertIn(r'\x' + near_limit_payload.hex(), buf.getvalue())

        # 3. Exceeding limit BLOB: limit_bytes + 1 -> Explicit ValueError raised before materializing
        mock_pg_cur.reset_mock()
        exceeding_payload = b'E' * (limit_bytes + 1)
        mock_fb_cur.fetchmany.side_effect = [[(3, exceeding_payload)], []]
        with self.assertRaises(ValueError) as ctx:
            _import_single_table(
                table, mock_fb_cur, mock_pg_cur, mock_pg_con,
                max_buffer_bytes=4096, max_blob_bytes=limit_bytes
            )
        self.assertIn("exceeds maximum allowed size of 1000 bytes", str(ctx.exception))

        # 4. Exceeding limit via stream: stream must not be read into memory past the limit
        class CountingStream:
            def __init__(self, max_bytes_to_serve):
                self.bytes_read = 0
                self.max_bytes_to_serve = max_bytes_to_serve

            def read(self, size=65536):
                if self.bytes_read >= self.max_bytes_to_serve:
                    return b""
                chunk_len = min(size, self.max_bytes_to_serve - self.bytes_read)
                self.bytes_read += chunk_len
                return b'X' * chunk_len

        # Stream has 100,000 bytes, but limit is 1,000 bytes
        oversized_stream = CountingStream(100000)
        mock_fb_cur.fetchmany.side_effect = [[(4, oversized_stream)], []]
        with self.assertRaises(ValueError) as ctx:
            _import_single_table(
                table, mock_fb_cur, mock_pg_cur, mock_pg_con,
                max_buffer_bytes=4096, max_blob_bytes=limit_bytes
            )
        self.assertIn("exceeds maximum allowed size of 1000 bytes", str(ctx.exception))
        # Verify reading aborted early without reading the remaining 99,000 bytes
        self.assertLessEqual(oversized_stream.bytes_read, 65536 + 1024)

    def test_multiple_blobs_in_same_row(self):
        """
        Criteria:
        - Vários BLOBs na linha.
        - Conteúdo copiado permanece exato.
        """
        table = Table('TAB_MULTI_BLOB')
        table.columns.append(Column('ID', 'INTEGER', nullable=False))
        table.columns.append(Column('FOTO', 'BLOB SUBTYPE 0', nullable=True))
        table.columns.append(Column('AUDIO', 'BYTEA', nullable=True))
        table.columns.append(Column('CERT', 'OCTETS', nullable=True))

        blob1 = b'\x00\x01\x02\x03\xff'
        blob2 = b'RIFF\x24\x00\x00\x00WAVEfmt '
        blob3 = b'BEGIN CERTIFICATE\x00\xaa\xbb'

        mock_fb_cur = MagicMock()
        mock_pg_cur = MagicMock()
        mock_pg_con = MagicMock()

        mock_fb_cur.fetchmany.side_effect = [[(1, blob1, blob2, blob3)], []]

        total_rows, _ = _import_single_table(
            table, mock_fb_cur, mock_pg_cur, mock_pg_con,
            max_buffer_bytes=1024 * 1024, max_blob_bytes=512 * 1024
        )
        self.assertEqual(total_rows, 1)
        mock_pg_cur.copy_expert.assert_called_once()
        buf = mock_pg_cur.copy_expert.call_args[0][1]
        line = buf.getvalue().strip()

        parts = line.split('\t')
        self.assertEqual(len(parts), 4)
        self.assertEqual(parts[0], '1')
        self.assertEqual(parts[1], r'\\x' + blob1.hex())
        self.assertEqual(parts[2], r'\\x' + blob2.hex())
        self.assertEqual(parts[3], r'\\x' + blob3.hex())

    def test_domain_based_blob_treatment(self):
        """
        Criteria:
        - BLOB baseado em domain recebe tratamento de BLOB.
        - Detecção, fetch_size=1, LPT scheduling, streaming e limite de tamanho.
        """
        col_direct = Column('DOC_DIRECT', 'BLOB SUBTYPE 0', nullable=True)
        col_domain = Column('DOC_DOMAIN', 'TEXT', nullable=True, domain_name='DM_ANEXO')
        col_regular = Column('NOME', 'VARCHAR(100)', nullable=True, domain_name='DM_NOME')

        blob_domains = {'DM_ANEXO', 'DM_DOCUMENTO'}

        self.assertTrue(is_blob_column(col_direct, blob_domains))
        self.assertTrue(is_blob_column(col_domain, blob_domains))
        self.assertFalse(is_blob_column(col_regular, blob_domains))

        # Verify case insensitivity in domain matching
        col_domain_lower = Column('ARQ', 'TEXT', nullable=True, domain_name='dm_anexo')
        self.assertTrue(is_blob_column(col_domain_lower, blob_domains))

        # Test table with domain BLOB uses fetch_size=1 and enforces max_blob_bytes
        table = Table('TAB_DOMAIN_BLOB')
        table.columns.append(Column('ID', 'INTEGER', nullable=False))
        table.columns.append(col_domain)

        mock_fb_cur = MagicMock()
        mock_pg_cur = MagicMock()
        mock_pg_con = MagicMock()

        mock_fb_cur.fetchmany.return_value = []
        _import_single_table(
            table, mock_fb_cur, mock_pg_cur, mock_pg_con,
            blob_domains=blob_domains
        )
        mock_fb_cur.fetchmany.assert_called_with(1)

        # Verify size rejection on domain-based BLOB column
        oversized = b'D' * 2000
        mock_fb_cur.fetchmany.side_effect = [[(1, oversized)], []]
        with self.assertRaises(ValueError) as ctx:
            _import_single_table(
                table, mock_fb_cur, mock_pg_cur, mock_pg_con,
                max_blob_bytes=1000, blob_domains=blob_domains
            )
        self.assertIn("exceeds maximum allowed size of 1000 bytes", str(ctx.exception))

    def test_textual_blob_direct_and_domain_preserves_accents_emojis_tabs_newlines_and_sanitizes_nul(self):
        """
        Regression for:
        'BLOB textual é carregado como hexadecimal'
        Verifies:
        1. Textual BLOB (BLOB SUBTYPE 1) and domain-based text BLOB are NEVER converted to hex (\\x).
        2. Accents ('Olá'), emojis ('🙂'), tabs ('\\t'), newlines ('\\n') are preserved 100% exact.
        3. NUL (0x00) bytes are stripped and audited in nul_stats.
        4. No UnicodeEncodeError occurs on emojis.
        """
        table = Table('TAB_TEXT_BLOB')
        table.columns.append(Column('ID', 'INTEGER', nullable=False))
        table.columns.append(Column('COL_TEXT_DIRECT', 'BLOB SUBTYPE 1', nullable=True))
        table.columns.append(Column('COL_TEXT_DOMAIN', 'TEXT', nullable=True, domain_name='DM_OBS_TEXT'))

        blob_domains = {'DM_OBS_TEXT'}
        binary_domains = set()  # DM_OBS_TEXT is text, not binary

        # Test value with accents, emojis, newlines, tabs, and embedded NUL bytes
        raw_text = "Olá mundo! 🙂\nSegunda linha\tcom tab\x00e NUL\x00e acentuação: Atenção & Coração"
        expected_cleaned = "Olá mundo! 🙂\nSegunda linha\tcom tabe NULe acentuação: Atenção & Coração"

        mock_fb_cur = MagicMock()
        mock_pg_cur = MagicMock()
        mock_pg_con = MagicMock()

        # Row 1: string values
        # Row 2: stream values (io.StringIO and io.BytesIO containing emojis)
        row1 = (1, raw_text, raw_text)
        row2 = (2, io.StringIO(raw_text), io.BytesIO(raw_text.encode('utf-8')))

        mock_fb_cur.fetchmany.side_effect = [[row1], [row2], []]

        total_rows, nul_stats = _import_single_table(
            table, mock_fb_cur, mock_pg_cur, mock_pg_con,
            blob_domains=blob_domains,
            binary_domains=binary_domains
        )

        self.assertEqual(total_rows, 2)
        # NUL stats: 2 NUL bytes per column per row = 4 per column
        self.assertEqual(nul_stats.get('COL_TEXT_DIRECT'), 4)
        self.assertEqual(nul_stats.get('COL_TEXT_DOMAIN'), 4)

        # Inspect COPY buffer output
        self.assertEqual(mock_pg_cur.copy_expert.call_count, 1)
        buf = mock_pg_cur.copy_expert.call_args[0][1]
        buffer_content = buf.getvalue()

        # 1. Must NOT contain hex prefix for text columns
        self.assertNotIn(r'\\x', buffer_content)

        # 2. Must contain properly escaped text with emojis and accents
        expected_escaped = expected_cleaned.replace('\\', '\\\\').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
        self.assertIn("Olá mundo! 🙂", buffer_content)
        self.assertIn("Atenção & Coração", buffer_content)
        self.assertIn(expected_escaped, buffer_content)

        # 3. Must not contain raw NUL bytes
        self.assertNotIn('\x00', buffer_content)

    def test_binary_blob_separated_from_textual_blob(self):
        """
        Criteria:
        - Separar 'objeto grande' de 'tipo binário'.
        - Testar BLOB binário separadamente, garantindo formato \\x<hex>.
        """
        table = Table('TAB_SEPARATION')
        table.columns.append(Column('ID', 'INTEGER', nullable=False))
        table.columns.append(Column('FOTO_BIN', 'BLOB SUBTYPE 0', nullable=True))
        table.columns.append(Column('OBS_TEXT', 'BLOB SUBTYPE 1', nullable=True))
        table.columns.append(Column('ARQ_DOM_BIN', 'BYTEA', nullable=True, domain_name='DM_ARQ_BIN'))
        table.columns.append(Column('NOTA_DOM_TEXT', 'TEXT', nullable=True, domain_name='DM_NOTA_TEXT'))

        blob_domains = {'DM_ARQ_BIN', 'DM_NOTA_TEXT'}
        binary_domains = {'DM_ARQ_BIN'}

        bin_data = b'\xde\xad\xbe\xef\x00\xff'
        text_data = "Texto de observação com acento: 'Último' e emoji 🙂\tcom tab\ncom newline"

        mock_fb_cur = MagicMock()
        mock_pg_cur = MagicMock()
        mock_pg_con = MagicMock()

        mock_fb_cur.fetchmany.side_effect = [[(1, bin_data, text_data, bin_data, text_data)], []]

        total_rows, _ = _import_single_table(
            table, mock_fb_cur, mock_pg_cur, mock_pg_con,
            blob_domains=blob_domains,
            binary_domains=binary_domains
        )
        self.assertEqual(total_rows, 1)

        mock_pg_cur.copy_expert.assert_called_once()
        buf = mock_pg_cur.copy_expert.call_args[0][1]
        line = buf.getvalue().strip()
        parts = line.split('\t')

        self.assertEqual(len(parts), 5)
        self.assertEqual(parts[0], '1')

        # Binary columns: must be hex formatted with \\x prefix
        expected_hex = r'\\x' + bin_data.hex()
        self.assertEqual(parts[1], expected_hex)
        self.assertEqual(parts[3], expected_hex)

        # Textual columns: must NOT be hex formatted, but escaped UTF-8 text
        expected_text = text_data.replace('\\', '\\\\').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
        self.assertEqual(parts[2], expected_text)
        self.assertEqual(parts[4], expected_text)

    def test_is_binary_column_vs_is_blob_column_separation(self):
        """
        Verifies helper classification separating large objects (LOB) from binary types.
        """
        # Textual BLOB: LOB = True, Binary = False
        col_text_blob = Column('T1', 'BLOB SUBTYPE 1', nullable=True)
        self.assertTrue(is_blob_column(col_text_blob))
        self.assertFalse(is_binary_column(col_text_blob))

        col_text_blob_alt = Column('T2', 'BLOB SUBTYPE TEXT', nullable=True)
        self.assertTrue(is_blob_column(col_text_blob_alt))
        self.assertFalse(is_binary_column(col_text_blob_alt))

        # Binary BLOB: LOB = True, Binary = True
        col_bin_blob = Column('B1', 'BLOB SUBTYPE 0', nullable=True)
        self.assertTrue(is_blob_column(col_bin_blob))
        self.assertTrue(is_binary_column(col_bin_blob))

        col_bytea = Column('B2', 'BYTEA', nullable=True)
        self.assertTrue(is_blob_column(col_bytea))
        self.assertTrue(is_binary_column(col_bytea))

        col_octets = Column('B3', 'CHAR(16) CHARACTER SET OCTETS', nullable=True)
        self.assertTrue(is_blob_column(col_octets))
        self.assertTrue(is_binary_column(col_octets))

        # Regular text: LOB = False, Binary = False
        col_varchar = Column('V1', 'VARCHAR(255)', nullable=True)
        self.assertFalse(is_blob_column(col_varchar))
        self.assertFalse(is_binary_column(col_varchar))

        # Domain classification
        col_dom_text = Column('D1', 'TEXT', nullable=True, domain_name='DM_TEXT')
        col_dom_bin = Column('D2', 'BYTEA', nullable=True, domain_name='DM_BIN')
        blob_domains = {'DM_TEXT', 'DM_BIN'}
        binary_domains = {'DM_BIN'}

        self.assertTrue(is_blob_column(col_dom_text, blob_domains))
        self.assertFalse(is_binary_column(col_dom_text, binary_domains))

        self.assertTrue(is_blob_column(col_dom_bin, blob_domains))
        self.assertTrue(is_binary_column(col_dom_bin, binary_domains))

    def test_memory_budget_distinguishes_total_from_worker(self):
        """
        Criteria:
        - Orçamento distingue memória por worker de memória total.
        """
        # Case 1: Defaults (4 workers)
        total, worker, blob_lim = DataMigrator.calculate_memory_budget(max_workers=4)
        self.assertEqual(worker, 32 * 1024 * 1024)
        self.assertEqual(total, 4 * 32 * 1024 * 1024)
        self.assertEqual(blob_lim, (worker - 1024) // 2)

        # Case 2: Total budget specified (e.g. 128MB total across 8 workers)
        total, worker, blob_lim = DataMigrator.calculate_memory_budget(
            max_workers=8, total_budget=128 * 1024 * 1024
        )
        self.assertEqual(total, 128 * 1024 * 1024)
        self.assertEqual(worker, 16 * 1024 * 1024)
        self.assertEqual(blob_lim, (worker - 1024) // 2)

        # Case 3: Per-worker budget explicitly specified (e.g. 64MB per worker, 4 workers)
        total, worker, blob_lim = DataMigrator.calculate_memory_budget(
            max_workers=4, per_worker_budget=64 * 1024 * 1024
        )
        self.assertEqual(worker, 64 * 1024 * 1024)
        self.assertEqual(total, 256 * 1024 * 1024)

        # Case 4: Explicit max_blob_bytes override
        total, worker, blob_lim = DataMigrator.calculate_memory_budget(
            max_workers=2,
            total_budget=64 * 1024 * 1024,
            max_blob_bytes=8 * 1024 * 1024
        )
        self.assertEqual(blob_lim, 8 * 1024 * 1024)

    def test_database_migrator_wires_blob_domains_and_config(self):
        """
        Criteria:
        - Integrates DatabaseMigrator, querying Firebird for domain BLOBs
          and propagating configured budgets to DataMigrator.
        """
        mock_fb_con = MagicMock()
        mock_pg_con = MagicMock()
        mock_fb_cur = MagicMock()
        mock_fb_con.cursor.return_value = mock_fb_cur

        # Mock catalog query for BLOB domains
        mock_fb_cur.fetchall.return_value = [
            ('DM_DOCUMENTO_PDF',),
            ('DM_FOTO_ALUNO',)
        ]

        cfg = MigrationConfig(
            total_memory_budget_bytes=256 * 1024 * 1024,
            max_buffer_bytes_per_worker=32 * 1024 * 1024,
            max_blob_bytes=10 * 1024 * 1024
        )

        migrator = DatabaseMigrator(mock_fb_con, mock_pg_con, config=cfg)
        domains = migrator._get_blob_domains()
        self.assertIn('DM_DOCUMENTO_PDF', domains)
        self.assertIn('DM_FOTO_ALUNO', domains)

        # Mock data_migrator.import_data
        migrator.data_migrator.import_data = MagicMock(return_value=True)
        migrator.table_objs = [Table('T1')]

        success = migrator.import_data(max_workers=4)
        self.assertTrue(success)

        migrator.data_migrator.import_data.assert_called_once()
        kwargs = migrator.data_migrator.import_data.call_args[1]
        self.assertEqual(kwargs['total_memory_budget'], 256 * 1024 * 1024)
        self.assertEqual(kwargs['per_worker_budget'], 32 * 1024 * 1024)
        self.assertEqual(kwargs['max_blob_bytes'], 10 * 1024 * 1024)
        self.assertIn('DM_DOCUMENTO_PDF', kwargs['blob_domains'])

    def test_peak_memory_in_separate_process_bounds_blob_materialization(self):
        """
        Criteria:
        - Medir pico de memória em processo separado e verificar conteúdo/rollback.
        - Comprovar que 5 cópias completas do BLOB não são materializadas na memória.
        """
        blob_size = 4 * 1024 * 1024  # 4MB raw blob
        max_buffer = 16 * 1024 * 1024
        max_blob = 8 * 1024 * 1024

        queue = multiprocessing.Queue()
        p = multiprocessing.Process(
            target=_worker_measure_peak_memory,
            args=(queue, blob_size, max_buffer, max_blob)
        )
        p.start()
        res = queue.get(timeout=30)
        p.join()

        self.assertTrue(res.get('success'), f"Subprocess failed: {res.get('error')}")
        self.assertTrue(res.get('is_exact'), "Copied BLOB content was corrupted or inexact!")
        self.assertEqual(res.get('total_rows'), 1)

        peak_delta = res.get('peak_delta')
        # In the old code:
        # raw (4MB) + read (4MB) + hex (8MB) + row_str (8MB) + encode (8MB) = ~32MB memory churn.
        # With chunked streaming directly to SerializedByteBuffer:
        # Only the raw stream + buffer are needed.
        # Serialized hex is 8MB in the buffer.
        # Peak memory delta must be well under 20MB (significantly less than 5x 4MB = 20-32MB).
        self.assertLess(
            peak_delta,
            20 * 1024 * 1024,
            f"Peak memory delta ({peak_delta / (1024 * 1024):.2f}MB) exceeded budget threshold!"
        )

    def test_incompatible_total_and_per_worker_rejected(self):
        """
        P2: total de 128 MiB com oito workers a 32 MiB/worker (256 MiB)
        deve ser rejeitado em vez de silenciosamente permitir estouro.
        """
        with self.assertRaises(ValueError) as ctx:
            DataMigrator.calculate_memory_budget(
                max_workers=8,
                total_budget=128 * 1024 * 1024,
                per_worker_budget=32 * 1024 * 1024,
            )
        self.assertIn("exceeds total budget", str(ctx.exception))

        # Blob serializado (~2x) maior que o worker também é incompatível.
        with self.assertRaises(ValueError) as ctx:
            DataMigrator.calculate_memory_budget(
                max_workers=2,
                total_budget=64 * 1024 * 1024,
                per_worker_budget=32 * 1024 * 1024,
                max_blob_bytes=32 * 1024 * 1024,
            )
        self.assertIn("exceeds", str(ctx.exception))

        # Linha máxima maior que o worker é incompatível.
        with self.assertRaises(ValueError):
            DataMigrator.calculate_memory_budget(
                max_workers=4,
                total_budget=128 * 1024 * 1024,
                per_worker_budget=32 * 1024 * 1024,
                max_row_bytes=64 * 1024 * 1024,
            )

    def test_eight_workers_under_smaller_budget(self):
        """
        Regressão: oito workers sob orçamento menor — o per-worker deriva
        do total e configurações impossíveis são rejeitadas; import_data
        propaga o erro antes de qualquer operação destrutiva.
        """
        total, worker, _ = DataMigrator.calculate_memory_budget(
            max_workers=8, total_budget=64 * 1024 * 1024
        )
        self.assertEqual(total, 64 * 1024 * 1024)
        self.assertEqual(worker, 8 * 1024 * 1024)
        self.assertLessEqual(8 * worker, total)

        # Orçamento impossivelmente pequeno para 8 workers (>=1 MiB/worker).
        with self.assertRaises(ValueError):
            DataMigrator.calculate_memory_budget(
                max_workers=8, total_budget=4 * 1024 * 1024
            )

        # import_data deve propagar a incompatibilidade sem desabilitar triggers.
        mock_fb_con = MagicMock()
        mock_pg_con = MagicMock()
        mock_fb_cur = MagicMock()
        mock_pg_cur = MagicMock()
        mock_fb_con.cursor.return_value = mock_fb_cur
        mock_pg_con.cursor.return_value = mock_pg_cur
        mock_fb_cur.fetchone.side_effect = [(1, 0), (0,)]
        migrator = DataMigrator(mock_fb_con, mock_pg_con)
        with self.assertRaises(ValueError):
            migrator.import_data(
                [Table('T1')],
                max_workers=8,
                total_memory_budget=128 * 1024 * 1024,
                per_worker_budget=32 * 1024 * 1024,
            )
        executed = [c[0][0] for c in mock_pg_cur.execute.call_args_list] if mock_pg_cur.execute.call_args_list else []
        self.assertNotIn('DISABLE TRIGGER ALL', str(executed))

    def test_multiple_blobs_in_same_row_enforce_row_cap(self):
        """
        Regressão: vários BLOBs individualmente válidos na mesma linha não
        podem acumular além do buffer do worker antes do flush.
        """
        table = Table('TAB_MULTI_ROW_CAP')
        table.columns.append(Column('ID', 'INTEGER', nullable=False))
        table.columns.append(Column('B1', 'BLOB SUBTYPE 0', nullable=True))
        table.columns.append(Column('B2', 'BLOB SUBTYPE 0', nullable=True))

        # Cada BLOB respeita o limite individual (3KB < 4KB) mas a linha
        # serializada (~12KB hex) excede o worker de 8KB.
        mock_fb_cur = MagicMock()
        mock_pg_cur = MagicMock()
        mock_pg_con = MagicMock()
        mock_fb_cur.fetchmany.side_effect = [[(1, b'A' * 3000, b'B' * 3000)], []]
        with self.assertRaises(ValueError) as ctx:
            _import_single_table(
                table, mock_fb_cur, mock_pg_cur, mock_pg_con,
                max_buffer_bytes=8 * 1024, max_blob_bytes=4 * 1024,
            )
        self.assertIn("exceeds per-worker buffer", str(ctx.exception))
        mock_pg_con.commit.assert_not_called()

        # Linha que cabe deve copiar conteúdo exato.
        mock_fb_cur2 = MagicMock()
        mock_pg_cur2 = MagicMock()
        mock_fb_cur2.fetchmany.side_effect = [[(1, b'A' * 100, b'B' * 100)], []]
        rows, _ = _import_single_table(
            table, mock_fb_cur2, mock_pg_cur2, mock_pg_con,
            max_buffer_bytes=8 * 1024, max_blob_bytes=4 * 1024,
        )
        self.assertEqual(rows, 1)
        buf = mock_pg_cur2.copy_expert.call_args[0][1]
        self.assertIn(r'\\x' + (b'A' * 100).hex(), buf.getvalue())
        self.assertIn(r'\\x' + (b'B' * 100).hex(), buf.getvalue())

    def test_aggregated_peak_across_workers_bounded_by_total(self):
        """
        Regressão: pico agregado dos processos (soma dos picos por worker)
        deve caber no orçamento total, não apenas o pico individual.
        """
        blob_size = 1 * 1024 * 1024
        per_worker = 8 * 1024 * 1024
        max_blob = 4 * 1024 * 1024
        workers = 2
        total, worker_bytes, _ = DataMigrator.calculate_memory_budget(
            max_workers=workers,
            total_budget=workers * per_worker,
            per_worker_budget=per_worker,
            max_blob_bytes=max_blob,
        )
        self.assertLessEqual(workers * worker_bytes, total)

        queue = multiprocessing.Queue()
        procs = [
            multiprocessing.Process(
                target=_worker_measure_peak_memory,
                args=(queue, blob_size, per_worker, max_blob),
            )
            for _ in range(workers)
        ]
        for p in procs:
            p.start()
        results = [queue.get(timeout=30) for _ in procs]
        for p in procs:
            p.join()

        for res in results:
            self.assertTrue(res.get('success'), f"Subprocess failed: {res.get('error')}")
            self.assertTrue(res.get('is_exact'))
        agg_peak = sum(r.get('peak_delta', 0) for r in results)
        self.assertLessEqual(
            agg_peak, total,
            f"Aggregated peak ({agg_peak / (1024*1024):.2f}MB) exceeds total budget "
            f"({total / (1024*1024):.2f}MB)!",
        )

    def test_estimate_is_upper_bound_for_unicode_text(self):
        """
        P2: 3 bytes/char underestimates 4-byte emoji. The estimator must be
        a guaranteed upper bound of the serialized bytes on every branch.
        """
        cases = [
            'plain ascii',
            'back\\slash\ttab\nnewline\rcarriage',
            'Ação e Atenção à兄弟',  # 2- and 3-byte chars
            '🚀🔥🐘' * 50,  # 4-byte emoji
            'mix 🚀 text\nwith\tescapes e acentuação çãõ',
            'NUL\x00inside\x00text',
            'x"quoted" \'sq\' \\ end',
        ]
        for col_type in ('VARCHAR(5000)', 'BLOB SUBTYPE 1'):
            for text in cases:
                table = Table('TAB_EST')
                table.columns.append(Column('ID', 'INTEGER', nullable=False))
                table.columns.append(Column('TXT', col_type, nullable=True))
                mock_fb_cur = MagicMock()
                mock_pg_cur = MagicMock()
                mock_pg_con = MagicMock()
                mock_fb_cur.fetchmany.side_effect = [[(1, text)], []]
                estimate = _estimate_row_bytes((1, text), 32 * 1024 * 1024)
                rows, _ = _import_single_table(
                    table, mock_fb_cur, mock_pg_cur, mock_pg_con,
                    max_buffer_bytes=64 * 1024 * 1024,
                    max_blob_bytes=32 * 1024 * 1024,
                )
                self.assertEqual(rows, 1)
                buf = mock_pg_cur.copy_expert.call_args[0][1]
                self.assertLessEqual(
                    buf.byte_count, estimate,
                    f"Estimate {estimate} below actual {buf.byte_count} for {col_type} {text[:20]!r}",
                )

    def test_copy_buffers_never_exceed_budget_unicode_and_multi_blob(self):
        """
        P2: the 1203-bytes-delivered-on-1150-limit hole. Across several
        flushes mixing emoji text and multiple binary BLOBs per row, every
        buffer handed to COPY must stay within the worker budget.
        """
        table = Table('TAB_CAP')
        table.columns.append(Column('ID', 'INTEGER', nullable=False))
        table.columns.append(Column('TXT', 'BLOB SUBTYPE 1', nullable=True))
        table.columns.append(Column('A', 'BLOB SUBTYPE 0', nullable=True))
        table.columns.append(Column('B', 'BLOB SUBTYPE 0', nullable=True))

        max_buffer = 1150
        # ~300B text (emoji-heavy) + 2x150B blobs serialize to ~920B/row.
        rows = [
            (1, 'Olá 🚀 mundo ' * 20, b'A' * 150, b'B' * 150),
            (2, 'Linha 🔥 dois ' * 20, b'C' * 150, b'D' * 150),
            (3, 'Linha 🐘 três ' * 20, b'E' * 150, b'F' * 150),
        ]
        mock_fb_cur = MagicMock()
        mock_pg_cur = MagicMock()
        mock_pg_con = MagicMock()
        mock_fb_cur.fetchmany.side_effect = [rows, []]

        total, _ = _import_single_table(
            table, mock_fb_cur, mock_pg_cur, mock_pg_con,
            max_buffer_bytes=max_buffer, max_blob_bytes=500,
        )
        self.assertEqual(total, 3)
        # Several incremental flushes happened...
        self.assertGreaterEqual(mock_pg_cur.copy_expert.call_count, 2)
        # ...and none delivered a buffer above the limit.
        for call in mock_pg_cur.copy_expert.call_args_list:
            buf = call[0][1]
            self.assertLessEqual(
                buf.byte_count, max_buffer,
                f"COPY buffer of {buf.byte_count} bytes exceeds {max_buffer} budget",
            )
        # Exact content survived the chunked path (emoji roundtrip).
        combined = ''.join(c[0][1].getvalue() for c in mock_pg_cur.copy_expert.call_args_list)
        self.assertIn('Olá 🚀 mundo', combined.replace('\\n', '\n'))


class _FakePgCur:
    """Minimal COPY-capturing cursor (spawn-picklable, no PG server needed)."""

    def __init__(self):
        self.copies = []
        self.executed = []

    def execute(self, sql, params=None):
        self.executed.append(sql)

    def copy_expert(self, sql, buf):
        buf.seek(0)
        self.copies.append(buf.getvalue())


class _FakePgConn:
    """Minimal connection stub around _FakePgCur."""

    def __init__(self):
        self.cur = _FakePgCur()
        self.commits = 0

    def cursor(self):
        return self.cur

    def commit(self):
        self.commits += 1

    def rollback(self):
        pass


class _CountingFbCur:
    """Wraps a real Firebird cursor counting fetchmany calls (built in-child)."""

    def __init__(self, real_cur):
        self._cur = real_cur
        self.fetchmany_calls = 0

    def execute(self, *args, **kwargs):
        return self._cur.execute(*args, **kwargs)

    def fetchmany(self, size):
        self.fetchmany_calls += 1
        return self._cur.fetchmany(size)

    def fetchone(self):
        return self._cur.fetchone()

    def fetchall(self):
        return self._cur.fetchall()


def _rss_peak_bytes():
    """Peak RSS of this process in bytes (ru_maxrss units differ per OS)."""
    import resource
    import sys
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return peak if sys.platform == 'darwin' else peak * 1024


def _child_real_driver_import(queue, table_name, max_buffer_bytes, max_blob_bytes):
    """
    Spawn target: runs _import_single_table with the REAL Firebird driver
    (which materializes BLOBs inside fetchmany) and a fake PG side, so the
    measured peak covers driver read + serialization + COPY buffering.
    Reports RSS peak delta, fetchmany count and copied content.
    """
    from engine.data_migrator import _import_single_table
    from models import Column, Table
    from tests.db_isolation import get_test_firebird_connection

    table = Table(table_name)
    table.columns.append(Column('ID', 'INTEGER', nullable=False))
    table.columns.append(Column('PAYLOAD', 'BLOB SUBTYPE 0', nullable=True))

    fb_con = get_test_firebird_connection()
    fb_cur = _CountingFbCur(fb_con.cursor())
    pg_con = _FakePgConn()
    baseline = _rss_peak_bytes()
    try:
        rows, _ = _import_single_table(
            table, fb_cur, pg_con.cur, pg_con,
            max_buffer_bytes=max_buffer_bytes,
            max_blob_bytes=max_blob_bytes,
        )
        copies = list(pg_con.cur.copies)
        queue.put({
            'success': True,
            'rows': rows,
            'peak_delta': _rss_peak_bytes() - baseline,
            'fetchmany_calls': fb_cur.fetchmany_calls,
            'copy_sizes': [len(c.encode('utf-8')) for c in copies],
            'copy_count': len(copies),
            'head_hex': copies[0][:256] if copies else '',
        })
    except Exception as exc:
        queue.put({
            'success': False,
            'error': f"{type(exc).__name__}: {exc}",
            'peak_delta': _rss_peak_bytes() - baseline,
            'fetchmany_calls': fb_cur.fetchmany_calls,
        })
    finally:
        try:
            fb_con.close()
        except Exception:
            pass


class TestRealDriverMemoryBudget(unittest.TestCase):
    """
    P2: BytesIO/tracemalloc cannot prove the real-driver path, whose C
    allocations tracemalloc never sees and which materializes whole BLOBs
    in fetchmany. These spawn a fresh process, drive the REAL Firebird
    driver through read + serialization + COPY buffering, and bound the
    RSS peak delta.
    """

    def _make_blob_table(self, payload_bytes):
        from tests.db_isolation import get_test_firebird_connection as _connect
        fb_con = _connect()
        try:
            table_name = unique_name('MEM_BLOB').upper()
            cur = fb_con.cursor()
            cur.execute(f"CREATE TABLE {table_name} (ID INTEGER, PAYLOAD BLOB SUB_TYPE 0)")
            fb_con.commit()
            cur.execute(f"INSERT INTO {table_name} VALUES (?, ?)", (1, payload_bytes))
            fb_con.commit()
        finally:
            try:
                fb_con.close()
            except Exception:
                pass
        return table_name

    def _drop_blob_table(self, table_name):
        from tests.db_isolation import get_test_firebird_connection as _connect
        # Fresh connection: the loader connection caches prepared statements
        # keeping an "interest" that would block DROP TABLE as "in use".
        fb_con = _connect()
        try:
            cur = fb_con.cursor()
            cur.execute(f"DROP TABLE {table_name}")
            fb_con.commit()
        finally:
            try:
                fb_con.close()
            except Exception:
                pass

    def _run_child(self, table_name, max_buffer_bytes, max_blob_bytes):
        ctx = multiprocessing.get_context('spawn')
        queue = ctx.Queue()
        proc = ctx.Process(
            target=_child_real_driver_import,
            args=(queue, table_name, max_buffer_bytes, max_blob_bytes),
        )
        proc.start()
        try:
            return queue.get(timeout=180)
        finally:
            proc.join(timeout=60)

    @requires_firebird
    def test_real_driver_import_bounds_rss_peak(self):
        """
        2 MiB BLOB through the real driver: read + hex serialization + COPY
        buffering peak stays bounded (bytes + hex + buffer + driver copy).
        """
        blob = os.urandom(2 * 1024 * 1024)
        table_name = self._make_blob_table(blob)
        try:
            res = self._run_child(table_name, 8 * 1024 * 1024, 4 * 1024 * 1024)
        finally:
            self._drop_blob_table(table_name)
        self.assertTrue(res.get('success'), f"Child failed: {res.get('error')}")
        self.assertEqual(res.get('rows'), 1)
        self.assertLess(
            res.get('peak_delta'), 48 * 1024 * 1024,
            f"RSS peak delta ({res['peak_delta'] / (1024 * 1024):.1f}MiB) exceeds bound "
            f"for a 2MiB BLOB under an 8MiB worker budget",
        )
        self.assertLessEqual(max(res.get('copy_sizes')), 8 * 1024 * 1024)
        self.assertIn(blob.hex()[:64], res.get('head_hex'))

    @requires_firebird
    def test_real_driver_rejects_oversized_blob_before_materialization(self):
        """
        3 MiB stored BLOB with a 1 MiB limit: the server-side MAX pre-check
        rejects before fetchmany ever runs, so the driver never allocates
        the blob and the RSS peak stays flat.
        """
        blob = os.urandom(3 * 1024 * 1024)
        table_name = self._make_blob_table(blob)
        try:
            res = self._run_child(table_name, 8 * 1024 * 1024, 1 * 1024 * 1024)
        finally:
            self._drop_blob_table(table_name)
        self.assertFalse(res.get('success'))
        self.assertIn('exceeds maximum allowed size', res.get('error'))
        self.assertEqual(
            res.get('fetchmany_calls'), 0,
            "Oversized BLOB must be rejected before any fetchmany materializes it",
        )
        self.assertLess(
            res.get('peak_delta'), 2 * 1024 * 1024,
            f"RSS peak delta ({res['peak_delta'] / (1024 * 1024):.2f}MiB) shows "
            f"the 3MiB BLOB was materialized despite the limit",
        )


if __name__ == '__main__':
    unittest.main()
