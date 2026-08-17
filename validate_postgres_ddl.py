"""
Validates the DDL syntax of converted PostgreSQL domains, views, functions/procedures, and triggers
against a live PostgreSQL database without making permanent changes (Dry-Run by default).
"""

import os
import re
import sys
from dataclasses import dataclass
from typing import List, Optional, Tuple

import psycopg2
from dotenv import load_dotenv

load_dotenv()

DEFAULT_TARGET_FILES = [
    'postgres_domains_dump.sql',
    'postgres_views_dump.sql',
    'postgres_procedures_dump.sql',
    'postgres_triggers_dump.sql'
]


@dataclass
class SQLStatement:
    file_name: str
    object_type: str  # 'DOMAIN', 'VIEW', 'FUNCTION', 'TRIGGER', 'OTHER'
    object_name: str
    sql: str
    start_line: int


@dataclass
class ValidationResult:
    statement: SQLStatement
    success: bool
    error_message: Optional[str] = None
    pg_code: Optional[str] = None


def split_sql_statements(file_path: str) -> List[SQLStatement]:
    """
    Parses a PostgreSQL SQL file into individual statements, correctly handling:
    - Single line comments (--)
    - Multi-line comments (/* ... */)
    - Single quotes ('...')
    - Dollar-quoted strings ($$...$$ or $tag$...$tag$)
    """
    if not os.path.exists(file_path):
        print(f"[WARNING] File '{file_path}' not found. Skipping.")
        return []

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    statements = []
    current_stmt = []
    current_line = 1
    stmt_start_line = 1

    in_single_quote = False
    in_line_comment = False
    in_block_comment = False
    dollar_tag = None  # Holds the closing tag, e.g. "$$" or "$func$"

    i = 0
    n = len(content)

    while i < n:
        ch = content[i]
        next_ch = content[i + 1] if i + 1 < n else ''

        # Track line numbers
        if ch == '\n':
            current_line += 1
            if in_line_comment:
                in_line_comment = False
            current_stmt.append(ch)
            i += 1
            continue

        # Handle line comments
        if in_line_comment:
            current_stmt.append(ch)
            i += 1
            continue

        # Handle block comments
        if in_block_comment:
            current_stmt.append(ch)
            if ch == '*' and next_ch == '/':
                current_stmt.append(next_ch)
                in_block_comment = False
                i += 2
                continue
            i += 1
            continue

        # Handle single quotes
        if in_single_quote:
            current_stmt.append(ch)
            if ch == "'":
                if next_ch == "'":  # Escaped single quote ''
                    current_stmt.append(next_ch)
                    i += 2
                    continue
                else:
                    in_single_quote = False
            i += 1
            continue

        # Handle dollar quotes ($$...$$)
        if dollar_tag is not None:
            if content.startswith(dollar_tag, i):
                current_stmt.append(dollar_tag)
                i += len(dollar_tag)
                dollar_tag = None
                continue
            current_stmt.append(ch)
            i += 1
            continue

        # --- OUTSIDE QUOTES AND COMMENTS ---

        # Check start of line comment
        if ch == '-' and next_ch == '-':
            in_line_comment = True
            current_stmt.append(ch)
            current_stmt.append(next_ch)
            i += 2
            continue

        # Check start of block comment
        if ch == '/' and next_ch == '*':
            in_block_comment = True
            current_stmt.append(ch)
            current_stmt.append(next_ch)
            i += 2
            continue

        # Check start of single quote
        if ch == "'":
            in_single_quote = True
            current_stmt.append(ch)
            i += 1
            continue

        # Check start of dollar quote ($...$)
        if ch == '$':
            match = re.match(r'^\$[a-zA-Z0-9_]*\$', content[i:])
            if match:
                dollar_tag = match.group(0)
                current_stmt.append(dollar_tag)
                i += len(dollar_tag)
                continue

        # Check statement delimiter ';'
        if ch == ';':
            current_stmt.append(ch)
            raw_sql = "".join(current_stmt).strip()

            if raw_sql and not all(line.strip().startswith('--') for line in raw_sql.splitlines() if line.strip()):
                obj_type, obj_name = identify_object(raw_sql)
                statements.append(
                    SQLStatement(
                        file_name=os.path.basename(file_path),
                        object_type=obj_type,
                        object_name=obj_name,
                        sql=raw_sql,
                        start_line=stmt_start_line
                    )
                )

            current_stmt = []
            stmt_start_line = current_line
            i += 1
            continue

        if not current_stmt and not ch.isspace():
            stmt_start_line = current_line

        current_stmt.append(ch)
        i += 1

    # Any remaining statement at EOF
    raw_sql = "".join(current_stmt).strip()
    if raw_sql and not all(line.strip().startswith('--') for line in raw_sql.splitlines() if line.strip()):
        obj_type, obj_name = identify_object(raw_sql)
        statements.append(
            SQLStatement(
                file_name=os.path.basename(file_path),
                object_type=obj_type,
                object_name=obj_name,
                sql=raw_sql,
                start_line=stmt_start_line
            )
        )

    return statements


