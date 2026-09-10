import logging
import os
import re
import sys

# Ensure the firebird_grammar directory is in the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'firebird_grammar'))

from collections import defaultdict
from typing import Any, TypeVar, Optional
from antlr4 import InputStream, CommonTokenStream, ParserRuleContext
from antlr4.atn.PredictionMode import PredictionMode
from antlr4.error.ErrorListener import ErrorListener
from antlr4.error.ErrorStrategy import BailErrorStrategy, DefaultErrorStrategy
from antlr4.error.Errors import ParseCancellationException, RecognitionException
from antlr4.TokenStreamRewriter import TokenStreamRewriter

from .firebird_grammar import FirebirdParserVisitor, FirebirdParser, FirebirdLexer
from models import pg_quote_ident, get_postgres_type
from utils import choose_dollar_tag

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=ParserRuleContext)


def _find_node(ctx: ParserRuleContext | None, node_type: type[T]) -> T | None:
    """
    Recursively searches the AST using depth-first search (DFS)
    for the first descendant node matching node_type.
    """
    if isinstance(ctx, node_type):
        return ctx
    if hasattr(ctx, 'children') and ctx.children:
        for child in ctx.children:
            res = _find_node(child, node_type)
            if res is not None:
                return res
    return None


def _is_inside(ctx: ParserRuleContext | None, context_type: type[ParserRuleContext]) -> bool:
    """
    Checks whether ctx is enclosed within an ancestor AST node of type context_type.
    """
    curr = ctx
    while curr:
        if isinstance(curr, context_type):
            return True
        curr = getattr(curr, 'parentCtx', None)
    return False


_EX_PATTERN = re.compile(
    r"('(?:''|[^'])*'|/\*.*?\*/|--[^\n]*)|"  # Group 1: strings / comments
    r"(\bEXCEPTION\s+([a-zA-Z0-9_$]+)\s+('(?:''|[^'])*')\s*;)",  # Group 2, 3, 4: EXCEPTION with msg
    flags=re.IGNORECASE
)

_OLD_NEW_PATTERN = re.compile(
    r"('(?:''|[^'])*'|/\*.*?\*/|--[^\n]*)|"  # Group 1: string literals and comments (preserve untouched)
    r"(\b(old|new)\.;?\s*\n\s*([a-zA-Z0-9_]+)\b)|"  # Group 2, 3, 4: split 'old.; \n col' recovery
    r"(\b(old|new)\.([a-zA-Z0-9_]+)\b)",  # Group 5, 6, 7: unquoted 'old.col'
    flags=re.IGNORECASE | re.DOTALL
)

_COLON_PATTERN = re.compile(
    r"('(?:''|[^'])*'|/\*.*?\*/|--[^\n]*)|"  # Group 1: strings / comments
    r"(\b(RETURNING|INTO|FROM|WHERE|AND|OR|SELECT|VALUES|SET|THEN|ELSE|DO|IF|IN|NOT|AS|JOIN|ON):([a-zA-Z0-9_$]+))",
    flags=re.IGNORECASE
)

_DATE_UNITS = (
    'YEAR', 'YEARS', 'MONTH', 'MONTHS', 'WEEK', 'WEEKS',
    'DAY', 'DAYS', 'HOUR', 'HOURS', 'MINUTE', 'MINUTES',
    'SECOND', 'SECONDS', 'MILLISECOND', 'MILLISECONDS', 'MS'
)
_DATE_UNITS_RE = '|'.join(_DATE_UNITS)
_TOKEN_DATE_FUNC_PATTERN = re.compile(
    r"('(?:''|[^'])*'|/\*.*?\*/|--[^\n]*)|(\bDATE(?:ADD|DIFF)\s*\()",
    flags=re.IGNORECASE | re.DOTALL
)

_STRIP_COMMENTS_PRESERVING_STRINGS = re.compile(
    r"('(?:''|[^'])*')|(/\*.*?\*/|--[^\n]*)",
    flags=re.DOTALL
)

_STRIP_SQL_LITERALS_AND_COMMENTS = re.compile(
    r"'(?:''|[^'])*'|/\*.*?\*/|--[^\n]*",
    flags=re.DOTALL
)

_CAST_DYNAMIC_DATE_PATTERN = re.compile(
    r"\bCAST\s*\(\s*'(NOW|TODAY|YESTERDAY|TOMORROW)'\s+AS\s+(DATE|TIMESTAMP|TIME)\b",
    flags=re.IGNORECASE
)

_NON_IMMUTABLE_PATTERN = re.compile(
    r'(\b(CURRENT_DATE|CURRENT_TIMESTAMP|CURRENT_TIME|LOCALTIMESTAMP|LOCALTIME)\b|'
    r'\b(NOW|RAND|RANDOM|CLOCK_TIMESTAMP|TIMEOFDAY|STATEMENT_TIMESTAMP|TRANSACTION_TIMESTAMP|NEXTVAL|CURRVAL|SETVAL)\s*\()',
    flags=re.IGNORECASE
)


def validate_immutable_expression(expr: str, context: str = "expression") -> None:
    """
    Validates that a PostgreSQL generated column or expression index does not reference
    volatile/stable functions (e.g. CURRENT_DATE, RANDOM(), nextval()) or dynamic date casts.
    Ignores plain string literals and comments to prevent false positives.
    """
    no_comments = _STRIP_COMMENTS_PRESERVING_STRINGS.sub(lambda match: match.group(1) if match.group(1) else " ", expr)
    m_cast = _CAST_DYNAMIC_DATE_PATTERN.search(no_comments)
    if m_cast:
        raise ValueError(
            f"Non-immutable date cast '{m_cast.group(0)}' in {context}: '{expr}' "
            f"is not permitted in PostgreSQL (generated columns and expression indexes must be IMMUTABLE)."
        )

    clean_expr = _STRIP_SQL_LITERALS_AND_COMMENTS.sub(" ", no_comments)
    if re.search(r'\bSELECT\b', clean_expr, re.IGNORECASE):
        raise ValueError(
            f"Subquery in {context}: '{expr}' "
            f"is not permitted in PostgreSQL (generated columns and expression indexes cannot contain subqueries)."
        )

    m = _NON_IMMUTABLE_PATTERN.search(clean_expr)
    if m:
        fn_or_kw = m.group(0).rstrip('(').strip()
        raise ValueError(
            f"Non-immutable function or keyword '{fn_or_kw}' in {context}: '{expr}' "
            f"is not permitted in PostgreSQL (generated columns and expression indexes must be IMMUTABLE)."
        )


def _normalize_date_funcs(sql: str) -> str:
    pos = 0
    result = []
    while pos < len(sql):
        m = _TOKEN_DATE_FUNC_PATTERN.search(sql, pos)
        if not m:
            result.append(sql[pos:])
            break
        result.append(sql[pos:m.start()])
        if m.group(1):
            result.append(m.group(1))
            pos = m.end()
            continue

        fn_match = m.group(2)
        fn_name = fn_match.split('(')[0].strip().upper()
        arg_start = m.end()
        idx = arg_start
        depth = 1
        in_str = False

        while idx < len(sql) and depth > 0:
            ch = sql[idx]
            if ch == "'":
                if not in_str:
                    in_str = True
                elif idx + 1 < len(sql) and sql[idx + 1] == "'":
                    idx += 1
                else:
                    in_str = False
            elif not in_str:
                if ch == '(':
                    depth += 1
                elif ch == ')':
                    depth -= 1
            idx += 1

        if depth != 0:
            result.append(sql[m.start():idx])
            pos = idx
            continue

        args_body = sql[arg_start:idx - 1]
        norm_args = _normalize_date_funcs(args_body)
        transformed = False

        if fn_name == 'DATEADD':
            d = 0
            s_in = False
            for i, c in enumerate(norm_args):
                if c == "'":
                    if not s_in:
                        s_in = True
                    elif i + 1 < len(norm_args) and norm_args[i + 1] == "'":
                        pass
                    else:
                        s_in = False
                elif not s_in:
                    if c == '(':
                        d += 1
                    elif c == ')':
                        d -= 1
                    elif d == 0:
                        tail = norm_args[i:]
                        m_to = re.match(rf"^(\b({_DATE_UNITS_RE})\b)\s+TO\b\s*", tail, re.IGNORECASE)
                        if m_to:
                            unit_found = m_to.group(1).upper()
                            num_expr = norm_args[:i].strip()
                            date_expr = norm_args[i + m_to.end():].strip()
                            if num_expr and date_expr:
                                result.append(f"DATEADD({unit_found}, {num_expr}, {date_expr})")
                                transformed = True
                                break
        elif fn_name == 'DATEDIFF':
            m_from = re.match(rf"^\s*(\b({_DATE_UNITS_RE})\b)\s+FROM\b", norm_args, re.IGNORECASE)
            if m_from:
                unit_found = m_from.group(1).upper()
                rest = norm_args[m_from.end():]
                d = 0
                s_in = False
                for i, c in enumerate(rest):
                    if c == "'":
                        if not s_in:
                            s_in = True
                        elif i + 1 < len(rest) and rest[i + 1] == "'":
                            pass
                        else:
                            s_in = False
                    elif not s_in:
                        if c == '(':
                            d += 1
                        elif c == ')':
                            d -= 1
                        elif d == 0:
                            m_to = re.match(r"^\bTO\b\s*", rest[i:], re.IGNORECASE)
                            if m_to:
                                d1_expr = rest[:i].strip()
                                d2_expr = rest[i + m_to.end():].strip()
                                if d1_expr and d2_expr:
                                    result.append(f"DATEDIFF({unit_found}, {d1_expr}, {d2_expr})")
                                    transformed = True
                                    break

        if not transformed:
            result.append(f"{fn_match}{norm_args})")
        pos = idx

    return "".join(result)


def _normalize_variable_declarations(sql: str) -> str:
    start_pat = re.compile(
        r"('(?:''|[^'])*'|/\*.*?\*/|--[^\n]*)|(\b(DECLARE\s+(?:VARIABLE\s+)?|VARIABLE\s+)([a-zA-Z0-9_$]+|\"[^\"]+\")\s+)",
        flags=re.IGNORECASE
    )
    pos = 0
    result = []
    while pos < len(sql):
        m = start_pat.search(sql, pos)
        if not m:
            result.append(sql[pos:])
            break
        result.append(sql[pos:m.start()])
        if m.group(1):
            result.append(m.group(1))
            pos = m.end()
            continue

        decl_kw = m.group(3).strip()
        var_name = m.group(4)
        decl_start = m.end()
        idx = decl_start
        in_str = False
        in_line_cmt = False
        in_block_cmt = False

        while idx < len(sql):
            c = sql[idx]
            if in_line_cmt:
                if c == '\n':
                    in_line_cmt = False
            elif in_block_cmt:
                if c == '*' and idx + 1 < len(sql) and sql[idx + 1] == '/':
                    in_block_cmt = False
                    idx += 1
            elif in_str:
                if c == "'":
                    if idx + 1 < len(sql) and sql[idx + 1] == "'":
                        idx += 1
                    else:
                        in_str = False
            else:
                if c == "'":
                    in_str = True
                elif c == '-' and idx + 1 < len(sql) and sql[idx + 1] == '-':
                    in_line_cmt = True
                    idx += 1
                elif c == '/' and idx + 1 < len(sql) and sql[idx + 1] == '*':
                    in_block_cmt = True
                    idx += 1
                elif c == ';':
                    break
            idx += 1

        if idx >= len(sql):
            result.append(sql[m.start():])
            break

        decl_body = sql[decl_start:idx].strip()
        pos = idx + 1

        d = 0
        s_in = False
        b_in = False
        l_in = False
        init_pos = None
        init_len = 0
        i = 0
        while i < len(decl_body):
            c = decl_body[i]
            if l_in:
                if c == '\n':
                    l_in = False
            elif b_in:
                if c == '*' and i + 1 < len(decl_body) and decl_body[i + 1] == '/':
                    b_in = False
                    i += 1
            elif s_in:
                if c == "'":
                    if i + 1 < len(decl_body) and decl_body[i + 1] == "'":
                        i += 1
                    else:
                        s_in = False
            else:
                if c == "'":
                    s_in = True
                elif c == '-' and i + 1 < len(decl_body) and decl_body[i + 1] == '-':
                    l_in = True
                    i += 1
                elif c == '/' and i + 1 < len(decl_body) and decl_body[i + 1] == '*':
                    b_in = True
                    i += 1
                elif c == '(':
                    d += 1
                elif c == ')':
                    d -= 1
                elif d == 0:
                    if decl_body[i:i+2] == ':=':
                        init_pos = i
                        init_len = 2
                        break
                    elif c == '=':
                        init_pos = i
                        init_len = 1
                        break
                    elif re.match(r'^\bDEFAULT\b', decl_body[i:], re.IGNORECASE):
                        m_def = re.match(r'^\bDEFAULT\b', decl_body[i:], re.IGNORECASE)
                        init_pos = i
                        init_len = m_def.end()
                        break
            i += 1

        has_not_null = False
        if init_pos is not None:
            type_part = decl_body[:init_pos].strip()
            expr = decl_body[init_pos + init_len:].strip()
            if re.search(r'\bNOT\s+NULL\s*$', expr, re.IGNORECASE):
                has_not_null = True
                expr = re.sub(r'\bNOT\s+NULL\s*$', '', expr, flags=re.IGNORECASE).strip()
            if re.search(r'\bNOT\s+NULL\s*$', type_part, re.IGNORECASE):
                has_not_null = True
                type_part = re.sub(r'\bNOT\s+NULL\s*$', '', type_part, flags=re.IGNORECASE).strip()
            nn_str = ' NOT NULL' if has_not_null else ''
            result.append(f'{decl_kw} {var_name} {type_part}{nn_str} DEFAULT {expr};')
        else:
            type_part = decl_body.strip()
            if re.search(r'\bNOT\s+NULL\s*$', type_part, re.IGNORECASE):
                has_not_null = True
                type_part = re.sub(r'\bNOT\s+NULL\s*$', '', type_part, flags=re.IGNORECASE).strip()
            nn_str = ' NOT NULL' if has_not_null else ''
            result.append(f'{decl_kw} {var_name} {type_part}{nn_str};')

    return ''.join(result)


def _split_param_literals(s: str) -> list[tuple[bool, str]]:
    chunks = []
    pat = re.compile(r"('(?:''|[^'])*'|/\*.*?\*/|--[^\n]*)", flags=re.DOTALL)
    last = 0
    for m in pat.finditer(s):
        if m.start() > last:
            chunks.append((False, s[last:m.start()]))
        chunks.append((True, m.group(0)))
        last = m.end()
    if last < len(s):
        chunks.append((False, s[last:]))
    return chunks


def _skip_comments_and_ws(sql: str, pos: int) -> int:
    idx = pos
    while idx < len(sql):
        c = sql[idx]
        if c.isspace():
            idx += 1
        elif c == '-' and idx + 1 < len(sql) and sql[idx + 1] == '-':
            idx += 2
            while idx < len(sql) and sql[idx] != '\n':
                idx += 1
        elif c == '/' and idx + 1 < len(sql) and sql[idx + 1] == '*':
            idx += 2
            while idx + 1 < len(sql) and not (sql[idx] == '*' and sql[idx + 1] == '/'):
                idx += 1
            idx += 2
        else:
            break
    return idx


def _scan_balanced_parens(sql: str, start_idx: int) -> tuple[int, str]:
    d = 1
    idx = start_idx + 1
    in_str = False
    in_line_cmt = False
    in_block_cmt = False
    while idx < len(sql) and d > 0:
        c = sql[idx]
        if in_line_cmt:
            if c == '\n':
                in_line_cmt = False
        elif in_block_cmt:
            if c == '*' and idx + 1 < len(sql) and sql[idx + 1] == '/':
                in_block_cmt = False
                idx += 1
        elif in_str:
            if c == "'":
                if idx + 1 < len(sql) and sql[idx + 1] == "'":
                    idx += 1
                else:
                    in_str = False
        else:
            if c == "'":
                in_str = True
            elif c == '-' and idx + 1 < len(sql) and sql[idx + 1] == '-':
                in_line_cmt = True
                idx += 1
            elif c == '/' and idx + 1 < len(sql) and sql[idx + 1] == '*':
                in_block_cmt = True
                idx += 1
            elif c == '(':
                d += 1
            elif c == ')':
                d -= 1
        idx += 1
    if d > 0:
        return -1, ""
    return idx - 1, sql[start_idx + 1:idx - 1]


