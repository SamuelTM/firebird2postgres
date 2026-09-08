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
            SELECT FIRST 1 ID FROM CLIENTES INTO :TOTAL;
            SELECT FIRST 1 SKIP 5 ID FROM CLIENTES ORDER BY ID DESC INTO :TOTAL;
            SUSPEND;
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("LIMIT 10 OFFSET 20", pg_sql)
        self.assertIn("LIMIT 1 INTO STRICT TOTAL;", pg_sql)
        self.assertIn("ORDER BY ID DESC LIMIT 1 OFFSET 5 INTO STRICT TOTAL;", pg_sql)

    def test_syntax_translations_first_skip_in_for_loop(self):
        fb_sql = """
        CREATE OR ALTER PROCEDURE SP_TEST_LOOP
        AS
        DECLARE VARIABLE V_ID INTEGER;
        BEGIN
            FOR SELECT FIRST 5 ID FROM CLIENTES INTO :V_ID DO
            BEGIN
            END
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("FOR V_ID IN SELECT  ID FROM CLIENTES LIMIT 5 LOOP", pg_sql)


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

    def test_gen_id_step_zero_and_one_and_rejection_of_custom_steps(self):
        fb_sql = """
        CREATE OR ALTER PROCEDURE SP_TEST_GEN
        RETURNS (CURR_VAL INTEGER, NEXT_VAL INTEGER)
        AS
        BEGIN
            CURR_VAL = GEN_ID(GEN_PEDIDOS, 0);
            NEXT_VAL = GEN_ID(GEN_PEDIDOS, 1);
            SUSPEND;
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("CURR_VAL := (SELECT CASE WHEN is_called THEN last_value ELSE last_value - 1 END FROM \"gen_pedidos\");", pg_sql)
        self.assertIn("NEXT_VAL := nextval('GEN_PEDIDOS');", pg_sql)

        for invalid_step in [2, 5, -1, 100]:
            with self.assertRaises(ValueError) as cm:
                FirebirdToPostgresVisitor.transpile(f"CREATE PROCEDURE P AS BEGIN DUMMY = GEN_ID(GEN_PEDIDOS, {invalid_step}); END;")
            self.assertIn("Unsupported GEN_ID step", str(cm.exception))

    def test_gen_id_with_configured_sequence_increment(self):
        fb_step10 = "CREATE PROCEDURE P AS BEGIN DUMMY = GEN_ID(GEN_STEP10, 10); END;"
        pg_step10 = FirebirdToPostgresVisitor.transpile(fb_step10, sequence_increments={'gen_step10': 10})
        self.assertIn("nextval('GEN_STEP10')", pg_step10)

        # GEN_ID(G, 1) when sequence increment is 10 must be rejected
        fb_step1_mismatch = "CREATE PROCEDURE P AS BEGIN DUMMY = GEN_ID(GEN_STEP10, 1); END;"
        with self.assertRaises(ValueError) as cm:
            FirebirdToPostgresVisitor.transpile(fb_step1_mismatch, sequence_increments={'gen_step10': 10})
        self.assertIn("sequence configured increment is 10", str(cm.exception))

        # GEN_ID(G, 0) with increment 10
        fb_step0_inc10 = "CREATE PROCEDURE P AS BEGIN DUMMY = GEN_ID(GEN_STEP10, 0); END;"
        pg_step0_inc10 = FirebirdToPostgresVisitor.transpile(fb_step0_inc10, sequence_increments={'gen_step10': 10})
        self.assertIn("last_value - 10", pg_step0_inc10)

        # GEN_ID(G, 0) with negative increment -2
        fb_step0_neg = "CREATE PROCEDURE P AS BEGIN DUMMY = GEN_ID(GEN_DESC, 0); END;"
        pg_step0_neg = FirebirdToPostgresVisitor.transpile(fb_step0_neg, sequence_increments={'gen_desc': -2})
        self.assertIn("last_value - (-2)", pg_step0_neg)

    def test_gen_id_with_quoted_sequence_name(self):
        fb_sql = """
        CREATE PROCEDURE P AS
        BEGIN
            DUMMY = GEN_ID("GEN_TEST", 1);
            CURRENT_VAL = GEN_ID("GEN_TEST", 0);
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("nextval('\"gen_test\"')", pg_sql)
        self.assertIn('FROM "gen_test"', pg_sql)

    def test_gen_id_with_internal_quotes_in_sequence_name(self):
        fb_sql = '''
        CREATE PROCEDURE P AS
        BEGIN
            DUMMY = GEN_ID("GEN_""SPECIAL""", 1);
            CURRENT_VAL = GEN_ID("GEN_""SPECIAL""", 0);
        END;
        '''
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn('nextval(\'"gen_""special"""\')', pg_sql)
        self.assertIn('FROM "gen_""special"""', pg_sql)

    def test_next_value_for_with_quoted_and_unquoted_sequence(self):
        fb_sql = """
        CREATE PROCEDURE P AS
        BEGIN
            DUMMY = NEXT VALUE FOR "GEN_TEST";
            DUMMY = NEXT VALUE FOR GEN_NORMAL;
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("nextval('\"gen_test\"')", pg_sql)
        self.assertIn("nextval('GEN_NORMAL')", pg_sql)

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

    def test_table_queries_and_filtered_queries_retain_exception_block(self):
        # Queries on tables or with WHERE clauses may return 0 rows and must preserve exception handling
        cases = [
            """
            CREATE OR ALTER PROCEDURE SP_COUNT_ACTIVE RETURNS (V_COUNT INTEGER) AS
            BEGIN
                SELECT COUNT(*) FROM CLIENTES WHERE ATIVO = 1 INTO :V_COUNT;
                SUSPEND;
            END;
            """,
            """
            CREATE OR ALTER PROCEDURE SP_FILTERED_RDB RETURNS (V INTEGER) AS
            BEGIN
                SELECT 1 FROM RDB$DATABASE WHERE 1=0 INTO :V;
            END;
            """,
            """
            CREATE OR ALTER PROCEDURE SP_STRING_AGG RETURNS (V VARCHAR(20)) AS
            BEGIN
                SELECT 'COUNT(' FROM SRC INTO :V;
            END;
            """,
            """
            CREATE OR ALTER PROCEDURE SP_SUBQUERY_AGG RETURNS (V INTEGER) AS
            BEGIN
                SELECT (SELECT COUNT(*) FROM DST) FROM SRC INTO :V;
            END;
            """,
            """
            CREATE OR ALTER PROCEDURE SP_HAVING_RDB RETURNS (V INTEGER) AS
            BEGIN
                SELECT COUNT(*) FROM RDB$DATABASE HAVING COUNT(*) = 0 INTO :V;
            END;
            """
        ]
        for fb_sql in cases:
            pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
            self.assertIn("EXCEPTION WHEN NO_DATA_FOUND THEN", pg_sql)
            self.assertIn("INTO STRICT", pg_sql)

    def test_for_loop_update_retains_procedural_cursor(self):
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
        self.assertIn("FOR V_MARC IN SELECT ID_MARCACAO FROM TAGENDA WHERE ID_APAC = P_ID LOOP", pg_sql)
        self.assertIn("WHERE TAGENDA_MARCACAO.ID_MARCACAO = V_MARC;", pg_sql)
        self.assertIn("END LOOP;", pg_sql)

    def test_for_loop_multiple_updates_retains_procedural_cursor(self):
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
        self.assertIn("FOR V_ID_NOTA IN SELECT DISTINCT ID_NOTA FROM TFATURA WHERE COD_FATURA = P_FATURA LOOP", pg_sql)
        self.assertIn("WHERE TNOTANF_SERV.ID_NOTA = V_ID_NOTA;", pg_sql)
        self.assertIn("WHERE TNOTANF.ID_NOTA = V_ID_NOTA;", pg_sql)
        self.assertIn("END LOOP;", pg_sql)

    def test_for_loop_delete_retains_procedural_cursor(self):
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
        self.assertIn("FOR V_LOG_ID IN SELECT ID FROM AUDIT WHERE USER_ID = P_USER_ID LOOP", pg_sql)
        self.assertIn("DELETE FROM LOG_ENTRIES WHERE LOG_ENTRIES.ID = V_LOG_ID;", pg_sql)
        self.assertIn("END LOOP;", pg_sql)

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

    def test_for_loop_with_nested_if_and_dml(self):
        fb_sql = """
        CREATE OR ALTER PROCEDURE SP_LOOP_NESTED_IF
        AS
        DECLARE VARIABLE V_ID INTEGER;
        BEGIN
            FOR SELECT ID FROM USERS INTO :V_ID DO
            BEGIN
                IF (V_ID > 10) THEN
                    UPDATE USERS SET STATUS = 1 WHERE USERS.ID = :V_ID;
            END
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("FOR V_ID IN SELECT ID FROM USERS LOOP", pg_sql)
        self.assertIn("IF (V_ID > 10) THEN", pg_sql)
        self.assertIn("UPDATE USERS SET STATUS = 1 WHERE USERS.ID = V_ID;", pg_sql)
        self.assertIn("END IF;", pg_sql)
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
            SELECT LIST(ID + 1, ', ') FROM CLIENTES;
            V_DT = DATEADD(DAY, 5, V_DT);
            V_DT = DATEADD(MONTH, -1, V_DT);
            V_DIFF = DATEDIFF(DAY, V_DT, CURRENT_DATE);
            V_DIFF = DATEDIFF(HOUR, V_DT, CURRENT_TIMESTAMP);
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("V_X := CASE WHEN V_X > 0 THEN CASE WHEN V_X > 10 THEN 100 ELSE 50 END ELSE 0 END;", pg_sql)
        self.assertIn("SELECT string_agg((NOME)::text, ',') FROM CLIENTES;", pg_sql)
        self.assertIn("SELECT string_agg((NOME)::text, '; ') FROM CLIENTES;", pg_sql)
        self.assertIn("SELECT string_agg((ID + 1)::text, ', ') FROM CLIENTES;", pg_sql)
        self.assertIn("V_DT := (V_DT + (5) * INTERVAL '1 day');", pg_sql)
        self.assertIn("V_DT := (V_DT + (-1) * INTERVAL '1 month');", pg_sql)
        self.assertIn("V_DIFF := (DATE(CURRENT_DATE) - DATE(V_DT));", pg_sql)
        self.assertIn("V_DIFF := ROUND(EXTRACT(EPOCH FROM (DATE_TRUNC('hour', CURRENT_TIMESTAMP::timestamp) - DATE_TRUNC('hour', V_DT::timestamp))) / 3600);", pg_sql)

    def test_datediff_with_time_parameters_and_variables(self):
        fb_sql = """
        CREATE PROCEDURE SP_CALC_TIME (T1 TIME, T2 TIME)
        RETURNS (DIFF_H INTEGER, DIFF_MS NUMERIC(18, 1))
        AS
        DECLARE VARIABLE V_START TIME;
        DECLARE VARIABLE V_END TIME;
        BEGIN
            DIFF_H = DATEDIFF(HOUR, T1, T2);
            DIFF_MS = DATEDIFF(MILLISECOND, V_START, V_END);
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("DATE_TRUNC('hour', T2) - DATE_TRUNC('hour', T1)", pg_sql)
        self.assertNotIn("T2::timestamp", pg_sql)
        self.assertNotIn("T1::timestamp", pg_sql)
        self.assertIn("(V_END - V_START)", pg_sql)
        self.assertNotIn("V_END::timestamp", pg_sql)
        self.assertNotIn("V_START::timestamp", pg_sql)

    def test_datediff_day_with_time_parameter_raises(self):
        fb_sql = """
        CREATE PROCEDURE SP_INVALID_TIME (T1 TIME, T2 TIME)
        AS
        BEGIN
            DELETE FROM T WHERE DATEDIFF(DAY, T1, T2) > 0;
        END;
        """
        with self.assertRaises(ValueError) as cm:
            FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("cannot be used with TIME values", str(cm.exception))

    def test_procedure_with_bigint_parameters_returns_and_variables(self):
        fb_sql = """
        CREATE PROCEDURE SP_BIGINT_OPS (IN_ID BIGINT)
        RETURNS (OUT_ID BIGINT)
        AS
        DECLARE VARIABLE V_TOTAL BIGINT;
        BEGIN
            V_TOTAL = :IN_ID * 2;
            OUT_ID = :V_TOTAL;
            SUSPEND;
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn('CREATE FUNCTION "sp_bigint_ops"(IN_ID BIGINT, OUT OUT_ID BIGINT) RETURNS SETOF BIGINT', pg_sql)
        self.assertIn('V_TOTAL BIGINT;', pg_sql)
        self.assertIn('V_TOTAL := IN_ID * 2;', pg_sql)
        self.assertIn('OUT_ID := V_TOTAL;', pg_sql)
        self.assertIn('RETURN NEXT;', pg_sql)

    def test_variable_declarations_initializers_and_not_null(self):
        fb_sql = """
        CREATE PROCEDURE SP_TEST_VARS
        AS
        DECLARE VARIABLE N INTEGER NOT NULL DEFAULT 7;
        DECLARE VARIABLE M INTEGER = 10;
        DECLARE VARIABLE K INTEGER NOT NULL = 20;
        DECLARE VARIABLE L INTEGER = 30 NOT NULL;
        DECLARE VARIABLE P_VAR INTEGER DEFAULT 40 NOT NULL;
        DECLARE VARIABLE S VARCHAR(100) = 'hello world';
        DECLARE VARIABLE S2 VARCHAR(100) = 'semi;colon';
        DECLARE VARIABLE G_ID BIGINT = GEN_ID(GEN_TEST, 1);
        DECLARE VARIABLE C CONSTANT INTEGER = 99;
        DECLARE VARIABLE PLAIN INTEGER;
        BEGIN
            N = N + M;
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn('N INTEGER NOT NULL DEFAULT 7;', pg_sql)
        self.assertIn('M INTEGER DEFAULT 10;', pg_sql)
        self.assertIn('K INTEGER NOT NULL DEFAULT 20;', pg_sql)
        self.assertIn('L INTEGER NOT NULL DEFAULT 30;', pg_sql)
        self.assertIn('P_VAR INTEGER NOT NULL DEFAULT 40;', pg_sql)
        self.assertIn("S VARCHAR(100) DEFAULT 'hello world';", pg_sql)
        self.assertIn("S2 VARCHAR(100) DEFAULT 'semi;colon';", pg_sql)
        self.assertIn("G_ID BIGINT DEFAULT nextval('GEN_TEST');", pg_sql)
        self.assertIn('C CONSTANT INTEGER DEFAULT 99;', pg_sql)
        self.assertIn('PLAIN INTEGER;', pg_sql)

    def test_procedure_with_parameter_defaults_and_domains(self):
        fb_sql = """
        CREATE PROCEDURE SP_PARAM_DEFAULTS (
            P_LIMIT INTEGER DEFAULT 10,
            P_PREFIX VARCHAR(20) = 'test',
            P_RATE DM_TAXA NOT NULL DEFAULT 0.05
        )
        RETURNS (
            OUT_COUNT INTEGER
        )
        AS
        BEGIN
            OUT_COUNT = P_LIMIT;
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn('CREATE FUNCTION "sp_param_defaults"(P_LIMIT INTEGER DEFAULT 10, '
                      "P_PREFIX VARCHAR(20) DEFAULT 'test', "
                      'P_RATE DM_TAXA DEFAULT 0.05, OUT OUT_COUNT INTEGER) RETURNS INTEGER', pg_sql)

    def test_quoted_variable_and_parameter_case_consistency(self):
        fb_sql = """
        CREATE PROCEDURE SP_QUOTED_CASE ("Param" INTEGER)
        RETURNS ("Result" INTEGER)
        AS
        DECLARE VARIABLE "Count" INTEGER = 0;
        BEGIN
            "Count" = :"Param" + 1;
            "Result" = "Count";
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        # Declaration and usage must have the exact same identifier casing
        self.assertIn('"param" INTEGER', pg_sql)
        self.assertIn('OUT "result" INTEGER', pg_sql)
        self.assertIn('"count" INTEGER DEFAULT 0;', pg_sql)
        self.assertIn('"count" := "param" + 1;', pg_sql)
        self.assertIn('"result" := "count";', pg_sql)

    def test_procedure_exit_translates_to_return(self):
        fb_sql = """
        CREATE PROCEDURE SP_TEST_EXIT (P_VAL INTEGER)
        AS
        BEGIN
            IF (P_VAL < 0) THEN
                EXIT;
            EXIT WHEN (P_VAL = 0);
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("RETURN;", pg_sql)
        self.assertIn("IF (P_VAL = 0) THEN RETURN; END IF;", pg_sql)
        self.assertNotIn("EXIT;", pg_sql)

    def test_procedure_leave_translates_to_exit(self):
        fb_sql = """
        CREATE PROCEDURE SP_TEST_LEAVE
        AS
        DECLARE VARIABLE I INTEGER = 0;
        BEGIN
            WHILE (I < 10) DO
            BEGIN
                IF (I = 5) THEN
                    LEAVE;
                I = I + 1;
            END
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("EXIT;", pg_sql)
        self.assertNotIn("LEAVE;", pg_sql)

    def test_column_and_variable_disambiguation(self):
        fb_sql = """
        CREATE PROCEDURE SP_GET_ID (ID INTEGER)
        RETURNS (
            RES INTEGER
        )
        AS
        BEGIN
            SELECT ID FROM T WHERE ID = :ID INTO :RES;
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("SELECT T.ID FROM T WHERE T.ID = ID INTO STRICT RES;", pg_sql)

    def test_procedure_output_id_disambiguation(self):
        fb_sql = """
        CREATE PROCEDURE SP_FETCH_RECORD
        RETURNS (
            ID INTEGER
        )
        AS
        BEGIN
            SELECT ID FROM T INTO :ID;
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("SELECT T.ID FROM T INTO STRICT ID;", pg_sql)

    def test_column_and_variable_disambiguation_with_alias(self):
        fb_sql = """
        CREATE PROCEDURE SP_GET_ALIASED
        RETURNS (
            ID INTEGER
        )
        AS
        BEGIN
            SELECT ID FROM T MY_ALIAS WHERE ID = :ID INTO :ID;
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("SELECT MY_ALIAS.ID FROM T MY_ALIAS WHERE MY_ALIAS.ID = ID INTO STRICT ID;", pg_sql)

    def test_procedure_with_suspend_literal_does_not_return_setof(self):
        fb_sql = """
        CREATE PROCEDURE SP_NO_SETOF
        RETURNS (
            MSG VARCHAR(50)
        )
        AS
        BEGIN
            -- This comment contains suspend
            MSG = 'suspend';
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("RETURNS VARCHAR(50)", pg_sql)
        self.assertNotIn("RETURNS SETOF", pg_sql)

    def test_dateadd_preserves_date_type(self):
        fb_sql = """
        CREATE PROCEDURE SP_TEST_DATE (D DATE)
        RETURNS (
            DIFF INTEGER
        )
        AS
        BEGIN
            DIFF = DATEADD(DAY, 1, D) - D;
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("DIFF := ((D + (1) * INTERVAL '1 day')::date) - D;", pg_sql)

    def test_datediff_with_compound_time_expressions(self):
        fb_sql = """
        CREATE PROCEDURE SP_TEST_COMPOUND_TIME (T1 TIME, T2 TIME)
        RETURNS (DIFF_H INTEGER)
        AS
        BEGIN
            DIFF_H = DATEDIFF(HOUR, COALESCE(T1, T2), COALESCE(T2, T1));
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertNotIn("::timestamp", pg_sql)
        self.assertIn("DATE_TRUNC('hour', COALESCE(T2, T1)) - DATE_TRUNC('hour', COALESCE(T1, T2))", pg_sql)

    def test_extract_weekday_yearday_millisecond(self):
        fb_sql = """
        CREATE PROCEDURE SP_TEST_EXTRACT (D DATE, TS TIMESTAMP)
        RETURNS (WD INTEGER, YD INTEGER, MS INTEGER)
        AS
        BEGIN
            WD = EXTRACT(WEEKDAY FROM D);
            YD = EXTRACT(YEARDAY FROM D);
            MS = EXTRACT(MILLISECOND FROM TS);
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("WD := EXTRACT(DOW FROM D);", pg_sql)
        self.assertIn("YD := ((EXTRACT(DOY FROM D))::integer - 1);", pg_sql)
        self.assertIn("MS := (EXTRACT(MILLISECOND FROM TS)::numeric % 1000);", pg_sql)

    def test_procedure_with_domain_map(self):
        fb_sql = """
        CREATE PROCEDURE SP_TEST_DOMAIN (IN_A FOO)
        RETURNS (OUT_B FOO)
        AS
        DECLARE VARIABLE V_TEMP FOO;
        BEGIN
            V_TEMP = IN_A;
            OUT_B = V_TEMP;
        END;
        """
        domain_map = {"FOO": "foo_dom_dom"}
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql, domain_map=domain_map)
        self.assertIn("IN_A foo_dom_dom", pg_sql)
        self.assertIn("OUT_B foo_dom_dom", pg_sql)
        self.assertIn("V_TEMP foo_dom_dom;", pg_sql)

    def test_procedure_standalone_skip_pagination(self):
        fb_sql = """
        CREATE PROCEDURE SP_TEST_SKIP
        AS
        DECLARE VARIABLE V INT;
        BEGIN
            SELECT SKIP 2 ID FROM CLIENTES INTO :V;
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("OFFSET 2 INTO STRICT V;", pg_sql)
        self.assertNotIn("SKIP 2", pg_sql)

    def test_procedure_dynamic_first_skip_expressions(self):
        fb_sql = """
        CREATE PROCEDURE SP_TEST_DYN_PAG (P_LIM INT, P_OFF INT)
        AS
        DECLARE VARIABLE V INT;
        BEGIN
            SELECT FIRST (1 + 1) ID FROM CLIENTES INTO :V;
            SELECT FIRST :P_LIM SKIP :P_OFF ID FROM CLIENTES INTO :V;
            SELECT SKIP (5 * 2) FIRST (10) ID FROM CLIENTES INTO :V;
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("LIMIT (1 + 1) INTO STRICT V;", pg_sql)
        self.assertIn("LIMIT P_LIM OFFSET P_OFF INTO STRICT V;", pg_sql)
        self.assertIn("LIMIT (10) OFFSET (5 * 2) INTO STRICT V;", pg_sql)

    def test_procedure_type_of_column_and_domain(self):
        fb_sql = """
        CREATE PROCEDURE SP_TEST_TYPE_OF (
            P_NAME TYPE OF COLUMN CLIENTES.NOME,
            P_STATUS TYPE OF DOM_STATUS,
            P_DIRECT DOM_STATUS
        )
        AS
        DECLARE VARIABLE V_ID TYPE OF COLUMN CLIENTES.ID;
        DECLARE VARIABLE V_DOM TYPE OF DOM_CUSTOM;
        DECLARE VARIABLE V_DIRECT DOM_CUSTOM;
        BEGIN
            V_ID = 1;
        END;
        """
        domain_map = {"DOM_STATUS": "dom_status", "DOM_CUSTOM": "dom_custom_type"}
        domain_types = {"DOM_STATUS": "VARCHAR(20)", "DOM_CUSTOM": "INTEGER"}
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql, domain_map=domain_map, domain_types=domain_types)
        self.assertIn("P_NAME CLIENTES.NOME%TYPE", pg_sql)
        self.assertIn("P_STATUS VARCHAR(20)", pg_sql)
        self.assertIn("P_DIRECT dom_status", pg_sql)
        self.assertIn("V_ID CLIENTES.ID%TYPE;", pg_sql)
        self.assertIn("V_DOM INTEGER;", pg_sql)
        self.assertIn("V_DIRECT dom_custom_type;", pg_sql)
        self.assertNotIn("TYPE OF", pg_sql)

    def test_procedure_when_any_exception_handler(self):
        fb_sql = """
        CREATE PROCEDURE SP_TEST_WHEN_ANY
        AS
        BEGIN
            INSERT INTO LOGS(MSG) VALUES ('START');
            WHEN ANY DO
            BEGIN
                INSERT INTO LOGS(MSG) VALUES ('ERROR');
            END
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("EXCEPTION", pg_sql)
        self.assertIn("WHEN OTHERS THEN", pg_sql)
        self.assertNotIn("WHEN ANY", pg_sql)

    def test_procedure_execute_procedure_returning_values(self):
        fb_sql = """
        CREATE PROCEDURE SP_TEST_RET
        AS
        DECLARE VARIABLE V1 INT;
        DECLARE VARIABLE V2 VARCHAR(10);
        BEGIN
            EXECUTE PROCEDURE OTHER_P(1, 2) RETURNING_VALUES :V1, :V2;
            EXECUTE PROCEDURE NO_ARG_P RETURNING_VALUES :V1;
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("SELECT * FROM OTHER_P(1, 2) INTO STRICT V1, V2;", pg_sql)
        self.assertIn("SELECT * FROM NO_ARG_P() INTO STRICT V1;", pg_sql)
        self.assertNotIn("RETURNING_VALUES", pg_sql)

    def test_procedure_with_dollar_quote_in_body(self):
        fb_sql = """
        CREATE PROCEDURE SP_TEST_DOLLAR
        AS
        DECLARE VARIABLE R VARCHAR(10);
        BEGIN
            R = '$$';
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("AS $body$", pg_sql)
        self.assertIn("$body$ LANGUAGE plpgsql STABLE;", pg_sql)
        self.assertIn("R := '$$';", pg_sql)

    def test_procedure_volatility_classification_and_optimization_advisories(self):
        # 1. Read-only procedure -> STABLE
        fb_readonly = """
        CREATE OR ALTER PROCEDURE SP_GET_CLIENTE (P_ID INTEGER)
        RETURNS (NOME VARCHAR(100))
        AS
        BEGIN
            SELECT NOME FROM CLIENTES WHERE ID = :P_ID INTO :NOME;
            SUSPEND;
        END;
        """
        pg_readonly = FirebirdToPostgresVisitor.transpile(fb_readonly)
        self.assertIn("LANGUAGE plpgsql STABLE;", pg_readonly)
        self.assertIn("Volatility: STABLE", pg_readonly)
        self.assertNotIn("IMMUTABLE", pg_readonly)
        self.assertNotIn("PARALLEL SAFE", pg_readonly)

        # 2. Modifying procedure (DML: UPDATE) -> VOLATILE
        fb_update = """
        CREATE OR ALTER PROCEDURE SP_UPDATE_CLIENTE (P_ID INTEGER, P_NOME VARCHAR(100))
        AS
        BEGIN
            UPDATE CLIENTES SET NOME = :P_NOME WHERE ID = :P_ID;
        END;
        """
        pg_update = FirebirdToPostgresVisitor.transpile(fb_update)
        self.assertIn("LANGUAGE plpgsql VOLATILE;", pg_update)
        self.assertIn("Volatility: VOLATILE (data modification (DML))", pg_update)

        # 3. Procedure accessing sequences (GEN_ID) -> VOLATILE
        fb_seq = """
        CREATE OR ALTER PROCEDURE SP_NEXT_ID
        RETURNS (NEW_ID INTEGER)
        AS
        BEGIN
            NEW_ID = GEN_ID(GEN_CLIENTES, 1);
            SUSPEND;
        END;
        """
        pg_seq = FirebirdToPostgresVisitor.transpile(fb_seq)
        self.assertIn("LANGUAGE plpgsql VOLATILE;", pg_seq)
        self.assertIn("Volatility: VOLATILE (sequence generator access)", pg_seq)

        # 4. Procedure calling another procedure (EXECUTE PROCEDURE / PERFORM) -> VOLATILE
        fb_call = """
        CREATE OR ALTER PROCEDURE SP_INVOKE_OTHER
        AS
        BEGIN
            EXECUTE PROCEDURE SP_AUDIT_LOG(1);
        END;
        """
        pg_call = FirebirdToPostgresVisitor.transpile(fb_call)
        self.assertIn("LANGUAGE plpgsql VOLATILE;", pg_call)
        self.assertIn("procedure call (PERFORM)", pg_call)

        # 5. Procedure with DECLARE initializer calling sequence -> VOLATILE
        fb_decl_init = """
        CREATE OR ALTER PROCEDURE SP_INIT_VAR
        AS
        DECLARE VARIABLE X INTEGER = GEN_ID(GEN_FOO, 1);
        BEGIN
            SUSPEND;
        END;
        """
        pg_decl_init = FirebirdToPostgresVisitor.transpile(fb_decl_init)
        self.assertIn("LANGUAGE plpgsql VOLATILE;", pg_decl_init)
        self.assertIn("sequence generator access", pg_decl_init)

        # 6. Procedure calling arbitrary external function -> VOLATILE
        fb_ext_func = """
        CREATE OR ALTER PROCEDURE SP_WITH_EXT_FUNC (P_IN INTEGER)
        RETURNS (P_OUT INTEGER)
        AS
        BEGIN
            P_OUT = SOME_EXTERNAL_FUNC(P_IN);
            SUSPEND;
        END;
        """
        pg_ext_func = FirebirdToPostgresVisitor.transpile(fb_ext_func)
        self.assertIn("LANGUAGE plpgsql VOLATILE;", pg_ext_func)
        self.assertIn("external function call", pg_ext_func)

    def test_volatility_classification_item_d_regression(self):
        # 1. String '--' followed by INSERT must not be stripped as a line comment
        fb_str_dash = """
        CREATE OR ALTER PROCEDURE SP_STR_DASH
        AS
        DECLARE VARIABLE S VARCHAR(50);
        BEGIN
            S = '--';
            INSERT INTO AUDIT_LOG (ID) VALUES (1);
        END;
        """
        pg_str_dash = FirebirdToPostgresVisitor.transpile(fb_str_dash)
        self.assertIn("LANGUAGE plpgsql VOLATILE;", pg_str_dash)
        self.assertIn("data modification (DML)", pg_str_dash)

        # 2. String containing '/*' must not swallow code up to next comment
        fb_str_block = """
        CREATE OR ALTER PROCEDURE SP_STR_BLOCK
        AS
        DECLARE VARIABLE S VARCHAR(50);
        BEGIN
            S = '/* not comment';
            INSERT INTO AUDIT_LOG (ID) VALUES (1);
            /* harmless trailing comment */
        END;
        """
        pg_str_block = FirebirdToPostgresVisitor.transpile(fb_str_block)
        self.assertIn("LANGUAGE plpgsql VOLATILE;", pg_str_block)
        self.assertIn("data modification (DML)", pg_str_block)

        # 3. Comments containing DML must not trigger false positives (read-only stays STABLE)
        fb_comment_dml = """
        CREATE OR ALTER PROCEDURE SP_COMMENT_DML (P_ID INTEGER)
        RETURNS (NOME VARCHAR(100))
        AS
        BEGIN
            -- INSERT INTO AUDIT_LOG VALUES (99);
            /* UPDATE CLIENTES SET NOME = 'X'; */
            SELECT NOME FROM CLIENTES WHERE ID = :P_ID INTO :NOME;
            SUSPEND;
        END;
        """
        pg_comment_dml = FirebirdToPostgresVisitor.transpile(fb_comment_dml)
        self.assertIn("LANGUAGE plpgsql STABLE;", pg_comment_dml)
        self.assertIn("Volatility: STABLE", pg_comment_dml)
        self.assertNotIn("VOLATILE", pg_comment_dml)

        # 4. Unknown delimited call ("Q"()) remains conservatively VOLATILE
        fb_delim_call = """
        CREATE OR ALTER PROCEDURE SP_DELIM_CALL
        RETURNS (R INTEGER)
        AS
        BEGIN
            R = "Q"();
            SUSPEND;
        END;
        """
        pg_delim_call = FirebirdToPostgresVisitor.transpile(fb_delim_call)
        self.assertIn("LANGUAGE plpgsql VOLATILE;", pg_delim_call)
        self.assertIn('external function call ("q")', pg_delim_call)

        # 5. Unknown qualified call (schema.q()) remains conservatively VOLATILE
        fb_qual_call = """
        CREATE OR ALTER PROCEDURE SP_QUAL_CALL
        RETURNS (R INTEGER)
        AS
        BEGIN
            R = SCHEMA.Q();
            SUSPEND;
        END;
        """
        pg_qual_call = FirebirdToPostgresVisitor.transpile(fb_qual_call)
        self.assertIn("LANGUAGE plpgsql VOLATILE;", pg_qual_call)
        self.assertIn("external function call (SCHEMA.Q)", pg_qual_call)

        # 6. Parameter initializer with sequence generator participates in classification
        fb_param_seq = """
        CREATE OR ALTER PROCEDURE SP_PARAM_SEQ (P_ID INTEGER = GEN_ID(GEN_TEST, 1))
        RETURNS (R INTEGER)
        AS
        BEGIN
            R = P_ID;
            SUSPEND;
        END;
        """
        pg_param_seq = FirebirdToPostgresVisitor.transpile(fb_param_seq)
        self.assertIn("LANGUAGE plpgsql VOLATILE;", pg_param_seq)
        self.assertIn("sequence generator access", pg_param_seq)

        # 7. Variable declaration initializer with sequence participates in classification
        fb_var_seq = """
        CREATE OR ALTER PROCEDURE SP_VAR_SEQ
        RETURNS (R INTEGER)
        AS
        DECLARE VARIABLE V_ID INTEGER = GEN_ID(GEN_TEST, 1);
        BEGIN
            R = V_ID;
            SUSPEND;
        END;
        """
        pg_var_seq = FirebirdToPostgresVisitor.transpile(fb_var_seq)
        self.assertIn("LANGUAGE plpgsql VOLATILE;", pg_var_seq)
        self.assertIn("sequence generator access", pg_var_seq)

        # 8. Function calling another modifier
        fb_call_modifier = """
        CREATE OR ALTER PROCEDURE SP_CALL_MODIFIER
        AS
        BEGIN
            EXECUTE PROCEDURE SP_DO_UPDATE(10);
        END;
        """
        pg_call_modifier = FirebirdToPostgresVisitor.transpile(fb_call_modifier)
        self.assertIn("LANGUAGE plpgsql VOLATILE;", pg_call_modifier)
        self.assertIn("procedure call (PERFORM)", pg_call_modifier)

        # 9. Optimization advisories do not promise speculative caching, inlining, or unmeasured gains
        for out in (pg_str_dash, pg_str_block, pg_comment_dml, pg_delim_call, pg_param_seq):
            self.assertNotIn("memoization", out.lower())
            self.assertNotIn("optimizer caching", out.lower())
            self.assertNotIn("inlined", out.lower())
            self.assertNotIn("pushdown", out.lower())

    def test_disambiguation_with_table_alias_and_variable_conflict(self):
        fb_sql = """
        CREATE OR ALTER PROCEDURE SP_DISAMBIGUATION_TEST (ID INTEGER, VALOR NUMERIC(15,2))
        AS
        BEGIN
            UPDATE T X SET VALOR = :VALOR WHERE ID = :ID;
            UPDATE T SET VALOR = :VALOR WHERE ID = :ID;
            DELETE FROM T X WHERE ID = :ID;
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("#variable_conflict use_variable", pg_sql)
        self.assertIn("WHERE X.ID = ID", pg_sql)
        self.assertNotIn("TX.ID", pg_sql)
        self.assertIn("WHERE T.ID = ID", pg_sql)
        self.assertIn("DELETE FROM T X WHERE X.ID = ID", pg_sql)

    def test_not_null_parameter_guard_and_string_literal_preservation(self):
        fb_sql = """
        CREATE OR ALTER PROCEDURE SP_PARAM_NOT_NULL_TEST (
            P_REQ INTEGER NOT NULL,
            P_STATUS VARCHAR(20) DEFAULT 'NOT NULL',
            P_STRICT VARCHAR(20) NOT NULL DEFAULT 'NOT NULL'
        )
        AS
        BEGIN
            UPDATE CONTAS SET STATUS = :P_STATUS WHERE ID = :P_REQ;
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        # Verify default 'NOT NULL' string literals are preserved intact without being stripped to ''
        self.assertIn("P_STATUS VARCHAR(20) DEFAULT 'NOT NULL'", pg_sql)
        self.assertIn("P_STRICT VARCHAR(20) DEFAULT 'NOT NULL'", pg_sql)
        self.assertNotIn("DEFAULT ''", pg_sql)

        # Verify runtime NOT NULL checks are injected for NOT NULL parameters but not for nullable ones
        self.assertIn("IF P_REQ IS NULL THEN RAISE EXCEPTION 'Parameter \"%\" cannot be NULL', 'P_REQ'; END IF;", pg_sql)
        self.assertIn("IF P_STRICT IS NULL THEN RAISE EXCEPTION 'Parameter \"%\" cannot be NULL', 'P_STRICT'; END IF;", pg_sql)
        self.assertNotIn("IF P_STATUS IS NULL", pg_sql)

    def test_modern_and_binary_data_types_in_procedure(self):
        fb_sql = """
        CREATE PROCEDURE SP_MODERN_TYPES (
            P_I128 INT128,
            P_DEC16 DECFLOAT(16),
            P_DEC34 DECFLOAT(34),
            P_RAW VARCHAR(16) CHARACTER SET OCTETS
        )
        RETURNS (
            OUT_I128 INT128,
            OUT_DEC DECFLOAT
        )
        AS
        DECLARE VARIABLE V_BIG INT128;
        DECLARE VARIABLE V_BYTES CHAR(32) CHARACTER SET OCTETS;
        BEGIN
            V_BIG = P_I128;
            V_BYTES = P_RAW;
            OUT_I128 = V_BIG;
            OUT_DEC = P_DEC16;
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn('P_I128 NUMERIC(39)', pg_sql)
        self.assertIn('P_DEC16 NUMERIC', pg_sql)
        self.assertIn('P_DEC34 NUMERIC', pg_sql)
        self.assertIn('P_RAW BYTEA', pg_sql)
        self.assertIn('OUT OUT_I128 NUMERIC(39)', pg_sql)
        self.assertIn('OUT OUT_DEC NUMERIC', pg_sql)
        self.assertIn('V_BIG NUMERIC(39);', pg_sql)
        self.assertIn('V_BYTES BYTEA;', pg_sql)

    def test_first_skip_expressions_are_transpiled(self):
        fb_sql = """
        CREATE PROCEDURE SP_PAGINATE (N INTEGER, M INTEGER)
        AS
        DECLARE VARIABLE X INTEGER;
        BEGIN
            SELECT FIRST (IIF(:N > 0, :N, 1)) SKIP (IIF(:M > 0, :M, 0)) ID
            FROM TAB
            INTO :X;
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("LIMIT (CASE WHEN N > 0 THEN N ELSE 1 END)", pg_sql)
        self.assertIn("OFFSET (CASE WHEN M > 0 THEN M ELSE 0 END)", pg_sql)
    def test_regression_disambiguation_update_set_increment_preserves_column(self):
        fb_sql = """
        CREATE OR ALTER PROCEDURE SP_INC (V INTEGER)
        AS
        BEGIN
            UPDATE T SET V = V + 1;
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("UPDATE T SET V = T.V + 1;", pg_sql)
        self.assertNotIn("SET T.V =", pg_sql)

    def test_regression_disambiguation_update_set_bind_variable_preserves_variable(self):
        fb_sql = """
        CREATE OR ALTER PROCEDURE SP_SET_VAR (V INTEGER)
        AS
        BEGIN
            UPDATE T SET V = :V;
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("UPDATE T SET V = V;", pg_sql)
        self.assertNotIn("SET V = T.V;", pg_sql)

    def test_regression_disambiguation_where_id_equals_bind_variable(self):
        fb_sql = """
        CREATE OR ALTER PROCEDURE SP_WHERE_DISAMBIG (ID INTEGER, V INTEGER)
        AS
        BEGIN
            UPDATE T SET V = :V WHERE ID = :ID;
        END;
        """
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        self.assertIn("UPDATE T SET V = V WHERE T.ID = ID;", pg_sql)

    def test_regression_disambiguation_join_second_table_column(self):
        fb_sql = """
        CREATE OR ALTER PROCEDURE SP_JOIN_SECOND_TABLE
        AS
        BEGIN
            SELECT COL_A, COL_B FROM T1 JOIN T2 ON T1.ID = T2.ID WHERE COL_B = 10;
        END;
        """
        symbols = {
            't1.id': 'INTEGER',
            't1.col_a': 'INTEGER',
            't2.id': 'INTEGER',
            't2.col_b': 'VARCHAR',
        }
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql, symbols=symbols)
        self.assertIn("T1.COL_A", pg_sql)
        self.assertIn("T2.COL_B", pg_sql)
        self.assertNotIn("T1.COL_B", pg_sql)
        self.assertIn("WHERE T2.COL_B = 10", pg_sql)

    def test_regression_disambiguation_unresolvable_column_raises_explicit_diagnostic(self):
        fb_sql = """
        CREATE OR ALTER PROCEDURE SP_AMBIG_TEST
        AS
        BEGIN
            SELECT UNRESOLVED_COL FROM T1 JOIN T2 ON T1.ID = T2.ID;
        END;
        """
        symbols = {'t1.id': 'INTEGER', 't2.id': 'INTEGER', 'unresolved_col': 'VARCHAR'}
        with self.assertRaises(ValueError) as ctx:
            FirebirdToPostgresVisitor.transpile(fb_sql, symbols=symbols)
        self.assertIn("Unresolvable column reference 'unresolved_col'", str(ctx.exception))

    def test_regression_disambiguation_correlated_subquery_delimited_aliases_and_homonymous_var(self):
        fb_sql = """
        CREATE OR ALTER PROCEDURE SP_CORRELATED_TEST
        AS
        DECLARE VARIABLE "MY_VAR" INTEGER = 50;
        DECLARE VARIABLE VAL INTEGER = 10;
        BEGIN
            SELECT "OutTbl".VAL, "OutTbl"."ID"
            FROM "OuterTable" "OutTbl"
            WHERE EXISTS (
                SELECT 1
                FROM "InnerTable" "InTbl"
                WHERE "InTbl"."PARENT_ID" = "OutTbl"."ID"
                  AND VAL = :VAL
            );
        END;
        """
        symbols = {
            'outertable.val': 'INTEGER',
            'outertable.id': 'INTEGER',
            'innertable.parent_id': 'INTEGER',
            'innertable.val': 'INTEGER',
        }
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql, symbols=symbols)
        # Verify delimited aliases preserve quotes
        self.assertIn('"outertable" "outtbl"', pg_sql)
        self.assertIn('"innertable" "intbl"', pg_sql)
        # Verify correlated reference to outer table is preserved
        self.assertIn('"intbl"."parent_id" = "outtbl"."id"', pg_sql)
        # Verify inner table column VAL is qualified with inner alias, not outer alias or local var
        self.assertIn('"InTbl".VAL = VAL', pg_sql)








