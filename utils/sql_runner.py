import os
import re
import logging
from .sql_splitter import split_sql_statements

logger = logging.getLogger(__name__)


_DOLLAR_TAG_RE = re.compile(r'\$[a-zA-Z0-9_]*\$')
_DO_OPEN_RE = re.compile(r'\bDO\s*$', re.IGNORECASE)
_EXECUTE_BEFORE_STRING_RE = re.compile(r'\bEXECUTE\s*$', re.IGNORECASE)
_CREATE_LEAD_RE = re.compile(r'^\s*CREATE\b', re.IGNORECASE)

# Opaque placeholder for quoted identifiers in code-only text: U+E000/U+E001
# (Unicode private-use, never word characters) wrap the identifier index.
# Identifier CONTENT (which may itself look like commands, e.g. a function
# named "CREATE DOMAIN fake") therefore can never match CREATE patterns;
# names are resolved back from the identifier table at capture time.
_IDENT_OPEN = '\ue000'
_IDENT_CLOSE = '\ue001'

# Quoted names match only the opaque placeholder emitted by the lexer;
# the decoded identifier is resolved from the identifier table.
_IDENT_REF = _IDENT_OPEN + r'(\d+)' + _IDENT_CLOSE
_IDENT_REF_NC = _IDENT_OPEN + r'\d+' + _IDENT_CLOSE
_BARE_IDENT = r'([\w$]+)'
_QUALIFIER = r'(?:(?:' + _IDENT_REF_NC + r'|[\w$]+)\.)?'


def _lex_sql(content: str) -> list[tuple]:
    """
    Lexes SQL into segments without executing anything.

    Returns a list of segments:
    - ('code', text): executable code (comments removed).
    - ('string', raw, value): single-quoted literal with '' unescaped to '.
    - ('ident', raw, value): double-quoted identifier with "" unescaped to ".
    - ('dollar', raw, (tag, body)): dollar-quoted body with its opening tag.
    String contents, comment contents, identifier contents and dollar bodies
    never leak into 'code'.
    """
    segs: list[tuple] = []
    buf: list[str] = []
    i, n = 0, len(content)

    def flush_code() -> None:
        if buf:
            segs.append(('code', ''.join(buf)))
            del buf[:]

    while i < n:
        ch = content[i]
        nxt = content[i + 1] if i + 1 < n else ''

        if ch == '-' and nxt == '-':
            flush_code()
            j = content.find('\n', i)
            j = n if j == -1 else j
            i = j
            continue

        if ch == '/' and nxt == '*':
            flush_code()
            depth, j = 1, i + 2
            while j < n and depth:
                if content[j] == '/' and j + 1 < n and content[j + 1] == '*':
                    depth += 1
                    j += 2
                elif content[j] == '*' and j + 1 < n and content[j + 1] == '/':
                    depth -= 1
                    j += 2
                else:
                    j += 1
            i = j
            continue

        if ch == "'":
            flush_code()
            j, val = i + 1, []
            while j < n:
                if content[j] == "'":
                    if j + 1 < n and content[j + 1] == "'":
                        val.append("'")
                        j += 2
                    else:
                        j += 1
                        break
                else:
                    val.append(content[j])
                    j += 1
            segs.append(('string', content[i:j], ''.join(val)))
            i = j
            continue

        if ch == '"':
            # Quoted identifier: emitted as an opaque placeholder segment so
            # its CONTENT never matches command patterns; "" escapes are
            # resolved into the decoded value. Consumed whole so ' and $
            # inside never open strings/bodies.
            flush_code()
            j = i + 1
            val = []
            while j < n:
                if content[j] == '"':
                    if j + 1 < n and content[j + 1] == '"':
                        val.append('"')
                        j += 2
                    else:
                        j += 1
                        break
                else:
                    val.append(content[j])
                    j += 1
            segs.append(('ident', content[i:j], ''.join(val)))
            i = j
            continue

        if ch == '$':
            m = _DOLLAR_TAG_RE.match(content, i)
            if m:
                tag = m.group(0)
                end = content.find(tag, i + len(tag))
                if end != -1:
                    flush_code()
                    segs.append(('dollar', content[i:end + len(tag)],
                                 (tag, content[i + len(tag):end])))
                    i = end + len(tag)
                    continue
            buf.append(ch)
            i += 1
            continue

        buf.append(ch)
        i += 1

    flush_code()
    return segs


