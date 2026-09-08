import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from config import DumpFiles
from engine.database_migrator import DatabaseMigrator
from engine.ddl_exporter import DdlExporter
from utils.sql_runner import SqlRunner


class TestEmptyCategoryRegression(unittest.TestCase):
    """
    Regression tests for distinguishing legitimately empty categories from
    missing, truncated, or comment-only dumps BEFORE destination teardown.
    """

    def setUp(self):
        self.mock_fb = MagicMock()
        self.mock_pg = MagicMock()
        self.mock_cur_pg = MagicMock()
        self.mock_pg.cursor.return_value = self.mock_cur_pg
        self.migrator = DatabaseMigrator(self.mock_fb, self.mock_pg)

    def test_comments_and_headers_do_not_count_as_exported_objects(self):
        """Header comments and banners must produce 0 executable statements."""
        with tempfile.NamedTemporaryFile("w+", suffix=".sql", delete=False) as f:
            f.write("/* POSTGRESQL DOMAINS DUMP (CONVERTED) */\n\n-- Just a banner\n/* multi\nline\ncomment */\n")
            f_path = f.name
        self.addCleanup(os.remove, f_path)

        runner = SqlRunner(self.mock_pg)
        count = runner.count_statements(f_path)
        self.assertEqual(count, 0)

        # When objects were expected, header-only file must raise ValueError
        with self.assertRaises(ValueError) as ctx:
            runner.validate_file(f_path, expected_count=3, allow_empty=False)
        self.assertIn("contains 0 executable statements (empty or comments only), but 3 objects were expected",
                      str(ctx.exception))

    def test_legitimate_empty_category_does_not_interrupt_migration(self):
        """When Firebird has 0 objects in a category, allow_empty is derived and migration succeeds."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create dump files: domains empty (header only), procedures has 1 statement
            domains_file = os.path.join(tmpdir, DumpFiles.DOMAINS_PG)
            with open(domains_file, "w", encoding="utf-8") as f:
                f.write("/* POSTGRESQL DOMAINS DUMP (CONVERTED) */\n")

            procs_file = os.path.join(tmpdir, DumpFiles.PROCEDURES_PG)
            with open(procs_file, "w", encoding="utf-8") as f:
                f.write("CREATE OR REPLACE FUNCTION foo() RETURNS void AS $$ BEGIN END; $$ LANGUAGE plpgsql;\n")

            views_file = os.path.join(tmpdir, DumpFiles.VIEWS_PG)
            with open(views_file, "w", encoding="utf-8") as f:
                f.write("/* VIEWS */\n")

            trigs_file = os.path.join(tmpdir, DumpFiles.TRIGGERS_PG)
            with open(trigs_file, "w", encoding="utf-8") as f:
                f.write("/* TRIGGERS */\n")

            # Catalog counts: domains=0, procedures=1, views=0, triggers=0
            expected = {
                DumpFiles.DOMAINS_PG: 0,
                DumpFiles.PROCEDURES_PG: 1,
                DumpFiles.VIEWS_PG: 0,
                DumpFiles.TRIGGERS_PG: 0,
            }

            verified = self.migrator.validate_artifacts(output_dir=tmpdir, expected_counts=expected)
            self.assertTrue(verified[DumpFiles.DOMAINS_PG])
            self.assertFalse(verified[DumpFiles.PROCEDURES_PG])
            self.assertTrue(verified[DumpFiles.VIEWS_PG])
            self.assertTrue(verified[DumpFiles.TRIGGERS_PG])

            # Applying legitimately empty files with verified allow_empty returns 0 without error
            res_domains = self.migrator.apply_sql_file(domains_file, allow_empty=verified[DumpFiles.DOMAINS_PG])
            self.assertEqual(res_domains, 0)

            # Applying non-empty file succeeds
            res_procs = self.migrator.apply_sql_file(procs_file, allow_empty=verified[DumpFiles.PROCEDURES_PG])
            self.assertEqual(res_procs, 1)

    def test_origin_without_each_category_individually(self):
        """Test missing source category for each individual category type."""
        categories = [
            DumpFiles.DOMAINS_PG,
            DumpFiles.PROCEDURES_PG,
            DumpFiles.VIEWS_PG,
            DumpFiles.TRIGGERS_PG,
        ]

        for empty_cat in categories:
            with tempfile.TemporaryDirectory() as tmpdir:
                expected = {}
                for cat in categories:
                    fpath = os.path.join(tmpdir, cat)
                    if cat == empty_cat:
                        expected[cat] = 0
                        with open(fpath, "w", encoding="utf-8") as f:
                            f.write("/* EMPTY CATEGORY */\n")
                    else:
                        expected[cat] = 1
                        with open(fpath, "w", encoding="utf-8") as f:
                            f.write("SELECT 1;\n")

                verified = self.migrator.validate_artifacts(output_dir=tmpdir, expected_counts=expected)
                self.assertTrue(verified[empty_cat], f"{empty_cat} should be verified empty")
                for other_cat in categories:
                    if other_cat != empty_cat:
                        self.assertFalse(verified[other_cat], f"{other_cat} should NOT be verified empty")

                # Applying empty category works
                res = self.migrator.apply_sql_file(
                    os.path.join(tmpdir, empty_cat),
                    allow_empty=verified[empty_cat]
                )
                self.assertEqual(res, 0)

    def test_missing_file_when_objects_expected_prevents_drop(self):
        """Missing artifact when objects were expected must raise FileNotFoundError BEFORE drop_schema."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create only procedures, views, triggers; DOMAINS_PG is missing
            for cat in [DumpFiles.PROCEDURES_PG, DumpFiles.VIEWS_PG, DumpFiles.TRIGGERS_PG]:
                with open(os.path.join(tmpdir, cat), "w", encoding="utf-8") as f:
                    f.write("SELECT 1;\n")

            expected = {
                DumpFiles.DOMAINS_PG: 2,  # 2 domains expected, but file missing!
                DumpFiles.PROCEDURES_PG: 1,
                DumpFiles.VIEWS_PG: 1,
                DumpFiles.TRIGGERS_PG: 1,
            }

            drop_called = []
            self.migrator.drop_schema = lambda: drop_called.append(True)

            # Pre-flight validation must fail before drop_schema is ever invoked
            with self.assertRaises(FileNotFoundError):
                self.migrator.validate_artifacts(output_dir=tmpdir, expected_counts=expected)

            self.assertEqual(len(drop_called), 0, "drop_schema MUST NOT be called when an artifact is missing")

    def test_comment_only_file_when_objects_expected_prevents_drop(self):
        """File with only comments when objects were expected must raise ValueError BEFORE drop_schema."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # DOMAINS_PG has only comments, but 3 were expected
            with open(os.path.join(tmpdir, DumpFiles.DOMAINS_PG), "w", encoding="utf-8") as f:
                f.write("/* POSTGRESQL DOMAINS DUMP (CONVERTED) */\n-- Empty dump\n")

            for cat in [DumpFiles.PROCEDURES_PG, DumpFiles.VIEWS_PG, DumpFiles.TRIGGERS_PG]:
                with open(os.path.join(tmpdir, cat), "w", encoding="utf-8") as f:
                    f.write("SELECT 1;\n")

            expected = {
                DumpFiles.DOMAINS_PG: 3,  # 3 expected!
                DumpFiles.PROCEDURES_PG: 1,
                DumpFiles.VIEWS_PG: 1,
                DumpFiles.TRIGGERS_PG: 1,
            }

            drop_called = []
            self.migrator.drop_schema = lambda: drop_called.append(True)

            with self.assertRaises(ValueError) as ctx:
                self.migrator.validate_artifacts(output_dir=tmpdir, expected_counts=expected)

            self.assertIn("contains 0 executable statements", str(ctx.exception))
            self.assertEqual(len(drop_called), 0, "drop_schema MUST NOT be called when an artifact is empty/comment-only")

    def test_truncated_file_when_objects_expected_prevents_drop(self):
        """Truncated file (actual statements < expected) must raise ValueError BEFORE drop_schema."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 5 procedures expected, but only 2 statements written
            with open(os.path.join(tmpdir, DumpFiles.PROCEDURES_PG), "w", encoding="utf-8") as f:
                f.write("CREATE OR REPLACE FUNCTION p1() RETURNS void AS $$ BEGIN END; $$ LANGUAGE plpgsql;\n"
                        "CREATE OR REPLACE FUNCTION p2() RETURNS void AS $$ BEGIN END; $$ LANGUAGE plpgsql;\n")

            for cat in [DumpFiles.DOMAINS_PG, DumpFiles.VIEWS_PG, DumpFiles.TRIGGERS_PG]:
                with open(os.path.join(tmpdir, cat), "w", encoding="utf-8") as f:
                    f.write("SELECT 1;\n")

            expected = {
                DumpFiles.DOMAINS_PG: 1,
                DumpFiles.PROCEDURES_PG: 5,  # 5 expected, only 2 present!
                DumpFiles.VIEWS_PG: 1,
                DumpFiles.TRIGGERS_PG: 1,
            }

            drop_called = []
            self.migrator.drop_schema = lambda: drop_called.append(True)

            with self.assertRaises(ValueError) as ctx:
                self.migrator.validate_artifacts(output_dir=tmpdir, expected_counts=expected)

            self.assertIn("is truncated or incomplete: expected at least 5 statements, but found 2",
                          str(ctx.exception))
            self.assertEqual(len(drop_called), 0, "drop_schema MUST NOT be called when an artifact is truncated")

    def test_allow_empty_not_enabled_indiscriminately(self):
        """allow_empty is derived from verified information and not enabled indiscriminately."""
        with tempfile.NamedTemporaryFile("w+", suffix=".sql", delete=False) as f:
            f.write("-- comment only\n")
            f_path = f.name
        self.addCleanup(os.remove, f_path)

        # Without validate_artifacts or when category is unverified, apply_sql_file defaults allow_empty=False
        with self.assertRaises(ValueError):
            self.migrator.apply_sql_file(f_path)

        # When verified_empty explicitly marks it empty, apply_sql_file uses verified state
        basename = os.path.basename(f_path)
        self.migrator.verified_empty[basename] = True
        self.assertEqual(self.migrator.apply_sql_file(f_path), 0)

        # When verified_empty marks it non-empty, apply_sql_file rejects empty content
        self.migrator.verified_empty[basename] = False
        with self.assertRaises(ValueError):
            self.migrator.apply_sql_file(f_path)

    def test_source_catalog_counts_query(self):
        """DdlExporter.get_source_object_counts queries Firebird system tables."""
        mock_fb = MagicMock()
        mock_cur = MagicMock()
        mock_fb.cursor.return_value = mock_cur

        mock_cur.fetchone.side_effect = [
            (0,),  # Domains count
            (10,), # Procedures count
            (4,),  # Views count
            (7,),  # Triggers count
            (2,),  # Generators count
        ]

        exporter = DdlExporter(mock_fb)
        counts = exporter.get_source_object_counts()

        self.assertEqual(counts[DumpFiles.DOMAINS_PG], 0)
        self.assertEqual(counts[DumpFiles.PROCEDURES_PG], 10)
        self.assertEqual(counts[DumpFiles.VIEWS_PG], 4)
        self.assertEqual(counts[DumpFiles.TRIGGERS_PG], 7)
        self.assertEqual(counts[DumpFiles.SEQUENCES_PG], 2)


if __name__ == '__main__':
    unittest.main()