def _normalize_single_param_list(params_body: str, is_output: bool = False,
                                 proc_name: str = "",
                                 not_null_dict: dict[str, list[str]] = None) -> str:
    p_d = 0
    p_in_str = False
    p_in_line = False
    p_in_block = False
    parts = []
    last_p = 0
    for i, c in enumerate(params_body):
        if p_in_line:
            if c == '\n':
                p_in_line = False
        elif p_in_block:
            if c == '*' and i + 1 < len(params_body) and params_body[i + 1] == '/':
                p_in_block = False
                i += 1
        elif p_in_str:
            if c == "'":
                if i + 1 < len(params_body) and params_body[i + 1] == "'":
                    pass
                else:
                    p_in_str = False
        else:
            if c == "'":
                p_in_str = True
            elif c == '-' and i + 1 < len(params_body) and params_body[i + 1] == '-':
                p_in_line = True
                i += 1
            elif c == '/' and i + 1 < len(params_body) and params_body[i + 1] == '*':
                p_in_block = True
                i += 1
            elif c in ('(', '['):
                p_d += 1
            elif c in (')', ']'):
                p_d -= 1
            elif c == ',' and p_d == 0:
                parts.append(params_body[last_p:i])
                last_p = i + 1
    parts.append(params_body[last_p:])

    norm_parts = []
    for part in parts:
        chunks = _split_param_literals(part)
        has_not_null = False
        cleaned_chunks = []
        param_name = None
        for is_lit, text in chunks:
            if is_lit:
                cleaned_chunks.append((is_lit, text))
            else:
                if param_name is None:
                    m_name = re.match(r'^\s*([a-zA-Z0-9_$]+|"[^"]+")', text)
                    if m_name:
                        param_name = m_name.group(1)
                if re.search(r"\bNOT\s+NULL\b", text, re.IGNORECASE):
                    has_not_null = True
                    text = re.sub(r"\bNOT\s+NULL\b", "", text, flags=re.IGNORECASE)
                cleaned_chunks.append((is_lit, text))

        if has_not_null and param_name and not_null_dict is not None and proc_name:
            not_null_dict.setdefault(proc_name, []).append(_normalize_ident_case(param_name))

        if not is_output:
            e_d = 0
            eq_chunk_idx = None
            eq_char_idx = None
            for c_idx, (is_lit, text) in enumerate(cleaned_chunks):
                if is_lit:
                    continue
                for j, ch in enumerate(text):
                    if ch in ('(', '['):
                        e_d += 1
                    elif ch in (')', ']'):
                        e_d -= 1
                    elif ch == '=' and e_d == 0:
                        eq_chunk_idx = c_idx
                        eq_char_idx = j
                        break
                if eq_chunk_idx is not None:
                    break

            if eq_chunk_idx is not None:
                before_eq = "".join(
                    text if not is_lit else ""
                    for is_lit, text in cleaned_chunks[:eq_chunk_idx]
                ) + cleaned_chunks[eq_chunk_idx][1][:eq_char_idx]
                if not re.search(r"\bDEFAULT\b", before_eq, re.IGNORECASE):
                    txt = cleaned_chunks[eq_chunk_idx][1]
                    cleaned_chunks[eq_chunk_idx] = (
                        False,
                        txt[:eq_char_idx] + " DEFAULT " + txt[eq_char_idx + 1:]
                    )

        norm_parts.append("".join(text for _, text in cleaned_chunks))

    return ",".join(norm_parts)


def _normalize_procedure_params(sql: str, not_null_params: dict[str, list[str]] = None,
                                not_null_outputs: dict[str, list[str]] = None) -> str:
    proc_pat = re.compile(
        r"('(?:''|[^'])*'|/\*.*?\*/|--[^\n]*)|(\b(?:CREATE(?:\s+OR\s+ALTER)?|RECREATE|ALTER)\s+PROCEDURE\s+([a-zA-Z0-9_$]+|\"[^\"]+\"))",
        flags=re.IGNORECASE
    )
    pos = 0
    result = []
    while pos < len(sql):
        m = proc_pat.search(sql, pos)
        if not m:
            result.append(sql[pos:])
            break
        result.append(sql[pos:m.start()])
        if m.group(1):
            result.append(m.group(1))
            pos = m.end()
            continue

        result.append(m.group(2))
        proc_name = m.group(3).strip('"').lower() if m.group(3) else ""
        cur = m.end()

        # Check for input parameters (...)
        next_tok_idx = _skip_comments_and_ws(sql, cur)
        if next_tok_idx < len(sql) and sql[next_tok_idx] == '(':
            end_paren, inside = _scan_balanced_parens(sql, next_tok_idx)
            if end_paren != -1:
                result.append(sql[cur:next_tok_idx])
                norm_in = _normalize_single_param_list(inside, is_output=False, proc_name=proc_name, not_null_dict=not_null_params)
                result.append(f"({norm_in})")
                cur = end_paren + 1

        # Check for RETURNS (...)
        next_tok_idx = _skip_comments_and_ws(sql, cur)
        m_ret = re.match(r'^RETURNS\b', sql[next_tok_idx:], re.IGNORECASE)
        if m_ret:
            ret_kw_end = next_tok_idx + m_ret.end()
            after_ret_idx = _skip_comments_and_ws(sql, ret_kw_end)
            if after_ret_idx < len(sql) and sql[after_ret_idx] == '(':
                end_ret_paren, ret_inside = _scan_balanced_parens(sql, after_ret_idx)
                if end_ret_paren != -1:
                    result.append(sql[cur:after_ret_idx])
                    norm_out = _normalize_single_param_list(ret_inside, is_output=True, proc_name=proc_name, not_null_dict=not_null_outputs)
                    result.append(f"({norm_out})")
                    cur = end_ret_paren + 1

        pos = cur

    return "".join(result)


def _parse_first_skip_val(s: str, pos: int) -> tuple[Optional[str], int]:
    while pos < len(s) and s[pos].isspace():
        pos += 1
    if pos >= len(s):
        return None, pos
    if s[pos] == '(':
        start = pos
        depth = 1
        pos += 1
        in_str = False
        while pos < len(s) and depth > 0:
            c = s[pos]
            if c == "'":
                if not in_str:
                    in_str = True
                elif pos + 1 < len(s) and s[pos + 1] == "'":
                    pos += 1
                else:
                    in_str = False
            elif not in_str:
                if c == '(':
                    depth += 1
                elif c == ')':
                    depth -= 1
            pos += 1
        return s[start:pos], pos
    elif s[pos] == ':':
        m = re.match(r"^:[a-zA-Z0-9_$]+", s[pos:])
        if m:
            return m.group(0), pos + m.end()
    else:
        m = re.match(r"^[0-9]+", s[pos:])
        if m:
            return m.group(0), pos + m.end()
        m_ident = re.match(r"^[a-zA-Z_][a-zA-Z0-9_$]*", s[pos:])
        if m_ident:
            val = m_ident.group(0)
            if val.upper() not in ("SKIP", "SELECT", "FROM", "WHERE", "GROUP", "HAVING", "ORDER", "UNION", "ROWS"):
                end_pos = pos + m_ident.end()
                next_pos = end_pos
                while next_pos < len(s) and s[next_pos].isspace():
                    next_pos += 1
                if next_pos < len(s) and s[next_pos] == '(':
                    fn_arg, fn_end = _parse_first_skip_val(s, next_pos)
                    if fn_arg:
                        return s[pos:fn_end], fn_end
                return val, end_pos
    return None, pos


def _normalize_first_skip(sql: str, expr_map: dict[str, str]) -> str:
    start_pat = re.compile(
        r"('(?:''|[^'])*'|/\*.*?\*/|--[^\n]*)|(\bSELECT\b)",
        flags=re.IGNORECASE
    )
    pos = 0
    result = []
    while pos < len(sql):
        m = start_pat.search(sql, pos)
        if not m:
            result.append(sql[pos:])
            break
        result.append(sql[pos:m.start()])
        if m.group(1):
            result.append(m.group(1))
            pos = m.end()
            continue

        sel_kw = m.group(2)
        cur = m.end()
        first_expr, skip_expr = None, None
        matched_any = False
        for _ in range(2):
            while cur < len(sql) and sql[cur].isspace():
                cur += 1
            m_kw = re.match(r"^(FIRST|SKIP)\b", sql[cur:], re.IGNORECASE)
            if m_kw:
                matched_any = True
                kw = m_kw.group(1).upper()
                val, cur = _parse_first_skip_val(sql, cur + m_kw.end())
                if kw == "FIRST":
                    first_expr = val
                else:
                    skip_expr = val
            else:
                break

        if not matched_any:
            result.append(sel_kw)
            pos = m.end()
            continue

        def process_val(v):
            if v is None:
                return None
            val_clean = v.strip()
            if val_clean.isdigit():
                return val_clean
            sentinel = f"888{len(expr_map):09d}"
            cleaned = re.sub(r":([a-zA-Z0-9_$]+)", r"\1", val_clean)
            expr_map[sentinel] = cleaned
            return sentinel

        f_num = process_val(first_expr)
        s_num = process_val(skip_expr)

        parts = [sel_kw]
        if f_num is not None:
            parts.append(f"FIRST {f_num}")
        if s_num is not None:
            parts.append(f"SKIP {s_num}")
        parts.append("")
        result.append(" ".join(parts))
        pos = cur

    return "".join(result)


def _normalize_type_of(sql: str, domain_types: dict[str, str] = None) -> str:
    pat = re.compile(
        r"('(?:''|[^'])*'|/\*.*?\*/|--[^\n]*)|(\bTYPE\s+OF\s+(?:COLUMN\s+)?(([a-zA-Z0-9_$]+|\"[^\"]+\")(?:\s*\.\s*([a-zA-Z0-9_$]+|\"[^\"]+\"))?))",
        flags=re.IGNORECASE
    )
    norm_domain_types = {k.strip(' "').upper(): v.strip() for k, v in (domain_types or {}).items()}

    def repl(m):
        if m.group(1):
            return m.group(1)
        full_kw = m.group(2)
        m_col = re.match(
            r'^\bTYPE\s+OF\s+COLUMN\s+(([a-zA-Z0-9_$]+|\"[^\"]+\")\s*\.\s*([a-zA-Z0-9_$]+|\"[^\"]+\"))',
            full_kw,
            re.IGNORECASE
        )
        if m_col:
            return f"{m_col.group(2)}.{m_col.group(3)}%TYPE"
        m_col_nodot = re.match(
            r'^\bTYPE\s+OF\s+(([a-zA-Z0-9_$]+|\"[^\"]+\")\s*\.\s*([a-zA-Z0-9_$]+|\"[^\"]+\"))',
            full_kw,
            re.IGNORECASE
        )
        if m_col_nodot:
            return f"{m_col_nodot.group(2)}.{m_col_nodot.group(3)}%TYPE"
        m_dom = re.match(r'^\bTYPE\s+OF\s+([a-zA-Z0-9_$]+|\"[^\"]+\")', full_kw, re.IGNORECASE)
        if m_dom:
            raw_dom = m_dom.group(1)
            is_delimited = len(raw_dom) >= 2 and raw_dom.startswith('"') and raw_dom.endswith('"')
            if is_delimited:
                clean_dom = raw_dom.strip(' "').upper()
                if clean_dom in norm_domain_types:
                    base_type = norm_domain_types[clean_dom]
                    try:
                        base_type = get_postgres_type(base_type)
                    except Exception:
                        pass
                    return base_type
                raise ValueError(f"Unknown domain '{raw_dom}' in TYPE OF expression.")
            clean_dom = raw_dom.upper()
            # Bare native type names denote the native type, never a homonym
            # domain: TYPE OF INTEGER is INTEGER even beside domain "INTEGER".
            if clean_dom in _NATIVE_TYPE_WORDS:
                try:
                    return get_postgres_type(clean_dom)
                except Exception:
                    return clean_dom
            if clean_dom in norm_domain_types:
                base_type = norm_domain_types[clean_dom]
                try:
                    base_type = get_postgres_type(base_type)
                except Exception:
                    pass
                return base_type
            raise ValueError(f"Unknown domain '{raw_dom}' in TYPE OF expression.")
        return full_kw

    return pat.sub(repl, sql)


# Single-word native type names that a BARE (unquoted) reference always
# denotes, even when a domain of the same name exists. Firebird resolves
# unquoted identifiers case-insensitively, and these reserved type names
# (Firebird 4 appendix C) can never address a delimited domain: only
# "NAME" (delimited) may resolve through the domain map.
_NATIVE_TYPE_WORDS = frozenset({
    'BIGINT', 'BLOB', 'BOOLEAN', 'CHAR', 'CHARACTER', 'DATE', 'DEC',
    'DECFLOAT', 'DECIMAL', 'DOUBLE', 'FLOAT', 'INT', 'INTEGER', 'INT128',
    'NUMERIC', 'SMALLINT', 'TIME', 'TIMESTAMP', 'VARCHAR',
})


def convert_firebird_type_declaration(raw_type: str, domain_map: dict[str, str] = None) -> str:
    if not raw_type:
        return ""
    # Check domain_map FIRST, before type substitutions, so delimited domains
    # whose names collide with native types (e.g. "INT128") resolve correctly.
    # But a bare word that IS a native type name never consults the map:
    # INT128 means NUMERIC(39) even in a database owning domain "INT128".
    if domain_map:
        stripped = raw_type.strip()
        if len(stripped) >= 2 and stripped.startswith('"') and stripped.endswith('"'):
            inner = stripped[1:-1].upper()
            if inner in domain_map:
                return domain_map[inner]
        else:
            u = stripped.upper()
            if u not in _NATIVE_TYPE_WORDS and u in domain_map:
                return domain_map[u]
    cleaned = re.sub(r'(?i)\bBLOB\s+SUBTYPE\s+(?:1|TEXT)\b', 'TEXT', raw_type)
    cleaned = re.sub(r'(?i)\bBLOB\s+SUBTYPE\s+(?:0|BINARY)\b', 'BYTEA', cleaned)
    cleaned = re.sub(r'(?i)\bBLOB\b', 'BYTEA', cleaned)
    cleaned = re.sub(r'(?i)\b(?:CHAR|VARCHAR)(?:\s*\(\s*\d+\s*\))?\s+CHARACTER\s+SET\s+OCTETS\b', 'BYTEA', cleaned)
    cleaned = re.sub(r'(?i)\bDECFLOAT(?:\s*\(\s*(?:16|34)\s*\))?\b', 'NUMERIC', cleaned)
    cleaned = re.sub(r'(?i)\bINT128\b', 'NUMERIC(39)', cleaned)
    cleaned = re.sub(r'(?i)\bTIME\s+WITH\s+TIME\s+ZONE\b', 'TIMETZ', cleaned)
    cleaned = re.sub(r'(?i)\bTIMESTAMP\s+WITH\s+TIME\s+ZONE\b', 'TIMESTAMPTZ', cleaned)
    return cleaned


def _normalize_data_types(sql: str) -> str:
    pat = re.compile(
        r"('(?:''|[^'])*'|\"(?:\"\"|[^\"])*\"|/\*.*?\*/|--[^\n]*)|(\bDECFLOAT\s*\(\s*(?:16|34)\s*\))",
        flags=re.IGNORECASE
    )
    def repl(m):
        if m.group(1):
            return m.group(1)
        return 'NUMERIC'
    return pat.sub(repl, sql)


def _normalize_when_any(sql: str) -> str:
    pat = re.compile(
        r"('(?:''|[^'])*'|/\*.*?\*/|--[^\n]*)|(\bWHEN\s+ANY\s+DO\b)",
        flags=re.IGNORECASE
    )
    def repl(m):
        if m.group(1):
            return m.group(1)
        return "/* __FB_WHEN_ANY__ */"
    return pat.sub(repl, sql)


def _normalize_returning_values(sql: str) -> str:
    pat = re.compile(
        r"('(?:''|[^'])*'|/\*.*?\*/|--[^\n]*)|(\bEXECUTE\s+PROCEDURE\s+([a-zA-Z0-9_$]+|\"[^\"]+\")(?:\s*(\([^;]*?\)))?\s+RETURNING_VALUES\s+([^;]+);)",
        flags=re.IGNORECASE
    )
    def repl(m):
        if m.group(1):
            return m.group(1)
        proc_name = m.group(3)
        args = m.group(4) if m.group(4) else "()"
        vars_part = m.group(5).strip()
        return f"SELECT * FROM {proc_name}{args} INTO {vars_part};"
    return pat.sub(repl, sql)


def _split_top_level_args(s: str) -> list[str]:
    parts = []
    depth = 0
    in_str = False
    last = 0
    for i, c in enumerate(s):
        if c == "'":
            if not in_str:
                in_str = True
            elif i + 1 < len(s) and s[i + 1] == "'":
                pass
            else:
                in_str = False
        elif not in_str:
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
            elif c == "," and depth == 0:
                parts.append(s[last:i].strip())
                last = i + 1
    parts.append(s[last:].strip())
    return [p for p in parts if p]


def _unwrap_outer_parens(s: str) -> str:
    s = s.strip()
    while s.startswith("(") and s.endswith(")"):
        d = 0
        matching = True
        for c in s[:-1]:
            if c == "(":
                d += 1
            elif c == ")":
                d -= 1
            if d == 0:
                matching = False
                break
        if matching:
            s = s[1:-1].strip()
        else:
            break
    return s


def _is_timestamp_type(type_str: str) -> bool:
    if not type_str:
        return False
    return 'TIMESTAMP' in type_str.strip().upper()


def _is_date_type(type_str: str) -> bool:
    if not type_str:
        return False
    u = type_str.strip().upper()
    return ('DATE' in u) and ('TIMESTAMP' not in u)


def _is_timestamp_expr(expr: str, symbols: dict[str, str] = None) -> bool:
    s = _unwrap_outer_parens(expr)
    upper = s.upper()
    if (
        upper.startswith("TIMESTAMP ")
        or upper.startswith("TIMESTAMP'")
        or upper in ("CURRENT_TIMESTAMP", "NOW()", "LOCALTIMESTAMP")
        or bool(re.search(r"\bAS\s+TIMESTAMP\b", upper))
        or upper.endswith("::TIMESTAMP")
    ):
        return True

    m_fn = re.match(r"^(COALESCE|NULLIF|IIF|DATEADD)\s*\((.*)\)$", s, re.IGNORECASE | re.DOTALL)
    if m_fn:
        fn = m_fn.group(1).upper()
        args = _split_top_level_args(m_fn.group(2))
        if fn == "DATEADD" and len(args) == 3:
            return _is_timestamp_expr(args[2], symbols)
        if fn == "NULLIF" and args:
            return _is_timestamp_expr(args[0], symbols)
        if fn == "IIF" and len(args) >= 3:
            return _is_timestamp_expr(args[1], symbols) or _is_timestamp_expr(args[2], symbols)
        if fn == "COALESCE" and args:
            return any(_is_timestamp_expr(arg, symbols) for arg in args)

    if upper.startswith("CASE") and upper.endswith("END"):
        then_parts = re.findall(r"\bTHEN\b\s+(.*?)\s+(?=\bWHEN\b|\bELSE\b|\bEND\b)", s, re.IGNORECASE | re.DOTALL)
        else_match = re.search(r"\bELSE\b\s+(.*?)\s+\bEND\b", s, re.IGNORECASE | re.DOTALL)
        branch_exprs = list(then_parts)
        if else_match:
            branch_exprs.append(else_match.group(1))
        if branch_exprs and any(_is_timestamp_expr(b, symbols) for b in branch_exprs):
            return True

    if symbols:
        clean = '.'.join(p.strip('":') for p in s.split('.')).lower()
        if '.' in clean:
            # Qualified ref: prefer qualified key; bare fallback only if qualified is absent
            col_part = clean.split('.')[-1]
            key = clean if clean in symbols else col_part
            if _is_timestamp_type(symbols.get(key, '')):
                return True
        else:
            if _is_timestamp_type(symbols.get(clean, '')):
                return True

    return False