def _ident_token(idx: int) -> str:
    return f"{_IDENT_OPEN}{idx}{_IDENT_CLOSE}"


def _scan_ddl_text(text: str, _depth: int = 0) -> tuple[str, list[str], list[str]]:
    """
    Splits DDL text into top-level code plus dynamic DDL literals.

    Returns (code_text, executed_ddls, idents) where code_text contains no
    comments, no string contents, no identifier contents and no
    dollar-quoted bodies (quoted identifiers appear as opaque placeholders
    resolved via idents), and executed_ddls holds the decoded value of every
    string literal immediately following EXECUTE (the exporter's DO-block
    idiom: EXECUTE 'CREATE DOMAIN ...'), plus the same for DO bodies scanned
    recursively. Dollar bodies that do not belong to DO are
    function/procedure implementations and are discarded.
    """
    if _depth > 5:
        return '', [], []
    items: list[tuple[str, bool]] = []  # (text, is_ident_token)
    executed: list[str] = []
    idents: list[str] = []
    segs = _lex_sql(text)
    for idx, seg in enumerate(segs):
        kind = seg[0]
        if kind == 'code':
            items.append((seg[1], False))
        elif kind == 'ident':
            idents.append(seg[2])
            items.append((_ident_token(len(idents) - 1), True))
        elif kind == 'string':
            prev_code = None
            for back in range(idx - 1, -1, -1):
                if segs[back][0] == 'code':
                    prev_code = segs[back][1]
                    break
            if prev_code is not None and _EXECUTE_BEFORE_STRING_RE.search(prev_code):
                value = seg[2]
                if _CREATE_LEAD_RE.match(value):
                    executed.append(value)
        elif kind == 'dollar':
            prev_code = None
            for back in range(idx - 1, -1, -1):
                if segs[back][0] == 'code':
                    prev_code = segs[back][1]
                    break
            if prev_code is not None and _DO_OPEN_RE.search(prev_code):
                _, nested_exec, _ = _scan_ddl_text(seg[2][1], _depth + 1)
                executed.extend(nested_exec)
    # Reassemble: identifiers glue to their neighbors exactly as in source
    # (public."x" must stay adjacent); anything removed (comments, strings,
    # bodies) leaves a whitespace separator so keywords never fuse.
    code_text = ''
    prev_ident = False
    first = True
    for text, is_ident in items:
        if not first and not prev_ident and not is_ident:
            code_text += ' '
        code_text += text
        prev_ident = is_ident
        first = False
    return code_text, executed, idents


def scan_ddl_text(text: str) -> tuple[str, list[str], list[str]]:
    """
    Public entry point to the SQL lexical scan: splits DDL text into
    top-level code (no comments, no string/identifier contents, no
    dollar-quoted bodies except DO), dynamic DDL literals following EXECUTE,
    and the quoted-identifier table backing the opaque placeholders.
    Shared by dump validation and DDL object identification so both agree
    on which command a statement effectively executes.
    """
    return _scan_ddl_text(text)


def _match_creates(code_text: str, patterns: list[tuple], idents: list[str]) -> set[str]:
    """Runs CREATE-object patterns over code-only text with opaque identifiers."""
    defined = set()
    for _, pat in patterns:
        for m in pat.finditer(code_text):
            if m.group(1) is not None:
                raw_name = idents[int(m.group(1))].strip()
            else:
                raw_name = m.group(2).strip()
            defined.add(raw_name.upper())
    return defined


