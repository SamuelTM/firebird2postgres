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


if __name__ == '__main__':
    unittest.main()
