"""
Shared SQL script splitter.

Splits a SQL script into individual statements, correctly handling:
- Single-quoted strings ('...' with '' escaping)
- Line comments (-- ...)
- Block comments (/* ... */)
- Dollar-quoted strings ($$...$$ or $tag$...$tag$)
"""

import re


def split_sql_statements(content: str) -> list[tuple[str, int]]:
    """
    Splits SQL script content into individual statements.

    Returns a list of (statement_text, start_line) tuples with 1-based line numbers.
    Empty and comment-only statements are skipped.
    """
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

    def flush_statement():
        raw_sql = "".join(current_stmt).strip()
        code_without_comments = re.sub(r'--[^\n]*', '', raw_sql)
        code_without_comments = re.sub(r'/\*.*?\*/', '', code_without_comments, flags=re.DOTALL)
        if code_without_comments.strip():
            statements.append((raw_sql, stmt_start_line))

    while i < n:
        ch = content[i]
        next_ch = content[i + 1] if i + 1 < n else ''

        # Track line numbers (also closes a line comment)
        if ch == '\n':
            current_line += 1
            if in_line_comment:
                in_line_comment = False
            if current_stmt:
                current_stmt.append(ch)
            i += 1
            continue

        if in_line_comment:
            if not current_stmt:
                stmt_start_line = current_line
            current_stmt.append(ch)
            i += 1
            continue

        if in_block_comment:
            if not current_stmt:
                stmt_start_line = current_line
            current_stmt.append(ch)
            if ch == '*' and next_ch == '/':
                current_stmt.append(next_ch)
                in_block_comment = False
                i += 2
                continue
            i += 1
            continue

        if in_single_quote:
            current_stmt.append(ch)
            if ch == "'":
                if next_ch == "'":  # Escaped single quote ''
                    current_stmt.append(next_ch)
                    i += 2
                    continue
                in_single_quote = False
            i += 1
            continue

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

        if not current_stmt:
            if ch.isspace():
                i += 1
                continue
            stmt_start_line = current_line

        if ch == '-' and next_ch == '-':
            in_line_comment = True
            current_stmt.append(ch)
            current_stmt.append(next_ch)
            i += 2
            continue

        if ch == '/' and next_ch == '*':
            in_block_comment = True
            current_stmt.append(ch)
            current_stmt.append(next_ch)
            i += 2
            continue

        if ch == "'":
            in_single_quote = True
            current_stmt.append(ch)
            i += 1
            continue

        if ch == '$':
            match = re.match(r'^\$[a-zA-Z0-9_]*\$', content[i:])
            if match:
                dollar_tag = match.group(0)
                current_stmt.append(dollar_tag)
                i += len(dollar_tag)
                continue

        if ch == ';':
            current_stmt.append(ch)
            flush_statement()
            current_stmt = []
            i += 1
            continue

        current_stmt.append(ch)
        i += 1

    # Any remaining statement at EOF
    flush_statement()

    return statements
