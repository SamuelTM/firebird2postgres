import unittest
from transpiler import FirebirdToPostgresVisitor


class TestTranspilerViews(unittest.TestCase):
    def test_simple_view_transpilation(self):
        fb_sql = """
        CREATE OR ALTER VIEW VW_CLIENTES_ATIVOS (ID, NOME) AS
        SELECT C.ID, C.NOME FROM CLIENTES C WHERE C.ATIVO = 1;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn('DROP VIEW IF EXISTS "VW_CLIENTES_ATIVOS" CASCADE;', pg_sql)
        self.assertIn('CREATE VIEW "VW_CLIENTES_ATIVOS" (ID, NOME) AS SELECT', pg_sql)
        self.assertIn('FROM CLIENTES C', pg_sql)

    def test_view_with_joins(self):
        fb_sql = """
        CREATE OR ALTER VIEW VW_PEDIDOS_CLIENTES AS
        SELECT P.ID, P.DATA_PEDIDO, C.NOME 
        FROM PEDIDOS P 
        JOIN CLIENTES C ON P.CLIENTE_ID = C.ID;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn('DROP VIEW IF EXISTS "VW_PEDIDOS_CLIENTES" CASCADE;', pg_sql)
        self.assertIn('CREATE VIEW "VW_PEDIDOS_CLIENTES" AS SELECT', pg_sql)
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
        self.assertIn('DROP VIEW IF EXISTS "VW_RESUMO_FINANCEIRO" CASCADE;', pg_sql)
        self.assertIn('CREATE VIEW "VW_RESUMO_FINANCEIRO" AS SELECT', pg_sql)
        self.assertIn('LEFT JOIN PEDIDOS P', pg_sql)
