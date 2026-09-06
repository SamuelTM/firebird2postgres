import unittest
from transpiler import FirebirdToPostgresVisitor


class TestTranspilerProcedures(unittest.TestCase):
    def test_executable_procedure(self):
        fb_sql = """
        CREATE OR ALTER PROCEDURE SP_ATUALIZA_SALDO (
            P_CONTA_ID INTEGER,
            P_VALOR NUMERIC(15,2)
        )
        AS
        BEGIN
            UPDATE CONTAS SET SALDO = SALDO + :P_VALOR WHERE ID = :P_CONTA_ID;
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn('DROP FUNCTION IF EXISTS "sp_atualiza_saldo" CASCADE;', pg_sql)
        self.assertIn('CREATE FUNCTION "sp_atualiza_saldo"(P_CONTA_ID INTEGER, P_VALOR NUMERIC(15,2)) '
                      'RETURNS void AS $$', pg_sql)
        self.assertIn("UPDATE CONTAS SET SALDO = SALDO +", pg_sql)

    def test_selectable_procedure_with_suspend(self):
        fb_sql = """
        CREATE OR ALTER PROCEDURE SP_LISTA_ATIVOS
        RETURNS (
            ID INTEGER,
            NOME VARCHAR(100)
        )
        AS
        BEGIN
            FOR SELECT ID, NOME FROM CLIENTES WHERE ATIVO = 1 INTO :ID, :NOME DO
            BEGIN
                SUSPEND;
            END
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn('DROP FUNCTION IF EXISTS "sp_lista_ativos" CASCADE;', pg_sql)
        self.assertIn("RETURNS SETOF record", pg_sql)
        self.assertIn("RETURN NEXT;", pg_sql)

    def test_syntax_translations_first_skip(self):
        fb_sql = """
        CREATE OR ALTER PROCEDURE SP_TEST_PAGINACAO
        RETURNS (TOTAL INTEGER)
        AS
        DECLARE VARIABLE X INTEGER;
        BEGIN
            SELECT COUNT(*) FROM (SELECT FIRST 10 SKIP 20 ID FROM CLIENTES) INTO :TOTAL;
            SUSPEND;
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("LIMIT 10 OFFSET 20", pg_sql)

    def test_syntax_translations_rdb_database(self):
        fb_sql = """
        CREATE OR ALTER PROCEDURE SP_CURRENT_TIME_TEST
        RETURNS (AGORA TIMESTAMP)
        AS
        BEGIN
            SELECT CURRENT_TIMESTAMP FROM RDB$DATABASE INTO :AGORA;
            SUSPEND;
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertNotIn("RDB$DATABASE", pg_sql)

    def test_exception_to_raise_exception(self):
        fb_sql = """
        CREATE OR ALTER PROCEDURE SP_VALIDA_ACESSO (
            P_NIVEL INTEGER
        )
        AS
        BEGIN
            IF (P_NIVEL < 1) THEN
            BEGIN
                EXCEPTION EX_ACESSO_NEGADO;
            END
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("RAISE EXCEPTION 'EX_ACESSO_NEGADO';", pg_sql)

    def test_exception_with_custom_message(self):
        fb_sql = """
        CREATE OR ALTER PROCEDURE SP_VALIDA_SALDO (
            P_SALDO NUMERIC(15,2)
        )
        AS
        BEGIN
            IF (P_SALDO < 0) THEN
            BEGIN
                EXCEPTION EX_SALDO_INSUFICIENTE 'Saldo insuficiente para a operacao';
            END
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("RAISE EXCEPTION 'EX_SALDO_INSUFICIENTE: %', 'Saldo insuficiente para a operacao';", pg_sql)

    def test_gen_id_currval_and_setval(self):
        fb_sql = """
        CREATE OR ALTER PROCEDURE SP_TEST_GEN
        RETURNS (CURR_VAL INTEGER, CUSTOM_STEP INTEGER)
        AS
        BEGIN
            CURR_VAL = GEN_ID(GEN_PEDIDOS, 0);
            CUSTOM_STEP = GEN_ID(GEN_PEDIDOS, 5);
            SUSPEND;
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("CURR_VAL := currval('GEN_PEDIDOS');", pg_sql)
        self.assertIn("CUSTOM_STEP := setval('GEN_PEDIDOS', nextval('GEN_PEDIDOS') + (5) - 1);", pg_sql)

    def test_execute_procedure_to_perform(self):
        fb_sql = """
        CREATE OR ALTER PROCEDURE SP_CHAMA_OUTRA
        AS
        BEGIN
            EXECUTE PROCEDURE SP_AUDIT(1, 'TESTE');
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("PERFORM SP_AUDIT(1, 'TESTE');", pg_sql)

    def test_while_loop_and_leave_to_exit(self):
        fb_sql = """
        CREATE OR ALTER PROCEDURE SP_LOOP_TEST
        AS
        DECLARE VARIABLE I INTEGER;
        BEGIN
            I = 0;
            WHILE (I < 10) DO
            BEGIN
                I = I + 1;
                IF (I = 5) THEN
                    LEAVE;
            END
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("WHILE (I < 10) LOOP", pg_sql)
        self.assertIn("EXIT;", pg_sql)
        self.assertIn("END LOOP;", pg_sql)

    def test_for_execute_statement_dynamic_loop(self):
        fb_sql = """
        CREATE OR ALTER PROCEDURE SP_DYNAMIC_FOR
        RETURNS (RES_ID INTEGER)
        AS
        BEGIN
            FOR EXECUTE STATEMENT 'SELECT ID FROM TABELA' INTO :RES_ID DO
            BEGIN
                SUSPEND;
            END
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("FOR RES_ID IN EXECUTE 'SELECT ID FROM TABELA' LOOP", pg_sql)
        self.assertIn("RETURN NEXT;", pg_sql)

    def test_blob_subtype_parameter_conversion(self):
        fb_sql = """
        CREATE OR ALTER PROCEDURE SP_BLOB_TEST (
            P_TEXTO BLOB SUBTYPE 1,
            P_BINARIO BLOB SUBTYPE 0
        )
        AS
        BEGIN
            INSERT INTO DADOS (DOC, ARQ) VALUES (:P_TEXTO, :P_BINARIO);
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn('CREATE FUNCTION "sp_blob_test"(P_TEXTO TEXT, P_BINARIO BYTEA) RETURNS void AS $$', pg_sql)
        self.assertIn("INSERT INTO DADOS (DOC, ARQ) VALUES (P_TEXTO, P_BINARIO);", pg_sql)

    def test_update_set_qualified_columns_stripped(self):
        fb_sql = """
        CREATE OR ALTER PROCEDURE LIFEMEDIC
        AS
        declare variable CONTINUA varchar(1);
        declare variable VIDCONTA integer;
        declare variable VIDCLASS integer;
        begin
            continua = 'T';
            while (continua <> 'F') do
            begin
                select first 1 tcontas_ccusto.id_ccusto,tcontas_ccusto.id_conta from tcontas_ccusto
                              inner join tcontas on (tcontas_ccusto.id_conta = tcontas.id)
                             where tcontas.id_class is null into :vidclass ,:vidconta;

                if (vidclass > 0) then
                    update tcontas set tcontas.id_class = :vidclass
                    where tcontas.id = :vidconta;

                if (vidclass < 1) then
                    continua = 'F';

                vidclass = 0;
            end
            suspend;
        end;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("update tcontas set id_class = vidclass", pg_sql)
        self.assertIn("where tcontas.id = vidconta;", pg_sql)
        self.assertNotIn("set tcontas.id_class", pg_sql)
        self.assertIn("into STRICT vidclass ,vidconta", pg_sql)
        self.assertIn("EXCEPTION WHEN NO_DATA_FOUND THEN", pg_sql)

    def test_singleton_select_into_strict_with_exception_block(self):
        fb_sql = """
        CREATE OR ALTER PROCEDURE SP_GET_INFO (
            P_ID INTEGER
        )
        RETURNS (
            V_NOME VARCHAR(100),
            V_VALOR NUMERIC(15,2)
        )
        AS
        DECLARE VARIABLE V_AUX INTEGER;
        BEGIN
            V_AUX = 0;
            SELECT NOME, VALOR FROM CLIENTES WHERE ID = :P_ID INTO :V_NOME, :V_VALOR;
            SUSPEND;
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("INTO STRICT V_NOME, V_VALOR", pg_sql)
        self.assertIn("EXCEPTION WHEN NO_DATA_FOUND THEN", pg_sql)
        self.assertIn("NULL;", pg_sql)

    def test_singleton_select_into_inside_for_loop_has_strict(self):
        fb_sql = """
        CREATE OR ALTER PROCEDURE SP_LOOP_NESTED_SELECT
        AS
        DECLARE VARIABLE V_ID INTEGER;
        DECLARE VARIABLE V_NOME VARCHAR(100);
        BEGIN
            FOR SELECT ID FROM USERS INTO :V_ID DO
            BEGIN
                SELECT NOME FROM DETAILS WHERE USER_ID = :V_ID INTO :V_NOME;
            END
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("FOR V_ID IN SELECT ID FROM USERS", pg_sql)
        self.assertIn("INTO STRICT V_NOME;", pg_sql)
        self.assertIn("EXCEPTION WHEN NO_DATA_FOUND THEN", pg_sql)

    def test_scalar_select_from_rdb_database_omits_exception_block(self):
        fb_sql = """
        CREATE OR ALTER PROCEDURE SP_NEXT_ID
        RETURNS (V_ID INTEGER)
        AS
        BEGIN
            SELECT GEN_ID(GEN_TEST, 1) FROM RDB$DATABASE INTO :V_ID;
            SUSPEND;
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("nextval('GEN_TEST')", pg_sql)
        self.assertIn("INTO STRICT V_ID;", pg_sql)
        self.assertNotIn("EXCEPTION WHEN NO_DATA_FOUND THEN", pg_sql)

    def test_aggregate_select_without_group_by_omits_exception_block(self):
        fb_sql = """
        CREATE OR ALTER PROCEDURE SP_COUNT_ACTIVE
        RETURNS (V_COUNT INTEGER)
        AS
        BEGIN
            SELECT COUNT(*) FROM CLIENTES WHERE ATIVO = 1 INTO :V_COUNT;
            SUSPEND;
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("SELECT COUNT(*) FROM CLIENTES", pg_sql)
        self.assertIn("INTO STRICT V_COUNT;", pg_sql)
        self.assertNotIn("EXCEPTION WHEN NO_DATA_FOUND THEN", pg_sql)

    def test_for_loop_update_converted_to_set_based(self):
        fb_sql = """
        CREATE OR ALTER PROCEDURE SP_UPDATE_LOOP (
            P_GRUPO INTEGER,
            P_ID INTEGER
        )
        AS
        DECLARE VARIABLE V_MARC INTEGER;
        BEGIN
            FOR SELECT ID_MARCACAO FROM TAGENDA WHERE ID_APAC = :P_ID INTO :V_MARC DO
            BEGIN
                UPDATE TAGENDA_MARCACAO
                SET ID_GRUPO = :P_GRUPO
                WHERE TAGENDA_MARCACAO.ID_MARCACAO = :V_MARC;
            END
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("WHERE TAGENDA_MARCACAO.ID_MARCACAO IN (SELECT ID_MARCACAO FROM TAGENDA WHERE ID_APAC = P_ID);", pg_sql)
        self.assertNotIn("FOR V_MARC IN", pg_sql)
        self.assertNotIn("END LOOP;", pg_sql)

    def test_for_loop_multiple_updates_converted_to_set_based(self):
        fb_sql = """
        CREATE OR ALTER PROCEDURE SP_MULTI_UPDATE_LOOP (
            P_FATURA VARCHAR(20)
        )
        AS
        DECLARE VARIABLE V_ID_NOTA INTEGER;
        BEGIN
            FOR SELECT DISTINCT ID_NOTA FROM TFATURA WHERE COD_FATURA = :P_FATURA INTO :V_ID_NOTA DO
            BEGIN
                UPDATE TNOTANF_SERV
                SET ID_FATURA = NULL
                WHERE TNOTANF_SERV.ID_NOTA = :V_ID_NOTA;
                UPDATE TNOTANF
                SET INATIVO = 'T'
                WHERE TNOTANF.ID_NOTA = :V_ID_NOTA;
            END
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("WHERE TNOTANF_SERV.ID_NOTA IN (SELECT DISTINCT ID_NOTA FROM TFATURA WHERE COD_FATURA = P_FATURA);", pg_sql)
        self.assertIn("WHERE TNOTANF.ID_NOTA IN (SELECT DISTINCT ID_NOTA FROM TFATURA WHERE COD_FATURA = P_FATURA);", pg_sql)
        self.assertNotIn("FOR V_ID_NOTA IN", pg_sql)

    def test_for_loop_delete_converted_to_set_based(self):
        fb_sql = """
        CREATE OR ALTER PROCEDURE SP_DELETE_LOOP (
            P_USER_ID INTEGER
        )
        AS
        DECLARE VARIABLE V_LOG_ID INTEGER;
        BEGIN
            FOR SELECT ID FROM AUDIT WHERE USER_ID = :P_USER_ID INTO :V_LOG_ID DO
                DELETE FROM LOG_ENTRIES WHERE LOG_ENTRIES.ID = :V_LOG_ID;
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("DELETE FROM LOG_ENTRIES WHERE LOG_ENTRIES.ID IN (SELECT ID FROM AUDIT WHERE USER_ID = P_USER_ID);", pg_sql)
        self.assertNotIn("FOR V_LOG_ID IN", pg_sql)
        self.assertNotIn("END LOOP;", pg_sql)

    def test_for_loop_retains_cursor_when_var_used_in_set(self):
        fb_sql = """
        CREATE OR ALTER PROCEDURE SP_LOOP_VAR_IN_SET
        AS
        DECLARE VARIABLE V_ID INTEGER;
        BEGIN
            FOR SELECT ID FROM USERS INTO :V_ID DO
            BEGIN
                UPDATE TOTALS SET LAST_ID = :V_ID WHERE TOTALS.KEY = 1;
            END
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("FOR V_ID IN SELECT ID FROM USERS", pg_sql)
        self.assertIn("END LOOP;", pg_sql)

    def test_firebird_builtins_iif_list_dateadd_datediff(self):
        fb_sql = """
        CREATE OR ALTER PROCEDURE SP_TEST_BUILTINS
        AS
        DECLARE VARIABLE V_X INTEGER;
        DECLARE VARIABLE V_DT TIMESTAMP;
        DECLARE VARIABLE V_DIFF INTEGER;
        BEGIN
            V_X = IIF(V_X > 0, IIF(V_X > 10, 100, 50), 0);
            SELECT LIST(NOME) FROM CLIENTES;
            SELECT LIST(NOME, '; ') FROM CLIENTES;
            V_DT = DATEADD(DAY, 5, V_DT);
            V_DT = DATEADD(MONTH, -1, V_DT);
            V_DIFF = DATEDIFF(DAY, V_DT, CURRENT_DATE);
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("V_X := CASE WHEN V_X > 0 THEN CASE WHEN V_X > 10 THEN 100 ELSE 50 END ELSE 0 END;", pg_sql)
        self.assertIn("SELECT string_agg(NOME::text, ',') FROM CLIENTES;", pg_sql)
        self.assertIn("SELECT string_agg(NOME::text, '; ') FROM CLIENTES;", pg_sql)
        self.assertIn("V_DT := (V_DT + (5) * INTERVAL '1 day');", pg_sql)
        self.assertIn("V_DT := (V_DT + (-1) * INTERVAL '1 month');", pg_sql)
        self.assertIn("V_DIFF := (DATE(CURRENT_DATE) - DATE(V_DT));", pg_sql)