def identify_object(sql_text: str) -> Tuple[str, str]:
    """
    Identifies the SQL object type and name from statement text.
    """
    clean_sql = re.sub(r'--[^\n]*\n', '\n', sql_text)
    clean_sql = re.sub(r'/\*.*?\*/', '', clean_sql, flags=re.DOTALL).strip()

    # Domain
    m = re.search(r'CREATE\s+DOMAIN\s+"?([a-zA-Z0-9_]+)"?', clean_sql, re.IGNORECASE)
    if m:
        return 'DOMAIN', m.group(1)

    # View
    m = re.search(r'CREATE\s+(?:OR\s+REPLACE\s+)?VIEW\s+"?([a-zA-Z0-9_]+)"?', clean_sql, re.IGNORECASE)
    if m:
        return 'VIEW', m.group(1)

    # Function
    m = re.search(r'CREATE\s+(?:OR\s+REPLACE\s+)?FUNCTION\s+"?([a-zA-Z0-9_]+)"?\s*\(', clean_sql, re.IGNORECASE)
    if m:
        return 'FUNCTION', m.group(1)

    # Procedure
    m = re.search(r'CREATE\s+(?:OR\s+REPLACE\s+)?PROCEDURE\s+"?([a-zA-Z0-9_]+)"?\s*\(', clean_sql, re.IGNORECASE)
    if m:
        return 'PROCEDURE', m.group(1)

    # Trigger
    m = re.search(r'CREATE\s+TRIGGER\s+"?([a-zA-Z0-9_]+)"?\s+', clean_sql, re.IGNORECASE)
    if m:
        return 'TRIGGER', m.group(1)

    return 'OTHER', 'UNKNOWN'


def run_ddl_validation(
    conn,
    target_files: List[str],
    apply_changes: bool = False
) -> List[ValidationResult]:
    """
    Executes each statement in sequence inside a PostgreSQL transaction using SAVEPOINTS.
    In dry-run mode (default), the entire transaction is rolled back at the end.
    """
    conn.autocommit = False
    cursor = conn.cursor()

    # Load and collect statements
    all_statements: List[SQLStatement] = []
    for fpath in target_files:
        stmts = split_sql_statements(fpath)
        all_statements.extend(stmts)

    print(f"[INFO] Total DDL statements loaded: {len(all_statements)}")
    print(f"[INFO] Mode: {'APPLY (CHANGES WILL BE PERSISTED)' if apply_changes else 'DRY-RUN (ROLLBACK AT THE END - SAFE)'}\n")

    results: List[ValidationResult] = []

    for idx, stmt in enumerate(all_statements, 1):
        sp_name = f"sp_validate_{idx}"
        cursor.execute(f"SAVEPOINT {sp_name};")

        try:
            cursor.execute(stmt.sql)
            results.append(ValidationResult(statement=stmt, success=True))
            # In dry-run we KEEP the object alive within the transaction so dependent objects can find it
        except Exception as e:
            cursor.execute(f"ROLLBACK TO SAVEPOINT {sp_name};")
            error_msg = str(e).strip()
            pg_code = getattr(e, 'pgcode', None)
            results.append(
                ValidationResult(
                    statement=stmt,
                    success=False,
                    error_message=error_msg,
                    pg_code=pg_code
                )
            )

    if apply_changes:
        failed_count = sum(1 for r in results if not r.success)
        if failed_count > 0:
            print(f"\n[WARNING] {failed_count} errors encountered. Applying only successful statements...")
        conn.commit()
        print("[SUCCESS] Changes committed to PostgreSQL database.")
    else:
        conn.rollback()
        print("[INFO] Test completed. Rollback executed (no changes persisted to database).")

    cursor.close()
    return results


