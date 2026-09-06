import logging
import os
import re
import sys

# Ensure the firebird_grammar directory is in the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'firebird_grammar'))

from typing import TypeVar
from antlr4 import InputStream, CommonTokenStream, ParserRuleContext
from antlr4.atn.PredictionMode import PredictionMode
from antlr4.error.ErrorListener import ErrorListener
from antlr4.error.ErrorStrategy import BailErrorStrategy, DefaultErrorStrategy
from antlr4.error.Errors import ParseCancellationException, RecognitionException
from antlr4.TokenStreamRewriter import TokenStreamRewriter

from .firebird_grammar import FirebirdParserVisitor, FirebirdParser, FirebirdLexer
from models import pg_quote_ident

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
    no_comments = _STRIP_COMMENTS_PRESERVING_STRINGS.sub(lambda m: m.group(1) if m.group(1) else " ", expr)
    m_cast = _CAST_DYNAMIC_DATE_PATTERN.search(no_comments)
    if m_cast:
        raise ValueError(
            f"Non-immutable date cast '{m_cast.group(0)}' in {context}: '{expr}' "
            f"is not permitted in PostgreSQL (generated columns and expression indexes must be IMMUTABLE)."
        )

    clean_expr = _STRIP_SQL_LITERALS_AND_COMMENTS.sub(" ", no_comments)
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


def _is_time_type(type_str: str) -> bool:
    if not type_str:
        return False
    u = type_str.strip().upper()
    return ('TIME' in u) and ('TIMESTAMP' not in u)


def _is_time_expr(expr: str, symbols: dict[str, str] = None) -> bool:
    s = expr.strip().strip("()").strip()
    upper = s.upper()
    if (
        upper.startswith("TIME ")
        or upper.startswith("TIME'")
        or upper in ("CURRENT_TIME", "LOCALTIME")
        or bool(re.search(r'\bAS\s+TIME\b', upper))
    ):
        return True

    if symbols:
        clean = s.lstrip(':').strip('"').lower()
        if _is_time_type(symbols.get(clean, '')):
            return True
        if '.' in clean:
            col_part = clean.split('.')[-1].strip('"')
            if _is_time_type(symbols.get(col_part, '')) or _is_time_type(symbols.get(clean, '')):
                return True

    return False