def _build_patterns(object_type: str = None) -> list[tuple]:
    ot = (object_type or '').upper()
    patterns = []

    if not ot or ot in ('PROCEDURE', 'PROCEDURES', 'FUNCTION', 'FUNCTIONS'):
        patterns.append(
            ('PROCEDURE', re.compile(
                r'\bCREATE\s+(?:OR\s+REPLACE\s+)?(?:FUNCTION|PROCEDURE)\s+'
                + _QUALIFIER + r'(?:' + _IDENT_REF + r'|' + _BARE_IDENT + r')',
                re.IGNORECASE
            ))
        )
    if not ot or ot in ('VIEW', 'VIEWS'):
        patterns.append(
            ('VIEW', re.compile(
                r'\bCREATE\s+(?:OR\s+REPLACE\s+)?VIEW\s+'
                + _QUALIFIER + r'(?:' + _IDENT_REF + r'|' + _BARE_IDENT + r')',
                re.IGNORECASE
            ))
        )
    if not ot or ot in ('TRIGGER', 'TRIGGERS'):
        patterns.append(
            ('TRIGGER', re.compile(
                r'\bCREATE\s+TRIGGER\s+'
                + _QUALIFIER + r'(?:' + _IDENT_REF + r'|' + _BARE_IDENT + r')',
                re.IGNORECASE
            ))
        )
    if not ot or ot in ('DOMAIN', 'DOMAINS'):
        patterns.append(
            ('DOMAIN', re.compile(
                r'\bCREATE\s+DOMAIN\s+'
                + _QUALIFIER + r'(?:' + _IDENT_REF + r'|' + _BARE_IDENT + r')',
                re.IGNORECASE
            ))
        )
    if not ot or ot in ('SEQUENCE', 'SEQUENCES', 'GENERATOR', 'GENERATORS'):
        patterns.append(
            ('SEQUENCE', re.compile(
                r'\bCREATE\s+SEQUENCE\s+'
                + _QUALIFIER + r'(?:' + _IDENT_REF + r'|' + _BARE_IDENT + r')',
                re.IGNORECASE
            ))
        )
    return patterns


def extract_defined_objects(content: str, object_type: str = None) -> set[str]:
    """
    Extracts defined object names from PostgreSQL DDL content, normalized to uppercase.

    Only real definitions count: string literals, comments, quoted-identifier
    contents and dollar-quoted function/procedure bodies are invisible to the
    matcher, so text such as RAISE NOTICE 'CREATE FUNCTION p2()' never
    fabricates an object — and neither does a hostile name like
    "CREATE DOMAIN fake". The one exception is the exporter's DO-block idiom
    EXECUTE 'CREATE ...', whose literal is real DDL executed when the file is
    applied. Handles schema-qualified names and "" escaped quotes inside
    identifiers.
    """
    patterns = _build_patterns(object_type)
    code_text, executed_ddls, idents = _scan_ddl_text(content)
    defined = _match_creates(code_text, patterns, idents)
    for ddl in executed_ddls:
        sub_code, nested, sub_idents = _scan_ddl_text(ddl)
        defined |= _match_creates(sub_code, patterns, sub_idents)
        for sub in nested:
            sub_code2, _, sub_idents2 = _scan_ddl_text(sub)
            defined |= _match_creates(sub_code2, patterns, sub_idents2)
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
                      expected_objects: list[str] | set[str] = None, object_type: str = None,
                      name_mapping: dict[str, str] = None) -> int:
        """
        Validates that a SQL artifact file exists, contains executable statements,
        and includes all expected objects by identity/type without executing them.

        name_mapping optionally translates expected names to defined names
        (both uppercase) for categories whose dump names differ from source
        names by an exact mapping (e.g. renamed domains). Without it, expected
        names must appear verbatim; no fuzzy aliasing is applied, so one
        defined object can never satisfy two expected identities.
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
                if name_mapping:
                    missing = sorted(
                        src for src in expected_set
                        if name_mapping.get(src, src) not in defined
                    )
                else:
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

