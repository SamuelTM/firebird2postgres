import os
import tempfile
import unittest
from unittest.mock import MagicMock

import firebirdsql

from engine.ddl_exporter import DdlExporter
from engine.schema_extractor import (
    SchemaExtractor,
    fetch_all_sequence_increments,
    is_column_not_found_error,
)


class MockFirebirdError(firebirdsql.Error):
    def __init__(self, message, sql_code=None, gds_codes=None):
        super().__init__(message)
        self.sql_code = sql_code
        self.gds_codes = set(gds_codes) if gds_codes else set()


class TestSequenceIncrementFallbackRegression(unittest.TestCase):
    def test_is_column_not_found_error_distinguishes_column_from_other_errors(self):
        # Specific evidence only: -206 naming the column as unknown, or the
        # specific facility code 335544578 (dsql_field_err) with the name.
        err_sql_code = MockFirebirdError(
            "Dynamic SQL Error SQL error code = -206 Column unknown -RDB$GENERATOR_INCREMENT",
            sql_code=-206,
        )
        self.assertTrue(is_column_not_found_error(err_sql_code, "RDB$GENERATOR_INCREMENT"))

        err_gds_code = MockFirebirdError(
            "Dynamic SQL Error Column unknown RDB$GENERATOR_INCREMENT",
            sql_code=-206,
            gds_codes=[335544569, 335544578],
        )
        self.assertTrue(is_column_not_found_error(err_gds_code, "RDB$GENERATOR_INCREMENT"))

        err_msg = MockFirebirdError("Dynamic SQL Error: Column unknown RDB$GENERATOR_INCREMENT")
        self.assertTrue(is_column_not_found_error(err_msg, "RDB$GENERATOR_INCREMENT"))

        # The generic wrapper 335544569 alone proves nothing.
        err_generic_gds = MockFirebirdError("Dynamic SQL Error", gds_codes=[335544569])
        self.assertFalse(is_column_not_found_error(err_generic_gds, "RDB$GENERATOR_INCREMENT"))

        # -206 alone, without naming the column, is not specific evidence.
        err_bare_code = MockFirebirdError("Dynamic SQL Error", sql_code=-206)
        self.assertFalse(is_column_not_found_error(err_bare_code, "RDB$GENERATOR_INCREMENT"))

        # Permission errors must never allow fallback
        err_perm = MockFirebirdError("no permission for read access to COLUMN RDB$GENERATOR_INCREMENT", sql_code=-551)
        self.assertFalse(is_column_not_found_error(err_perm, "RDB$GENERATOR_INCREMENT"))

        err_priv = MockFirebirdError("user lacks privilege", gds_codes=[335544352])
        self.assertFalse(is_column_not_found_error(err_priv, "RDB$GENERATOR_INCREMENT"))

        # Connection errors must never allow fallback
        err_conn = MockFirebirdError("Unable to complete network request to host / connection lost")
        self.assertFalse(is_column_not_found_error(err_conn, "RDB$GENERATOR_INCREMENT"))

        # Non-firebirdsql error must never allow fallback
        self.assertFalse(is_column_not_found_error(RuntimeError("Unknown column"), "RDB$GENERATOR_INCREMENT"))

    def test_syntax_error_with_generic_wrapper_aborts_instead_of_fallback(self):
        """
        P1 regression: a -104 syntax error carries the generic 335544569
        wrapper. It must abort extraction, never fall back to increment 1.
        """
        syntax_err = MockFirebirdError(
            "Dynamic SQL Error SQL error code = -104 Token unknown",
            sql_code=-104,
            gds_codes=[335544569, 335544436],
        )
        self.assertFalse(
            is_column_not_found_error(syntax_err, "RDB$GENERATOR_INCREMENT"))

        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = syntax_err
        with self.assertRaises(RuntimeError) as cm:
            fetch_all_sequence_increments(mock_cursor)
        self.assertIn("Failed to fetch sequence increments from Firebird", str(cm.exception))
        # The fallback query must never run: only the failing statement.
        self.assertEqual(mock_cursor.execute.call_count, 1)

    def test_other_missing_column_aborts_instead_of_fallback(self):
        """
        P1 regression: -206 naming a DIFFERENT column is not evidence that
        RDB$GENERATOR_INCREMENT is absent. Extraction must abort.
        """
        other_col_err = MockFirebirdError(
            "Dynamic SQL Error SQL error code = -206 Column unknown -RDB$SOMETHING_ELSE",
            sql_code=-206,
            gds_codes=[335544569, 335544578],
        )
        self.assertFalse(
            is_column_not_found_error(other_col_err, "RDB$GENERATOR_INCREMENT"))

        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = other_col_err
        with self.assertRaises(RuntimeError) as cm:
            fetch_all_sequence_increments(mock_cursor)
        self.assertIn("Failed to fetch sequence increments from Firebird", str(cm.exception))

    def test_catalog_failure_aborts_instead_of_fallback(self):
        """
        P1 regression: a catalog failure with no column-unknown evidence
        (e.g. corrupt database) must halt extraction/export, not default.
        """
        catalog_err = MockFirebirdError("I/O error during read operation on database file")
        self.assertFalse(
            is_column_not_found_error(catalog_err, "RDB$GENERATOR_INCREMENT"))

        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = catalog_err
        with self.assertRaises(RuntimeError) as cm:
            fetch_all_sequence_increments(mock_cursor)
        self.assertIn("Failed to fetch sequence increments from Firebird", str(cm.exception))

    def test_fetch_all_sequence_increments_permits_fallback_only_on_column_not_found(self):
        mock_cursor = MagicMock()
        fb25_col_error = MockFirebirdError("Column unknown RDB$GENERATOR_INCREMENT", sql_code=-206)
        mock_cursor.execute.side_effect = [
            fb25_col_error,
            None,  # fallback query succeeds
        ]
        mock_cursor.fetchall.return_value = [
            ("GEN_LEGACY", 1),
        ]

        increments = fetch_all_sequence_increments(mock_cursor)
        self.assertEqual(increments, {"gen_legacy": 1})

    def test_fetch_all_sequence_increments_aborts_on_permission_error(self):
        mock_cursor = MagicMock()
        perm_error = MockFirebirdError("no permission for read access to TABLE RDB$GENERATORS", sql_code=-551)
        mock_cursor.execute.side_effect = perm_error

        with self.assertRaises(RuntimeError) as cm:
            fetch_all_sequence_increments(mock_cursor)
        self.assertIn("Failed to fetch sequence increments from Firebird", str(cm.exception))

    def test_fetch_all_sequence_increments_aborts_on_connection_error(self):
        mock_cursor = MagicMock()
        conn_error = MockFirebirdError("Connection reset by peer / network connection broken")
        mock_cursor.execute.side_effect = conn_error

        with self.assertRaises(RuntimeError) as cm:
            fetch_all_sequence_increments(mock_cursor)
        self.assertIn("Failed to fetch sequence increments from Firebird", str(cm.exception))

    def test_fetch_all_sequence_increments_aborts_on_invalid_increment(self):
        # String instead of int
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("GEN_TEST", "INVALID_VAL")]
        with self.assertRaises(ValueError) as cm:
            fetch_all_sequence_increments(mock_cursor)
        self.assertIn("must be a valid integer", str(cm.exception))

        # None / NULL increment
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("GEN_TEST", None)]
        with self.assertRaises(ValueError) as cm:
            fetch_all_sequence_increments(mock_cursor)
        self.assertIn("cannot be null", str(cm.exception))

        # Zero increment
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("GEN_TEST", 0)]
        with self.assertRaises(ValueError) as cm:
            fetch_all_sequence_increments(mock_cursor)
        self.assertIn("cannot be zero", str(cm.exception))

    def test_fetch_all_sequence_increments_accepts_positive_and_negative_increments(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            ("GEN_UP", 5),
            ("GEN_DOWN", -2),
        ]
        increments = fetch_all_sequence_increments(mock_cursor)
        self.assertEqual(increments["gen_up"], 5)
        self.assertEqual(increments["gen_down"], -2)

    def test_schema_extractor_sequences_fallback_and_aborts(self):
        mock_cursor = MagicMock()
        # Fallback on column unknown
        fb25_err = MockFirebirdError("Column unknown RDB$GENERATOR_INCREMENT", sql_code=-206)
        mock_cursor.execute.side_effect = [
            fb25_err,
            None,  # fallback query
            None,  # GEN_ID fetch
        ]
        mock_cursor.fetchall.return_value = [("GEN_A", 1)]
        mock_cursor.fetchone.return_value = (42,)

        seqs = SchemaExtractor._extract_sequences(mock_cursor)
        self.assertEqual(len(seqs), 1)
        self.assertEqual(seqs[0].increment, 1)

        # Abort on permission error
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = MockFirebirdError("No permission", sql_code=-551)
        with self.assertRaises(RuntimeError):
            SchemaExtractor._extract_sequences(mock_cursor)

        # Abort on zero increment
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("GEN_BAD", 0)]
        with self.assertRaises(ValueError) as cm:
            SchemaExtractor._extract_sequences(mock_cursor)
        self.assertIn("cannot be zero", str(cm.exception))

    def test_ddl_exporter_generators_fallback_and_aborts(self):
        mock_con = MagicMock()
        mock_cursor = MagicMock()
        mock_con.cursor.return_value = mock_cursor

        # Fallback on column unknown
        fb25_err = MockFirebirdError("Column unknown RDB$GENERATOR_INCREMENT", sql_code=-206)
        mock_cursor.execute.side_effect = [
            fb25_err,
            None,  # fallback query
            None,  # GEN_ID fetch
        ]
        mock_cursor.fetchall.return_value = [("GEN_OLD", 1)]
        mock_cursor.fetchone.return_value = (10,)

        exporter = DdlExporter(mock_con)
        with tempfile.TemporaryDirectory() as tmpdir:
            fb_out = os.path.join(tmpdir, "fb.sql")
            pg_out = os.path.join(tmpdir, "pg.sql")
            exporter.export_firebird_generators(fb_out, pg_out)
            with open(pg_out, "r") as f:
                content = f.read()
            self.assertIn('CREATE SEQUENCE "gen_old" START WITH 11;', content)

        # Abort on permission error
        mock_cursor = MagicMock()
        mock_con.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = MockFirebirdError("No privilege", sql_code=-551)
        with tempfile.TemporaryDirectory() as tmpdir:
            fb_out = os.path.join(tmpdir, "fb.sql")
            pg_out = os.path.join(tmpdir, "pg.sql")
            with self.assertRaises(RuntimeError):
                exporter.export_firebird_generators(fb_out, pg_out)

        # Abort on invalid increment (null or zero or string)
        for bad_inc in [None, 0, "bad"]:
            mock_cursor = MagicMock()
            mock_con.cursor.return_value = mock_cursor
            mock_cursor.fetchall.return_value = [("GEN_FAIL", bad_inc)]
            with tempfile.TemporaryDirectory() as tmpdir:
                fb_out = os.path.join(tmpdir, "fb.sql")
                pg_out = os.path.join(tmpdir, "pg.sql")
                with self.assertRaises(ValueError):
                    exporter.export_firebird_generators(fb_out, pg_out)


if __name__ == "__main__":
    unittest.main()
