import unittest
from unittest.mock import MagicMock, call
from engine.data_migrator import DataMigrator
from models import Table, Column


class TestDataMigrator(unittest.TestCase):
    def setUp(self):
        self.mock_fb_con = MagicMock()
        self.mock_pg_con = MagicMock()
        self.mock_fb_cur = MagicMock()
        self.mock_pg_cur = MagicMock()

        self.mock_pg_con.encoding = 'UTF8'
        self.mock_pg_cur.connection.encoding = 'UTF8'
        self.mock_pg_cur.mogrify.return_value = b"(1, 'test')"

        self.mock_fb_con.cursor.return_value = self.mock_fb_cur
        self.mock_pg_con.cursor.return_value = self.mock_pg_cur

        self.migrator = DataMigrator(self.mock_fb_con, self.mock_pg_con)

    def test_data_migration_sanitizes_nul_bytes_only_when_present(self):
        table = Table('CLIENTES')
        table.columns.append(Column('ID', 'INTEGER', nullable=False, sequence_name='GEN_CLIENTES_ID'))
        table.columns.append(Column('NOME', 'VARCHAR(100)', nullable=False))
        table.columns.append(Column('OBS', 'TEXT', nullable=True))

        # Row 1 has NUL byte in NOME, Row 2 is clean
        raw_rows = [
            (1, 'JOAO\x00 SILVA', 'OBS NORMAL'),
            (2, 'MARIA SANTOS', 'SEM NUL')
        ]

        # fetchmany returns rows first time, empty list second time
        self.mock_fb_cur.fetchmany.side_effect = [raw_rows, []]

        success = self.migrator.import_data([table])
        self.assertTrue(success)

        # Check commit was called
        self.mock_pg_con.commit.assert_called()

    def test_data_migration_zero_copy_for_numeric_tables(self):
        table = Table('ESTATISTICAS')
        table.columns.append(Column('ID', 'INTEGER', nullable=False))
        table.columns.append(Column('VALOR', 'NUMERIC(15,2)', nullable=False))
        table.columns.append(Column('QUANTIDADE', 'INTEGER', nullable=False))

        raw_rows = [
            (1, 150.50, 10),
            (2, 300.00, 20)
        ]

        self.mock_fb_cur.fetchmany.side_effect = [raw_rows, []]

        success = self.migrator.import_data([table])
        self.assertTrue(success)

    def test_data_migration_handles_failure_and_rollback(self):
        table = Table('FALHA')
        table.columns.append(Column('ID', 'INTEGER', nullable=False))

        self.mock_fb_cur.fetchmany.side_effect = Exception("DB Connection dropped")

        success = self.migrator.import_data([table])
        self.assertFalse(success)
        self.mock_pg_con.rollback.assert_called()
