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

    def test_item_e_date_type_inference_with_homonymous_columns(self):
        """
        Item E: Validates that homonymous columns across tables resolve type
        from the correct relation/scope, not from whichever table was stored first.
        Acceptance criteria:
        - Colunas homônimas de tipos diferentes não se sobrescrevem semanticamente.
        - Ordem de leitura do catálogo não altera o SQL gerado.
        - Referências simples, qualificadas e por alias chegam ao mesmo tipo quando apontam à mesma coluna.
        - Expressões mistas preservam seu tipo.
        """
        symbols_a_first = {"a.d": "TIMESTAMP", "b.d": "DATE"}
        symbols_b_first = {"b.d": "DATE", "a.d": "TIMESTAMP"}

        # -------- 1. Qualified refs always resolve to the correct table --------
        fb_view_b = "CREATE VIEW V_B AS SELECT DATEADD(DAY, 1, B.D) AS NEXT_DAY FROM B;"
        pg_b = FirebirdToPostgresVisitor.transpile(fb_view_b, symbols=symbols_a_first)
        self.assertIn("::date)", pg_b, "Qualified B.D (DATE) must produce ::date cast")

        fb_view_a = "CREATE VIEW V_A AS SELECT DATEADD(DAY, 1, A.D) AS NEXT_DT FROM A;"
        pg_a = FirebirdToPostgresVisitor.transpile(fb_view_a, symbols=symbols_a_first)
        self.assertNotIn("::date)", pg_a, "Qualified A.D (TIMESTAMP) must not produce ::date cast")

        # -------- 2. Reversed catalog order must produce identical results --------
        pg_b2 = FirebirdToPostgresVisitor.transpile(fb_view_b, symbols=symbols_b_first)
        self.assertEqual(pg_b, pg_b2, "Reversing symbol order must produce identical SQL for table B")

        pg_a2 = FirebirdToPostgresVisitor.transpile(fb_view_a, symbols=symbols_b_first)
        self.assertEqual(pg_a, pg_a2, "Reversing symbol order must produce identical SQL for table A")

        # -------- 3. Simple (unqualified) refs resolve to queried relation's type --------
        # In a view over B, bare D points to B.D (DATE) -> must produce ::date
        fb_bare_b = "CREATE VIEW V_BARE_B AS SELECT DATEADD(DAY, 1, D) AS R FROM B;"
        pg_bare_b = FirebirdToPostgresVisitor.transpile(fb_bare_b, symbols=symbols_a_first)
        self.assertIn("::date)", pg_bare_b, "Bare D over table B (DATE) must produce ::date cast")

        # In a view over A, bare D points to A.D (TIMESTAMP) -> must NOT produce ::date
        fb_bare_a = "CREATE VIEW V_BARE_A AS SELECT DATEADD(DAY, 1, D) AS R FROM A;"
        pg_bare_a = FirebirdToPostgresVisitor.transpile(fb_bare_a, symbols=symbols_a_first)
        self.assertNotIn("::date)", pg_bare_a, "Bare D over table A (TIMESTAMP) must not produce ::date cast")

        # Order independence for bare refs
        self.assertEqual(pg_bare_b, FirebirdToPostgresVisitor.transpile(fb_bare_b, symbols=symbols_b_first))
        self.assertEqual(pg_bare_a, FirebirdToPostgresVisitor.transpile(fb_bare_a, symbols=symbols_b_first))

        # -------- 4. Alias references resolve to underlying table's type --------
        # Table alias x for B -> x.D is DATE -> must produce ::date
        fb_alias_b = "CREATE VIEW V_ALIAS_B AS SELECT DATEADD(DAY, 1, x.D) AS R FROM B x;"
        pg_alias_b = FirebirdToPostgresVisitor.transpile(fb_alias_b, symbols=symbols_a_first)
        self.assertIn("::date)", pg_alias_b, "Alias x.D over table B (DATE) must produce ::date cast")

        # Table alias y for A -> y.D is TIMESTAMP -> must NOT produce ::date
        fb_alias_a = "CREATE VIEW V_ALIAS_A AS SELECT DATEADD(DAY, 1, y.D) AS R FROM A y;"
        pg_alias_a = FirebirdToPostgresVisitor.transpile(fb_alias_a, symbols=symbols_a_first)
        self.assertNotIn("::date)", pg_alias_a, "Alias y.D over table A (TIMESTAMP) must not produce ::date cast")

        # Bare ref in aliased table: FROM B x with D -> rewrites to x.D (DATE) -> ::date
        fb_bare_alias_b = "CREATE VIEW V_BARE_ALIAS_B AS SELECT DATEADD(DAY, 1, D) AS R FROM B x;"
        pg_bare_alias_b = FirebirdToPostgresVisitor.transpile(fb_bare_alias_b, symbols=symbols_a_first)
        self.assertIn("::date)", pg_bare_alias_b, "Bare D over aliased table B x must produce ::date cast")

        # -------- 5. Procedure parameters register correctly --------
        fb_proc_bare = """
        CREATE PROCEDURE SP_BARE_D (D DATE)
        RETURNS (R DATE)
        AS
        BEGIN
            R = DATEADD(DAY, 1, D);
            SUSPEND;
        END;
        """
        pg_bare = FirebirdToPostgresVisitor.transpile(fb_proc_bare, symbols=symbols_a_first)
        self.assertIn("::date)", pg_bare, "Procedure param D(DATE) must produce ::date cast")

        # -------- 6. COALESCE mixing date/timestamp yields timestamp (no ::date) --------
        fb_coalesce = "CREATE VIEW V_MIX AS SELECT DATEADD(DAY, 1, COALESCE(A.D, CURRENT_DATE)) AS R FROM A;"
        pg_mix = FirebirdToPostgresVisitor.transpile(fb_coalesce, symbols=symbols_a_first)
        self.assertNotIn("::date)", pg_mix, "COALESCE with TIMESTAMP branch must not cast to ::date")

        # -------- 7. DATEADD arithmetic preserves type --------
        fb_arith = "CREATE VIEW V_ARITH AS SELECT DATEADD(DAY, 1, B.D) - B.D AS DIFF FROM B;"
        pg_arith = FirebirdToPostgresVisitor.transpile(fb_arith, symbols=symbols_a_first)
        self.assertIn("::date)", pg_arith, "DATEADD on B.D (DATE) must cast to ::date in arithmetic")


