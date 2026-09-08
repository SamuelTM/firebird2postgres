import os
import re
import logging
from .sql_splitter import split_sql_statements

logger = logging.getLogger(__name__)


def extract_defined_objects(content: str, object_type: str = None) -> set[str]:
    """
    Extracts defined object names from PostgreSQL DDL content, normalized to uppercase.
    Handles schema-qualified names, quoted identifiers, and DO EXECUTE blocks.
    """
    clean = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    clean = re.sub(r'--[^\n]*', '', clean)

    ot = (object_type or '').upper()
    patterns = []

    if not ot or ot in ('PROCEDURE', 'PROCEDURES', 'FUNCTION', 'FUNCTIONS'):
        patterns.append(
            ('PROCEDURE', re.compile(
                r'\bCREATE\s+(?:OR\s+REPLACE\s+)?(?:FUNCTION|PROCEDURE)\s+(?:(?:"[^"]+"|[\w$]+)\.)?(?:"([^"]+)"|([\w$]+))',
                re.IGNORECASE
            ))
        )
    if not ot or ot in ('VIEW', 'VIEWS'):
        patterns.append(
            ('VIEW', re.compile(
                r'\bCREATE\s+(?:OR\s+REPLACE\s+)?VIEW\s+(?:(?:"[^"]+"|[\w$]+)\.)?(?:"([^"]+)"|([\w$]+))',
                re.IGNORECASE
            ))
        )
    if not ot or ot in ('TRIGGER', 'TRIGGERS'):
        patterns.append(
            ('TRIGGER', re.compile(
                r'\bCREATE\s+TRIGGER\s+(?:(?:"[^"]+"|[\w$]+)\.)?(?:"([^"]+)"|([\w$]+))',
                re.IGNORECASE
            ))
        )
    if not ot or ot in ('DOMAIN', 'DOMAINS'):
        patterns.append(
            ('DOMAIN', re.compile(
                r'\bCREATE\s+DOMAIN\s+(?:(?:"[^"]+"|[\w$]+)\.)?(?:"([^"]+)"|([\w$]+))',
                re.IGNORECASE
            ))
        )
    if not ot or ot in ('SEQUENCE', 'SEQUENCES', 'GENERATOR', 'GENERATORS'):
        patterns.append(
            ('SEQUENCE', re.compile(
                r'\bCREATE\s+SEQUENCE\s+(?:(?:"[^"]+"|[\w$]+)\.)?(?:"([^"]+)"|([\w$]+))',
                re.IGNORECASE
            ))
        )

    defined = set()
    for cat, pat in patterns:
        for m in pat.finditer(clean):
            raw_name = (m.group(1) or m.group(2)).strip()
            upper_name = raw_name.upper()
            defined.add(upper_name)
            if cat == 'TRIGGER':
                # Strip sequence prefix if present (e.g. trg_00000_bi_ped -> BI_PED)
                stripped = re.sub(r'^trg_\d+_', '', raw_name, flags=re.IGNORECASE).upper()
                defined.add(stripped)
            elif cat == 'DOMAIN':
                # Strip _dom suffix if present due to collision resolution
                stripped = re.sub(r'(_dom)+$', '', raw_name, flags=re.IGNORECASE).upper()
                defined.add(stripped)

    return defined