def print_diagnostic_report(results: List[ValidationResult]) -> bool:
    """
    Formats and prints a comprehensive diagnostic report.
    Returns True if all statements passed, False otherwise.
    """
    total = len(results)
    if total == 0:
        print("\nNo statements to validate.")
        return True

    passed = [r for r in results if r.success]
    failed = [r for r in results if not r.success]

    # Category counts
    by_type = {}
    for r in results:
        t = r.statement.object_type
        if t not in by_type:
            by_type[t] = {'total': 0, 'passed': 0, 'failed': 0}
        by_type[t]['total'] += 1
        if r.success:
            by_type[t]['passed'] += 1
        else:
            by_type[t]['failed'] += 1

    print("\n" + "=" * 80)
    print("           DDL VALIDATION REPORT - POSTGRESQL (LAYER 1)")
    print("=" * 80)

    print(f"\n{'OBJECT TYPE':<18} | {'TOTAL':<8} | {'SUCCESS':<10} | {'FAILED':<8} | {'RATE':<8}")
    print("-" * 65)
    for obj_type, counts in sorted(by_type.items()):
        rate = (counts['passed'] / counts['total']) * 100 if counts['total'] > 0 else 0
        print(f"{obj_type:<18} | {counts['total']:<8} | {counts['passed']:<10} | {counts['failed']:<8} | {rate:>6.1f}%")
    print("-" * 65)
    total_rate = (len(passed) / total) * 100
    print(f"{'OVERALL TOTAL':<18} | {total:<8} | {len(passed):<10} | {len(failed):<8} | {total_rate:>6.1f}%")

    if failed:
        print("\n" + "=" * 80)
        print(f"  FAILURE DETAILS ({len(failed)} OBJECTS WITH COMPILATION ERRORS)")
        print("=" * 80)

        for idx, r in enumerate(failed, 1):
            stmt = r.statement
            print(f"\n[{idx}/{len(failed)}] ❌ {stmt.object_type}: {stmt.object_name}")
            print(f"  File: {stmt.file_name} (Line ~{stmt.start_line})")
            if r.pg_code:
                print(f"  SQLState Code: {r.pg_code}")

            # Format error message cleanly
            err_lines = r.error_message.splitlines() if r.error_message else ["Unknown error"]
            print("  PostgreSQL Error:")
            for line in err_lines[:4]:
                print(f"    ▶ {line}")

            # Show snippet of the SQL
            sql_snippet = "\n".join(stmt.sql.splitlines()[:6])
            if len(stmt.sql.splitlines()) > 6:
                sql_snippet += "\n    ..."
            print("  SQL Snippet:")
            for s_line in sql_snippet.splitlines():
                print(f"    | {s_line}")

        print("\n" + "=" * 80)
        print(f"💡 TIP: Use the error messages above to add translation rules in 'firebird_visitor.py'.")
        print("=" * 80)
        return False
    else:
        print("\n🎉 CONGRATULATIONS! 100% of SQL objects compiled in PostgreSQL without any errors!")
        return True


def validate_postgres_ddl(
    pg_connection=None,
    target_files: Optional[List[str]] = None,
    apply_changes: bool = False
) -> bool:
    """
    Validates the generated PostgreSQL DDL files against a PostgreSQL instance.
    If no connection is provided, it connects using the .env configuration.
    """
    close_connection = False
    if target_files is None:
        target_files = DEFAULT_TARGET_FILES

    if pg_connection is None:
        required_env_vars = ['POSTGRES_HOST', 'POSTGRES_PORT', 'POSTGRES_DB',
                             'POSTGRES_USER', 'POSTGRES_PASSWORD']
        missing = [var for var in required_env_vars if not os.getenv(var)]
        if missing:
            print(f"[FATAL ERROR] Missing required environment variables: {', '.join(missing)}")
            print("  Set them in your .env file (see .env.example).")
            return False

        host = os.environ['POSTGRES_HOST']
        port = int(os.environ['POSTGRES_PORT'])
        dbname = os.environ['POSTGRES_DB']
        user = os.environ['POSTGRES_USER']
        password = os.environ['POSTGRES_PASSWORD']

        print(f"\n[INFO] Connecting to PostgreSQL at '{host}:{port}/{dbname}'...")
        try:
            pg_connection = psycopg2.connect(
                host=host,
                port=port,
                dbname=dbname,
                user=user,
                password=password
            )
            close_connection = True
        except Exception as e:
            print(f"[FATAL ERROR] Could not connect to PostgreSQL: {e}")
            return False

    try:
        results = run_ddl_validation(
            conn=pg_connection,
            target_files=target_files,
            apply_changes=apply_changes
        )
        return print_diagnostic_report(results)
    finally:
        if close_connection:
            pg_connection.close()


if __name__ == '__main__':
    success = validate_postgres_ddl()
    if not success:
        sys.exit(1)
