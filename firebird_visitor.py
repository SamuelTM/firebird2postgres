import os
import re
import sys

# Ensure the firebird_grammar directory is in the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'firebird_grammar'))

from antlr4 import InputStream, CommonTokenStream
from antlr4.atn.PredictionMode import PredictionMode
from antlr4.error.ErrorStrategy import BailErrorStrategy, DefaultErrorStrategy
from antlr4.error.Errors import ParseCancellationException, RecognitionException
from antlr4.TokenStreamRewriter import TokenStreamRewriter

from firebird_grammar.FirebirdParserVisitor import FirebirdParserVisitor
# noinspection PyUnresolvedReferences
from firebird_grammar.FirebirdParser import FirebirdParser
from firebird_grammar.FirebirdLexer import FirebirdLexer


class ASTDialectRewriter(FirebirdParserVisitor):
    """
    Pass 1 Visitor: Operates on AST nodes and rewrites tokens directly in the TokenStreamRewriter.
    This guarantees that dialect transformations (bind variables, sequence functions, procedure calls,
    exception statements, limit/offset clauses, leave statements, and RDB$DATABASE removals)
    are performed in semantic context, leaving string literals and comments 100% untouched.
    """

    def __init__(self, rewriter: TokenStreamRewriter):
        super().__init__()
        self.rewriter = rewriter
        self.handled_qbs = set()

    def visitBind_variable(self, ctx: FirebirdParser.Bind_variableContext):
        raw = ctx.getText()
        if raw.startswith(':'):
            self.rewriter.replaceRangeTokens(ctx.start, ctx.stop, f" {raw.lstrip(':')}")
        return self.visitChildren(ctx)

    def visitTableview_name(self, ctx: FirebirdParser.Tableview_nameContext):
        # In CREATE VIEW context, quote table names in uppercase on the AST token stream
        curr = ctx
        is_in_view = False
        while curr:
            if isinstance(curr, FirebirdParser.Create_viewContext):
                is_in_view = True
                break
            curr = getattr(curr, 'parentCtx', None)

        if is_in_view:
            text = ctx.getText()
            if not (text.startswith('"') and text.endswith('"')):
                self.rewriter.replaceRangeTokens(ctx.start, ctx.stop, f'"{text.upper()}"')

        return self.visitChildren(ctx)

    def visitGeneral_element_part(self, ctx: FirebirdParser.General_element_partContext):
        if ctx.id_expression() and ctx.id_expression().getText().upper() == 'GEN_ID':
            if ctx.function_argument():
                func_arg = ctx.function_argument(0)
                if hasattr(func_arg, 'argument'):
                    args = func_arg.argument()
                    if len(args) >= 2:
                        seq_name = args[0].getText()
                        step = args[1].getText().strip()
                        if step == '1':
                            self.rewriter.replaceRangeTokens(ctx.start, ctx.stop, f"nextval('{seq_name}')")
                        elif step == '0':
                            self.rewriter.replaceRangeTokens(ctx.start, ctx.stop, f"currval('{seq_name}')")
                        else:
                            self.rewriter.replaceRangeTokens(
                                ctx.start, ctx.stop, f"setval('{seq_name}', nextval('{seq_name}') + ({step}) - 1)"
                            )
            return self.visitChildren(ctx)

        # In CREATE VIEW context, quote table.column references in uppercase on the AST token stream
        curr = ctx
        is_in_view = False
        while curr:
            if isinstance(curr, FirebirdParser.Create_viewContext):
                is_in_view = True
                break
            curr = getattr(curr, 'parentCtx', None)

        if is_in_view:
            text = ctx.getText()
            if not (text.startswith('"') and text.endswith('"')):
                self.rewriter.replaceRangeTokens(ctx.start, ctx.stop, f'"{text.upper()}"')

        return self.visitChildren(ctx)

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

    def _rewrite_first_skip(self, ctx):
        """
        Extracts FIRST n [SKIP m] tokens from the query block and relocates them
        as LIMIT n [OFFSET m] to the end of the enclosing select_statement or subquery.
        """
        qb = self.find_query_block(ctx)
        if qb and qb.FIRST() and id(qb) not in self.handled_qbs:
            self.handled_qbs.add(id(qb))
            first_val = qb.numeric(0).getText()
            skip_val = qb.numeric(1).getText() if qb.SKIP_() else None
            end_token = qb.numeric(1).stop if qb.SKIP_() else qb.numeric(0).stop
            self.rewriter.replaceRangeTokens(qb.FIRST().symbol, end_token, '')
            limit_clause = f' LIMIT {first_val}' + (f' OFFSET {skip_val}' if skip_val else '')
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

    def find_query_block(self, ctx):
        if isinstance(ctx, FirebirdParser.Query_blockContext):
            return ctx
        if hasattr(ctx, 'children') and ctx.children:
            for child in ctx.children:
                res = self.find_query_block(child)
                if res:
                    return res
        return None

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


