import unittest
from unittest.mock import MagicMock

from engine.schema_extractor import SchemaExtractor
from models import Table, Column


class TestSchemaExtractorSequenceBinding(unittest.TestCase):
    def test_bind_sequence_generators_case_insensitivity_and_variations(self):
        table1 = Table('CLIENTES')
        col1 = Column('ID', 'INTEGER', nullable=False)
        table1.columns.append(col1)

        table2 = Table('PEDIDOS')
        col2 = Column('NUMERO', 'INTEGER', nullable=False)
        col3 = Column('CODIGO_EXTERNO', 'INTEGER', nullable=False)
        table2.columns.append(col2)
        table2.columns.append(col3)

        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            # Lowercase relation & column, mixed-case gen_id
            ("clientes", "AS BEGIN if (new.id is null) then new.id = gen_id(gen_clientes_id, 1); END;"),
            # Upper relation, multiple assignments in same trigger including NEXT VALUE FOR
            ("PEDIDOS", "AS BEGIN NEW.NUMERO = GEN_ID(GEN_PEDIDOS, 1); new.codigo_externo = next value for GEN_COD_EXT; END;"),
        ]

        SchemaExtractor._bind_sequence_generators(mock_cursor, [table1, table2])

        self.assertEqual(col1.sequence_name, "gen_clientes_id")
        self.assertEqual(col2.sequence_name, "gen_pedidos")
        self.assertEqual(col3.sequence_name, "gen_cod_ext")

    def test_bind_sequence_generators_ignores_inactive_triggers_in_sql(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []

        table = Table('USERS')
        table.columns.append(Column('ID', 'INTEGER', nullable=False))

        SchemaExtractor._bind_sequence_generators(mock_cursor, [table])

        # Verify SQL query executed includes inactive trigger filter
        called_sql = mock_cursor.execute.call_args[0][0]
        self.assertIn("RDB$TRIGGER_INACTIVE = 0", called_sql)
        self.assertIn("RDB$TRIGGER_INACTIVE IS NULL", called_sql)

    def test_bind_sequence_generators_filters_non_defaults_and_comments(self):
        table = Table('USERS')
        col_id = Column('ID', 'INTEGER', nullable=False)
        col_ext = Column('EXT_ID', 'INTEGER', nullable=True)
        col_audit = Column('AUDIT_ID', 'INTEGER', nullable=True)
        table.columns.extend([col_id, col_ext, col_audit])

        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            # Commented out code should NOT bind
            ("USERS", "AS BEGIN /* NEW.ID = GEN_ID(GEN_COMMENTED, 1); */ -- NEW.ID = GEN_ID(GEN_SINGLE, 1);\n END;", 1),
            # Step 0 (inspect current value) should NOT bind
            ("USERS", "AS BEGIN NEW.ID = GEN_ID(GEN_CURRENT, 0); END;", 1),
            # Condition on another column should NOT bind (arbitrary business logic)
            ("USERS", "AS BEGIN IF (NEW.STATUS = 'SPECIAL') THEN NEW.EXT_ID = GEN_ID(GEN_SPECIAL, 1); END;", 1),
            # Non-BEFORE INSERT trigger (e.g. trigger_type 3 = BEFORE UPDATE) should NOT bind
            ("USERS", "AS BEGIN NEW.AUDIT_ID = GEN_ID(GEN_AUDIT, 1); END;", 3),
        ]

        SchemaExtractor._bind_sequence_generators(mock_cursor, [table])

        self.assertIsNone(col_id.sequence_name)
        self.assertIsNone(col_ext.sequence_name)
        self.assertIsNone(col_audit.sequence_name)

    def test_extract_columns_transpiles_computed_source(self):
        mock_cursor = MagicMock()
        # column tuple: name, type, subtype, length, null_flag, prec, scale, col_def, dom_def, fld_src, comp_src
        mock_cursor.fetchall.return_value = [
            ("TOTAL", 16, 2, 8, 1, 15, 2, None, None, "RDB$123", "IIF(STATUS = 1, 100, 0)"),
        ]

        columns = SchemaExtractor._extract_columns(mock_cursor, "SALES", {"SALES"})
        self.assertEqual(len(columns), 1)
        self.assertFalse(columns[0].nullable)
        self.assertEqual(columns[0].computed_source, "CASE WHEN STATUS = 1 THEN 100 ELSE 0 END")

    def test_extract_columns_passes_symbols_for_time_expressions(self):
        mock_cursor = MagicMock()
        # column tuple: name, type, subtype, length, null_flag, prec, scale, col_def, dom_def, fld_src, comp_src
        # Firebird type 13 = TIME
        mock_cursor.fetchall.return_value = [
            ("START_TIME", 13, 0, 4, 1, None, None, None, None, "RDB$1", None),
            ("END_TIME", 13, 0, 4, 1, None, None, None, None, "RDB$2", None),
            ("DURATION", 8, 0, 4, 1, None, None, None, None, "RDB$3", "DATEDIFF(HOUR, START_TIME, END_TIME)"),
        ]

        columns = SchemaExtractor._extract_columns(mock_cursor, "SHIFTS", {"SHIFTS"})
        self.assertEqual(len(columns), 3)
        self.assertNotIn("::timestamp", columns[2].computed_source)
        self.assertIn("DATE_TRUNC('hour', END_TIME)", columns[2].computed_source)

    def test_extract_indexes_transpiles_expression(self):
        mock_cursor = MagicMock()
        # index tuple: index_name, unique, inactive, col_name, col_pos, expr_source
        mock_cursor.fetchall.return_value = [
            ("IDX_EXPR", 0, 0, None, 0, "DATEADD(DAY, 5, DT)"),
        ]

        indexes = SchemaExtractor._extract_indexes(mock_cursor, "SALES")
        self.assertEqual(len(indexes), 1)
        self.assertEqual(indexes[0].expression, "(DT + (5) * INTERVAL '1 day')")

    def test_extract_indexes_passes_symbols_for_time_expressions(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            ("IDX_TIME_DIFF", 0, 0, None, 0, "DATEDIFF(MINUTE, START_TIME, END_TIME)"),
        ]

        symbols = {"start_time": "TIME", "end_time": "TIME"}
        indexes = SchemaExtractor._extract_indexes(mock_cursor, "SHIFTS", symbols=symbols)
        self.assertEqual(len(indexes), 1)
        self.assertNotIn("::timestamp", indexes[0].expression)
        self.assertIn("DATE_TRUNC('minute', END_TIME)", indexes[0].expression)

    def test_transpile_expression_functions(self):
        from transpiler import FirebirdToPostgresVisitor
        self.assertEqual(
            FirebirdToPostgresVisitor.transpile_expression("IIF(X > 0, 'Y', 'N')"),
            "CASE WHEN X > 0 THEN 'Y' ELSE 'N' END",
        )
        self.assertEqual(
            FirebirdToPostgresVisitor.transpile_expression("DATEADD(MONTH, 2, DT)"),
            "(DT + (2) * INTERVAL '1 month')",
        )
        self.assertEqual(
            FirebirdToPostgresVisitor.transpile_expression("DATEDIFF(DAY, D1, D2)"),
            "(DATE(D2) - DATE(D1))",
        )
        self.assertEqual(
            FirebirdToPostgresVisitor.transpile_expression("DATEDIFF(WEEK, D1, D2)"),
            "((DATE_TRUNC('week', D2::timestamp)::date - DATE_TRUNC('week', D1::timestamp)::date) / 7)",
        )
        self.assertEqual(
            FirebirdToPostgresVisitor.transpile_expression("DATEDIFF(HOUR, D1, D2)"),
            "ROUND(EXTRACT(EPOCH FROM (DATE_TRUNC('hour', D2::timestamp) - DATE_TRUNC('hour', D1::timestamp))) / 3600)",
        )
        self.assertEqual(
            FirebirdToPostgresVisitor.transpile_expression("DATEDIFF(MINUTE, D1, D2)"),
            "ROUND(EXTRACT(EPOCH FROM (DATE_TRUNC('minute', D2::timestamp) - DATE_TRUNC('minute', D1::timestamp))) / 60)",
        )
        self.assertEqual(
            FirebirdToPostgresVisitor.transpile_expression("DATEDIFF(SECOND, D1, D2)"),
            "ROUND(EXTRACT(EPOCH FROM (DATE_TRUNC('second', D2::timestamp) - DATE_TRUNC('second', D1::timestamp))))",
        )
        self.assertEqual(
            FirebirdToPostgresVisitor.transpile_expression("DATEDIFF(MILLISECOND, D1, D2)"),
            "ROUND((EXTRACT(EPOCH FROM (D2::timestamp - D1::timestamp)) * 1000)::numeric, 1)",
        )
        self.assertEqual(
            FirebirdToPostgresVisitor.transpile_expression("DATEDIFF(HOUR, TIME '10:59', TIME '11:00')"),
            "ROUND(EXTRACT(EPOCH FROM (DATE_TRUNC('hour', TIME '11:00') - DATE_TRUNC('hour', TIME '10:59'))) / 3600)",
        )
        self.assertEqual(
            FirebirdToPostgresVisitor.transpile_expression("DATEDIFF(MINUTE, TIME '10:59', TIME '11:00')"),
            "ROUND(EXTRACT(EPOCH FROM (DATE_TRUNC('minute', TIME '11:00') - DATE_TRUNC('minute', TIME '10:59'))) / 60)",
        )
        self.assertEqual(
            FirebirdToPostgresVisitor.transpile_expression("DATEDIFF(SECOND, TIME '10:59:00', TIME '10:59:05')"),
            "ROUND(EXTRACT(EPOCH FROM (DATE_TRUNC('second', TIME '10:59:05') - DATE_TRUNC('second', TIME '10:59:00'))))",
        )
        self.assertEqual(
            FirebirdToPostgresVisitor.transpile_expression("DATEDIFF(MILLISECOND, TIME '10:59:00.0000', TIME '10:59:00.0001')"),
            "ROUND((EXTRACT(EPOCH FROM (TIME '10:59:00.0001' - TIME '10:59:00.0000')) * 1000)::numeric, 1)",
        )
        with self.assertRaises(RuntimeError) as cm:
            FirebirdToPostgresVisitor.transpile_expression("DATEDIFF(DAY, TIME '10:00', TIME '11:00')")
        self.assertIn("cannot be used with TIME values", str(cm.exception))
        self.assertEqual(
            FirebirdToPostgresVisitor.transpile_expression("GEN_ID(GEN_SEQ, 1)"),
            "nextval('GEN_SEQ')",
        )
        self.assertEqual(
            FirebirdToPostgresVisitor.transpile_expression("DATEADD(1 DAY TO D)"),
            "(D + (1) * INTERVAL '1 day')",
        )
        self.assertEqual(
            FirebirdToPostgresVisitor.transpile_expression("DATEADD((N + 1) DAY TO D)"),
            "(D + ((N + 1)) * INTERVAL '1 day')",
        )
        self.assertEqual(
            FirebirdToPostgresVisitor.transpile_expression("DATEDIFF(DAY FROM D1 TO D2)"),
            "(DATE(D2) - DATE(D1))",
        )
        self.assertEqual(
            FirebirdToPostgresVisitor.transpile_expression("DATEDIFF(DAY FROM (D1 + 1) TO (D2 - 1))"),
            "(DATE((D2 - 1)) - DATE((D1 + 1)))",
        )
        self.assertEqual(
            FirebirdToPostgresVisitor.transpile_expression("EXTRACT(WEEKDAY FROM D)"),
            "EXTRACT(DOW FROM D)",
        )
        self.assertEqual(
            FirebirdToPostgresVisitor.transpile_expression("EXTRACT(YEARDAY FROM D)"),
            "((EXTRACT(DOY FROM D))::integer - 1)",
        )
        self.assertEqual(
            FirebirdToPostgresVisitor.transpile_expression("EXTRACT(MILLISECOND FROM TS)"),
            "(FLOOR(EXTRACT(MILLISECOND FROM TS))::integer % 1000)",
        )
        with self.assertRaises(RuntimeError) as cm:
            FirebirdToPostgresVisitor.transpile_expression("FOOBAR $$$ INVALID")
        self.assertIn("Failed to transpile Firebird expression", str(cm.exception))

    def test_validate_immutable_expression(self):
        from transpiler import validate_immutable_expression

        # Valid immutable expressions (including string constants and comments)
        validate_immutable_expression("(D + 1)")
        validate_immutable_expression("'TODAY'")
        validate_immutable_expression("CASE WHEN STATUS = 'TODAY' THEN 1 ELSE 0 END")
        validate_immutable_expression("CASE WHEN STATUS = 'CURRENT_DATE' THEN 1 ELSE 0 END")
        validate_immutable_expression("1 /* CURRENT_TIMESTAMP */")
        validate_immutable_expression("1 -- CURRENT_TIMESTAMP")
        validate_immutable_expression("1 /* CAST('TODAY' AS DATE) */")
        validate_immutable_expression("'--'")
        validate_immutable_expression("'/*'")
        validate_immutable_expression("'*/'")

        # Non-immutable functions, sequences or dynamic date casts
        with self.assertRaises(ValueError):
            validate_immutable_expression("CURRENT_DATE")
        with self.assertRaises(ValueError):
            validate_immutable_expression("CURRENT_TIMESTAMP")
        with self.assertRaises(ValueError):
            validate_immutable_expression("NOW()")
        with self.assertRaises(ValueError):
            validate_immutable_expression("RANDOM()")
        with self.assertRaises(ValueError):
            validate_immutable_expression("CAST('TODAY' AS DATE)")
        with self.assertRaises(ValueError):
            validate_immutable_expression("nextval('g')")
        with self.assertRaises(ValueError):
            validate_immutable_expression("currval('g')")
        with self.assertRaises(ValueError):
            validate_immutable_expression("setval('g', 1)")
        with self.assertRaises(ValueError):
            validate_immutable_expression("'--' || CAST(CURRENT_DATE AS VARCHAR(20))")
        with self.assertRaises(ValueError):
            validate_immutable_expression("'/*' || CURRENT_TIMESTAMP")
        with self.assertRaises(ValueError):
            validate_immutable_expression("'*/' || NOW()")

    def test_extract_columns_rejects_non_immutable_expression(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            ("COL1", 12, 0, 4, 1, 0, 0, None, None, "RDB$1", "CURRENT_DATE"),
        ]
        with self.assertRaises(ValueError) as cm:
            SchemaExtractor._extract_columns(mock_cursor, "SALES", {"SALES"})
        self.assertIn("computed column 'COL1' in table 'SALES'", str(cm.exception))

    def test_extract_indexes_rejects_non_immutable_expression(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            ("IDX_NOW", 0, 0, None, 0, "CURRENT_TIMESTAMP"),
        ]
        with self.assertRaises(ValueError) as cm:
            SchemaExtractor._extract_indexes(mock_cursor, "SALES")
        self.assertIn("expression index 'IDX_NOW' in table 'SALES'", str(cm.exception))


    def test_extract_sequences_standalone_and_current_values(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            ("GEN_CLIENTES_ID   ",),
            ("GEN_TATENDIMENTOS_APAC_ID   ",),
            ("GEN_TPROCS_ATENDIMENTO_APAC_ID",),
        ]
        mock_cursor.fetchone.side_effect = [
            (50,),
            (120,),
            (0,),
        ]

        sequences = SchemaExtractor._extract_sequences(mock_cursor)
        self.assertEqual(len(sequences), 3)

        self.assertEqual(sequences[0].name, "GEN_CLIENTES_ID")
        self.assertEqual(sequences[0].pg_name, "gen_clientes_id")
        self.assertEqual(sequences[0].current_value, 50)
        self.assertEqual(sequences[0].get_create_sequence_query(), 'CREATE SEQUENCE "gen_clientes_id" START WITH 51;')

        self.assertEqual(sequences[1].name, "GEN_TATENDIMENTOS_APAC_ID")
        self.assertEqual(sequences[1].pg_name, "gen_tatendimentos_apac_id")
        self.assertEqual(sequences[1].current_value, 120)
        self.assertEqual(sequences[1].get_create_sequence_query(), 'CREATE SEQUENCE "gen_tatendimentos_apac_id" START WITH 121;')

        self.assertEqual(sequences[2].name, "GEN_TPROCS_ATENDIMENTO_APAC_ID")
        self.assertEqual(sequences[2].pg_name, "gen_tprocs_atendimento_apac_id")
        self.assertEqual(sequences[2].current_value, 0)
        self.assertEqual(sequences[2].get_create_sequence_query(), 'CREATE SEQUENCE "gen_tprocs_atendimento_apac_id";')

    def test_extract_sequences_quotes_names_and_supports_negative_values(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            ('gen_lowercase',),
            ('GEN_WITH_"QUOTE"',),
        ]
        mock_cursor.fetchone.side_effect = [
            (-15,),
            (-1,),
        ]

        sequences = SchemaExtractor._extract_sequences(mock_cursor)
        self.assertEqual(len(sequences), 2)
        self.assertEqual(sequences[0].name, 'gen_lowercase')
        self.assertEqual(sequences[0].current_value, -15)
        self.assertEqual(
            sequences[0].get_create_sequence_query(),
            'CREATE SEQUENCE "gen_lowercase" MINVALUE -9223372036854775807 START WITH -14;'
        )
        self.assertEqual(sequences[1].current_value, -1)
        self.assertEqual(
            sequences[1].get_create_sequence_query(),
            'CREATE SEQUENCE "gen_with_""quote""" MINVALUE -9223372036854775807 START WITH 0;'
        )

        executed_queries = [call[0][0] for call in mock_cursor.execute.call_args_list[1:]]
        self.assertIn('SELECT GEN_ID("gen_lowercase", 0) FROM RDB$DATABASE;', executed_queries)
        self.assertIn('SELECT GEN_ID("GEN_WITH_""QUOTE""", 0) FROM RDB$DATABASE;', executed_queries)

    def test_extract_sequences_raises_on_read_failure(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("GEN_FAIL",)]
        mock_cursor.fetchone.side_effect = Exception("Firebird connection dropped")

        with self.assertRaises(RuntimeError) as cm:
            SchemaExtractor._extract_sequences(mock_cursor)
        self.assertIn("Failed to read current value for generator 'GEN_FAIL'", str(cm.exception))

    def test_extract_sequences_raises_on_none_row(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("GEN_NONE",)]
        mock_cursor.fetchone.return_value = None

        with self.assertRaises(RuntimeError) as cm:
            SchemaExtractor._extract_sequences(mock_cursor)
        self.assertIn("no value returned", str(cm.exception))

    def test_extract_check_constraints(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            ("CHK_QUANTIDADE", "CHECK (QUANTIDADE > 0)"),
            ("CHK_VALOR", "VALOR >= 0"),
        ]
        checks = SchemaExtractor._extract_check_constraints(mock_cursor, "ITENS")
        self.assertEqual(len(checks), 2)
        self.assertEqual(checks[0].name, "chk_quantidade")
        self.assertEqual(checks[0].expression, "QUANTIDADE > 0")
        self.assertEqual(checks[1].name, "chk_valor")
        self.assertEqual(checks[1].expression, "VALOR >= 0")


if __name__ == '__main__':
    unittest.main()