class SqlRunner:
    """
    Executes PostgreSQL SQL files against a live database connection with statement splitting
    (handling dollar-quoting, block/line comments, single quotes) and transaction management.
    """

    def __init__(self, pg_con):
        self.pg_con = pg_con

    extract_defined_objects = staticmethod(extract_defined_objects)

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

    def validate_file(self, file_path: str, expected_count: int = None, allow_empty: bool = False,
                      expected_objects: list[str] | set[str] = None, object_type: str = None) -> int:
        """
        Validates that a SQL artifact file exists, contains executable statements,
        and includes all expected objects by identity/type without executing them.
        """
        if not os.path.exists(file_path):
            is_empty_allowed = allow_empty and (
                (expected_count is None or expected_count == 0) and
                (expected_objects is None or len(expected_objects) == 0)
            )
            if is_empty_allowed:
                return 0
            raise FileNotFoundError(f"SQL file '{file_path}' not found.")

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        actual_count = len([sql for sql, _ in split_sql_statements(content)])

        # Identity-based validation when expected_objects is provided
        if expected_objects is not None:
            expected_set = {obj.strip().upper() for obj in expected_objects if obj and obj.strip()}
            if len(expected_set) > 0:
                if actual_count == 0:
                    raise ValueError(
                        f"SQL file '{file_path}' contains 0 executable statements (empty or comments only), "
                        f"but {len(expected_set)} objects were expected."
                    )
                ot = object_type
                if not ot:
                    fname = os.path.basename(file_path).lower()
                    if 'proc' in fname:
                        ot = 'PROCEDURE'
                    elif 'view' in fname:
                        ot = 'VIEW'
                    elif 'trig' in fname:
                        ot = 'TRIGGER'
                    elif 'dom' in fname:
                        ot = 'DOMAIN'
                    elif 'seq' in fname or 'gen' in fname:
                        ot = 'SEQUENCE'

                defined = extract_defined_objects(content, object_type=ot)
                missing = sorted(list(expected_set - defined))
                if missing:
                    raise ValueError(
                        f"SQL file '{file_path}' is incomplete: missing {len(missing)} expected {ot or 'object'}(s): "
                        f"{', '.join(missing)}."
                    )
            elif actual_count == 0 and not allow_empty:
                raise ValueError(
                    f"SQL file '{file_path}' contains 0 executable statements (empty or comments only). "
                    f"Set allow_empty=True if this is expected."
                )
        elif expected_count is not None and expected_count > 0:
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
                   expected_count: int = None, expected_objects: list[str] | set[str] = None,
                   object_type: str = None) -> int:
        """
        Executes a PostgreSQL SQL file against the connected database.
        Returns the number of successfully executed statements.
        Raises FileNotFoundError if file does not exist.
        Raises ValueError if file contains no executable statements and allow_empty is False,
        or if expected objects/counts are not satisfied.
        """
        if not os.path.exists(file_path):
            is_empty_allowed = allow_empty and (
                (expected_count is None or expected_count == 0) and
                (expected_objects is None or len(expected_objects) == 0)
            )
            if is_empty_allowed:
                logger.info(f"SQL file '{file_path}' not found, skipping (allow_empty=True)")
                return 0
            raise FileNotFoundError(f"SQL file '{file_path}' not found.")

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        statements = [sql for sql, _ in split_sql_statements(content)]

        if expected_objects is not None:
            expected_set = {obj.strip().upper() for obj in expected_objects if obj and obj.strip()}
            if len(expected_set) > 0:
                if not statements:
                    raise ValueError(
                        f"SQL file '{file_path}' contains 0 executable statements (empty or comments only), "
                        f"but {len(expected_set)} objects were expected."
                    )
                ot = object_type
                if not ot:
                    fname = os.path.basename(file_path).lower()
                    if 'proc' in fname:
                        ot = 'PROCEDURE'
                    elif 'view' in fname:
                        ot = 'VIEW'
                    elif 'trig' in fname:
                        ot = 'TRIGGER'
                    elif 'dom' in fname:
                        ot = 'DOMAIN'
                    elif 'seq' in fname or 'gen' in fname:
                        ot = 'SEQUENCE'
                defined = extract_defined_objects(content, object_type=ot)
                missing = sorted(list(expected_set - defined))
                if missing:
                    raise ValueError(
                        f"SQL file '{file_path}' is incomplete: missing {len(missing)} expected {ot or 'object'}(s): "
                        f"{', '.join(missing)}."
                    )
        elif expected_count is not None and expected_count > 0 and len(statements) < expected_count:
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

