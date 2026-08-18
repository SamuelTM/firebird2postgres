import unittest
from utils import split_sql_statements


class TestSqlSplitter(unittest.TestCase):
    def test_simple_statements(self):
        sql = "CREATE TABLE t1 (id INT); CREATE TABLE t2 (id INT);"
        stmts = split_sql_statements(sql)
        self.assertEqual(len(stmts), 2)
        self.assertEqual(stmts[0][0], "CREATE TABLE t1 (id INT);")
        self.assertEqual(stmts[0][1], 1)
        self.assertEqual(stmts[1][0], "CREATE TABLE t2 (id INT);")
        self.assertEqual(stmts[1][1], 1)

    def test_line_number_tracking(self):
        sql = """-- Header comment
CREATE TABLE t1 (
    id INT
);

CREATE TABLE t2 (
    id INT
);"""
        stmts = split_sql_statements(sql)
        self.assertEqual(len(stmts), 2)
        self.assertEqual(stmts[0][1], 1)
        self.assertEqual(stmts[1][1], 6)

    def test_semicolon_inside_single_quotes(self):
        sql = "INSERT INTO t VALUES ('hello; world'); SELECT * FROM t;"
        stmts = split_sql_statements(sql)
        self.assertEqual(len(stmts), 2)
        self.assertEqual(stmts[0][0], "INSERT INTO t VALUES ('hello; world');")
        self.assertEqual(stmts[1][0], "SELECT * FROM t;")

    def test_escaped_quotes_inside_single_quotes(self):
        sql = "INSERT INTO t VALUES ('It''s a test; with semicolon'); SELECT 1;"
        stmts = split_sql_statements(sql)
        self.assertEqual(len(stmts), 2)
        self.assertIn("It''s a test; with semicolon", stmts[0][0])
        self.assertEqual(stmts[1][0], "SELECT 1;")

    def test_semicolon_inside_line_and_block_comments(self):
        sql = """
        -- Comment with ; semicolon
        SELECT 1;
        /* Block comment with ; semicolon
           multi line */
        SELECT 2;
        """
        stmts = split_sql_statements(sql)
        self.assertEqual(len(stmts), 2)
        self.assertIn("SELECT 1;", stmts[0][0])
        self.assertIn("SELECT 2;", stmts[1][0])

    def test_dollar_quoted_functions(self):
        sql = """
        CREATE OR REPLACE FUNCTION test_func() RETURNS void AS $$
        BEGIN
            INSERT INTO t VALUES (1);
            UPDATE t SET id = 2;
        END;
        $$ LANGUAGE plpgsql;

        SELECT test_func();
        """
        stmts = split_sql_statements(sql)
        self.assertEqual(len(stmts), 2)
        self.assertIn("$$ LANGUAGE plpgsql;", stmts[0][0])
        self.assertIn("INSERT INTO t VALUES (1);", stmts[0][0])
        self.assertEqual(stmts[1][0], "SELECT test_func();")

    def test_named_dollar_quoted_tags(self):
        sql = """
        CREATE FUNCTION custom_tag() RETURNS int AS $body$
        BEGIN
            RETURN 42;
        END;
        $body$ LANGUAGE plpgsql;
        """
        stmts = split_sql_statements(sql)
        self.assertEqual(len(stmts), 1)
        self.assertIn("$body$ LANGUAGE plpgsql;", stmts[0][0])

    def test_mixed_multiple_dollar_tags(self):
        sql = """
        CREATE FUNCTION f1() RETURNS void AS $$ BEGIN NULL; END; $$ LANGUAGE plpgsql;
        CREATE FUNCTION f2() RETURNS void AS $tag$ BEGIN NULL; END; $tag$ LANGUAGE plpgsql;
        """
        stmts = split_sql_statements(sql)
        self.assertEqual(len(stmts), 2)
        self.assertIn("CREATE FUNCTION f1()", stmts[0][0])
        self.assertIn("CREATE FUNCTION f2()", stmts[1][0])

    def test_empty_and_whitespace_scripts(self):
        self.assertEqual(split_sql_statements(""), [])
        self.assertEqual(split_sql_statements("   \n\n\t  \n  "), [])

    def test_comment_only_scripts(self):
        sql = """
        -- Single line comment
        -- Another line comment
        /* Multi-line
           comment block */
        """
        self.assertEqual(split_sql_statements(sql), [])

    def test_statement_without_trailing_semicolon(self):
        sql = "SELECT * FROM users"
        stmts = split_sql_statements(sql)
        self.assertEqual(len(stmts), 1)
        self.assertEqual(stmts[0][0], "SELECT * FROM users")
        self.assertEqual(stmts[0][1], 1)
