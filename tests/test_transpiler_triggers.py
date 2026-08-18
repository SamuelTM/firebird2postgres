import unittest
from transpiler import FirebirdToPostgresVisitor


class TestTranspilerTriggers(unittest.TestCase):
    def test_before_insert_trigger_with_gen_id(self):
        fb_sql = """
        CREATE TRIGGER BI_CLIENTES FOR CLIENTES BEFORE INSERT
        AS
        BEGIN
            IF (NEW.ID IS NULL) THEN
                NEW.ID = GEN_ID(GEN_CLIENTES_ID, 1);
        END
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn('CREATE OR REPLACE FUNCTION "BI_CLIENTES_func"()', pg_sql)
        self.assertIn("nextval('GEN_CLIENTES_ID')", pg_sql)
        self.assertIn("RETURN NEW;", pg_sql)
        self.assertIn('DROP TRIGGER IF EXISTS "BI_CLIENTES" ON "CLIENTES";', pg_sql)
        self.assertIn('CREATE TRIGGER "BI_CLIENTES" BEFORE INSERT ON "CLIENTES"', pg_sql)
        self.assertIn('EXECUTE FUNCTION "BI_CLIENTES_func"()', pg_sql)

    def test_before_update_trigger_with_new_and_old(self):
        fb_sql = """
        CREATE TRIGGER BU_CLIENTES FOR CLIENTES BEFORE UPDATE
        AS
        BEGIN
            IF (NEW.NOME <> OLD.NOME) THEN
                NEW.DATA_ALTERACAO = CURRENT_TIMESTAMP;
        END
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn('CREATE OR REPLACE FUNCTION "BU_CLIENTES_func"()', pg_sql)
        self.assertIn("NEW.DATA_ALTERACAO := CURRENT_TIMESTAMP;", pg_sql)
        self.assertIn("RETURN NEW;", pg_sql)
        self.assertIn('BEFORE UPDATE ON "CLIENTES"', pg_sql)

    def test_before_delete_trigger_returns_old(self):
        fb_sql = """
        CREATE TRIGGER BD_CLIENTES FOR CLIENTES BEFORE DELETE
        AS
        BEGIN
            INSERT INTO LOG_DELETES (ID) VALUES (OLD.ID);
        END
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn('CREATE OR REPLACE FUNCTION "BD_CLIENTES_func"()', pg_sql)
        self.assertIn('BEFORE DELETE ON "CLIENTES"', pg_sql)
        self.assertIn("RETURN OLD;", pg_sql)

    def test_after_delete_trigger_returns_null(self):
        fb_sql = """
        CREATE TRIGGER AD_LOG_DELETE FOR CLIENTES AFTER DELETE
        AS
        BEGIN
            INSERT INTO AUDIT_LOG (TABELA, REGISTRO_ID) VALUES ('CLIENTES', OLD.ID);
        END
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn('CREATE OR REPLACE FUNCTION "AD_LOG_DELETE_func"()', pg_sql)
        self.assertIn('AFTER DELETE ON "CLIENTES"', pg_sql)
        self.assertIn("RETURN NULL;", pg_sql)

    def test_multi_event_trigger_returns_new(self):
        fb_sql = """
        CREATE TRIGGER BIU_CLIENTES FOR CLIENTES BEFORE INSERT OR UPDATE
        AS
        BEGIN
            NEW.DATA_ATUALIZACAO = CURRENT_TIMESTAMP;
        END
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn('CREATE OR REPLACE FUNCTION "BIU_CLIENTES_func"()', pg_sql)
        self.assertIn('BEFORE INSERT OR UPDATE ON "CLIENTES"', pg_sql)
        self.assertIn("RETURN NEW;", pg_sql)

    def test_trigger_with_variable_declarations(self):
        fb_sql = """
        CREATE TRIGGER BI_VENDAS FOR VENDAS BEFORE INSERT
        AS
        DECLARE VARIABLE V_TOTAL NUMERIC(15,2);
        BEGIN
            SELECT SUM(VALOR) FROM ITENS INTO :V_TOTAL;
        END
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn('CREATE OR REPLACE FUNCTION "BI_VENDAS_func"()', pg_sql)
        self.assertIn("DECLARE\nV_TOTAL NUMERIC(15,2);", pg_sql)
        self.assertIn("RETURN NEW;", pg_sql)
