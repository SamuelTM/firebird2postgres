import unittest
from unittest.mock import MagicMock
from engine.schema_migrator import SchemaMigrator
from models import Table, Column, ForeignKey, UniqueKey, Index


class TestSchemaMigrator(unittest.TestCase):
    def setUp(self):
        self.mock_pg_con = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_pg_con.cursor.return_value = self.mock_cursor
        self.migrator = SchemaMigrator(self.mock_pg_con)

        # Build sample tables
        self.table = Table('CLIENTES')
        self.table.columns.append(Column('ID', 'INTEGER', nullable=False, sequence_name='GEN_CLIENTES_ID'))
        self.table.columns.append(Column('NOME', 'VARCHAR(100)', nullable=False))
        self.table.unique_keys.append(UniqueKey('PK_CLIENTES', 'ID', is_primary_key=True))
        self.table.indexes.append(
            Index('IDX_CLIENTES_NOME', unique=False, inactive=False, column_name='NOME', column_index=0))

        self.table_orders = Table('ORDERS')
        self.table_orders.columns.append(Column('ID', 'INTEGER', nullable=False))
        self.table_orders.columns.append(Column('CLIENTE_ID', 'INTEGER', nullable=False))
        self.table_orders.foreign_keys.append(
            ForeignKey('FK_ORDERS_CLIENTES', 'CLIENTE_ID', 0, 'CLIENTES', 'ID', 0)
        )

    def test_create_tables_only_creates_tables_and_sequences(self):
        self.migrator.create_tables([self.table, self.table_orders])

        executed_queries = [call[0][0] for call in self.mock_cursor.execute.call_args_list]

        # Should drop old tables/sequences
        self.assertTrue(any('DROP TABLE IF EXISTS "clientes" CASCADE;' in q for q in executed_queries))
        self.assertTrue(any('DROP SEQUENCE IF EXISTS "gen_clientes_id" CASCADE;' in q for q in executed_queries))

        # Should create sequences and tables
        self.assertTrue(any('CREATE SEQUENCE "gen_clientes_id";' in q for q in executed_queries))
        self.assertTrue(any('CREATE TABLE "clientes"' in q for q in executed_queries))
        self.assertTrue(any('CREATE TABLE "orders"' in q for q in executed_queries))

        # Should NOT create constraints or secondary indexes in base table creation
        self.assertFalse(any('PRIMARY KEY' in q for q in executed_queries))
        self.assertFalse(any('CREATE INDEX' in q for q in executed_queries))
        self.assertFalse(any('FOREIGN KEY' in q for q in executed_queries))

        self.mock_pg_con.commit.assert_called()

    def test_create_constraints_and_indexes(self):
        self.migrator.create_constraints_and_indexes([self.table, self.table_orders])

        executed_queries = [call[0][0] for call in self.mock_cursor.execute.call_args_list]

        # Should create PK / Unique Keys
        self.assertTrue(
            any('ALTER TABLE "clientes" ADD CONSTRAINT "pk_clientes" PRIMARY KEY' in q for q in executed_queries))

        # Should create Secondary Indexes
        self.assertTrue(any('CREATE INDEX "idx_clientes_nome" ON "clientes"' in q for q in executed_queries))

        # Should create Foreign Keys
        self.assertTrue(
            any('ALTER TABLE "orders" ADD CONSTRAINT "fk_orders_clientes" FOREIGN KEY' in q for q in executed_queries))

        self.mock_pg_con.commit.assert_called()

    def test_migrate_schema_combines_both_steps(self):
        self.migrator.migrate_schema([self.table, self.table_orders])

        executed_queries = [call[0][0] for call in self.mock_cursor.execute.call_args_list]

        self.assertTrue(any('CREATE TABLE "clientes"' in q for q in executed_queries))
        self.assertTrue(any('PRIMARY KEY' in q for q in executed_queries))
        self.assertTrue(any('CREATE INDEX' in q for q in executed_queries))
        self.assertTrue(any('FOREIGN KEY' in q for q in executed_queries))

    def test_drop_schema(self):
        self.mock_cursor.fetchall.return_value = [('public', 'dom_status')]

        self.migrator.drop_schema([self.table])

        executed_queries = [call[0][0] for call in self.mock_cursor.execute.call_args_list]

        self.assertTrue(any('DROP TABLE IF EXISTS "clientes" CASCADE;' in q for q in executed_queries))
        self.assertTrue(any('DROP SEQUENCE IF EXISTS "gen_clientes_id" CASCADE;' in q for q in executed_queries))
        self.assertTrue(any('DROP DOMAIN "public"."dom_status" CASCADE;' in q for q in executed_queries))
        self.mock_pg_con.commit.assert_called()