def _is_date_expr(expr: str, symbols: dict[str, str] = None) -> bool:
    if _is_timestamp_expr(expr, symbols):
        return False
    s = _unwrap_outer_parens(expr)
    upper = s.upper()
    if (
        upper.startswith("DATE ")
        or upper.startswith("DATE'")
        or upper == "CURRENT_DATE"
        or bool(re.search(r"\bAS\s+DATE\b", upper))
        or upper.endswith("::DATE")
    ):
        return True

    m_fn = re.match(r"^(COALESCE|NULLIF|IIF|DATEADD)\s*\((.*)\)$", s, re.IGNORECASE | re.DOTALL)
    if m_fn:
        fn = m_fn.group(1).upper()
        args = _split_top_level_args(m_fn.group(2))
        if fn == "DATEADD" and len(args) == 3:
            return _is_date_expr(args[2], symbols)
        if fn == "NULLIF" and args:
            return _is_date_expr(args[0], symbols)
        if fn == "IIF" and len(args) >= 3:
            branches = [args[1], args[2]]
            b_non_null = [b for b in branches if b.strip().upper() != "NULL"]
            return bool(b_non_null) and all(_is_date_expr(b, symbols) for b in b_non_null)
        if fn == "COALESCE" and args:
            non_null = [a for a in args if a.strip().upper() != "NULL"]
            return bool(non_null) and all(_is_date_expr(arg, symbols) for arg in non_null)

    if upper.startswith("CASE") and upper.endswith("END"):
        then_parts = re.findall(r"\bTHEN\b\s+(.*?)\s+(?=\bWHEN\b|\bELSE\b|\bEND\b)", s, re.IGNORECASE | re.DOTALL)
        else_match = re.search(r"\bELSE\b\s+(.*?)\s+\bEND\b", s, re.IGNORECASE | re.DOTALL)
        branch_exprs = list(then_parts)
        if else_match:
            branch_exprs.append(else_match.group(1))
        b_non_null = [b for b in branch_exprs if b.strip().upper() != "NULL"]
        return bool(b_non_null) and all(_is_date_expr(b, symbols) for b in b_non_null)

    if symbols:
        clean = '.'.join(p.strip('":') for p in s.split('.')).lower()
        if '.' in clean:
            # Qualified ref: prefer qualified key; bare fallback only if qualified is absent
            col_part = clean.split('.')[-1]
            key = clean if clean in symbols else col_part
            if _is_date_type(symbols.get(key, '')):
                return True
        else:
            if _is_date_type(symbols.get(clean, '')):
                return True

    return False


def _is_time_type(type_str: str) -> bool:
    if not type_str:
        return False
    u = type_str.strip().upper()
    return ('TIME' in u) and ('TIMESTAMP' not in u)


def _is_time_expr(expr: str, symbols: dict[str, str] = None) -> bool:
    if _is_timestamp_expr(expr, symbols):
        return False
    s = _unwrap_outer_parens(expr)
    upper = s.upper()
    if (
        upper.startswith("TIME ")
        or upper.startswith("TIME'")
        or upper in ("CURRENT_TIME", "LOCALTIME")
        or bool(re.search(r'\bAS\s+TIME\b', upper))
        or upper.endswith("::TIME")
    ):
        return True

    m_fn = re.match(r"^(COALESCE|NULLIF|IIF|DATEADD)\s*\((.*)\)$", s, re.IGNORECASE | re.DOTALL)
    if m_fn:
        fn = m_fn.group(1).upper()
        args = _split_top_level_args(m_fn.group(2))
        if fn == "DATEADD" and len(args) == 3:
            return _is_time_expr(args[2], symbols)
        if fn == "NULLIF" and args:
            return _is_time_expr(args[0], symbols)
        if fn == "IIF" and len(args) >= 3:
            branches = [args[1], args[2]]
            b_non_null = [b for b in branches if b.strip().upper() != "NULL"]
            return bool(b_non_null) and all(_is_time_expr(b, symbols) for b in b_non_null)
        if fn == "COALESCE" and args:
            non_null = [a for a in args if a.strip().upper() != "NULL"]
            return bool(non_null) and all(_is_time_expr(arg, symbols) for arg in non_null)

    if upper.startswith("CASE") and upper.endswith("END"):
        then_parts = re.findall(r"\bTHEN\b\s+(.*?)\s+(?=\bWHEN\b|\bELSE\b|\bEND\b)", s, re.IGNORECASE | re.DOTALL)
        else_match = re.search(r"\bELSE\b\s+(.*?)\s+\bEND\b", s, re.IGNORECASE | re.DOTALL)
        branch_exprs = list(then_parts)
        if else_match:
            branch_exprs.append(else_match.group(1))
        b_non_null = [b for b in branch_exprs if b.strip().upper() != "NULL"]
        return bool(b_non_null) and all(_is_time_expr(b, symbols) for b in b_non_null)

    if symbols:
        clean = '.'.join(p.strip('":') for p in s.split('.')).lower()
        if '.' in clean:
            # Qualified ref: prefer qualified key; bare fallback only if qualified is absent
            col_part = clean.split('.')[-1]
            key = clean if clean in symbols else col_part
            if _is_time_type(symbols.get(key, '')):
                return True
        else:
            if _is_time_type(symbols.get(clean, '')):
                return True

    return False


def _normalize_ident_case(raw_ident: str) -> str:
    if not raw_ident:
        return ""
    if raw_ident.startswith('"') and raw_ident.endswith('"'):
        clean = raw_ident[1:-1].replace('""', '"')
        return pg_quote_ident(clean.lower())
    return raw_ident


class TableSource:
    def __init__(self, table_name: str, alias: Optional[str] = None, qualifier: str = "", subquery_ctx: Optional[Any] = None):
        self.table_name = table_name
        self.table_name_clean = table_name.strip('":').lower()
        self.alias = alias
        self.alias_clean = alias.strip('":').lower() if alias else None
        self.qualifier = qualifier
        self.subquery_ctx = subquery_ctx


class QueryScope:
    def __init__(self, parent=None, tables: Optional[list[TableSource]] = None, using_columns: Optional[set[str]] = None):
        self.parent: Optional[QueryScope] = parent
        self.tables: list[TableSource] = tables or []
        self.using_columns: set[str] = using_columns or set()


