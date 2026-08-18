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

    def apply_file(self, file_path: str, continue_on_error: bool = False) -> int:
        """
        Executes a PostgreSQL SQL file against the connected database.
        Returns the number of successfully executed statements.
        """
        if not os.path.exists(file_path):
            logger.warning(f"File '{file_path}' not found. Skipping.")
            return 0

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        statements = [sql for sql, _ in split_sql_statements(content)]

        pg_cur = self.pg_con.cursor()
        success_count = 0
        for stmt in statements:
            try:
                logger.debug(stmt)
                pg_cur.execute(stmt)
                success_count += 1
            except Exception as e:
                self.pg_con.rollback()
                logger.error(f"Error executing statement: {e}")
                logger.debug(f"Failed query: {stmt}")
                if not continue_on_error:
                    raise e

        self.pg_con.commit()
        logger.info(f"Successfully applied {success_count} statements from '{file_path}'.")
        return success_count
