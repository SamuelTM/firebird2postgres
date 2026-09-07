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
        self.assertIn('DROP TRIGGER IF EXISTS "BI_CLIENTES" ON "clientes";', pg_sql)
        self.assertIn('CREATE TRIGGER "BI_CLIENTES" BEFORE INSERT ON "clientes"', pg_sql)
        self.assertIn('WHEN (NEW."id" IS NULL)', pg_sql)
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
        self.assertIn('BEFORE UPDATE ON "clientes"', pg_sql)

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
        self.assertIn('BEFORE DELETE ON "clientes"', pg_sql)
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
        self.assertIn('AFTER DELETE ON "clientes"', pg_sql)
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
        self.assertIn('BEFORE INSERT OR UPDATE ON "clientes"', pg_sql)
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

    def test_trigger_with_unspaced_into_bind_variable(self):
        fb_sql = """
        CREATE TRIGGER TPROCS_LIMPA_APAC FOR TPROCS_ATENDIMENTO_APAC AFTER DELETE
        AS
        DECLARE VARIABLE VID INTEGER;
        BEGIN
            SELECT FIRST 1 ID FROM TPROCS_ATENDIMENTO_APAC WHERE ID = OLD.ID INTO:VID;
        END
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("LIMIT 1 INTO STRICT VID;", pg_sql)
        self.assertNotIn("INTOVID", pg_sql.upper())

    def test_trigger_with_unspaced_where_and_returning_bind_variable(self):
        fb_sql = """
        CREATE TRIGGER BI_ORDERS FOR ORDERS BEFORE INSERT
        AS
        DECLARE VARIABLE V_ID INTEGER;
        BEGIN
            INSERT INTO LOG_ORDERS (ID) VALUES (NEW.ID) RETURNING ID INTO:V_ID;
            SELECT 1 FROM DUAL WHERE:V_ID > 0 INTO :V_ID;
        END
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("RETURNING ID INTO V_ID;", pg_sql)
        self.assertIn("WHERE V_ID > 0", pg_sql)

    def test_before_multi_event_trigger_with_delete_returns_old_or_new(self):
        fb_sql = """
        CREATE TRIGGER BIUD_TEST FOR TEST BEFORE INSERT OR UPDATE OR DELETE
        AS
        BEGIN
            IF (DELETING) THEN
                INSERT INTO AUDIT_LOG (ACTION) VALUES ('DEL');
        END
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("IF (TG_OP = 'DELETE') THEN", pg_sql)
        self.assertIn("IF TG_OP = 'DELETE' THEN\n        RETURN OLD;\n    ELSE\n        RETURN NEW;\n    END IF;", pg_sql)

    def test_trigger_event_predicates_inserting_updating_deleting(self):
        fb_sql = """
        CREATE TRIGGER TRG_AUDIT FOR CLIENTES AFTER INSERT OR UPDATE OR DELETE
        AS
        BEGIN
            IF (INSERTING) THEN
                INSERT INTO AUDIT (EVENT) VALUES ('INS');
            IF (UPDATING AND OLD.NOME <> NEW.NOME) THEN
                INSERT INTO AUDIT (EVENT) VALUES ('UPD');
            IF (DELETING) THEN
                INSERT INTO AUDIT (EVENT) VALUES ('DEL');
            IF (NEW.DELETING = 1) THEN
                INSERT INTO AUDIT (EVENT) VALUES ('COL_PRESERVED');
        END
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("IF (TG_OP = 'INSERT') THEN", pg_sql)
        self.assertIn("IF (TG_OP = 'UPDATE' AND OLD.NOME <> NEW.NOME) THEN", pg_sql)
        self.assertIn("IF (TG_OP = 'DELETE') THEN", pg_sql)
        self.assertIn("IF (NEW.DELETING = 1) THEN", pg_sql)

    def test_insert_trigger_with_additional_logic_omits_when_clause(self):
        fb_sql = """
        CREATE TRIGGER BI_MIXED FOR CLIENTES BEFORE INSERT
        AS
        BEGIN
            IF (NEW.ID IS NULL) THEN
                NEW.ID = GEN_ID(GEN_CLIENTES_ID, 1);
            NEW.DATA_CRIOU = CURRENT_TIMESTAMP;
        END
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertNotIn("WHEN", pg_sql)
        self.assertIn('CREATE TRIGGER "BI_MIXED" BEFORE INSERT ON "clientes" FOR EACH ROW EXECUTE FUNCTION "BI_MIXED_func"();', pg_sql)

    def test_trigger_preserves_old_new_in_string_literals(self):
        fb_sql = """
        CREATE TRIGGER BU_AUDIT FOR CLIENTES BEFORE UPDATE
        AS
        BEGIN
            IF (NEW.STATUS <> OLD.STATUS) THEN
            BEGIN
                INSERT INTO LOGS (MSG) VALUES ('"old".status alterado para "new".status');
            END
        END
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("NEW.STATUS <> OLD.STATUS", pg_sql)
        self.assertIn('\'"old".status alterado para "new".status\'', pg_sql)


