import sys
import os

# Ensure the firebird_grammar directory is in the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'firebird_grammar'))

from firebird_grammar.FirebirdParserVisitor import FirebirdParserVisitor
from firebird_grammar.FirebirdParser import FirebirdParser


class FirebirdToPostgresVisitor(FirebirdParserVisitor):
    """
    Visitor that traverses the Firebird AST and translates it into PostgreSQL PL/pgSQL code.
    """

    def visitSql_script(self, ctx: FirebirdParser.Sql_scriptContext):
        statements = []
        for child in ctx.children:
            result = self.visit(child)
            if result:
                statements.append(result)
        return "\n\n".join(statements)

    def visitUnit_statement(self, ctx: FirebirdParser.Unit_statementContext):
        return self.visitChildren(ctx)

    def visitCreate_procedure_body(self, ctx: FirebirdParser.Create_procedure_bodyContext):
        proc_name = ctx.procedure_name().getText()

        has_returns = False
        in_params = []
        out_params = []
        for child in ctx.children:
            if hasattr(child, 'getText') and child.getText().upper() == 'RETURNS':
                has_returns = True
            elif isinstance(child, FirebirdParser.ParameterContext):
                param_str = self.visit(child)
                if has_returns:
                    out_params.append(f"OUT {param_str}")
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

        return (f"CREATE OR REPLACE FUNCTION {proc_name}({params_str}) RETURNS void AS $$\n{decl_str}{body_str}\n"
                f"$$ LANGUAGE plpgsql;")

    def visitParameter(self, ctx: FirebirdParser.ParameterContext):
        param_name = ctx.parameter_name().getText()
        # Firebird allows datatype directly or TYPE OF
        # Extract the raw tokens for the type to preserve spaces (e.g. VARCHAR(255))
        type_spec = ""
        if ctx.type_spec():
            type_spec = self.get_raw_text(ctx.type_spec())
        return f"{param_name} {type_spec}".strip()

    def visitCreate_trigger(self, ctx: FirebirdParser.Create_triggerContext):
        trigger_name = ctx.trigger_name().getText()
        # Extract table name and events
        table_name = ctx.tableview_name().getText() if ctx.tableview_name() else "UNKNOWN_TABLE"

        # Simple extraction of timing and events
        simple_dml = ctx.simple_dml_trigger()
        timing = "BEFORE"
        events = "INSERT"
        if simple_dml:
            timing_node = simple_dml.getChild(0)  # BEFORE, AFTER, INSTEAD OF
            timing = timing_node.getText()
            events = self.get_raw_text(simple_dml.dml_event_clause())

        body_str = self.visit(ctx.trigger_body()) if ctx.trigger_body() else ""

        # Postgres uses a function for the trigger body, and then CREATE TRIGGER
        func_name = f"{trigger_name}_func"

        func_sql = f"CREATE OR REPLACE FUNCTION {func_name}() RETURNS TRIGGER AS $$\n{body_str}\n$$ LANGUAGE plpgsql;"
        trigger_sql = f"CREATE TRIGGER {trigger_name} {timing} {events} ON {table_name} FOR EACH ROW EXECUTE FUNCTION {func_name}();"

        return f"{func_sql}\n{trigger_sql}"

    def visitCreate_view(self, ctx: FirebirdParser.Create_viewContext):
        view_name = ctx.id_expression(0).getText()
        # We can extract the select statement raw
        select_stmt = self.get_raw_text(ctx.select_only_statement())
        return f"CREATE OR REPLACE VIEW {view_name} AS {select_stmt};"

    def visitBody(self, ctx: FirebirdParser.BodyContext):
        statements = []
        if ctx.seq_of_statements():
            for stmt in ctx.seq_of_statements().statement():
                stmt_str = self.visit(stmt)
                if stmt_str:
                    statements.append(stmt_str)

        inner_code = "\n".join(f"    {s}" for s in statements)
        return f"BEGIN\n{inner_code}\nEND;"

    @staticmethod
    def get_raw_text(ctx):
        if ctx is None:
            return ""
        if hasattr(ctx, 'start') and hasattr(ctx, 'stop') and ctx.start and ctx.stop:
            start_idx = ctx.start.start
            stop_idx = ctx.stop.stop
            stream = ctx.start.getInputStream()
            return stream.getText(start_idx, stop_idx)
        return ctx.getText()

    def visitSeq_of_declare_specs(self, ctx: FirebirdParser.Seq_of_declare_specsContext):
        declarations = []
        for child in ctx.children:
            decl = self.visit(child)
            if decl:
                declarations.append(decl)
        return "\n".join(declarations)

    def visitVariable_declaration(self, ctx: FirebirdParser.Variable_declarationContext):
        var_name = ctx.identifier().getText()
        type_spec = self.get_raw_text(ctx.type_spec())
        return f"    {var_name} {type_spec};"

    def visitAssignment_statement(self, ctx: FirebirdParser.Assignment_statementContext):
        left = self.get_raw_text(ctx.getChild(0))
        right = self.get_raw_text(ctx.expression())
        return f"{left} := {right};"

    def visitTerminal(self, node):
        return None