class ASTDialectRewriter(FirebirdParserVisitor):
    """
    Pass 1 Visitor: Operates on AST nodes and rewrites tokens directly in the TokenStreamRewriter.
    This guarantees that dialect transformations (bind variables, sequence functions, procedure calls,
    exception statements, limit/offset clauses, leave statements, and RDB$DATABASE removals)
    are performed in semantic context, leaving string literals and comments 100% untouched.
    """

    def __init__(self, rewriter: TokenStreamRewriter, symbols: dict[str, str] = None, expr_map: dict[str, str] = None, sequence_increments: dict[str, int] = None, domain_map: dict[str, str] = None):
        super().__init__()
        self.rewriter = rewriter
        self.handled_qbs = set()
        self.symbols: dict[str, str] = {k.strip('":').lower(): v.upper() for k, v in symbols.items()} if symbols else {}
        self.expr_map: dict[str, str] = expr_map or {}
        self.domain_map: dict[str, str] = domain_map or {}
        self.sequence_increments: dict[str, int] | None = (
            {k.strip('":').lower(): v for k, v in sequence_increments.items()}
            if sequence_increments is not None
            else None
        )
        if symbols:
            for k, v in symbols.items():
                if k.lower().startswith("__seq_inc__"):
                    if self.sequence_increments is None:
                        self.sequence_increments = {}
                    try:
                        self.sequence_increments[k[len("__seq_inc__"):].lower()] = int(v)
                    except (ValueError, TypeError):
                        pass
        self.local_vars: set[str] = set()
        self.params: set[str] = set()
        self.is_trigger: bool = False
        self.trigger_return: str = "RETURN NEW;"
        self.current_scope: Optional[QueryScope] = None
        self.table_columns: dict[str, set[str]] = {}
        if symbols:
            for k in symbols.keys():
                k_clean = k.strip('":').lower()
                if '.' in k_clean:
                    tbl, col = k_clean.split('.', 1)
                    if tbl not in self.table_columns:
                        self.table_columns[tbl] = set()
                    self.table_columns[tbl].add(col)

    def visitCreate_procedure_body(self, ctx: FirebirdParser.Create_procedure_bodyContext):
        old_symbols = self.symbols.copy()
        old_local_vars = self.local_vars.copy()
        try:
            return self.visitChildren(ctx)
        finally:
            self.symbols = old_symbols
            self.local_vars = old_local_vars

    def visitCreate_trigger(self, ctx: FirebirdParser.Create_triggerContext):
        old_symbols = self.symbols.copy()
        old_local_vars = self.local_vars.copy()
        old_is_trigger = self.is_trigger
        old_trigger_return = self.trigger_return
        self.is_trigger = True

        table_name = ctx.tableview_name().getText().strip('":').lower() if ctx.tableview_name() else ""
        if not table_name:
            tables_in_symbols = {k.split('.')[0] for k in old_symbols if '.' in k and not k.startswith(('new.', 'old.'))}
            if len(tables_in_symbols) == 1:
                table_name = next(iter(tables_in_symbols))

        if table_name:
            prefix = f"{table_name}."
            for k, v in list(old_symbols.items()):
                if k.startswith(prefix):
                    col = k[len(prefix):]
                    self.symbols[f"new.{col}"] = v
                    self.symbols[f"old.{col}"] = v
                elif '.' not in k:
                    self.symbols[f"new.{k}"] = v
                    self.symbols[f"old.{k}"] = v
        else:
            for k, v in list(old_symbols.items()):
                col = k.split('.')[-1]
                self.symbols[f"new.{col}"] = v
                self.symbols[f"old.{col}"] = v

        simple_dml = ctx.simple_dml_trigger()
        timing = "BEFORE"
        events = "INSERT"
        if simple_dml:
            timing_node = simple_dml.getChild(0)
            timing = timing_node.getText()
            events = self._get_tokens_text(simple_dml.dml_event_clause())

        timing_upper = timing.upper()
        events_upper = events.upper()
        if "BEFORE" in timing_upper:
            if "DELETE" in events_upper and ("INSERT" in events_upper or "UPDATE" in events_upper):
                self.trigger_return = "IF TG_OP = 'DELETE' THEN RETURN OLD; ELSE RETURN NEW; END IF;"
            elif "DELETE" in events_upper:
                self.trigger_return = "RETURN OLD"
            else:
                self.trigger_return = "RETURN NEW"
        else:
            self.trigger_return = "RETURN NULL"

        try:
            return self.visitChildren(ctx)
        finally:
            self.symbols = old_symbols
            self.local_vars = old_local_vars
            self.is_trigger = old_is_trigger
            self.trigger_return = old_trigger_return

    def _convert_type(self, raw_type: str) -> str:
        return convert_firebird_type_declaration(raw_type, domain_map=self.domain_map)

    def visitType_spec(self, ctx: FirebirdParser.Type_specContext):
        raw_type = self._get_tokens_text(ctx)
        converted = self._convert_type(raw_type)
        if converted != raw_type:
            self.rewriter.replaceRangeTokens(ctx.start, ctx.stop, converted)
        return None

    def visitParameter(self, ctx: FirebirdParser.ParameterContext):
        if ctx.parameter_name() and ctx.type_spec():
            name = ctx.parameter_name().getText().strip('":').lower()
            raw_type = self._get_tokens_text(ctx.type_spec())
            self.symbols[name] = self._convert_type(raw_type).upper()
            self.params.add(name)
        return self.visitChildren(ctx)

    def visitVariable_declaration(self, ctx: FirebirdParser.Variable_declarationContext):
        if ctx.identifier() and ctx.type_spec():
            name = ctx.identifier().getText().strip('":').lower()
            raw_type = self._get_tokens_text(ctx.type_spec())
            self.symbols[name] = self._convert_type(raw_type).upper()
            self.local_vars.add(name)
        return self.visitChildren(ctx)

    def visitColumn_definition(self, ctx: FirebirdParser.Column_definitionContext):
        if ctx.column_name():
            name = ctx.column_name().getText().strip('":').lower()
            type_ctx = ctx.datatype() or ctx.type_name()
            if type_ctx:
                self.symbols[name] = type_ctx.getText().upper()
        return self.visitChildren(ctx)

    def visitBind_variable(self, ctx: FirebirdParser.Bind_variableContext):
        raw = ctx.getText()
        if raw.startswith(':'):
            name = raw.lstrip(':')
            norm = _normalize_ident_case(name)
            self.rewriter.replaceRangeTokens(ctx.start, ctx.stop, norm)
        return self.visitChildren(ctx)

    def _get_tokens_text(self, ctx) -> str:
        if ctx is None:
            return ""
        if hasattr(ctx, 'start') and hasattr(ctx, 'stop') and ctx.start and ctx.stop:
            return self.rewriter.getText(
                TokenStreamRewriter.DEFAULT_PROGRAM_NAME,
                ctx.start.tokenIndex,
                ctx.stop.tokenIndex
            )
        return ctx.getText()

    def visitId_expression(self, ctx: FirebirdParser.Id_expressionContext):
        if ctx.DELIMITED_ID():
            raw = ctx.getText()
            if raw.startswith('"') and raw.endswith('"'):
                clean = raw[1:-1].replace('""', '"')
                if clean.upper() not in ('NEW', 'OLD'):
                    norm = pg_quote_ident(clean.lower())
                    if norm != raw:
                        self.rewriter.replaceRangeTokens(ctx.start, ctx.stop, norm)
        return self.visitChildren(ctx)

    @staticmethod
    def _normalize_sequence_target(raw_seq: str) -> tuple[str, str, str]:
        raw = raw_seq.strip()
        if raw.startswith('"') and raw.endswith('"'):
            clean = raw[1:-1].replace('""', '"')
            quoted = pg_quote_ident(clean.lower())
            return quoted.replace("'", "''"), quoted, clean
        clean = raw
        quoted = pg_quote_ident(clean.lower())
        return raw.replace("'", "''"), quoted, clean

    def visitGeneral_element_part(self, ctx: FirebirdParser.General_element_partContext):
        self.visitChildren(ctx)

        if not ctx.id_expression():
            return None

        if not ctx.function_argument():
            ident = ctx.id_expression().getText().upper()
            if ident in ('INSERTING', 'UPDATING', 'DELETING'):
                parent = ctx.parentCtx
                if isinstance(parent, FirebirdParser.General_elementContext) and len(parent.children) == 1:
                    op = {'INSERTING': 'INSERT', 'UPDATING': 'UPDATE', 'DELETING': 'DELETE'}[ident]
                    self.rewriter.replaceRangeTokens(ctx.start, ctx.stop, f"TG_OP = '{op}'")
            return None

        fn_name = ctx.id_expression().getText().upper()
        func_arg = ctx.function_argument(0)
        if not hasattr(func_arg, 'argument'):
            return None
        args = func_arg.argument()

        if fn_name == 'GEN_ID' and len(args) >= 2:
            raw_seq = args[0].getText()
            seq_target, quoted_seq, clean_seq = self._normalize_sequence_target(raw_seq)
            step = self._get_tokens_text(args[1]).strip()

            if self.sequence_increments is not None:
                if clean_seq.lower() not in self.sequence_increments:
                    raise ValueError(
                        f"Cannot transpile GEN_ID for sequence '{clean_seq}': "
                        f"sequence increment metadata is missing or sequence does not exist."
                    )
                seq_inc = self.sequence_increments[clean_seq.lower()]
            else:
                seq_inc = 1

            if step == str(seq_inc):
                self.rewriter.replaceRangeTokens(ctx.start, ctx.stop, f"nextval('{seq_target}')")
            elif step == '0':
                dec_expr = f"{seq_inc}" if seq_inc >= 0 else f"({seq_inc})"
                self.rewriter.replaceRangeTokens(
                    ctx.start, ctx.stop,
                    f"(SELECT CASE WHEN is_called THEN last_value ELSE last_value - {dec_expr} END FROM {quoted_seq})"
                )
            elif step == '1' and seq_inc != 1:
                raise ValueError(
                    f"Cannot transpile GEN_ID for sequence '{clean_seq}' with step '{step}': "
                    f"sequence configured increment is {seq_inc}. PostgreSQL nextval only advances by the configured sequence increment."
                )
            else:
                raise ValueError(
                    f"Unsupported GEN_ID step '{step}' for sequence '{clean_seq}' (configured increment: {seq_inc}). "
                    f"PostgreSQL sequences only support advancing by configured increment {seq_inc} (nextval) and step 0 (current state inspection)."
                )
        elif fn_name == 'IIF' and len(args) == 3:
            cond_str = self._get_tokens_text(args[0]).strip()
            true_str = self._get_tokens_text(args[1]).strip()
            false_str = self._get_tokens_text(args[2]).strip()
            self.rewriter.replaceRangeTokens(
                ctx.start, ctx.stop,
                f"CASE WHEN {cond_str} THEN {true_str} ELSE {false_str} END"
            )
        elif fn_name == 'LIST' and (1 <= len(args) <= 2):
            col_str = self._get_tokens_text(args[0]).strip()
            sep_str = self._get_tokens_text(args[1]).strip() if len(args) == 2 else "','"
            self.rewriter.replaceRangeTokens(
                ctx.start, ctx.stop,
                f"string_agg(({col_str})::text, {sep_str})"
            )
        elif fn_name == 'DATEADD' and len(args) == 3:
            part_str = self._get_tokens_text(args[0]).strip().lower()
            num_str = self._get_tokens_text(args[1]).strip()
            date_str = self._get_tokens_text(args[2]).strip()
            if _is_date_expr(date_str, self.symbols):
                self.rewriter.replaceRangeTokens(
                    ctx.start, ctx.stop,
                    f"(({date_str} + ({num_str}) * INTERVAL '1 {part_str}')::date)"
                )
            elif _is_time_expr(date_str, self.symbols):
                self.rewriter.replaceRangeTokens(
                    ctx.start, ctx.stop,
                    f"(({date_str} + ({num_str}) * INTERVAL '1 {part_str}')::time)"
                )
            else:
                self.rewriter.replaceRangeTokens(
                    ctx.start, ctx.stop,
                    f"({date_str} + ({num_str}) * INTERVAL '1 {part_str}')"
                )
        elif fn_name == 'DATEDIFF' and len(args) == 3:
            part_str = self._get_tokens_text(args[0]).strip().strip("'\"").lower()
            d1_str = self._get_tokens_text(args[1]).strip()
            d2_str = self._get_tokens_text(args[2]).strip()
            is_time = _is_time_expr(d1_str, self.symbols) or _is_time_expr(d2_str, self.symbols)
            cast = "" if is_time else "::timestamp"

            if is_time and part_str in ('day', 'days', 'week', 'weeks', 'month', 'months', 'year', 'years'):
                raise ValueError(f"DATEDIFF unit '{part_str}' cannot be used with TIME values")

            if part_str in ('day', 'days'):
                self.rewriter.replaceRangeTokens(
                    ctx.start, ctx.stop,
                    f"(DATE({d2_str}) - DATE({d1_str}))"
                )
            elif part_str in ('year', 'years'):
                self.rewriter.replaceRangeTokens(
                    ctx.start, ctx.stop,
                    f"(EXTRACT(YEAR FROM {d2_str}::timestamp) - EXTRACT(YEAR FROM {d1_str}::timestamp))"
                )
            elif part_str in ('month', 'months'):
                self.rewriter.replaceRangeTokens(
                    ctx.start, ctx.stop,
                    f"((EXTRACT(YEAR FROM {d2_str}::timestamp) - EXTRACT(YEAR FROM {d1_str}::timestamp)) * 12 + "
                    f"EXTRACT(MONTH FROM {d2_str}::timestamp) - EXTRACT(MONTH FROM {d1_str}::timestamp))"
                )
            elif part_str in ('week', 'weeks'):
                self.rewriter.replaceRangeTokens(
                    ctx.start, ctx.stop,
                    f"((DATE_TRUNC('week', {d2_str}::timestamp)::date - DATE_TRUNC('week', {d1_str}::timestamp)::date) / 7)"
                )
            elif part_str in ('hour', 'hours'):
                self.rewriter.replaceRangeTokens(
                    ctx.start, ctx.stop,
                    f"ROUND(EXTRACT(EPOCH FROM (DATE_TRUNC('hour', {d2_str}{cast}) - DATE_TRUNC('hour', {d1_str}{cast}))) / 3600)"
                )
            elif part_str in ('minute', 'minutes'):
                self.rewriter.replaceRangeTokens(
                    ctx.start, ctx.stop,
                    f"ROUND(EXTRACT(EPOCH FROM (DATE_TRUNC('minute', {d2_str}{cast}) - DATE_TRUNC('minute', {d1_str}{cast}))) / 60)"
                )
            elif part_str in ('second', 'seconds'):
                self.rewriter.replaceRangeTokens(
                    ctx.start, ctx.stop,
                    f"ROUND(EXTRACT(EPOCH FROM (DATE_TRUNC('second', {d2_str}{cast}) - DATE_TRUNC('second', {d1_str}{cast}))))"
                )
            elif part_str in ('millisecond', 'milliseconds', 'ms'):
                self.rewriter.replaceRangeTokens(
                    ctx.start, ctx.stop,
                    f"ROUND((EXTRACT(EPOCH FROM ({d2_str}{cast} - {d1_str}{cast})) * 1000)::numeric, 1)"
                )
            else:
                raise ValueError(f"Unsupported DATEDIFF unit: '{part_str}'")

        return None

    def visitOther_function(self, ctx: FirebirdParser.Other_functionContext):
        self.visitChildren(ctx)
        if ctx.EXTRACT() and ctx.regular_id() and ctx.concatenation(0):
            part = ctx.regular_id().getText().upper()
            expr = self._get_tokens_text(ctx.concatenation(0)).strip()
            if part in ('WEEKDAY', 'WEEKDAYS'):
                self.rewriter.replaceRangeTokens(ctx.start, ctx.stop, f"EXTRACT(DOW FROM {expr})")
            elif part in ('YEARDAY', 'YEARDAYS'):
                self.rewriter.replaceRangeTokens(ctx.start, ctx.stop, f"((EXTRACT(DOY FROM {expr}))::integer - 1)")
            elif part in ('MILLISECOND', 'MILLISECONDS'):
                self.rewriter.replaceRangeTokens(ctx.start, ctx.stop, f"(EXTRACT(MILLISECOND FROM {expr})::numeric % 1000)")
        return None

    def visitUnary_expression(self, ctx: FirebirdParser.Unary_expressionContext):
        raw = ctx.getText().upper()
        if 'NEXTVALUEFOR' in raw and ctx.identifier():
            seq_target, _, _ = self._normalize_sequence_target(ctx.identifier().getText())
            self.rewriter.replaceRangeTokens(ctx.start, ctx.stop, f"nextval('{seq_target}')")
            return None
        return self.visitChildren(ctx)

    def visitCall_statement(self, ctx: FirebirdParser.Call_statementContext):
        raw = ctx.getText().upper()
        if raw.startswith('EXECUTEPROCEDURE') and ctx.routine_name():
            routine = ctx.routine_name(0).getText()
            self.rewriter.replaceRangeTokens(ctx.start, ctx.routine_name(0).stop, f"PERFORM {routine}")
        return self.visitChildren(ctx)

    def visitExit_statement(self, ctx: FirebirdParser.Exit_statementContext):
        first_tok = ctx.getChild(0).getText().upper()
        if first_tok == 'LEAVE':
            self.rewriter.replaceRangeTokens(ctx.start, ctx.start, 'EXIT')
        elif first_tok == 'EXIT':
            # In Firebird, EXIT without a label exits the current routine (procedure or trigger)
            if not ctx.label_name():
                ret = self.trigger_return if self.is_trigger else "RETURN"
                if ctx.condition():
                    cond = self._get_tokens_text(ctx.condition())
                    self.rewriter.replaceRangeTokens(ctx.start, ctx.stop, f"IF {cond} THEN {ret}; END IF")
                else:
                    self.rewriter.replaceRangeTokens(ctx.start, ctx.start, ret)
        return self.visitChildren(ctx)

    def visitFrom_clause(self, ctx: FirebirdParser.From_clauseContext):
        if ctx.table_ref_list() and ctx.table_ref_list().getText().upper() == 'RDB$DATABASE':
            self.rewriter.replaceRangeTokens(ctx.start, ctx.stop, '')
        return self.visitChildren(ctx)

    def visitColumn_based_update_set_clause(self, ctx: FirebirdParser.Column_based_update_set_clauseContext):
        """
        In PostgreSQL, target columns in UPDATE ... SET cannot be table-qualified
        (e.g. 'SET tcontas.id_class = ...' causes ERROR: 42703: SET target columns cannot be qualified).
        This strips any table qualifier from the target column(s).
        """
        if ctx.column_name():
            col_name_ctx = ctx.column_name()
            if col_name_ctx.id_expression():
                target_col = col_name_ctx.id_expression()[-1].getText()
                self.rewriter.replaceRangeTokens(col_name_ctx.start, col_name_ctx.stop, target_col)
        elif ctx.paren_column_list() and ctx.paren_column_list().column_name():
            for col_name_ctx in ctx.paren_column_list().column_name():
                if col_name_ctx.id_expression():
                    target_col = col_name_ctx.id_expression()[-1].getText()
                    self.rewriter.replaceRangeTokens(col_name_ctx.start, col_name_ctx.stop, target_col)
        return self.visitChildren(ctx)

    def visitInto_clause(self, ctx: FirebirdParser.Into_clauseContext):
        """
        In PostgreSQL PL/pgSQL, a singleton SELECT ... INTO that finds no rows overwrites
        target variables with NULL. In Firebird PSQL, variables preserve their existing values.
        Adding STRICT causes PL/pgSQL to raise NO_DATA_FOUND before overwriting variables,
        which is caught and handled in visitStatement to preserve Firebird semantics.
        """
        # Only add STRICT to singleton SELECT statements (not FOR loops, nor INSERT/UPDATE/DELETE RETURNING)
        is_select_into = isinstance(ctx.parentCtx,
                                    (FirebirdParser.Query_blockContext, FirebirdParser.Select_statementContext))

        curr = ctx.parentCtx
        is_loop_cursor = False
        prev = ctx
        while curr:
            if isinstance(curr, FirebirdParser.Loop_statementContext):
                if hasattr(curr, 'FOR') and curr.FOR():
                    is_loop_cursor = (prev != curr.statement())
                break
            prev = curr
            curr = curr.parentCtx

        if is_select_into and not is_loop_cursor:
            for c in ctx.children:
                if hasattr(c, 'symbol') and c.symbol.text.upper() == 'INTO':
                    self.rewriter.replaceRangeTokens(c.symbol, c.symbol, f"{c.symbol.text} STRICT")
                    break
        return self.visitChildren(ctx)

    def _rewrite_first_skip(self, ctx):
        """
        Extracts FIRST n [SKIP m] tokens from the query block and relocates them
        as LIMIT n [OFFSET m] to the end of the enclosing select_statement or subquery.
        """
        qb = _find_node(ctx, FirebirdParser.Query_blockContext)
        if qb and (qb.FIRST() or qb.SKIP_()) and id(qb) not in self.handled_qbs:
            self.handled_qbs.add(id(qb))
            if qb.FIRST() and qb.SKIP_():
                first_val = qb.numeric(0).getText()
                skip_val = qb.numeric(1).getText()
                start_token = qb.FIRST().symbol
                end_token = qb.numeric(1).stop
            elif qb.FIRST():
                first_val = qb.numeric(0).getText()
                skip_val = None
                start_token = qb.FIRST().symbol
                end_token = qb.numeric(0).stop
            else:
                first_val = None
                skip_val = qb.numeric(0).getText()
                start_token = qb.SKIP_().symbol
                end_token = qb.numeric(0).stop

            if first_val and first_val in self.expr_map:
                raw_expr = self.expr_map[first_val]
                first_val = FirebirdToPostgresVisitor.transpile_expression(
                    raw_expr, symbols=self.symbols, sequence_increments=self.sequence_increments
                )
            if skip_val and skip_val in self.expr_map:
                raw_expr = self.expr_map[skip_val]
                skip_val = FirebirdToPostgresVisitor.transpile_expression(
                    raw_expr, symbols=self.symbols, sequence_increments=self.sequence_increments
                )

            def _wrap_limit_expr(val: str) -> str:
                v = val.strip()
                if " " in v and not (v.startswith("(") and v.endswith(")")):
                    return f"({v})"
                return v

            if first_val and skip_val:
                limit_clause = f' LIMIT {_wrap_limit_expr(first_val)} OFFSET {_wrap_limit_expr(skip_val)}'
            elif first_val:
                limit_clause = f' LIMIT {_wrap_limit_expr(first_val)}'
            else:
                limit_clause = f' OFFSET {_wrap_limit_expr(skip_val)}'

            self.rewriter.replaceRangeTokens(start_token, end_token, '')

            into_ctx = _find_node(ctx, FirebirdParser.Into_clauseContext)
            if into_ctx:
                prev_token_idx = into_ctx.start.tokenIndex - 1
                while prev_token_idx >= ctx.start.tokenIndex and self.rewriter.tokens.tokens[prev_token_idx].channel != 0:
                    prev_token_idx -= 1
                prev_token = self.rewriter.tokens.tokens[max(ctx.start.tokenIndex, prev_token_idx)]
                self.rewriter.insertAfterToken(prev_token, limit_clause)
                return

            target_token = ctx.stop
            if target_token and target_token.text == ')':
                self.rewriter.insertBeforeToken(target_token, limit_clause)
            else:
                self.rewriter.insertAfterToken(target_token, limit_clause)

    def _disambiguate_scope(self, scope_node, scope: QueryScope):
        if not scope_node or not scope or not scope.tables:
            return

        def find_unqualified_col_parts(node):
            res = []
            if node is None:
                return res
            # Do not recurse into nested subqueries
            if isinstance(node, FirebirdParser.Query_blockContext) and node != scope_node:
                return res
            # Do not touch INTO clause target variables
            if isinstance(node, FirebirdParser.Into_clauseContext):
                return res
            # Do not touch bind variables (:V)
            if isinstance(node, FirebirdParser.Bind_variableContext):
                return res
            # In column_based_update_set_clause (e.g. V = V + 1), only recurse into value expression, not the target column name!
            if isinstance(node, FirebirdParser.Column_based_update_set_clauseContext):
                if hasattr(node, 'expression') and node.expression():
                    res.extend(find_unqualified_col_parts(node.expression()))
                return res
            if isinstance(node, FirebirdParser.General_element_partContext):
                res.append(node)
            if hasattr(node, "children") and node.children:
                for child in node.children:
                    res.extend(find_unqualified_col_parts(child))
            return res

        for p in find_unqualified_col_parts(scope_node):
            if hasattr(p, 'function_argument') and len(p.function_argument()) > 0:
                continue
            curr = p.parentCtx
            is_qualified = False
            while curr and curr != scope_node:
                if isinstance(curr, FirebirdParser.General_elementContext) and len(curr.children) > 1:
                    is_qualified = True
                    break
                curr = curr.parentCtx
            if is_qualified:
                continue
            if not (hasattr(p, 'id_expression') and p.id_expression()):
                continue

            raw_col_text = p.id_expression().getText()
            col_name = raw_col_text.strip('":').lower()

            curr_s = scope
            is_using_col = False
            while curr_s:
                if col_name in curr_s.using_columns:
                    is_using_col = True
                    break
                curr_s = curr_s.parent

            if is_using_col:
                continue

            curr_s = scope
            chosen_tbl = None
            ambiguous_candidates = []
            unresolvable_scope = None

            while curr_s:
                active_tables = [t for t in curr_s.tables if t.table_name_clean.upper() != 'RDB$DATABASE']
                if not active_tables:
                    curr_s = curr_s.parent
                    continue

                tbl_matches = []
                for tbl in active_tables:
                    known_cols = self.table_columns.get(tbl.table_name_clean)
                    if known_cols is not None and len(known_cols) > 0:
                        if col_name in known_cols:
                            tbl_matches.append(tbl)
                    elif len(active_tables) == 1:
                        # Single table in scope and no table_columns catalog for it
                        # If col_name is known in symbols or procedure parameters/vars:
                        if col_name in self.symbols or col_name in self.params or col_name in self.local_vars:
                            tbl_matches.append(tbl)

                if len(tbl_matches) == 1:
                    chosen_tbl = tbl_matches[0]
                    break
                elif len(tbl_matches) > 1:
                    ambiguous_candidates = tbl_matches
                    break
                else:
                    # 0 matches in this scope.
                    # If multiple tables in this scope and col_name is a known symbol:
                    if len(active_tables) > 1 and (col_name in self.symbols or col_name in self.params or col_name in self.local_vars):
                        unresolvable_scope = active_tables
                    curr_s = curr_s.parent

            if ambiguous_candidates:
                raise ValueError(
                    f"Ambiguous column reference '{col_name}' between tables "
                    f"{[t.qualifier for t in ambiguous_candidates]} in query scope"
                )

            if not chosen_tbl and unresolvable_scope:
                raise ValueError(
                    f"Unresolvable column reference '{col_name}' between tables "
                    f"{[t.qualifier for t in unresolvable_scope]}: metadata required to disambiguate table ownership"
                )

            if chosen_tbl:
                self.rewriter.replaceRangeTokens(
                    p.id_expression().start,
                    p.id_expression().stop,
                    f"{chosen_tbl.qualifier}.{raw_col_text}"
                )

    @staticmethod
    def _extract_tables_from_query_block(qb: FirebirdParser.Query_blockContext) -> list[TableSource]:
        tables = []
        if not qb or not qb.from_clause():
            return tables
        trl = qb.from_clause().table_ref_list()
        if not trl:
            return tables

        def extract_from_aux(aux) -> Optional[TableSource]:
            if not aux:
                return None
            alias = aux.table_alias().getText().strip() if aux.table_alias() else None
            t_int = aux.table_ref_aux_internal()
            t_name = t_int.getText().strip() if t_int else ""
            qualifier = alias if alias else t_name
            subquery_ctx = None
            if t_int and hasattr(t_int, 'dml_table_expression_clause') and t_int.dml_table_expression_clause():
                dml = t_int.dml_table_expression_clause()
                if hasattr(dml, 'select_statement') and dml.select_statement():
                    subquery_ctx = dml.select_statement()
            return TableSource(table_name=t_name, alias=alias, qualifier=qualifier, subquery_ctx=subquery_ctx)

        for tr in trl.table_ref():
            if hasattr(tr, 'table_ref_aux') and tr.table_ref_aux():
                src = extract_from_aux(tr.table_ref_aux())
                if src:
                    tables.append(src)
            if hasattr(tr, 'join_clause') and tr.join_clause():
                for jc in tr.join_clause():
                    if hasattr(jc, 'table_ref_aux') and jc.table_ref_aux():
                        src = extract_from_aux(jc.table_ref_aux())
                        if src:
                            tables.append(src)
        return tables

    @staticmethod
    def _extract_cte_definitions(select_only) -> dict[str, tuple]:
        """
        Maps lowercase CTE name -> (subquery_ctx, column_aliases) for the WITH
        clause of a select_only_statement. Column aliases come from the
        optional paren column list: WITH X(a, b) AS (...).
        """
        cte_defs: dict[str, tuple] = {}
        try:
            if not select_only or not hasattr(select_only, 'with_clause'):
                return cte_defs
            with_clause = select_only.with_clause()
            if not with_clause:
                return cte_defs
            for factoring in with_clause.with_factoring_clause() or []:
                sub_factoring = factoring.subquery_factoring_clause()
                if not sub_factoring:
                    continue
                qname = sub_factoring.query_name()
                if not qname:
                    continue
                cte_name = qname.getText().strip('":').lower()
                sub_ctx = sub_factoring.subquery() if hasattr(sub_factoring, 'subquery') else None
                aliases: list[str] = []
                try:
                    pcl = sub_factoring.paren_column_list()
                    if pcl and pcl.column_list():
                        for col in pcl.column_list().column_name():
                            raw = col.getText().strip('":').lower()
                            if raw:
                                aliases.append(raw)
                except Exception:
                    pass
                if cte_name and sub_ctx is not None:
                    cte_defs[cte_name] = (sub_ctx, aliases)
        except Exception:
            pass
        return cte_defs

    def _infer_subquery_projections(self, select_stmt, symbols: dict[str, str],
                                    cte_defs: dict[str, tuple] = None,
                                    _resolving: frozenset = frozenset()) -> list[tuple[str, str | None]]:
        """
        Infers the projected columns of a subquery as an ORDERED list of
        (name, type) pairs. Order and duplicates are preserved: SELECT T.D,
        U.D yields two 'd' entries in written order, and SELECT * expands
        per participating table. Type may be None when unknown (kept as a
        positional slot, e.g. for CTE column-alias mapping).
        """
        projections: list[tuple[str, str | None]] = []
        if not select_stmt:
            return projections
        try:
            # Accepts Select_statementContext (derived tables, has
            # select_only_statement) and bare SubqueryContext (CTE bodies,
            # which wrap subquery_basic_elements directly in parentheses).
            sub_only = None
            if hasattr(select_stmt, 'select_only_statement'):
                try:
                    sub_only = select_stmt.select_only_statement()
                except Exception:
                    sub_only = None
            if sub_only is not None and sub_only.subquery() is not None:
                sub = sub_only.subquery()
            elif hasattr(select_stmt, 'subquery_basic_elements'):
                sub = select_stmt
            else:
                return projections
            basic = sub.subquery_basic_elements()
            if not basic or not basic.query_block():
                return projections
            qb = basic.query_block()
            if not qb.selected_list():
                return projections

            # CTEs defined by this statement shadow outer ones of the same name.
            merged_ctes = dict(cte_defs) if cte_defs else {}
            if sub_only is not None:
                merged_ctes.update(self._extract_cte_definitions(sub_only))

            sub_tables = self._extract_tables_from_query_block(qb)
            sub_symbols = symbols.copy()
            for st in sub_tables:
                if st.subquery_ctx:
                    inner_proj = self._infer_subquery_projections(
                        st.subquery_ctx, symbols, merged_ctes, _resolving)
                    alias_use = st.alias_clean or st.table_name_clean
                    for c_name, c_type in inner_proj:
                        if c_type:
                            sub_symbols[f"{alias_use}.{c_name}"] = c_type
                elif st.table_name_clean in merged_ctes and st.table_name_clean not in _resolving:
                    sub_ctx, col_aliases = merged_ctes[st.table_name_clean]
                    inner_proj = self._infer_subquery_projections(
                        sub_ctx, symbols, merged_ctes,
                        _resolving | {st.table_name_clean})
                    if col_aliases:
                        inner_proj = [(alias_name, c_type)
                                      for alias_name, (_, c_type)
                                      in zip(col_aliases, inner_proj)]
                    quals = {st.table_name_clean}
                    if st.alias_clean:
                        quals.add(st.alias_clean)
                    for c_name, c_type in inner_proj:
                        if c_type:
                            for q in quals:
                                sub_symbols[f"{q}.{c_name}"] = c_type
                elif st.alias_clean and st.table_name_clean:
                    prefix = f"{st.table_name_clean}."
                    for k, v in list(symbols.items()):
                        if k.startswith(prefix):
                            col = k[len(prefix):]
                            sub_symbols[f"{st.alias_clean}.{col}"] = v

            active_tables = [st for st in sub_tables if st.table_name_clean.upper() != 'RDB$DATABASE']
            if len(active_tables) == 1:
                st = active_tables[0]
                prefixes = [f"{st.table_name_clean}."]
                if st.alias_clean:
                    prefixes.insert(0, f"{st.alias_clean}.")
                for prefix in prefixes:
                    for k, v in list(sub_symbols.items()):
                        if k.startswith(prefix):
                            sub_symbols[k[len(prefix):]] = v

            sl = qb.selected_list()
            if sl.getText() == '*':
                # SELECT * projects only columns of tables that actually
                # participate in this subquery (no out-of-scope leaks), one
                # qualifier namespace per table (alias preferred), in FROM
                # order. Duplicates across tables are kept in order, EXCEPT
                # JOIN ... USING columns: per SQL/Firebird semantics the
                # shared column is presented only once (first occurrence
                # wins), so later tables skip already-projected USING cols.
                # Qualified T.* keeps every explicitly requested column.
                using_cols = set()
                try:
                    using_cols = {
                        c.lower()
                        for c in self._extract_using_columns_from_query_block(qb)
                    }
                except Exception:
                    pass
                emitted_using: set[str] = set()
                for st in sub_tables:
                    qualifier = (st.alias_clean or st.table_name_clean or '').lower()
                    if not qualifier:
                        continue
                    prefix = qualifier + '.'
                    for k, v in sub_symbols.items():
                        if k.lower().startswith(prefix):
                            col = k.split('.')[-1]
                            if col.lower() in using_cols:
                                if col.lower() in emitted_using:
                                    continue
                                emitted_using.add(col.lower())
                            projections.append((col, v))
                return projections

            if hasattr(sl, 'select_list_elements') and sl.select_list_elements():
                for el in sl.select_list_elements():
                    if hasattr(el, 'ASTERISK') and el.ASTERISK() and hasattr(el, 'tableview_name') and el.tableview_name():
                        t_name = el.tableview_name().getText().strip('":').lower()
                        prefix = f"{t_name}."
                        for k, v in sub_symbols.items():
                            if k.lower().startswith(prefix):
                                projections.append((k[len(prefix):], v))
                    elif hasattr(el, 'expression') and el.expression():
                        col_name = None
                        if hasattr(el, 'column_alias') and el.column_alias():
                            ca = el.column_alias()
                            raw_a = ca.identifier().getText() if hasattr(ca, 'identifier') and ca.identifier() else ca.getText()
                            col_name = re.sub(r'(?i)^\s*AS\s+', '', raw_a).strip('":').lower()
                        if not col_name:
                            expr_raw = el.expression().getText().strip()
                            col_name = expr_raw.split('.')[-1].strip('":').lower()

                        expr_str = self._get_tokens_text(el.expression()).strip()
                        col_type = None
                        if _is_date_expr(expr_str, sub_symbols):
                            col_type = 'DATE'
                        elif _is_timestamp_expr(expr_str, sub_symbols):
                            col_type = 'TIMESTAMP'
                        elif _is_time_expr(expr_str, sub_symbols):
                            col_type = 'TIME'
                        else:
                            clean_expr = '.'.join(p.strip('":') for p in expr_str.split('.')).lower()
                            if clean_expr in sub_symbols:
                                col_type = sub_symbols[clean_expr]
                            else:
                                col_part = clean_expr.split('.')[-1]
                                if col_part in sub_symbols:
                                    col_type = sub_symbols[col_part]
                        if col_name:
                            projections.append((col_name, col_type))
        except Exception:
            pass
        return projections

    @staticmethod
    def _extract_using_columns_from_query_block(qb: FirebirdParser.Query_blockContext) -> set[str]:
        using_cols = set()
        if not qb or not qb.from_clause():
            return using_cols
        trl = qb.from_clause().table_ref_list()
        if not trl:
            return using_cols
        for tr in trl.table_ref():
            if hasattr(tr, 'join_clause') and tr.join_clause():
                for jc in tr.join_clause():
                    if hasattr(jc, 'join_using_part') and jc.join_using_part():
                        jups = jc.join_using_part()
                        if not isinstance(jups, list):
                            jups = [jups]
                        for jup in jups:
                            if hasattr(jup, 'paren_column_list') and jup.paren_column_list():
                                pcl = jup.paren_column_list()
                                if hasattr(pcl, 'column_list') and pcl.column_list():
                                    for col in pcl.column_list().column_name():
                                        raw_text = col.getText().strip('":').lower()
                                        if raw_text:
                                            using_cols.add(raw_text)
        return using_cols

    def visitQuery_block(self, ctx: FirebirdParser.Query_blockContext):
        self._rewrite_first_skip(ctx)
        tables = self._extract_tables_from_query_block(ctx)
        using_columns = self._extract_using_columns_from_query_block(ctx)
        scope = QueryScope(parent=self.current_scope, tables=tables, using_columns=using_columns)
        self.current_scope = scope
        old_symbols = self.symbols.copy()
        try:
            if tables:
                # CTEs visible in this scope: nearest enclosing WITH clause.
                scope_ctes: dict[str, tuple] = {}
                probe = ctx.parentCtx
                while probe is not None:
                    if isinstance(probe, FirebirdParser.Select_only_statementContext):
                        scope_ctes = self._extract_cte_definitions(probe)
                        if scope_ctes:
                            break
                    probe = probe.parentCtx
                for tbl in tables:
                    if tbl.subquery_ctx:
                        proj = self._infer_subquery_projections(
                            tbl.subquery_ctx, old_symbols, scope_ctes)
                        alias = tbl.alias_clean or tbl.table_name_clean
                        for col_name, col_type in proj:
                            if col_type:
                                self.symbols[f"{alias}.{col_name}"] = col_type
                        if hasattr(self, 'table_columns'):
                            cols = set(self.table_columns.get(tbl.table_name_clean, []))
                            cols.update(c for c, _ in proj)
                            self.table_columns[tbl.table_name_clean] = cols
                            if tbl.alias_clean:
                                self.table_columns[tbl.alias_clean] = cols
                    elif tbl.table_name_clean in scope_ctes:
                        sub_ctx, col_aliases = scope_ctes[tbl.table_name_clean]
                        proj = self._infer_subquery_projections(
                            sub_ctx, old_symbols, scope_ctes,
                            frozenset({tbl.table_name_clean}))
                        if col_aliases:
                            proj = [(alias_name, c_type)
                                    for alias_name, (_, c_type)
                                    in zip(col_aliases, proj)]
                        quals = {tbl.table_name_clean}
                        if tbl.alias_clean:
                            quals.add(tbl.alias_clean)
                        for col_name, col_type in proj:
                            if col_type:
                                for q in quals:
                                    self.symbols[f"{q}.{col_name}"] = col_type
                        if hasattr(self, 'table_columns'):
                            cols = set(self.table_columns.get(tbl.table_name_clean, []))
                            cols.update(c for c, _ in proj)
                            self.table_columns[tbl.table_name_clean] = cols
                            if tbl.alias_clean:
                                self.table_columns[tbl.alias_clean] = cols
                    elif tbl.alias_clean and tbl.table_name_clean:
                        prefix = f"{tbl.table_name_clean}."
                        for k, v in list(old_symbols.items()):
                            if k.startswith(prefix):
                                col = k[len(prefix):]
                                self.symbols[f"{tbl.alias_clean}.{col}"] = v
                self._disambiguate_scope(ctx, scope)
                curr_p = ctx.parentCtx
                while curr_p:
                    if hasattr(curr_p, 'order_by_clause') and curr_p.order_by_clause():
                        ob_list = curr_p.order_by_clause()
                        if isinstance(ob_list, list):
                            for ob in ob_list:
                                self._disambiguate_scope(ob, scope)
                        else:
                            self._disambiguate_scope(ob_list, scope)
                        break
                    if isinstance(curr_p, (FirebirdParser.StatementContext, FirebirdParser.SubqueryContext)):
                        break
                    curr_p = curr_p.parentCtx
            return self.visitChildren(ctx)
        finally:
            self.symbols = old_symbols
            self.current_scope = scope.parent

    @staticmethod
    def _extract_table_source_from_general_table_ref(general_table_ref) -> Optional[TableSource]:
        if not general_table_ref:
            return None
        alias = None
        if hasattr(general_table_ref, 'table_alias') and general_table_ref.table_alias():
            alias = general_table_ref.table_alias().getText().strip()
        table_name = ""
        if hasattr(general_table_ref, 'dml_table_expression_clause') and general_table_ref.dml_table_expression_clause():
            table_name = general_table_ref.dml_table_expression_clause().getText().strip()
        if not table_name:
            text = general_table_ref.getText().strip()
            table_name = text.split()[0] if text else ""
        qualifier = alias if alias else table_name
        return TableSource(table_name=table_name, alias=alias, qualifier=qualifier)

    def _extract_table_qualifier(self, general_table_ref) -> str:
        src = self._extract_table_source_from_general_table_ref(general_table_ref)
        return src.qualifier if src else ""

    def visitUpdate_statement(self, ctx: FirebirdParser.Update_statementContext):
        table_source = self._extract_table_source_from_general_table_ref(ctx.general_table_ref())
        if table_source and table_source.table_name_clean.upper() != 'RDB$DATABASE':
            scope = QueryScope(parent=self.current_scope, tables=[table_source])
            self.current_scope = scope
            old_symbols = self.symbols.copy()
            if table_source.alias_clean and table_source.table_name_clean:
                prefix = f"{table_source.table_name_clean}."
                for k, v in list(old_symbols.items()):
                    if k.startswith(prefix):
                        col = k[len(prefix):]
                        self.symbols[f"{table_source.alias_clean}.{col}"] = v
            try:
                if ctx.update_set_clause():
                    self._disambiguate_scope(ctx.update_set_clause(), scope)
                if ctx.where_clause():
                    self._disambiguate_scope(ctx.where_clause(), scope)
                return self.visitChildren(ctx)
            finally:
                self.symbols = old_symbols
                self.current_scope = scope.parent
        return self.visitChildren(ctx)

    def visitDelete_statement(self, ctx: FirebirdParser.Delete_statementContext):
        table_source = self._extract_table_source_from_general_table_ref(ctx.general_table_ref())
        if table_source and table_source.table_name_clean.upper() != 'RDB$DATABASE':
            scope = QueryScope(parent=self.current_scope, tables=[table_source])
            self.current_scope = scope
            old_symbols = self.symbols.copy()
            if table_source.alias_clean and table_source.table_name_clean:
                prefix = f"{table_source.table_name_clean}."
                for k, v in list(old_symbols.items()):
                    if k.startswith(prefix):
                        col = k[len(prefix):]
                        self.symbols[f"{table_source.alias_clean}.{col}"] = v
            try:
                if ctx.where_clause():
                    self._disambiguate_scope(ctx.where_clause(), scope)
                return self.visitChildren(ctx)
            finally:
                self.symbols = old_symbols
                self.current_scope = scope.parent
        return self.visitChildren(ctx)

    def visitSelect_statement(self, ctx: FirebirdParser.Select_statementContext):
        self._rewrite_first_skip(ctx)
        return self.visitChildren(ctx)

    def visitSubquery(self, ctx: FirebirdParser.SubqueryContext):
        self._rewrite_first_skip(ctx)
        return self.visitChildren(ctx)

    def visitSeq_of_statements(self, ctx: FirebirdParser.Seq_of_statementsContext):
        if not ctx.children:
            return self.visitChildren(ctx)
        children = ctx.children
        i = 0
        while i < len(children):
            child = children[i]
            if isinstance(child, FirebirdParser.StatementContext):
                text = child.getText().upper()
                if text == 'EXCEPTION' and (i + 1) < len(children):
                    next_child = children[i + 1]
                    if isinstance(next_child, FirebirdParser.StatementContext):
                        ex_name = next_child.getText().strip(';')
                        stop_token = next_child.stop
                        inc = 2
                        custom_msg = None

                        # Check if next statement is a custom message string literal (Firebird 2.0+)
                        if (i + 2) < len(children) and isinstance(children[i + 2], FirebirdParser.StatementContext):
                            cand = children[i + 2].getText().strip(';')
                            if cand.startswith("'") and cand.endswith("'"):
                                custom_msg = cand
                                stop_token = children[i + 2].stop
                                inc = 3

                        if (i + inc) < len(children) and children[i + inc].getText() == ';':
                            stop_token = children[i + inc].symbol
                            inc += 1

                        if custom_msg:
                            self.rewriter.replaceRangeTokens(child.start, child.stop,
                                                             f"RAISE EXCEPTION '{ex_name}: %', {custom_msg};")
                        else:
                            self.rewriter.replaceRangeTokens(child.start, child.stop, f"RAISE EXCEPTION '{ex_name}';")

                        self.rewriter.replaceRangeTokens(next_child.start, stop_token, "")
                        i += inc
                        continue
            i += 1
        return self.visitChildren(ctx)

    def visitTerminal(self, node):
        if node.getText().upper() == 'SUSPEND':
            self.rewriter.replaceRangeTokens(node.symbol, node.symbol, 'RETURN NEXT')
        return None


