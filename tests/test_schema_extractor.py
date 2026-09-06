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
            FirebirdToPostgresVisitor.transpile_expression("GEN_ID(GEN_SEQ, 1)"),
            "nextval('GEN_SEQ')",
        )


if __name__ == '__main__':
    unittest.main()

