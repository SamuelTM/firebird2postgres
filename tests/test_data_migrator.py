import unittest
from unittest.mock import MagicMock

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

        self.mock_fb_cur.fetchmany.side_effect = OSError("DB Connection dropped")

        success = self.migrator.import_data([table], max_workers=1)
        self.assertFalse(success)
        self.mock_pg_con.rollback.assert_called()

    def test_parallel_data_migration_with_workers(self):
        from unittest.mock import patch, MagicMock

        t1 = Table('TABELA1')
        t1.columns.append(Column('ID', 'INTEGER', nullable=False))
        t2 = Table('TABELA2')
        t2.columns.append(Column('ID', 'INTEGER', nullable=False))

        created_fb_conns = []
        created_pg_conns = []

        class MockFbCursor:
            def __init__(self):
                self._fetched = False

            def execute(self, query):
                self._fetched = False

            def fetchmany(self, batch_size):
                if not self._fetched:
                    self._fetched = True
                    return [(1,), (2,)]
                return []

        def make_fb_con():
            fb_con = MagicMock()
            cur = MockFbCursor()
            fb_con.cursor.return_value = cur
            created_fb_conns.append(fb_con)
            return fb_con

        def make_pg_con():
            pg_con = MagicMock()
            pg_cur = MagicMock()
            pg_con.encoding = 'UTF8'
            pg_cur.connection.encoding = 'UTF8'
            pg_cur.mogrify.return_value = b"(1)"
            pg_con.cursor.return_value = pg_cur
            created_pg_conns.append(pg_con)
            return pg_con

        from concurrent.futures import ThreadPoolExecutor

        with patch('engine.data_migrator.get_firebird_connection', side_effect=make_fb_con), \
             patch('engine.data_migrator.get_postgres_connection', side_effect=make_pg_con), \
             ThreadPoolExecutor(max_workers=2) as test_executor:

            success = self.migrator.import_data([t1, t2], max_workers=2, executor=test_executor)
            self.assertTrue(success)

            # Each worker opened its own isolated connection
            self.assertEqual(len(created_fb_conns), 2)
            self.assertEqual(len(created_pg_conns), 2)

            # All worker connections were cleanly closed
            for fb_conn in created_fb_conns:
                fb_conn.close.assert_called_once()
            for pg_conn in created_pg_conns:
                pg_conn.close.assert_called_once()

            # Commits were executed across worker connections
            total_commits = sum(pg_conn.commit.call_count for pg_conn in created_pg_conns)
            self.assertGreaterEqual(total_commits, 2)


