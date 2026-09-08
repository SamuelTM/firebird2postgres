import os
import logging
from .sql_splitter import split_sql_statements

logger = logging.getLogger(__name__)


class SqlRunner:
    """
    Executes PostgreSQL SQL files against a live database connection with statement splitting
    (handling dollar-quoting, block/line comments, single quotes) and transaction management.
    """

    def __init__(self, pg_con):
        self.pg_con = pg_con

    @staticmethod
    def count_statements(file_path: str) -> int:
        """
        Counts executable SQL statements in a file, ignoring comments and headers.
        Raises FileNotFoundError if file does not exist.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"SQL file '{file_path}' not found.")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return len([sql for sql, _ in split_sql_statements(content)])

    def validate_file(self, file_path: str, expected_count: int = None, allow_empty: bool = False) -> int:
        """
        Validates that a SQL artifact file exists and contains executable statements
        without executing them against the database.
        """
        if not os.path.exists(file_path):
            if allow_empty and (expected_count is None or expected_count == 0):
                return 0
            raise FileNotFoundError(f"SQL file '{file_path}' not found.")

        actual_count = self.count_statements(file_path)

        if expected_count is not None and expected_count > 0:
            if actual_count == 0:
                raise ValueError(
                    f"SQL file '{file_path}' contains 0 executable statements (empty or comments only), "
                    f"but {expected_count} objects were expected."
                )
            if actual_count < expected_count:
                raise ValueError(
                    f"SQL file '{file_path}' is truncated or incomplete: "
                    f"expected at least {expected_count} statements, but found {actual_count}."
                )
        elif actual_count == 0 and not allow_empty:
            raise ValueError(
                f"SQL file '{file_path}' contains 0 executable statements (empty or comments only). "
                f"Set allow_empty=True if this is expected."
            )

        return actual_count

    def apply_file(self, file_path: str, continue_on_error: bool = False, allow_empty: bool = False,
                   expected_count: int = None) -> int:
        """
        Executes a PostgreSQL SQL file against the connected database.
        Returns the number of successfully executed statements.
        Raises FileNotFoundError if file does not exist.
        Raises ValueError if file contains no executable statements and allow_empty is False,
        or if expected_count is specified and fewer statements are found.
        """
        if not os.path.exists(file_path):
            if allow_empty and (expected_count is None or expected_count == 0):
                logger.info(f"SQL file '{file_path}' not found, skipping (allow_empty=True)")
                return 0
            raise FileNotFoundError(f"SQL file '{file_path}' not found.")

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        statements = [sql for sql, _ in split_sql_statements(content)]

        if expected_count is not None and expected_count > 0 and len(statements) < expected_count:
            raise ValueError(
                f"SQL file '{file_path}' is truncated or incomplete: "
                f"expected at least {expected_count} statements, but found {len(statements)}."
            )

        if not statements:
            if not allow_empty:
                raise ValueError(
                    f"SQL file '{file_path}' contains 0 executable statements (empty or comments only). "
                    f"Set allow_empty=True if this is expected."
                )
            logger.info(f"SQL file '{file_path}' contains 0 executable statements (empty allowed).")
            return 0

        pg_cur = self.pg_con.cursor()
        success_count = 0
        for i, stmt in enumerate(statements):
            if continue_on_error:
                savepoint = f"stmt_sp_{i}"
                pg_cur.execute(f"SAVEPOINT {savepoint};")
                try:
                    logger.debug(stmt)
                    pg_cur.execute(stmt)
                    pg_cur.execute(f"RELEASE SAVEPOINT {savepoint};")
                    success_count += 1
                except Exception as e:
                    pg_cur.execute(f"ROLLBACK TO SAVEPOINT {savepoint};")
                    logger.error(f"Error executing statement: {e}")
                    logger.debug(f"Failed query: {stmt}")
            else:
                try:
                    logger.debug(stmt)
                    pg_cur.execute(stmt)
                    success_count += 1
                except Exception as e:
                    self.pg_con.rollback()
                    logger.error(f"Error executing statement: {e}")
                    logger.debug(f"Failed query: {stmt}")
                    raise e

        self.pg_con.commit()
        logger.info(f"Successfully applied {success_count} statements from '{file_path}'.")
        return success_count

