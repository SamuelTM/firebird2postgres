import unittest
from antlr4.error.Errors import ParseCancellationException
from transpiler import FirebirdToPostgresVisitor


class TestTranspilerErrors(unittest.TestCase):
    def test_invalid_syntax_raises_parse_cancellation_exception(self):
        invalid_sql = "CREATE TRIGGER INVALID_TRIGGER FOR"
        with self.assertRaises(ParseCancellationException):
            FirebirdToPostgresVisitor.transpile(invalid_sql)

    def test_unclosed_block_raises_parse_cancellation_exception(self):
        unclosed_sql = """
        CREATE OR ALTER PROCEDURE SP_BROKEN
        AS
        BEGIN
            SELECT 1 FROM RDB$DATABASE;
        """
        with self.assertRaises(ParseCancellationException):
            FirebirdToPostgresVisitor.transpile(unclosed_sql)

    def test_garbled_statement_raises_parse_cancellation_exception(self):
        garbled_sql = "FOOBAR BAZ QUX %$$#@! 123"
        with self.assertRaises(ParseCancellationException):
            FirebirdToPostgresVisitor.transpile(garbled_sql)

    def test_unsupported_datediff_unit_raises_value_error(self):
        sql = """
        CREATE OR ALTER PROCEDURE SP_BAD_DATEDIFF
        AS
        DECLARE VARIABLE V_X INTEGER;
        BEGIN
            V_X = DATEDIFF(FOOBAR, CURRENT_DATE, CURRENT_DATE);
        END;
        """
        with self.assertRaises(ValueError):
            FirebirdToPostgresVisitor.transpile(sql)

    def test_datediff_day_with_time_raises_value_error(self):
        sql = """
        CREATE OR ALTER PROCEDURE SP_BAD_TIME_DATEDIFF
        AS
        DECLARE VARIABLE V_X INTEGER;
        BEGIN
            V_X = DATEDIFF(DAY, TIME '10:00', TIME '11:00');
        END;
        """
        with self.assertRaises(ValueError):
            FirebirdToPostgresVisitor.transpile(sql)