class _CollectingErrorListener(ErrorListener):
    """
    Custom ANTLR error listener that captures syntax and lexical errors in memory
    instead of printing verbose diagnostic dumps directly to sys.stderr.
    """

    def __init__(self):
        super().__init__()
        self.errors: list[str] = []

    # noinspection PyPep8Naming
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.errors.append(f"line {line}:{column} {msg}")

_SAFE_PROC_CALLS = {
    'if', 'while', 'loop', 'for', 'in', 'case', 'when', 'then', 'else', 'end',
    'select', 'from', 'where', 'into', 'values', 'set', 'join', 'on', 'using',
    'group', 'by', 'having', 'order', 'limit', 'offset', 'exists', 'between',
    'like', 'similar', 'not', 'and', 'or', 'is', 'null', 'over', 'filter', 'row', 'check',
    'raise', 'format', 'return', 'exit', 'continue', 'declare', 'begin',
    'coalesce', 'nullif', 'iif', 'greatest', 'least',
    'abs', 'round', 'ceil', 'ceiling', 'floor', 'trunc', 'sign', 'power', 'sqrt', 'mod', 'exp', 'ln', 'log',
    'sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'atan2',
    'upper', 'lower', 'initcap', 'length', 'char_length', 'character_length', 'octet_length', 'bit_length',
    'trim', 'btrim', 'ltrim', 'rtrim', 'left', 'right', 'lpad', 'rpad', 'repeat', 'replace', 'reverse',
    'substr', 'substring', 'position', 'strpos', 'concat', 'concat_ws', 'split_part',
    'cast', 'extract', 'date_part', 'date_trunc', 'age',
    'dateadd', 'datediff',
    'to_char', 'to_date', 'to_timestamp', 'to_number',
    'count', 'sum', 'avg', 'min', 'max', 'stddev', 'variance',
    'row_number', 'rank', 'dense_rank',
    'quote_ident', 'quote_literal', 'quote_nullable',
    'varchar', 'char', 'numeric', 'decimal', 'float', 'double', 'int', 'integer',
    'smallint', 'bigint', 'timestamp', 'date', 'time', 'boolean', 'text', 'bytea',
    'interval', 'blob', 'clob', 'precision'
}