class ASTDialectRewriter(FirebirdParserVisitor):
    """
    Pass 1 Visitor: Operates on AST nodes and rewrites tokens directly in the TokenStreamRewriter.
    This guarantees that dialect transformations (bind variables, sequence functions, procedure calls,
    exception statements, limit/offset clauses, leave statements, and RDB$DATABASE removals)
    are performed in semantic context, leaving string literals and comments 100% untouched.
    """

    def __init__(self, rewriter: TokenStreamRewriter, symbols: dict[str, str] = None):
        super().__init__()
        self.rewriter = rewriter
        self.handled_qbs = set()
        self.symbols: dict[str, str] = {k.strip('":').lower(): v.upper() for k, v in symbols.items()} if symbols else {}

    def visitCreate_procedure_body(self, ctx: FirebirdParser.Create_procedure_bodyContext):
        old_symbols = self.symbols.copy()
        try:
            return self.visitChildren(ctx)
        finally:
            self.symbols = old_symbols

    def visitCreate_trigger(self, ctx: FirebirdParser.Create_triggerContext):
        old_symbols = self.symbols.copy()
        try:
            return self.visitChildren(ctx)
        finally:
            self.symbols = old_symbols

    def visitParameter(self, ctx: FirebirdParser.ParameterContext):
        if ctx.parameter_name() and ctx.type_spec():
            name = ctx.parameter_name().getText().strip('":').lower()
            self.symbols[name] = ctx.type_spec().getText().upper()
        return self.visitChildren(ctx)

    def visitVariable_declaration(self, ctx: FirebirdParser.Variable_declarationContext):
        if ctx.identifier() and ctx.type_spec():
            name = ctx.identifier().getText().strip('":').lower()
            self.symbols[name] = ctx.type_spec().getText().upper()
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
            self.rewriter.replaceRangeTokens(ctx.start, ctx.stop, raw.lstrip(':'))
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
            clean_seq = raw_seq.strip('\'"').lower()
            quoted_seq = pg_quote_ident(clean_seq)
            step = args[1].getText().strip()
            if step == '1':
                if raw_seq.startswith('"') and raw_seq.endswith('"'):
                    seq_target = quoted_seq.replace("'", "''")
                else:
                    seq_target = raw_seq.replace("'", "''")
                self.rewriter.replaceRangeTokens(ctx.start, ctx.stop, f"nextval('{seq_target}')")
            elif step == '0':
                self.rewriter.replaceRangeTokens(
                    ctx.start, ctx.stop,
                    f"(SELECT CASE WHEN is_called THEN last_value ELSE last_value - 1 END FROM {quoted_seq})"
                )
            else:
                raise ValueError(
                    f"Unsupported GEN_ID step '{step}' for sequence '{clean_seq}'. "
                    f"PostgreSQL sequences only support atomic step 1 (nextval) and step 0 (current state inspection)."
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

    def visitUnary_expression(self, ctx: FirebirdParser.Unary_expressionContext):
        raw = ctx.getText().upper()
        if 'NEXTVALUEFOR' in raw and ctx.identifier():
            seq_name = ctx.identifier().getText()
            self.rewriter.replaceRangeTokens(ctx.start, ctx.stop, f"nextval('{seq_name}')")
        return self.visitChildren(ctx)

    def visitCall_statement(self, ctx: FirebirdParser.Call_statementContext):
        raw = ctx.getText().upper()
        if raw.startswith('EXECUTEPROCEDURE') and ctx.routine_name():
            routine = ctx.routine_name(0).getText()
            self.rewriter.replaceRangeTokens(ctx.start, ctx.routine_name(0).stop, f"PERFORM {routine}")
        return self.visitChildren(ctx)

    def visitExit_statement(self, ctx: FirebirdParser.Exit_statementContext):
        if ctx.getChild(0).getText().upper() == 'LEAVE':
            self.rewriter.replaceRangeTokens(ctx.start, ctx.start, 'EXIT')
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
        if qb and qb.FIRST() and id(qb) not in self.handled_qbs:
            self.handled_qbs.add(id(qb))
            first_val = qb.numeric(0).getText()
            skip_val = qb.numeric(1).getText() if qb.SKIP_() else None
            end_token = qb.numeric(1).stop if qb.SKIP_() else qb.numeric(0).stop
            self.rewriter.replaceRangeTokens(qb.FIRST().symbol, end_token, '')
            limit_clause = f' LIMIT {first_val}' + (f' OFFSET {skip_val}' if skip_val else '')

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


class FirebirdToPostgresVisitor(FirebirdParserVisitor):
    """
    Visitor that traverses the Firebird AST and translates it into PostgreSQL PL/pgSQL code.
    """

    def __init__(self, rewriter: TokenStreamRewriter = None):
        super().__init__()
        self.rewriter = rewriter

    @classmethod
    def _normalize_sql(cls, sql: str) -> str:
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
        return _normalize_date_funcs(sql)

    @classmethod
    def transpile(cls, firebird_sql_string: str, symbols: dict[str, str] = None) -> str:
        """
        Parses Firebird SQL using Two-Stage Parsing (SLL -> LL), traverses the AST with the visitor,
        and applies dialect token rewriting to produce clean PostgreSQL SQL.
        """
        normalized_sql = cls._normalize_sql(firebird_sql_string)

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
        dialect_rewriter = ASTDialectRewriter(rewriter, symbols=symbols)
        dialect_rewriter.visit(tree)

        # Pass 2: High-level PL/pgSQL structure visitor
        visitor = cls(rewriter=rewriter)
        pg_sql = visitor.visit(tree)

        if pg_sql:
            pg_sql = cls._clean_sql(pg_sql)

        return pg_sql

    @classmethod
    def transpile_expression(cls, expr: str, symbols: dict[str, str] = None) -> str:
        """
        Transpiles a standalone Firebird SQL scalar expression (e.g. computed column, expression index)
        to PostgreSQL SQL, rewriting built-ins like IIF, DATEADD, DATEDIFF, LIST, GEN_ID.
        """
        if not expr:
            return ""
        expr_clean = expr.strip()
        dummy_sql = f'CREATE VIEW "__v__" AS SELECT {expr_clean} FROM RDB$DATABASE;'
        try:
            view_sql = cls.transpile(dummy_sql, symbols=symbols)
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

        # Step 2: Strip protective double-quotes on trigger pseudo-records
        pg_sql = re.sub(r'"(old|new)"\.', r'\1.', pg_sql, flags=re.IGNORECASE)
        return pg_sql

    def visitSql_script(self, ctx: FirebirdParser.Sql_scriptContext):
        statements = []
        for child in ctx.children:
            result = self.visit(child)
            if result:
                statements.append(result)
        return "\n\n".join(statements)

    @staticmethod
    def _convert_type(raw_type: str) -> str:
        if not raw_type:
            return ""
        cleaned = re.sub(r'(?i)\bBLOB\s+SUBTYPE\s+(?:1|TEXT)\b', 'TEXT', raw_type)
        cleaned = re.sub(r'(?i)\bBLOB\s+SUBTYPE\s+(?:0|BINARY)\b', 'BYTEA', cleaned)
        cleaned = re.sub(r'(?i)\bBLOB\b', 'BYTEA', cleaned)
        return cleaned

    def visitUnit_statement(self, ctx: FirebirdParser.Unit_statementContext):
        return self.visitChildren(ctx)

    def visitCreate_procedure_body(self, ctx: FirebirdParser.Create_procedure_bodyContext):
        proc_name = ctx.procedure_name().getText().strip('"')

        # In PostgreSQL, we translate procedures to functions
        has_returns = False
        in_params = []
        out_params = []
        out_types = []
        for child in ctx.children:
            if hasattr(child, 'getText') and child.getText().upper() == 'RETURNS':
                has_returns = True
            elif isinstance(child, FirebirdParser.ParameterContext):
                param_str = self.visit(child)
                type_spec = self._convert_type(self.get_raw_text(child.type_spec())) if child.type_spec() else "TEXT"
                if has_returns:
                    out_params.append(f"OUT {param_str}")
                    out_types.append(type_spec)
                else:
                    in_params.append(param_str)

        all_params = in_params + out_params
        params_str = ", ".join(all_params)

        # Declarations
        decl_str = ""
        if ctx.seq_of_declare_specs():
            decl_str = self.visit(ctx.seq_of_declare_specs())
            if decl_str:
                decl_str = f"DECLARE\n{decl_str}\n"

        # Translate the body
        body_str = self.visit(ctx.body()) if ctx.body() else ""

        # Determine correct return type for PostgreSQL
        has_return_next = "RETURN NEXT" in body_str or "suspend" in body_str.lower()
        if not out_params:
            return_type = "RETURNS void"
            # In void functions, SUSPEND / RETURN NEXT must be a plain RETURN;
            body_str = re.sub(r'\bRETURN\s+NEXT\b\s*;?', 'RETURN;', body_str)
        elif len(out_params) == 1:
            return_type = f"RETURNS SETOF {out_types[0]}" if has_return_next else f"RETURNS {out_types[0]}"
        else:
            return_type = "RETURNS SETOF record" if has_return_next else "RETURNS record"

        # DROP first to guarantee idempotency, since changing an existing function's
        # signature (parameter types or return type) requires recreating it
        return (f'DROP FUNCTION IF EXISTS "{proc_name.lower()}" CASCADE;\n'
                f'CREATE FUNCTION "{proc_name.lower()}"({params_str}) {return_type} AS $$\n{decl_str}{body_str}\n'
                f'$$ LANGUAGE plpgsql;')

    def visitParameter(self, ctx: FirebirdParser.ParameterContext):
        param_name = ctx.parameter_name().getText()
        # Firebird allows datatype directly or TYPE OF
        # Extract the raw tokens for the type to preserve spaces (e.g. VARCHAR(255))
        type_spec = ""
        if ctx.type_spec():
            type_spec = self._convert_type(self.get_raw_text(ctx.type_spec()))
        return f"{param_name} {type_spec}".strip()

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

        func_sql = f'CREATE OR REPLACE FUNCTION "{func_name}"() RETURNS TRIGGER AS $$\n{body_str}\n$$ LANGUAGE plpgsql;'
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

        inner_code = "\n".join(f"    {s}" for s in items)
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
                FirebirdParser.If_statementContext,
                FirebirdParser.Loop_statementContext
        )):
            return self.visit(child)

        # Singleton SELECT ... INTO statements are wrapped in BEGIN ... EXCEPTION WHEN NO_DATA_FOUND THEN NULL; END;
        # to match Firebird PSQL semantics (preserving target variable values when no rows are found).
        # We omit this wrapper when the query is guaranteed to return exactly one row (e.g. constant/scalar
        # queries without FROM, or pure aggregates without GROUP BY) to eliminate subtransaction overhead.
        into_ctx = _find_node(ctx, FirebirdParser.Into_clauseContext)
        select_ctx = _find_node(ctx, FirebirdParser.Select_statementContext)
        if into_ctx and select_ctx and not self._guarantees_single_row(select_ctx):
            raw_stmt = self.get_raw_text(ctx).strip()
            if not raw_stmt.endswith(';'):
                raw_stmt += ';'
            stmt_lines = [f"    {line}" for line in raw_stmt.split('\n')]
            indented_stmt = "\n".join(stmt_lines)
            return f"BEGIN\n{indented_stmt}\nEXCEPTION WHEN NO_DATA_FOUND THEN\n    NULL;\nEND;"

        # For all other SQL statements (UPDATE, DELETE, EXECUTE, plain SELECT, etc.)
        # we just return their rewritten text.
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
        var_name = ctx.identifier().getText()
        type_spec = self._convert_type(self.get_raw_text(ctx.type_spec()))
        return f"    {var_name} {type_spec};"

    def visitAssignment_statement(self, ctx: FirebirdParser.Assignment_statementContext):
        left = self.get_raw_text(ctx.getChild(0)).lstrip(':')
        if ctx.expression():
            self.visit(ctx.expression())
        right = self.get_raw_text(ctx.expression())
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

            end_header_token = ctx.select_statement().stop
            loop_comments = self._get_comments_in_range(end_header_token.tokenIndex + 1,
                                                        ctx.statement().start.tokenIndex - 1) \
                if end_header_token and ctx.statement().start else []
            comment_str = ('\n    ' + '\n    '.join(loop_comments) + '\n') if loop_comments else ' '

            body_sql = self.visit(ctx.statement())
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
