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

    def test_extract_indexes_transpiles_expression(self):
        mock_cursor = MagicMock()
        # index tuple: index_name, unique, inactive, col_name, col_pos, expr_source
        mock_cursor.fetchall.return_value = [
            ("IDX_EXPR", 0, 0, None, 0, "DATEADD(DAY, 5, DT)"),
        ]

        indexes = SchemaExtractor._extract_indexes(mock_cursor, "SALES")
        self.assertEqual(len(indexes), 1)
        self.assertEqual(indexes[0].expression, "(DT + (5) * INTERVAL '1 day')")

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
            "ROUND(EXTRACT(EPOCH FROM (DATE_TRUNC('milliseconds', D2::timestamp) - DATE_TRUNC('milliseconds', D1::timestamp))) * 1000)",
        )
        self.assertEqual(
            FirebirdToPostgresVisitor.transpile_expression("GEN_ID(GEN_SEQ, 1)"),
            "nextval('GEN_SEQ')",
        )


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


if __name__ == '__main__':
    unittest.main()