class FirebirdToPostgresVisitor(FirebirdParserVisitor):
    """
    Visitor that traverses the Firebird AST and translates it into PostgreSQL PL/pgSQL code.
    """

    def __init__(self, rewriter: TokenStreamRewriter = None, domain_map: dict[str, str] = None,
                 not_null_params: dict[str, list[str]] = None,
                 not_null_outputs: dict[str, list[str]] = None):
        super().__init__()
        self.rewriter = rewriter
        self.domain_map = {k.strip().upper(): v.strip() for k, v in domain_map.items()} if domain_map else {}
        self.not_null_params = not_null_params or {}
        self.not_null_outputs = not_null_outputs or {}
        self.current_not_null_outputs: dict[str, dict[str, str]] = {}
        self.current_proc_has_suspend: bool = False

    @classmethod
    def _normalize_sql(cls, sql: str, expr_map: dict[str, str] = None,
                       not_null_params: dict[str, list[str]] = None,
                       not_null_outputs: dict[str, list[str]] = None,
                       domain_types: dict[str, str] = None) -> str:
        """
        Pre-parse normalization:
        1. Firebird allows custom exception messages: `EXCEPTION <name> '<msg>';`.
           We normalize this to `/* __FB_EX_MSG__:<name>:<msg> */ EXCEPTION <name>;`
           so the ANTLR grammar parses it cleanly as a standard EXCEPTION statement.
        2. In the Firebird grammar, 'old' and 'new' are reserved keywords in unquoted context.
           When followed by a dot (e.g. 'old.field'), the lexer splits them unless quoted.
           This function temporarily wraps record names in double quotes ("old".field),
           while ensuring string literals ('...') and comments (-- ... / /* ... */) remain 100% untouched.
           These temporary quotes are cleanly stripped in `_clean_sql` after parsing.
        3. Normalizes keywords directly attached to colon bind variables without
           whitespace (e.g. `into:vid` -> `into :vid`).
        """
        if expr_map is None:
            expr_map = {}

        # Step 1: Normalize custom exception messages (e.g. EXCEPTION EX_ERR 'custom msg';)
        def ex_repl(match):
            if match.group(1):
                return match.group(1)
            ex_name = match.group(3)
            ex_msg = match.group(4)
            return f"/* __FB_EX_MSG__:{ex_name}:{ex_msg} */ EXCEPTION {ex_name};"

        sql = _EX_PATTERN.sub(ex_repl, sql)

        # Step 2: Normalize OLD / NEW trigger records
        def repl(match):
            if match.group(1):
                return match.group(1)
            if match.group(2):
                rec = re.split(r'[.;\s]', match.group(2))[0]
                return f'"{rec}".{match.group(4)}'
            if match.group(5):
                return f'"{match.group(6)}".{match.group(7)}'
            return match.group(0)

        sql = _OLD_NEW_PATTERN.sub(repl, sql)

        # Step 3: Normalize keyword attached directly to a colon variable without space (e.g. into:vid -> into :vid)
        def colon_repl(match):
            if match.group(1):
                return match.group(1)
            return f"{match.group(3)} :{match.group(4)}"

        sql = _COLON_PATTERN.sub(colon_repl, sql)

        # Step 4: Normalize alternative Firebird syntax DATEADD(...) and DATEDIFF(...)
        sql = _normalize_date_funcs(sql)

        # Step 4.5: Normalize modern and binary datatypes (DECFLOAT, INT128, OCTETS)
        sql = _normalize_data_types(sql)

        # Step 5: Normalize TYPE OF COLUMN and TYPE OF domain
        sql = _normalize_type_of(sql, domain_types=domain_types)

        # Step 6: Normalize variable declarations (= initializers, DEFAULT ... NOT NULL, etc.)
        sql = _normalize_variable_declarations(sql)

        # Step 7: Normalize procedure parameters (= to DEFAULT, strip NOT NULL)
        sql = _normalize_procedure_params(sql, not_null_params=not_null_params, not_null_outputs=not_null_outputs)

        # Step 8: Normalize EXECUTE PROCEDURE ... RETURNING_VALUES ...
        sql = _normalize_returning_values(sql)

        # Step 9: Normalize WHEN ANY DO exception handlers
        sql = _normalize_when_any(sql)

        # Step 10: Normalize FIRST/SKIP pagination (expressions, variable parameters, standalone SKIP, ordering)
        return _normalize_first_skip(sql, expr_map)

    @classmethod
    def transpile(cls, firebird_sql_string: str, symbols: dict[str, str] = None, domain_map: dict[str, str] = None,
                  sequence_increments: dict[str, int] = None, domain_types: dict[str, str] = None) -> str:
        """
        Parses Firebird SQL using Two-Stage Parsing (SLL -> LL), traverses the AST with the visitor,
        and applies dialect token rewriting to produce clean PostgreSQL SQL.
        """
        norm_domain_map = {}
        extracted_domain_types = {}
        if domain_map:
            for k, v in domain_map.items():
                k_norm = k.strip().upper()
                if isinstance(v, (tuple, list)) and len(v) == 2:
                    norm_domain_map[k_norm] = str(v[0]).strip()
                    extracted_domain_types[k_norm] = str(v[1]).strip()
                elif isinstance(v, dict):
                    norm_domain_map[k_norm] = str(v.get('pg_name', k)).strip()
                    if 'base_type' in v:
                        extracted_domain_types[k_norm] = str(v['base_type']).strip()
                elif hasattr(v, 'pg_name') and hasattr(v, 'base_type'):
                    norm_domain_map[k_norm] = str(v.pg_name).strip()
                    extracted_domain_types[k_norm] = str(v.base_type).strip()
                else:
                    norm_domain_map[k_norm] = str(v).strip()

        combined_domain_types = {}
        if extracted_domain_types:
            combined_domain_types.update(extracted_domain_types)
        if domain_types:
            for k, v in domain_types.items():
                combined_domain_types[k.strip().upper()] = str(v).strip()

        expr_map = {}
        not_null_params = {}
        not_null_outputs = {}
        normalized_sql = cls._normalize_sql(
            firebird_sql_string,
            expr_map=expr_map,
            not_null_params=not_null_params,
            not_null_outputs=not_null_outputs,
            domain_types=combined_domain_types
        )

        error_listener = _CollectingErrorListener()

        lexer = FirebirdLexer(InputStream(normalized_sql))
        lexer.removeErrorListeners()
        lexer.addErrorListener(error_listener)

        stream = CommonTokenStream(lexer)
        parser = FirebirdParser(stream)
        parser.removeErrorListeners()
        parser.addErrorListener(error_listener)

        # Stage 1: Fast SLL mode
        # noinspection PyProtectedMember
        parser._interp.predictionMode = PredictionMode.SLL
        # noinspection PyProtectedMember
        parser._errHandler = BailErrorStrategy()

        try:
            tree = parser.sql_script()
        except (ParseCancellationException, RecognitionException):
            # Stage 2: Fallback to LL mode if SLL encounters ambiguity
            stream.seek(0)
            parser.reset()
            # noinspection PyProtectedMember
            parser._errHandler = DefaultErrorStrategy()
            # noinspection PyProtectedMember
            parser._interp.predictionMode = PredictionMode.LL
            tree = parser.sql_script()

        # Ensure syntax errors in LL mode fail loudly rather than returning partial/corrupt AST
        syntax_errors = parser.getNumberOfSyntaxErrors()
        if syntax_errors > 0 or error_listener.errors:
            details = "; ".join(error_listener.errors[:3])
            count = len(error_listener.errors) if error_listener.errors else syntax_errors
            raise ParseCancellationException(
                f"Syntax error during parsing: {count} error(s) encountered in Firebird SQL script ({details})."
            )

        rewriter = TokenStreamRewriter(stream)

        # Pass 1: Semantic token rewriting on AST
        dialect_rewriter = ASTDialectRewriter(rewriter, symbols=symbols, expr_map=expr_map, sequence_increments=sequence_increments, domain_map=norm_domain_map)
        dialect_rewriter.visit(tree)

        # Pass 2: High-level PL/pgSQL structure visitor
        visitor = cls(rewriter=rewriter, domain_map=norm_domain_map, not_null_params=not_null_params, not_null_outputs=not_null_outputs)
        pg_sql = visitor.visit(tree)

        if pg_sql:
            pg_sql = cls._clean_sql(pg_sql)

        return pg_sql

    @classmethod
    def transpile_expression(cls, expr: str, symbols: dict[str, str] = None, sequence_increments: dict[str, int] = None) -> str:
        """
        Transpiles a standalone Firebird SQL scalar expression (e.g. computed column, expression index)
        to PostgreSQL SQL, rewriting built-ins like IIF, DATEADD, DATEDIFF, LIST, GEN_ID.
        """
        if not expr:
            return ""
        expr_clean = expr.strip()
        dummy_sql = f'CREATE VIEW "__v__" AS SELECT {expr_clean} FROM RDB$DATABASE;'
        try:
            view_sql = cls.transpile(dummy_sql, symbols=symbols, sequence_increments=sequence_increments)
            m = re.search(r'AS\s+SELECT\s+(.*)\s*;?$', view_sql, re.IGNORECASE | re.DOTALL)
            if m:
                return m.group(1).strip().rstrip(';').strip()
            raise RuntimeError(f"Could not extract expression from transpiled statement: {view_sql}")
        except Exception as e:
            logger.error(
                "Failed to transpile Firebird expression '%s' to PostgreSQL: %s",
                expr_clean, e
            )
            raise RuntimeError(f"Failed to transpile Firebird expression '{expr_clean}' to PostgreSQL: {e}") from e

    @classmethod
    def transpile_default_clause(cls, default_str: str | None, symbols: dict[str, str] = None, sequence_increments: dict[str, int] = None) -> str | None:
        if not default_str:
            return None
        s = default_str.strip()
        m = re.match(r'^\s*DEFAULT\s+(.*)$', s, re.IGNORECASE | re.DOTALL)
        if m:
            expr = m.group(1).strip()
            has_default_kw = True
        else:
            expr = s
            has_default_kw = False
        pg_expr = cls.transpile_expression(expr, symbols=symbols, sequence_increments=sequence_increments)
        return f"DEFAULT {pg_expr}" if has_default_kw else pg_expr

    @classmethod
    def transpile_check_clause(cls, check_str: str | None, symbols: dict[str, str] = None, sequence_increments: dict[str, int] = None) -> str | None:
        if not check_str:
            return None
        s = check_str.strip()
        m = re.match(r'^\s*CHECK\s*\((.*)\)\s*$', s, re.IGNORECASE | re.DOTALL)
        if m:
            expr = m.group(1).strip()
        else:
            m2 = re.match(r'^\s*CHECK\s+(.*)$', s, re.IGNORECASE | re.DOTALL)
            expr = m2.group(1).strip() if m2 else s
        pg_expr = cls.transpile_expression(expr, symbols=symbols, sequence_increments=sequence_increments)
        return f"CHECK ({pg_expr})"

    @staticmethod
    def _clean_sql(pg_sql: str) -> str:
        """
        Post-transpilation cleanup:
        1. Restores custom exception messages into `RAISE EXCEPTION '<name>: %', '<msg>';`.
        2. Strips protective double-quotes on trigger pseudo-records ("old".col -> old.col).
        """
        # Step 1: Restore custom exception messages
        ex_clean = re.compile(
            r"/\*\s*__FB_EX_MSG__:([a-zA-Z0-9_$]+):('(?:''|[^'])*')\s*\*/\s*RAISE\s+EXCEPTION\s+'\1';",
            flags=re.IGNORECASE
        )
        pg_sql = ex_clean.sub(r"RAISE EXCEPTION '\1: %', \2;", pg_sql)

        # Step 2: Strip protective double-quotes on trigger pseudo-records (preserving strings and comments)
        clean_pattern = re.compile(
            r"('(?:''|[^'])*'|/\*.*?\*/|--[^\n]*)|(\"(old|new)\"\.)",
            flags=re.IGNORECASE
        )
        pg_sql = clean_pattern.sub(lambda m: m.group(1) if m.group(1) else f"{m.group(3)}.", pg_sql)

        # Step 3: Restore WHEN ANY exception handling
        pg_sql = re.sub(r"/\*\s*__FB_WHEN_ANY__\s*\*/", "EXCEPTION\n    WHEN OTHERS THEN", pg_sql)
        return pg_sql

    def visitSql_script(self, ctx: FirebirdParser.Sql_scriptContext):
        statements = []
        for child in ctx.children:
            result = self.visit(child)
            if result:
                statements.append(result)
        return "\n\n".join(statements)

    def _convert_type(self, raw_type: str) -> str:
        dmap = getattr(self, 'domain_map', None)
        return convert_firebird_type_declaration(raw_type, domain_map=dmap)

    def visitUnit_statement(self, ctx: FirebirdParser.Unit_statementContext):
        return self.visitChildren(ctx)

    def _has_suspend_node(self, node) -> bool:
        if node is None:
            return False
        if hasattr(node, 'symbol') and hasattr(node.symbol, 'type'):
            if node.symbol.type == FirebirdParser.SUSPEND:
                return True
        if hasattr(node, 'SUSPEND') and callable(node.SUSPEND) and node.SUSPEND():
            return True
        if hasattr(node, 'children') and node.children:
            for child in node.children:
                if self._has_suspend_node(child):
                    return True
        return False

    @staticmethod
    def _strip_sql_comments_and_strings(sql: str) -> str:
        """
        Strips comments and replaces string literal contents with empty quotes in a single pass.
        This prevents strings containing '--' or '/*' from hiding or swallowing code,
        and prevents comments containing DML or function calls from triggering false positives.
        """
        pattern = re.compile(
            r"('(?:''|[^'])*')"    # Group 1: string literal -> replace with "''"
            r"|(--[^\r\n]*)"       # Group 2: line comment -> replace with ' '
            r"|(/\*[\s\S]*?\*/)",  # Group 3: block comment -> replace with ' '
            re.MULTILINE
        )
        return pattern.sub(lambda m: "''" if m.group(1) is not None else " ", sql)

    @staticmethod
    def _classify_procedure_volatility(body_str: str, decl_str: str = "", params_str: str = "") -> tuple[str, list[str]]:
        """
        Analyzes transpiled PL/pgSQL procedure body, declarations, and parameter defaults to determine volatility.
        Returns (volatility, reasons).

        Promotion Policy for STABLE:
        - Default volatility in PostgreSQL PL/pgSQL functions is VOLATILE.
        - Promotion to STABLE requires strictly demonstrated read-only purity:
          1. No data modification (INSERT, UPDATE, DELETE, MERGE, TRUNCATE).
          2. No procedure calls (PERFORM, CALL, EXECUTE PROCEDURE).
          3. No dynamic SQL execution (EXECUTE ...).
          4. No sequence generator access (NEXT VALUE FOR, GEN_ID, nextval, setval, currval).
          5. No transaction control (COMMIT, ROLLBACK, AUTONOMOUS).
          6. No volatile built-in functions (random, gen_random_uuid, clock_timestamp, timeofday).
          7. No unverified external or qualified function calls (including delimited "Q"() and schema.q()),
             as their dependencies and purity cannot be statically guaranteed.
          8. Parameter defaults and local variable initializers participate in classification under these same rules.
        - If any side effect or unverified dependency is present, the function remains VOLATILE.
        """
        full_code = f"{params_str}\n{decl_str}\n{body_str}" if (params_str or decl_str) else body_str
        clean_code = FirebirdToPostgresVisitor._strip_sql_comments_and_strings(full_code)

        side_effects = []
        if re.search(r'\b(INSERT\s+INTO|UPDATE\b|DELETE\s+FROM|DELETE\b|MERGE\s+INTO|TRUNCATE\b)\b', clean_code, re.IGNORECASE):
            side_effects.append("data modification (DML)")
        if re.search(r'\b(PERFORM|EXECUTE\s+PROCEDURE)\b', clean_code, re.IGNORECASE):
            side_effects.append("procedure call (PERFORM)")
        elif re.search(r'\bCALL\b', clean_code, re.IGNORECASE):
            side_effects.append("procedure call (CALL)")
        if re.search(r'\bEXECUTE\s+(?!PROCEDURE\b)', clean_code, re.IGNORECASE):
            side_effects.append("dynamic SQL / external execution")
        if re.search(r'\b(NEXT\s+VALUE\s+FOR|GEN_ID|nextval|setval|currval)\b', clean_code, re.IGNORECASE):
            side_effects.append("sequence generator access")
        if re.search(r'\b(AUTONOMOUS|COMMIT|ROLLBACK)\b', clean_code, re.IGNORECASE):
            side_effects.append("autonomous transaction / transaction control")
        if re.search(r'\b(random|gen_random_uuid|clock_timestamp|timeofday)\s*\(', clean_code, re.IGNORECASE):
            side_effects.append("volatile built-in function")

        # Extract function calls: support unquoted, delimited ("Q"()), and qualified (schema.q()) calls.
        call_matches = re.findall(
            r'(?:([a-zA-Z_][a-zA-Z0-9_$]*|"[^"\r\n]+")\s*\.\s*)?'
            r'([a-zA-Z_][a-zA-Z0-9_$]*|"[^"\r\n]+")\s*\(',
            clean_code,
            re.MULTILINE
        )
        _sequence_calls = {'nextval', 'gen_id', 'setval', 'currval'}
        _volatile_builtin_calls = {'random', 'gen_random_uuid', 'clock_timestamp', 'timeofday'}
        unknown_calls = set()
        for qual, raw_name in call_matches:
            if qual:
                # Schema-qualified calls are external/unverified dependencies -> VOLATILE
                unknown_calls.add(f"{qual}.{raw_name}")
            else:
                clean_name = raw_name.strip('"').lower()
                if clean_name not in _SAFE_PROC_CALLS and clean_name not in _sequence_calls and clean_name not in _volatile_builtin_calls:
                    unknown_calls.add(raw_name)

        if unknown_calls:
            sorted_unknown = sorted(unknown_calls)
            side_effects.append(f"external function call ({', '.join(sorted_unknown)})")

        if side_effects:
            return "VOLATILE", side_effects
        return "STABLE", ["read-only query/computation"]

    def visitCreate_procedure_body(self, ctx: FirebirdParser.Create_procedure_bodyContext):
        proc_name = ctx.procedure_name().getText().strip('"')

        # In PostgreSQL, we translate procedures to functions
        has_returns = False
        in_params = []
        in_param_names = []
        out_params = []
        out_types = []
        for child in ctx.children:
            if hasattr(child, 'getText') and child.getText().upper() == 'RETURNS':
                has_returns = True
            elif isinstance(child, FirebirdParser.ParameterContext):
                type_spec = self._convert_type(self.get_raw_text(child.type_spec())) if child.type_spec() else "TEXT"
                if has_returns:
                    param_name = _normalize_ident_case(child.parameter_name().getText())
                    out_params.append(f"OUT {param_name} {type_spec}".strip())
                    out_types.append(type_spec)
                else:
                    param_name = _normalize_ident_case(child.parameter_name().getText())
                    in_param_names.append(param_name)
                    param_str = self.visit(child)
                    in_params.append(param_str)

        all_params = in_params + out_params
        params_str = ", ".join(all_params)

        # Declarations
        decl_str = ""
        if ctx.seq_of_declare_specs():
            decl_str = self.visit(ctx.seq_of_declare_specs())
            if decl_str:
                decl_str = f"DECLARE\n{decl_str}\n"

        # Determine if procedure is selectable (has SUSPEND)
        has_return_next = self._has_suspend_node(ctx.body()) if ctx.body() else False
        not_null_out_list = self.not_null_outputs.get(proc_name.lower(), [])

        prev_not_null_outputs = getattr(self, 'current_not_null_outputs', {})
        prev_proc_has_suspend = getattr(self, 'current_proc_has_suspend', False)
        self.current_not_null_outputs = {}
        for p in not_null_out_list:
            p_clean = p.strip('"')
            p_ident = pg_quote_ident(p_clean.lower()) if (p.startswith('"') and p.endswith('"')) else p
            self.current_not_null_outputs[p_clean.lower()] = {
                'ident': p_ident,
                'name': p_clean
            }
        self.current_proc_has_suspend = has_return_next

        # Translate the body
        try:
            body_str = self.visit(ctx.body()) if ctx.body() else ""
        finally:
            self.current_not_null_outputs = prev_not_null_outputs
            self.current_proc_has_suspend = prev_proc_has_suspend

        # Inject runtime NOT NULL guards for input parameters declared NOT NULL in Firebird
        not_null_list = self.not_null_params.get(proc_name.lower(), [])
        if not_null_list and body_str:
            not_null_set = {p.strip('"').lower() for p in not_null_list}
            guards = []
            for p in in_param_names:
                if p.strip('"').lower() in not_null_set:
                    p_clean = p.strip('"')
                    guards.append(f"IF {p} IS NULL THEN RAISE EXCEPTION 'Parameter \"%\" cannot be NULL', '{p_clean}'; END IF;")
            if guards:
                guards_str = "\n".join(f"    {g}" for g in guards)
                m_begin = re.match(r'^(BEGIN\s*\r?\n)', body_str, re.IGNORECASE)
                if m_begin:
                    body_str = m_begin.group(1) + guards_str + "\n" + body_str[m_begin.end():]
                else:
                    body_str = re.sub(r'(\bBEGIN\b)', r'\1\n' + guards_str, body_str, count=1, flags=re.IGNORECASE)

        # Inject runtime NOT NULL guards at routine end for output parameters in executable procedures
        if not has_return_next and not_null_out_list and body_str:
            end_guards = []
            for p in not_null_out_list:
                p_clean = p.strip('"')
                p_ident = pg_quote_ident(p_clean) if p.startswith('"') else p_clean
                end_guards.append(f"IF {p_ident} IS NULL THEN RAISE EXCEPTION 'validation error for variable %, value null', '{p_clean}'; END IF;")
            if end_guards:
                end_guards_str = "\n".join(f"    {g}" for g in end_guards)
                body_str = re.sub(r'(\n?\s*\bEND\s*;\s*)$', r'\n' + end_guards_str + r'\nEND;', body_str.rstrip(), flags=re.IGNORECASE)

        # Determine correct return type for PostgreSQL
        if not out_params:
            return_type = "RETURNS void"
            # In void functions, SUSPEND / RETURN NEXT must be a plain RETURN;
            body_str = re.sub(r'\bRETURN\s+NEXT\b\s*;?', 'RETURN;', body_str)
        elif len(out_params) == 1:
            return_type = f"RETURNS SETOF {out_types[0]}" if has_return_next else f"RETURNS {out_types[0]}"
        else:
            return_type = "RETURNS SETOF record" if has_return_next else "RETURNS record"

        # Classify volatility (STABLE vs VOLATILE) and generate volatility advisory
        volatility, reasons = self._classify_procedure_volatility(body_str, decl_str, params_str)

        advisory_lines = [
            f'-- [CLASSIFICATION & VOLATILITY ADVISORY]',
            f'-- Volatility: {volatility} ({", ".join(reasons)})'
        ]
        if volatility == "STABLE":
            advisory_lines.append(
                '-- Volatility note: STABLE indicates the function does not modify database state and returns '
                'consistent results within a single statement.'
            )
        else:
            advisory_lines.append(
                '-- Volatility note: VOLATILE indicates the function may modify database state, '
                'depend on sequence/external calls, or produce side effects across evaluations.'
            )
        advisory_str = "\n".join(advisory_lines) + "\n"

        # DROP first to guarantee idempotency, since changing an existing function's
        # signature (parameter types or return type) requires recreating it
        tag = choose_dollar_tag(f"{decl_str}{body_str}")
        return (f'{advisory_str}'
                f'DROP FUNCTION IF EXISTS "{proc_name.lower()}" CASCADE;\n'
                f'CREATE FUNCTION "{proc_name.lower()}"({params_str}) {return_type} AS {tag}\n'
                f'#variable_conflict use_variable\n'
                f'{decl_str}{body_str}\n'
                f'{tag} LANGUAGE plpgsql {volatility};')

    def visitParameter(self, ctx: FirebirdParser.ParameterContext):
        param_name = _normalize_ident_case(ctx.parameter_name().getText())
        # Firebird allows datatype directly or TYPE OF
        # Extract the raw tokens for the type to preserve spaces (e.g. VARCHAR(255))
        type_spec = ""
        if ctx.type_spec():
            type_spec = self._convert_type(self.get_raw_text(ctx.type_spec()))
        default_part = ""
        if ctx.default_value_part():
            expr_node = ctx.default_value_part().expression()
            if expr_node:
                self.visit(expr_node)
                expr_str = self.get_raw_text(expr_node).strip()
                default_part = f" DEFAULT {expr_str}"
        return f"{param_name} {type_spec}{default_part}".strip()

    def visitCreate_trigger(self, ctx: FirebirdParser.Create_triggerContext):
        trigger_name = ctx.trigger_name().getText().strip('"')
        # Extract table name and events
        table_name = ctx.tableview_name().getText().strip('"') if ctx.tableview_name() else "UNKNOWN_TABLE"

        # Simple extraction of timing and events
        simple_dml = ctx.simple_dml_trigger()
        timing = "BEFORE"
        events = "INSERT"
        if simple_dml:
            timing_node = simple_dml.getChild(0)  # BEFORE, AFTER, INSTEAD OF
            timing = timing_node.getText()
            events = self.get_raw_text(simple_dml.dml_event_clause())

        body_str = self.visit(ctx.trigger_body()) if ctx.trigger_body() else ""

        # Determine the return statement for Postgres trigger function
        timing_upper = timing.upper()
        events_upper = events.upper()
        if "BEFORE" in timing_upper:
            has_delete = "DELETE" in events_upper
            has_insert_or_update = "INSERT" in events_upper or "UPDATE" in events_upper
            if has_delete and has_insert_or_update:
                return_stmt = ("IF TG_OP = 'DELETE' THEN\n"
                               "        RETURN OLD;\n"
                               "    ELSE\n"
                               "        RETURN NEW;\n"
                               "    END IF;")
            elif has_delete:
                return_stmt = "RETURN OLD;"
            else:
                return_stmt = "RETURN NEW;"
        else:
            return_stmt = "RETURN NULL;"

        # Check if the trigger is purely an auto-increment ID assignment:
        # IF (NEW.col IS NULL) THEN NEW.col := nextval(...); END IF;
        # Lifting this guard to WHEN (NEW."col" IS NULL) ensures PostgreSQL's C engine
        # skips invoking the PL/pgSQL function on standard inserts where DEFAULT nextval(...)
        # already populated the column, eliminating redundant trigger execution overhead.
        when_clause = ""
        if timing_upper == "BEFORE" and "INSERT" in events_upper and "DELETE" not in events_upper:
            norm_body = " ".join(body_str.split())
            id_match = re.match(
                r'^BEGIN\s+IF\s*\(?\s*"?(?:new|NEW)"?\.([a-zA-Z0-9_$]+)\s+IS\s+NULL\s*\)?\s+THEN\s+'
                r'"?(?:new|NEW)"?\.\1\s*:=\s*nextval\([^)]+\);\s*END\s+IF;\s*END;?$',
                norm_body,
                re.IGNORECASE
            )
            if id_match:
                col_name = id_match.group(1).lower()
                when_clause = f' WHEN (NEW."{col_name}" IS NULL)'

        if body_str:
            if body_str.rstrip().endswith("END;"):
                idx = body_str.rstrip().rfind("END;")
                body_str = f"{body_str[:idx]}    {return_stmt}\nEND;"
            else:
                body_str = f"{body_str}\n    {return_stmt}"

        # Postgres uses a function for the trigger body, and then CREATE TRIGGER
        func_name = f"{trigger_name}_func"

        tag = choose_dollar_tag(body_str)
        func_sql = f'CREATE OR REPLACE FUNCTION "{func_name}"() RETURNS TRIGGER AS {tag}\n#variable_conflict use_variable\n{body_str}\n{tag} LANGUAGE plpgsql;'
        trigger_sql = (f'DROP TRIGGER IF EXISTS "{trigger_name}" ON "{table_name.lower()}";\n'
                       f'CREATE TRIGGER "{trigger_name}" {timing} {events} ON "{table_name.lower()}" '
                       f'FOR EACH ROW{when_clause} EXECUTE FUNCTION "{func_name}"();')

        return f"{func_sql}\n{trigger_sql}"

    def _get_comments_in_range(self, start_idx: int, stop_idx: int) -> list[str]:
        """
        Extracts hidden channel comment tokens located between start_idx and stop_idx (inclusive).
        """
        comments = []
        if not self.rewriter or not self.rewriter.tokens:
            return comments
        tokens = self.rewriter.tokens.tokens
        for idx in range(max(0, start_idx), min(len(tokens), stop_idx + 1)):
            t = tokens[idx]
            if t.channel == 1 and ('--' in t.text or '/*' in t.text):
                txt = t.text.strip()
                if txt:
                    comments.append(txt)
        return comments

    def _collect_with_comments(self, child_nodes: list[ParserRuleContext],
                               start_token_idx: int = 0,
                               stop_token_idx: int = 0,
                               indent_comments: bool = False,
                               ensure_semicolon: bool = False) -> list[str]:
        """
        Visits a list of AST child nodes while extracting and preserving hidden-channel
        comments situated before, between, and after each node.
        """
        items = []
        if not child_nodes:
            if stop_token_idx >= start_token_idx > 0:
                for c in self._get_comments_in_range(start_token_idx, stop_token_idx):
                    items.append(f"    {c}" if indent_comments else c)
            return items

        curr_token_idx = start_token_idx if start_token_idx > 0 else (
            child_nodes[0].start.tokenIndex if child_nodes and child_nodes[0].start else 0
        )

        for child in child_nodes:
            if child.start:
                pre_comments = self._get_comments_in_range(curr_token_idx, child.start.tokenIndex - 1)
                for c in pre_comments:
                    items.append(f"    {c}" if indent_comments else c)

            res = self.visit(child)
            if res:
                res_str = res.strip()
                if ensure_semicolon and not res_str.endswith(';'):
                    res_str += ';'
                items.append(res_str)

            if child.stop:
                curr_token_idx = child.stop.tokenIndex + 1

        if stop_token_idx >= curr_token_idx and stop_token_idx > 0:
            trailing_comments = self._get_comments_in_range(curr_token_idx, stop_token_idx)
            for c in trailing_comments:
                items.append(f"    {c}" if indent_comments else c)

        return items

    def _visit_declarations(self, declare_specs: list[ParserRuleContext]) -> str:
        if not declare_specs:
            return ""
        start_idx = declare_specs[0].start.tokenIndex if declare_specs[0].start else 0
        stop_idx = declare_specs[-1].stop.tokenIndex if declare_specs[-1].stop else 0
        items = self._collect_with_comments(declare_specs, start_idx, stop_idx, indent_comments=True)
        return "DECLARE\n" + "\n".join(items) + "\n" if items else ""

    def visitTrigger_block(self, ctx: FirebirdParser.Trigger_blockContext):
        decl_str = self._visit_declarations(ctx.declare_spec()) if ctx.declare_spec() else ""
        body_str = self.visit(ctx.body()) if ctx.body() else ""
        return f"{decl_str}{body_str}"

    def visitCreate_view(self, ctx: FirebirdParser.Create_viewContext):
        raw_name = ctx.id_expression(0).getText().strip()
        clean_name = raw_name[1:-1].replace('""', '"') if raw_name.startswith('"') and raw_name.endswith('"') else raw_name
        view_name = clean_name.lower()
        select_stmt = self.get_raw_text(ctx.select_only_statement())

        view_opts = ""
        if ctx.view_options():
            vac = ctx.view_options().view_alias_constraint()
            if vac and vac.table_alias():
                cols = []
                for ta in vac.table_alias():
                    raw_col = (ta.identifier().getText() if ta.identifier() else ta.getText()).strip()
                    clean_col = raw_col[1:-1].replace('""', '"') if raw_col.startswith('"') and raw_col.endswith('"') else raw_col
                    cols.append(pg_quote_ident(clean_col.lower()))
                if cols:
                    view_opts = f" ({', '.join(cols)})"
            if not view_opts:
                view_opts = f" {self.get_raw_text(ctx.view_options())}"

        # DROP first to guarantee idempotency, since changing the column list of an
        # existing view (names, order or types) requires recreating it
        return f'DROP VIEW IF EXISTS {pg_quote_ident(view_name)} CASCADE;\nCREATE VIEW {pg_quote_ident(view_name)}{view_opts} AS {select_stmt};'

    def visitSelect_statement(self, ctx: FirebirdParser.Select_statementContext):
        raw = self.get_raw_text(ctx).strip()
        if raw.endswith(';'):
            return raw
        return raw + ';'

    def visitBody(self, ctx: FirebirdParser.BodyContext):
        # A body is usually BEGIN ... END
        stmt_contexts = []
        if ctx.seq_of_statements() and ctx.seq_of_statements().children:
            for child in ctx.seq_of_statements().children:
                if isinstance(child, FirebirdParser.StatementContext):
                    stmt_contexts.append(child)

        start_token_idx = ctx.start.tokenIndex + 1 if ctx.start else 0
        stop_token_idx = ctx.stop.tokenIndex - 1 if ctx.stop else 0
        items = self._collect_with_comments(stmt_contexts, start_token_idx, stop_token_idx, ensure_semicolon=True)

        indented_lines = []
        for s in items:
            for line in s.split('\n'):
                indented_lines.append(f"    {line}" if line.strip() else line)
        inner_code = "\n".join(indented_lines)
        return f"BEGIN\n{inner_code}\nEND;"

    @staticmethod
    def _guarantees_single_row(select_ctx: ParserRuleContext) -> bool:
        """
        Returns True if the SELECT query structurally guarantees returning exactly 1 row:
        Pure scalar evaluation without filters:
        - No FROM clause, or FROM RDB$DATABASE
        - AND no WHERE, GROUP BY, HAVING, MODEL, HIERARCHICAL, FIRST, or SKIP clauses.
        In these cases, NO_DATA_FOUND can never be raised in PostgreSQL, making
        BEGIN ... EXCEPTION WHEN NO_DATA_FOUND subtransactions completely unnecessary.
        """
        qb = _find_node(select_ctx, FirebirdParser.Query_blockContext)
        if not qb:
            return False

        # Any compound operations (UNION, INTERSECT, MINUS) disqualify single-row guarantee
        if _find_node(select_ctx, FirebirdParser.Subquery_operation_partContext):
            return False

        # Any offset or fetch clauses disqualify
        if hasattr(select_ctx, 'offset_clause') and select_ctx.offset_clause():
            return False
        if hasattr(select_ctx, 'fetch_clause') and select_ctx.fetch_clause():
            return False

        # Inside the query block, any filtering or row-modifying clause disqualifies:
        # WHERE, GROUP BY (which includes HAVING), hierarchical query, model, FIRST, SKIP
        if hasattr(qb, 'where_clause') and qb.where_clause():
            return False
        if hasattr(qb, 'group_by_clause') and qb.group_by_clause():
            return False
        if hasattr(qb, 'hierarchical_query_clause') and qb.hierarchical_query_clause():
            return False
        if hasattr(qb, 'model_clause') and qb.model_clause():
            return False
        if hasattr(qb, 'FIRST') and qb.FIRST():
            return False
        if hasattr(qb, 'SKIP_') and qb.SKIP_():
            return False

        from_clause = qb.from_clause() if hasattr(qb, 'from_clause') else None
        if not from_clause:
            return True
        if hasattr(from_clause, 'table_ref_list') and from_clause.table_ref_list():
            ref_text = from_clause.table_ref_list().getText().upper()
            if ref_text == 'RDB$DATABASE':
                return True

        return False

    def visitStatement(self, ctx: FirebirdParser.StatementContext):
        child = ctx.getChild(0)

        if isinstance(child, (
                FirebirdParser.BodyContext,
                FirebirdParser.BlockContext,
                FirebirdParser.Assignment_statementContext,
                FirebirdParser.Exit_statementContext,
                FirebirdParser.If_statementContext,
                FirebirdParser.Loop_statementContext
        )):
            return self.visit(child)

        # Check for SUSPEND
        if (hasattr(ctx, 'SUSPEND') and ctx.SUSPEND()) or (child and hasattr(child, 'getText') and child.getText().upper() == 'SUSPEND'):
            if getattr(self, 'current_not_null_outputs', None):
                guards = []
                for p_clean, info in self.current_not_null_outputs.items():
                    guards.append(f"IF {info['ident']} IS NULL THEN RAISE EXCEPTION 'validation error for variable %, value null', '{info['name']}'; END IF;")
                guards.append("RETURN NEXT;")
                return "\n".join(guards)
            return "RETURN NEXT;"

        # Singleton SELECT ... INTO statements are wrapped in BEGIN ... EXCEPTION WHEN NO_DATA_FOUND THEN NULL; END;
        # to match Firebird PSQL semantics (preserving target variable values when no rows are found).
        # We omit this wrapper when the query is guaranteed to return exactly one row (e.g. constant/scalar
        # queries without FROM, or pure aggregates without GROUP BY) to eliminate subtransaction overhead.
        into_ctx = _find_node(ctx, FirebirdParser.Into_clauseContext)
        select_ctx = _find_node(ctx, FirebirdParser.Select_statementContext)
        if into_ctx and select_ctx:
            into_vars = []
            for c in into_ctx.children:
                if isinstance(c, (FirebirdParser.General_elementContext, FirebirdParser.Bind_variableContext)):
                    v_name = self.get_raw_text(c).strip().lstrip(':').strip('"').lower()
                    into_vars.append(v_name)
            not_null_into = [v for v in into_vars if v in getattr(self, 'current_not_null_outputs', {})]
            if not_null_into:
                into_guards = [
                    f"IF {self.current_not_null_outputs[v]['ident']} IS NULL THEN RAISE EXCEPTION 'validation error for variable %, value null', '{self.current_not_null_outputs[v]['name']}'; END IF;"
                    for v in not_null_into
                ]
                into_guards_str = "\n".join(into_guards)
                if not self._guarantees_single_row(select_ctx):
                    raw_stmt = self.get_raw_text(ctx).strip()
                    if not raw_stmt.endswith(';'):
                        raw_stmt += ';'
                    stmt_lines = [f"    {line}" for line in raw_stmt.split('\n')]
                    stmt_lines.extend(f"    {g}" for g in into_guards)
                    indented_stmt = "\n".join(stmt_lines)
                    return f"BEGIN\n{indented_stmt}\nEXCEPTION WHEN NO_DATA_FOUND THEN\n    NULL;\nEND;"
                else:
                    raw_stmt = self.get_raw_text(ctx).strip()
                    if not raw_stmt.endswith(';'):
                        raw_stmt += ';'
                    return f"{raw_stmt}\n{into_guards_str}"

        if into_ctx and select_ctx and not self._guarantees_single_row(select_ctx):
            raw_stmt = self.get_raw_text(ctx).strip()
            if not raw_stmt.endswith(';'):
                raw_stmt += ';'
            stmt_lines = [f"    {line}" for line in raw_stmt.split('\n')]
            indented_stmt = "\n".join(stmt_lines)
            return f"BEGIN\n{indented_stmt}\nEXCEPTION WHEN NO_DATA_FOUND THEN\n    NULL;\nEND;"

        # DML RETURNING INTO (INSERT/UPDATE/DELETE ... RETURNING ... INTO :var)
        # can assign NULL to NOT NULL output params — inject guards after the statement.
        ret_ctx = _find_node(ctx, FirebirdParser.Static_returning_clauseContext)
        if ret_ctx and getattr(self, 'current_not_null_outputs', None):
            ret_into = _find_node(ret_ctx, FirebirdParser.Into_clauseContext)
            if ret_into:
                ret_vars = []
                for c in ret_into.children:
                    if isinstance(c, (FirebirdParser.General_elementContext, FirebirdParser.Bind_variableContext)):
                        v_name = self.get_raw_text(c).strip().lstrip(':').strip('"').lower()
                        ret_vars.append(v_name)
                not_null_ret = [v for v in ret_vars if v in self.current_not_null_outputs]
                if not_null_ret:
                    raw_stmt = self.get_raw_text(ctx).strip()
                    if not raw_stmt.endswith(';'):
                        raw_stmt += ';'
                    ret_guards = [
                        f"IF {self.current_not_null_outputs[v]['ident']} IS NULL THEN RAISE EXCEPTION 'validation error for variable %, value null', '{self.current_not_null_outputs[v]['name']}'; END IF;"
                        for v in not_null_ret
                    ]
                    return f"{raw_stmt}\n" + "\n".join(ret_guards)

        # For all other SQL statements (UPDATE, DELETE, EXECUTE, plain SELECT, etc.)
        # we just return their rewritten text.
        return self.get_raw_text(ctx)


    def visitExit_statement(self, ctx: FirebirdParser.Exit_statementContext):
        first_tok = ctx.getChild(0).getText().upper()
        if first_tok == 'LEAVE' or ctx.label_name():
            return self.get_raw_text(ctx)

        if not getattr(self, 'current_proc_has_suspend', False) and getattr(self, 'current_not_null_outputs', None):
            guards = []
            for p_clean, info in self.current_not_null_outputs.items():
                guards.append(f"IF {info['ident']} IS NULL THEN RAISE EXCEPTION 'validation error for variable %, value null', '{info['name']}'; END IF;")
            guards.append("RETURN;")
            guards_block = "\n".join(guards)
            if ctx.condition():
                cond = self.get_raw_text(ctx.condition())
                indented = "\n".join(f"    {line}" for line in guards_block.split('\n'))
                return f"IF {cond} THEN\n{indented}\nEND IF;"
            return guards_block

        return self.get_raw_text(ctx)

    def visitBlock(self, ctx: FirebirdParser.BlockContext):
        decl_str = self._visit_declarations(ctx.declare_spec()) if ctx.declare_spec() else ""
        body_str = self.visit(ctx.body()) if ctx.body() else ""
        return f"{decl_str}{body_str}"

    def visitIf_statement(self, ctx: FirebirdParser.If_statementContext):
        if ctx.condition():
            self.visit(ctx.condition())
        cond = self.get_raw_text(ctx.condition())
        then_stmt = self.visit(ctx.statement(0))
        if then_stmt:
            then_stmt = then_stmt.strip()
            if not then_stmt.endswith(';'):
                then_stmt += ';'

        then_comments = self._get_comments_in_range(ctx.condition().stop.tokenIndex + 1,
                                                    ctx.statement(0).start.tokenIndex - 1) \
            if ctx.condition().stop and ctx.statement(0).start else []
        then_comment_str = ('\n    ' + '\n    '.join(then_comments) + '\n') if then_comments else ''

        sql = f"IF {cond} THEN{then_comment_str}\n    {then_stmt}\n"

        if len(ctx.statement()) > 1:
            else_comments = self._get_comments_in_range(ctx.statement(0).stop.tokenIndex + 1,
                                                        ctx.statement(1).start.tokenIndex - 1) \
                if ctx.statement(0).stop and ctx.statement(1).start else []
            else_comment_str = ('\n    ' + '\n    '.join(else_comments) + '\n') if else_comments else ''
            else_stmt = self.visit(ctx.statement(1))
            if else_stmt:
                else_stmt = else_stmt.strip()
                if not else_stmt.endswith(';'):
                    else_stmt += ';'
            sql += f"ELSE{else_comment_str}\n    {else_stmt}\n"

        sql += "END IF;"
        return sql

    def get_raw_text(self, ctx):
        if ctx is None:
            return ""
        if hasattr(ctx, 'start') and hasattr(ctx, 'stop') and ctx.start and ctx.stop:
            if self.rewriter:
                text = self.rewriter.getText(
                    TokenStreamRewriter.DEFAULT_PROGRAM_NAME,
                    ctx.start.tokenIndex,
                    ctx.stop.tokenIndex
                )
                if ctx.stop.tokenIndex < len(self.rewriter.tokens.tokens) - 1:
                    prog = self.rewriter.programs.get(TokenStreamRewriter.DEFAULT_PROGRAM_NAME)
                    if prog:
                        for op in prog:
                            if isinstance(op, TokenStreamRewriter.InsertAfterOp) and op.index == ctx.stop.tokenIndex + 1:
                                text += op.text
                return text
            start_idx = ctx.start.start
            stop_idx = ctx.stop.stop
            stream = ctx.start.getInputStream()
            return stream.getText(start_idx, stop_idx)
        return ctx.getText()

    def visitSeq_of_declare_specs(self, ctx: FirebirdParser.Seq_of_declare_specsContext):
        decl_children = [c for c in ctx.children if hasattr(c, 'start') and hasattr(c, 'stop')] if ctx.children else []
        start_token_idx = ctx.start.tokenIndex if ctx.start else 0
        stop_token_idx = ctx.stop.tokenIndex if ctx.stop else 0
        items = self._collect_with_comments(decl_children, start_token_idx, stop_token_idx, indent_comments=True)
        return "\n".join(items)

    def visitVariable_declaration(self, ctx: FirebirdParser.Variable_declarationContext):
        var_name = _normalize_ident_case(ctx.identifier().getText())
        is_const = " CONSTANT" if (hasattr(ctx, 'CONSTANT') and ctx.CONSTANT()) else ""
        type_spec = self._convert_type(self.get_raw_text(ctx.type_spec()))
        not_null = " NOT NULL" if (hasattr(ctx, 'NOT') and ctx.NOT()) else ""
        default_part = ""
        if ctx.default_value_part():
            expr_node = ctx.default_value_part().expression()
            if expr_node:
                self.visit(expr_node)
                expr_str = self.get_raw_text(expr_node).strip()
                default_part = f" DEFAULT {expr_str}"
        return f"    {var_name}{is_const} {type_spec}{not_null}{default_part};"

    def visitAssignment_statement(self, ctx: FirebirdParser.Assignment_statementContext):
        left = self.get_raw_text(ctx.getChild(0)).strip().lstrip(':')
        if ctx.expression():
            self.visit(ctx.expression())
        right = self.get_raw_text(ctx.expression())
        left_clean = left.strip('"').lower()
        if getattr(self, 'current_not_null_outputs', None) and left_clean in self.current_not_null_outputs:
            info = self.current_not_null_outputs[left_clean]
            p_ident = info['ident']
            p_name = info['name']
            return (
                f"{left} := {right};\n"
                f"IF {p_ident} IS NULL THEN\n"
                f"    RAISE EXCEPTION 'validation error for variable %, value null', '{p_name}';\n"
                f"END IF;"
            )
        return f"{left} := {right};"

    def visitLoop_statement(self, ctx: FirebirdParser.Loop_statementContext):
        # Case 1: FOR EXECUTE STATEMENT expression into_clause? DO statement
        if hasattr(ctx, 'EXECUTE') and ctx.EXECUTE():
            expr = self.get_raw_text(ctx.expression())
            into_vars = []
            end_header_token = ctx.expression().stop
            if ctx.into_clause():
                end_header_token = ctx.into_clause().stop
                for child in ctx.into_clause().children:
                    if isinstance(child, (FirebirdParser.General_elementContext, FirebirdParser.Bind_variableContext)):
                        into_vars.append(self.get_raw_text(child).strip().lstrip(':'))

            target = ", ".join(into_vars) if into_vars else "_rec"
            loop_guards = []
            for v in into_vars:
                v_clean = v.strip('"').lower()
                if getattr(self, 'current_not_null_outputs', None) and v_clean in self.current_not_null_outputs:
                    info = self.current_not_null_outputs[v_clean]
                    loop_guards.append(f"IF {info['ident']} IS NULL THEN RAISE EXCEPTION 'validation error for variable %, value null', '{info['name']}'; END IF;")

            loop_comments = self._get_comments_in_range(end_header_token.tokenIndex + 1,
                                                        ctx.statement().start.tokenIndex - 1) \
                if end_header_token and ctx.statement().start else []
            comment_str = ('\n    ' + '\n    '.join(loop_comments) + '\n') if loop_comments else ' '

            body_sql = self.visit(ctx.statement())
            if loop_guards:
                guards_prefix = "\n".join(loop_guards) + "\n"
                body_sql = guards_prefix + (body_sql or "")
            if body_sql:
                body_sql = body_sql.strip()
                if not body_sql.endswith(';'):
                    body_sql += ';'
            body_lines = body_sql.split('\n')
            indented_body = "\n".join(f"    {line}" if line.strip() else line for line in body_lines)
            return f"FOR {target} IN EXECUTE {expr}{comment_str}LOOP\n{indented_body}\nEND LOOP;"

        # Case 2: FOR select_statement DO statement
        if ctx.select_statement():
            into_ctx = _find_node(ctx.select_statement(), FirebirdParser.Into_clauseContext)

            into_vars = []
            if into_ctx:
                for child in into_ctx.children:
                    if isinstance(child, (FirebirdParser.General_elementContext, FirebirdParser.Bind_variableContext)):
                        into_vars.append(self.get_raw_text(child).strip().lstrip(':'))

            select_sql = self.get_text_without_node(ctx.select_statement(), into_ctx).strip()
            select_sql = select_sql.rstrip(';').strip()
            target = ", ".join(into_vars) if into_vars else "_rec"
            loop_guards = []
            for v in into_vars:
                v_clean = v.strip('"').lower()
                if getattr(self, 'current_not_null_outputs', None) and v_clean in self.current_not_null_outputs:
                    info = self.current_not_null_outputs[v_clean]
                    loop_guards.append(f"IF {info['ident']} IS NULL THEN RAISE EXCEPTION 'validation error for variable %, value null', '{info['name']}'; END IF;")

            end_header_token = ctx.select_statement().stop
            loop_comments = self._get_comments_in_range(end_header_token.tokenIndex + 1,
                                                        ctx.statement().start.tokenIndex - 1) \
                if end_header_token and ctx.statement().start else []
            comment_str = ('\n    ' + '\n    '.join(loop_comments) + '\n') if loop_comments else ' '

            body_sql = self.visit(ctx.statement())
            if loop_guards:
                guards_prefix = "\n".join(loop_guards) + "\n"
                body_sql = guards_prefix + (body_sql or "")
            if body_sql:
                body_sql = body_sql.strip()
                if not body_sql.endswith(';'):
                    body_sql += ';'

            # Indent body_sql properly
            body_lines = body_sql.split('\n')
            indented_body = "\n".join(f"    {line}" if line.strip() else line for line in body_lines)

            return f"FOR {target} IN {select_sql}{comment_str}LOOP\n{indented_body}\nEND LOOP;"

        # Case 3: WHILE condition DO statement
        if ctx.condition():
            self.visit(ctx.condition())
            cond = self.get_raw_text(ctx.condition())
            end_header_token = ctx.condition().stop
            loop_comments = self._get_comments_in_range(end_header_token.tokenIndex + 1,
                                                        ctx.statement().start.tokenIndex - 1) \
                if end_header_token and ctx.statement().start else []
            comment_str = ('\n    ' + '\n    '.join(loop_comments) + '\n') if loop_comments else ' '

            body_sql = self.visit(ctx.statement())
            if body_sql:
                body_sql = body_sql.strip()
                if not body_sql.endswith(';'):
                    body_sql += ';'
            body_lines = body_sql.split('\n')
            indented_body = "\n".join(f"    {line}" if line.strip() else line for line in body_lines)
            return f"WHILE {cond}{comment_str}LOOP\n{indented_body}\nEND LOOP;"

        return self.get_raw_text(ctx)

    def get_text_without_node(self, parent_ctx, exclude_ctx):
        if exclude_ctx is None:
            return self.get_raw_text(parent_ctx)
        if self.rewriter and hasattr(parent_ctx, 'start') and hasattr(parent_ctx, 'stop'):
            before = self.rewriter.getText(
                TokenStreamRewriter.DEFAULT_PROGRAM_NAME,
                parent_ctx.start.tokenIndex,
                exclude_ctx.start.tokenIndex - 1
            )
            after = self.rewriter.getText(
                TokenStreamRewriter.DEFAULT_PROGRAM_NAME,
                exclude_ctx.stop.tokenIndex + 1,
                parent_ctx.stop.tokenIndex
            )
            return before + after
        stream = parent_ctx.start.getInputStream()
        before = stream.getText(parent_ctx.start.start, exclude_ctx.start.start - 1)
        after = stream.getText(exclude_ctx.stop.stop + 1, parent_ctx.stop.stop)
        return before + after