class FirebirdToPostgresVisitor(FirebirdParserVisitor):
    """
    Visitor that traverses the Firebird AST and translates it into PostgreSQL PL/pgSQL code.
    """

    def __init__(self, rewriter: TokenStreamRewriter = None):
        super().__init__()
        self.rewriter = rewriter

    @classmethod
    def _normalize_trigger_records(cls, sql: str) -> str:
        """
        Pre-parse normalization:
        In the Firebird grammar, 'old' and 'new' are reserved keywords in unquoted context.
        When followed by a dot (e.g. 'old.field'), the lexer splits them unless quoted.
        This function temporarily wraps record names in double quotes ("old".field),
        while ensuring string literals ('...') and comments (-- ... / /* ... */) remain 100% untouched.
        These temporary quotes are cleanly stripped in `_clean_sql` after parsing.
        """
        pattern = re.compile(
            r"('(?:''|[^'])*'|/\*.*?\*/|--[^\n]*)|"  # Group 1: string literals and comments (preserve untouched)
            r"(\b(old|new)\.;?\s*\n\s*([a-zA-Z0-9_]+)\b)|"  # Group 2, 3, 4: split 'old.; \n col' recovery
            r"(\b(old|new)\.([a-zA-Z0-9_]+)\b)",  # Group 5, 6, 7: unquoted 'old.col'
            flags=re.IGNORECASE | re.DOTALL
        )

        def repl(match):
            if match.group(1):
                return match.group(1)
            if match.group(2):
                rec = re.split(r'[.;\s]', match.group(2))[0]
                return f'"{rec}".{match.group(4)}'
            if match.group(5):
                return f'"{match.group(6)}".{match.group(7)}'
            return match.group(0)

        return pattern.sub(repl, sql)

    @classmethod
    def transpile(cls, firebird_sql_string: str) -> str:
        """
        Parses Firebird SQL using Two-Stage Parsing (SLL -> LL), traverses the AST with the visitor,
        and applies dialect token rewriting to produce clean PostgreSQL SQL.
        """
        normalized_sql = cls._normalize_trigger_records(firebird_sql_string)

        lexer = FirebirdLexer(InputStream(normalized_sql))
        stream = CommonTokenStream(lexer)
        parser = FirebirdParser(stream)

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
        if syntax_errors > 0:
            raise ParseCancellationException(
                f"Syntax error during parsing: {syntax_errors} errors encountered in Firebird SQL script."
            )

        rewriter = TokenStreamRewriter(stream)

        # Pass 1: Semantic token rewriting on AST
        dialect_rewriter = ASTDialectRewriter(rewriter)
        dialect_rewriter.visit(tree)

        # Pass 2: High-level PL/pgSQL structure visitor
        visitor = cls(rewriter=rewriter)
        pg_sql = visitor.visit(tree)

        if pg_sql:
            pg_sql = cls._clean_sql(pg_sql)

        return pg_sql

    @staticmethod
    def _clean_sql(pg_sql: str) -> str:
        """
        Post-transpilation cleanup:
        Strips the temporary protective double-quotes on trigger pseudo-records
        ("old".col / "new".col -> old.col / new.col) that were injected prior to parsing
        to prevent Firebird lexer keyword collision. In PL/pgSQL, OLD/NEW are unquoted records.
        """
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

        return (f'CREATE OR REPLACE FUNCTION "{proc_name}"({params_str}) {return_type} AS $$\n{decl_str}{body_str}\n'
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
            if "DELETE" in events_upper and "INSERT" not in events_upper and "UPDATE" not in events_upper:
                return_stmt = "RETURN OLD;"
            else:
                return_stmt = "RETURN NEW;"
        else:
            return_stmt = "RETURN NULL;"

        if body_str:
            if body_str.rstrip().endswith("END;"):
                idx = body_str.rstrip().rfind("END;")
                body_str = f"{body_str[:idx]}    {return_stmt}\nEND;"
            else:
                body_str = f"{body_str}\n    {return_stmt}"

        # Postgres uses a function for the trigger body, and then CREATE TRIGGER
        func_name = f"{trigger_name}_func"

        func_sql = f'CREATE OR REPLACE FUNCTION "{func_name}"() RETURNS TRIGGER AS $$\n{body_str}\n$$ LANGUAGE plpgsql;'
        trigger_sql = (f'CREATE TRIGGER "{trigger_name}" {timing} {events} ON "{table_name}" '
                       f'FOR EACH ROW EXECUTE FUNCTION "{func_name}"();')

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

    def visitTrigger_block(self, ctx: FirebirdParser.Trigger_blockContext):
        decl_str = ""
        if ctx.declare_spec():
            decl_items = []
            curr_token_idx = ctx.declare_spec(0).start.tokenIndex if ctx.declare_spec(0).start else 0
            for d in ctx.declare_spec():
                if d.start:
                    pre_comments = self._get_comments_in_range(curr_token_idx, d.start.tokenIndex - 1)
                    for c in pre_comments:
                        decl_items.append(f"    {c}")
                res = self.visit(d)
                if res:
                    decl_items.append(res)
                if d.stop:
                    curr_token_idx = d.stop.tokenIndex + 1
            if decl_items:
                decl_str = "DECLARE\n" + "\n".join(decl_items) + "\n"
        body_str = self.visit(ctx.body()) if ctx.body() else ""
        return f"{decl_str}{body_str}"

    def visitCreate_view(self, ctx: FirebirdParser.Create_viewContext):
        view_name = ctx.id_expression(0).getText().strip('"')
        select_stmt = self.get_raw_text(ctx.select_only_statement())

        view_opts = ""
        if ctx.view_options():
            view_opts = self.get_raw_text(ctx.view_options())
            view_opts = f" {view_opts}"

        return f'CREATE OR REPLACE VIEW "{view_name}"{view_opts} AS {select_stmt};'

    def visitBody(self, ctx: FirebirdParser.BodyContext):
        # A body is usually BEGIN ... END
        items = []
        stmt_contexts = []
        if ctx.seq_of_statements() and ctx.seq_of_statements().children:
            for child in ctx.seq_of_statements().children:
                if isinstance(child, FirebirdParser.StatementContext):
                    stmt_contexts.append(child)

        start_token_idx = ctx.start.tokenIndex + 1 if ctx.start else 0
        stop_token_idx = ctx.stop.tokenIndex - 1 if ctx.stop else 0
        curr_token_idx = start_token_idx

        for stmt_ctx in stmt_contexts:
            if stmt_ctx.start:
                pre_comments = self._get_comments_in_range(curr_token_idx, stmt_ctx.start.tokenIndex - 1)
                items.extend(pre_comments)

            stmt_str = self.visit(stmt_ctx)
            if stmt_str:
                stmt_str = stmt_str.strip()
                if not stmt_str.endswith(';'):
                    stmt_str += ';'
                items.append(stmt_str)

            if stmt_ctx.stop:
                curr_token_idx = stmt_ctx.stop.tokenIndex + 1

        trailing_comments = self._get_comments_in_range(curr_token_idx, stop_token_idx)
        items.extend(trailing_comments)

        inner_code = "\n".join(f"    {s}" for s in items)
        return f"BEGIN\n{inner_code}\nEND;"

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

        # For all other SQL statements (SELECT, UPDATE, DELETE, EXECUTE, etc.)
        # we just return their rewritten text.
        return self.get_raw_text(ctx)

    def visitBlock(self, ctx: FirebirdParser.BlockContext):
        decl_str = ""
        if ctx.declare_spec():
            decl_items = []
            curr_token_idx = ctx.declare_spec(0).start.tokenIndex if ctx.declare_spec(0).start else 0
            for d in ctx.declare_spec():
                if d.start:
                    pre_comments = self._get_comments_in_range(curr_token_idx, d.start.tokenIndex - 1)
                    for c in pre_comments:
                        decl_items.append(f"    {c}")
                res = self.visit(d)
                if res:
                    decl_items.append(res)
                if d.stop:
                    curr_token_idx = d.stop.tokenIndex + 1
            if decl_items:
                decl_str = "DECLARE\n" + "\n".join(decl_items) + "\n"
        body_str = self.visit(ctx.body()) if ctx.body() else ""
        return f"{decl_str}{body_str}"

    def visitIf_statement(self, ctx: FirebirdParser.If_statementContext):
        cond = self.get_raw_text(ctx.condition())
        then_stmt = self.visit(ctx.statement(0))
        if then_stmt:
            then_stmt = then_stmt.strip()
            if not then_stmt.endswith(';'):
                then_stmt += ';'

        then_comments = self._get_comments_in_range(ctx.condition().stop.tokenIndex + 1, ctx.statement(0).start.tokenIndex - 1) if ctx.condition().stop and ctx.statement(0).start else []
        then_comment_str = ('\n    ' + '\n    '.join(then_comments) + '\n') if then_comments else ''

        sql = f"IF {cond} THEN{then_comment_str}\n    {then_stmt}\n"

        if len(ctx.statement()) > 1:
            else_comments = self._get_comments_in_range(ctx.statement(0).stop.tokenIndex + 1, ctx.statement(1).start.tokenIndex - 1) if ctx.statement(0).stop and ctx.statement(1).start else []
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
                return self.rewriter.getText(
                    TokenStreamRewriter.DEFAULT_PROGRAM_NAME,
                    ctx.start.tokenIndex,
                    ctx.stop.tokenIndex
                )
            start_idx = ctx.start.start
            stop_idx = ctx.stop.stop
            stream = ctx.start.getInputStream()
            return stream.getText(start_idx, stop_idx)
        return ctx.getText()

    def visitSeq_of_declare_specs(self, ctx: FirebirdParser.Seq_of_declare_specsContext):
        items = []
        decl_children = [c for c in ctx.children if hasattr(c, 'start') and hasattr(c, 'stop')] if ctx.children else []

        start_token_idx = ctx.start.tokenIndex if ctx.start else 0
        stop_token_idx = ctx.stop.tokenIndex if ctx.stop else 0
        curr_token_idx = start_token_idx

        for child in decl_children:
            if child.start:
                pre_comments = self._get_comments_in_range(curr_token_idx, child.start.tokenIndex - 1)
                for c in pre_comments:
                    items.append(f"    {c}")

            decl_str = self.visit(child)
            if decl_str:
                items.append(decl_str)

            if child.stop:
                curr_token_idx = child.stop.tokenIndex + 1

        trailing_comments = self._get_comments_in_range(curr_token_idx, stop_token_idx)
        for c in trailing_comments:
            items.append(f"    {c}")

        return "\n".join(items)

    def visitVariable_declaration(self, ctx: FirebirdParser.Variable_declarationContext):
        var_name = ctx.identifier().getText()
        type_spec = self._convert_type(self.get_raw_text(ctx.type_spec()))
        return f"    {var_name} {type_spec};"

    def visitAssignment_statement(self, ctx: FirebirdParser.Assignment_statementContext):
        left = self.get_raw_text(ctx.getChild(0)).lstrip(':')
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
                        into_vars.append(self.get_raw_text(child).lstrip(':'))

            target = ", ".join(into_vars) if into_vars else "_rec"
            loop_comments = self._get_comments_in_range(end_header_token.tokenIndex + 1, ctx.statement().start.tokenIndex - 1) if end_header_token and ctx.statement().start else []
            comment_str = ('\n    ' + '\n    '.join(loop_comments) + '\n') if loop_comments else ' '

            body_sql = self.visit(ctx.statement())
            body_lines = body_sql.split('\n')
            indented_body = "\n".join(f"    {line}" if line.strip() else line for line in body_lines)
            return f"FOR {target} IN EXECUTE {expr}{comment_str}LOOP\n{indented_body}\nEND LOOP;"

        # Case 2: FOR select_statement DO statement
        if ctx.select_statement():
            into_ctx = self.find_node(ctx.select_statement(), FirebirdParser.Into_clauseContext)

            into_vars = []
            if into_ctx:
                for child in into_ctx.children:
                    if isinstance(child, (FirebirdParser.General_elementContext, FirebirdParser.Bind_variableContext)):
                        into_vars.append(self.get_raw_text(child).lstrip(':'))

            select_sql = self.get_text_without_node(ctx.select_statement(), into_ctx).strip()
            target = ", ".join(into_vars) if into_vars else "_rec"

            end_header_token = ctx.select_statement().stop
            loop_comments = self._get_comments_in_range(end_header_token.tokenIndex + 1, ctx.statement().start.tokenIndex - 1) if end_header_token and ctx.statement().start else []
            comment_str = ('\n    ' + '\n    '.join(loop_comments) + '\n') if loop_comments else ' '

            body_sql = self.visit(ctx.statement())

            # Indent body_sql properly
            body_lines = body_sql.split('\n')
            indented_body = "\n".join(f"    {line}" if line.strip() else line for line in body_lines)

            return f"FOR {target} IN {select_sql}{comment_str}LOOP\n{indented_body}\nEND LOOP;"

        # Case 3: WHILE condition DO statement
        if ctx.condition():
            cond = self.get_raw_text(ctx.condition())
            end_header_token = ctx.condition().stop
            loop_comments = self._get_comments_in_range(end_header_token.tokenIndex + 1, ctx.statement().start.tokenIndex - 1) if end_header_token and ctx.statement().start else []
            comment_str = ('\n    ' + '\n    '.join(loop_comments) + '\n') if loop_comments else ' '

            body_sql = self.visit(ctx.statement())
            body_lines = body_sql.split('\n')
            indented_body = "\n".join(f"    {line}" if line.strip() else line for line in body_lines)
            return f"WHILE {cond}{comment_str}LOOP\n{indented_body}\nEND LOOP;"

        return self.get_raw_text(ctx)

    def find_node(self, ctx, node_type):
        if isinstance(ctx, node_type):
            return ctx
        if hasattr(ctx, 'children') and ctx.children:
            for child in ctx.children:
                res = self.find_node(child, node_type)
                if res:
                    return res
        return None

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
