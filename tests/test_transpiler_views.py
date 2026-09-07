import unittest
from transpiler import FirebirdToPostgresVisitor


class TestTranspilerViews(unittest.TestCase):
    def test_simple_view_transpilation(self):
        fb_sql = """
        CREATE OR ALTER VIEW VW_CLIENTES_ATIVOS (ID, NOME) AS
        SELECT C.ID, C.NOME FROM CLIENTES C WHERE C.ATIVO = 1;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn('DROP VIEW IF EXISTS "vw_clientes_ativos" CASCADE;', pg_sql)
        self.assertIn('CREATE VIEW "vw_clientes_ativos" ("id", "nome") AS SELECT', pg_sql)
        self.assertIn('FROM CLIENTES C', pg_sql)

    def test_view_with_joins(self):
        fb_sql = """
        CREATE OR ALTER VIEW VW_PEDIDOS_CLIENTES AS
        SELECT P.ID, P.DATA_PEDIDO, C.NOME 
        FROM PEDIDOS P 
        JOIN CLIENTES C ON P.CLIENTE_ID = C.ID;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn('DROP VIEW IF EXISTS "vw_pedidos_clientes" CASCADE;', pg_sql)
        self.assertIn('CREATE VIEW "vw_pedidos_clientes" AS SELECT', pg_sql)
        self.assertIn('JOIN CLIENTES C', pg_sql)

    def test_view_with_column_expressions_and_aliases(self):
        fb_sql = """
        CREATE OR ALTER VIEW VW_RESUMO_FINANCEIRO AS
        SELECT C.ID AS CLIENTE_ID, UPPER(C.NOME) AS NOME_UPPER, COALESCE(SUM(P.VALOR), 0) AS TOTAL_GASTO
        FROM CLIENTES C
        LEFT JOIN PEDIDOS P ON P.CLIENTE_ID = C.ID
        GROUP BY C.ID, C.NOME;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn('DROP VIEW IF EXISTS "vw_resumo_financeiro" CASCADE;', pg_sql)
        self.assertIn('CREATE VIEW "vw_resumo_financeiro" AS SELECT', pg_sql)
        self.assertIn('LEFT JOIN PEDIDOS P', pg_sql)

    def test_chained_views_with_unquoted_and_quoted_references(self):
        fb_sql = """
        CREATE VIEW "V_BASE" ("ID") AS SELECT ID FROM T;
        CREATE VIEW "V_CHILD" ("ID") AS SELECT ID FROM V_BASE;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn('DROP VIEW IF EXISTS "v_base" CASCADE;', pg_sql)
        self.assertIn('CREATE VIEW "v_base" ("id") AS SELECT ID FROM T;', pg_sql)
        self.assertIn('DROP VIEW IF EXISTS "v_child" CASCADE;', pg_sql)
        self.assertIn('CREATE VIEW "v_child" ("id") AS SELECT ID FROM V_BASE;', pg_sql)

    def test_view_with_quoted_identifiers_in_select_body(self):
        fb_sql = """
        CREATE VIEW "V_BASE" ("ID") AS SELECT "ID" FROM "T";
        CREATE VIEW "V_CHILD" ("ID") AS SELECT "ID" FROM "V_BASE";
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn('DROP VIEW IF EXISTS "v_base" CASCADE;', pg_sql)
        self.assertIn('CREATE VIEW "v_base" ("id") AS SELECT "id" FROM "t";', pg_sql)
        self.assertIn('DROP VIEW IF EXISTS "v_child" CASCADE;', pg_sql)
        self.assertIn('CREATE VIEW "v_child" ("id") AS SELECT "id" FROM "v_base";', pg_sql)

    def test_view_with_columns_containing_spaces_and_keywords(self):
        fb_sql = '''
        CREATE OR ALTER VIEW "V_ORDERS" ("Order Total", "SELECT", "Col ""Special""") AS
        SELECT total, sel, col FROM orders;
        '''
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn('DROP VIEW IF EXISTS "v_orders" CASCADE;', pg_sql)
        self.assertIn('CREATE VIEW "v_orders" ("order total", "select", "col ""special""") AS SELECT', pg_sql)

    def test_dateadd_timestamp_precedence_in_coalesce(self):
        expr = "DATEADD(DAY, 1, COALESCE(CAST(NULL AS DATE), TIMESTAMP '2020-01-01 12:00:00'))"
        res = FirebirdToPostgresVisitor.transpile_expression(expr)
        self.assertNotIn("::date", res)
        self.assertIn("INTERVAL '1 day'", res)

    def test_view_transpilation_propagates_column_symbols(self):
        fb_sql = "CREATE VIEW V AS SELECT DATEADD(DAY, 1, D) - D AS DIFF FROM T;"
        symbols = {"d": "DATE", "t.d": "DATE"}
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql, symbols=symbols)
        self.assertIn("((T.D + (1) * INTERVAL '1 day')::date) - T.D", pg_sql)


