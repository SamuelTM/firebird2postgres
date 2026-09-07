import os
import tempfile
import unittest
from unittest.mock import MagicMock
from utils.sql_runner import SqlRunner


class TestSqlRunner(unittest.TestCase):
    def setUp(self):
        self.mock_con = MagicMock()
        self.mock_cur = MagicMock()
        self.mock_con.cursor.return_value = self.mock_cur
        self.runner = SqlRunner(self.mock_con)

    def test_apply_file_not_found_returns_zero(self):
        result = self.runner.apply_file("/nonexistent/file.sql")
        self.assertEqual(result, 0)
        self.mock_con.cursor.assert_not_called()

    def test_apply_file_all_successful(self):
        with tempfile.NamedTemporaryFile("w+", suffix=".sql", delete=False) as f:
            f.write("CREATE TABLE t1 (id int);\nCREATE TABLE t2 (id int);\n")
            temp_path = f.name
        self.addCleanup(os.remove, temp_path)

        result = self.runner.apply_file(temp_path, continue_on_error=False)
        self.assertEqual(result, 2)
        self.mock_con.commit.assert_called_once()
        self.mock_con.rollback.assert_not_called()

    def test_apply_file_abort_on_error(self):
        with tempfile.NamedTemporaryFile("w+", suffix=".sql", delete=False) as f:
            f.write("CREATE TABLE t1 (id int);\nBAD SYNTAX;\nCREATE TABLE t2 (id int);\n")
            temp_path = f.name
        self.addCleanup(os.remove, temp_path)

        def mock_exec(query):
            if "BAD SYNTAX" in query:
                raise RuntimeError("Syntax error")

        self.mock_cur.execute.side_effect = mock_exec

        with self.assertRaises(RuntimeError):
            self.runner.apply_file(temp_path, continue_on_error=False)

        self.mock_con.rollback.assert_called_once()
        self.mock_con.commit.assert_not_called()

    def test_apply_file_continue_on_error_uses_savepoints(self):
        with tempfile.NamedTemporaryFile("w+", suffix=".sql", delete=False) as f:
            f.write("CREATE TABLE t1 (id int);\nFAIL STATEMENT;\nCREATE TABLE t2 (id int);\n")
            temp_path = f.name
        self.addCleanup(os.remove, temp_path)

        def mock_exec(query):
            if "FAIL STATEMENT" in query:
                raise RuntimeError("Failed statement")

        self.mock_cur.execute.side_effect = mock_exec

        result = self.runner.apply_file(temp_path, continue_on_error=True)
        self.assertEqual(result, 2)

        # Full rollback must NOT be called when continue_on_error is True
        self.mock_con.rollback.assert_not_called()
        self.mock_con.commit.assert_called_once()

        executed_queries = [c[0][0] for c in self.mock_cur.execute.call_args_list]
        self.assertIn("SAVEPOINT stmt_sp_0;", executed_queries)
        self.assertIn("RELEASE SAVEPOINT stmt_sp_0;", executed_queries)
        self.assertIn("SAVEPOINT stmt_sp_1;", executed_queries)
        self.assertIn("ROLLBACK TO SAVEPOINT stmt_sp_1;", executed_queries)
        self.assertIn("SAVEPOINT stmt_sp_2;", executed_queries)
        self.assertIn("RELEASE SAVEPOINT stmt_sp_2;", executed_queries)


if __name__ == '__main__':
    unittest.main()
