import unittest
from models import (
    Table,
    Column,
    ForeignKey,
    UniqueKey,
    Index,
    get_postgres_type,
    resolve_firebird_type,
    resolve_pg_domain_name,
    decode_trigger_type,
)


class TestFirebirdTypes(unittest.TestCase):
    def test_get_postgres_type_basic_mappings(self):
        self.assertEqual(get_postgres_type('SMALLINT'), 'SMALLINT')
        self.assertEqual(get_postgres_type('INTEGER'), 'INTEGER')
        self.assertEqual(get_postgres_type('FLOAT'), 'REAL')
        self.assertEqual(get_postgres_type('DOUBLE PRECISION'), 'DOUBLE PRECISION')
        self.assertEqual(get_postgres_type('BLOB SUBTYPE 1'), 'TEXT')
        self.assertEqual(get_postgres_type('BLOB SUBTYPE 0'), 'BYTEA')
        self.assertEqual(get_postgres_type('VARCHAR(100)'), 'VARCHAR(100)')
        self.assertEqual(get_postgres_type('CUSTOM_TYPE'), 'CUSTOM_TYPE')

    def test_resolve_firebird_type(self):
        # 7 = SMALLINT, 8 = INTEGER, 14 = CHAR, 37 = VARCHAR, 16 = BIGINT / INT64
        self.assertEqual(resolve_firebird_type(field_type=8), 'INTEGER')
        self.assertEqual(resolve_firebird_type(field_type=7), 'SMALLINT')
        self.assertEqual(resolve_firebird_type(field_type=37, field_length=50), 'VARCHAR(50)')
        self.assertEqual(resolve_firebird_type(field_type=14, field_length=10), 'CHAR(10)')
        # Numeric with precision and scale
        self.assertEqual(resolve_firebird_type(field_type=16, field_subtype=1, field_precision=15, field_scale=-2), 'NUMERIC(15, 2)')
        self.assertEqual(resolve_firebird_type(field_type=8, field_subtype=1, field_precision=9, field_scale=0), 'NUMERIC(9, 0)')
        self.assertEqual(resolve_firebird_type(field_type=8, field_subtype=1, field_precision=None), 'NUMERIC')
        self.assertEqual(resolve_firebird_type(field_type=261, field_subtype=1), 'BLOB SUBTYPE 1')
        self.assertEqual(resolve_firebird_type(field_type=261, field_subtype=0), 'BLOB SUBTYPE 0')
        # Unknown type
        self.assertIsNone(resolve_firebird_type(field_type=999))

    def test_resolve_pg_domain_name(self):
        relation_names = {'users', 'orders'}
        # Domain name with no relation collision is lowercased
        self.assertEqual(resolve_pg_domain_name('DOM_STATUS', relation_names), 'dom_status')
        # Domain name that collides with a relation name gets _dom suffix
        self.assertEqual(resolve_pg_domain_name('USERS', relation_names), 'users_dom')
        self.assertEqual(resolve_pg_domain_name('orders', relation_names), 'orders_dom')
        # Cascading collision resolution
        relation_names_collision = {'users', 'users_dom'}
        self.assertEqual(resolve_pg_domain_name('USERS', relation_names_collision), 'users_dom_dom')

    def test_decode_trigger_type(self):
        # 1 = BEFORE INSERT, 2 = AFTER INSERT, 3 = BEFORE UPDATE, 4 = AFTER UPDATE, 5 = BEFORE DELETE, 6 = AFTER DELETE
        self.assertIn('BEFORE INSERT', decode_trigger_type(1))
        self.assertIn('AFTER INSERT', decode_trigger_type(2))
        self.assertIn('BEFORE UPDATE', decode_trigger_type(3))
        self.assertIn('AFTER UPDATE', decode_trigger_type(4))
        self.assertIn('BEFORE DELETE', decode_trigger_type(5))
        self.assertIn('AFTER DELETE', decode_trigger_type(6))
        # Multi-action trigger: bit 1 (insert) and bit 3 (update)
        # raw = phase | (1 << 1) | (2 << 3) = 0 | 2 | 16 = 18 -> trigger_type = 17
        decoded = decode_trigger_type(17)
        self.assertTrue('BEFORE' in decoded and 'INSERT' in decoded and 'UPDATE' in decoded)
        # Unknown trigger type
        self.assertEqual(decode_trigger_type(-1), '/* UNKNOWN TYPE -1 */')


class TestTableDdlGenerators(unittest.TestCase):
    def test_table_create_and_sequence_ddl(self):
        table = Table('CLIENTES')
        table.columns.append(Column('ID', 'INTEGER', nullable=False, sequence_name='GEN_CLIENTES_ID'))
        table.columns.append(Column('NOME', 'VARCHAR(100)', nullable=False))
        table.columns.append(Column('OBS', 'TEXT', nullable=True, default_value="'N/A'"))
        table.columns.append(Column('STATUS', 'VARCHAR(10)', nullable=False, domain_name='dom_status'))

        # Sequences
        seqs = table.get_sequence_queries()
        self.assertEqual(len(seqs), 1)
        self.assertEqual(seqs[0], 'CREATE SEQUENCE "gen_clientes_id";')

        # Create Table
        create_sql = table.get_create_table_query()
        self.assertIn('CREATE TABLE "clientes"', create_sql)
        self.assertIn('"id" INTEGER DEFAULT nextval(\'"gen_clientes_id"\') NOT NULL', create_sql)
        self.assertIn('"nome" VARCHAR(100) NOT NULL', create_sql)
        self.assertIn('"obs" TEXT \'N/A\'', create_sql)
        self.assertIn('"status" public."dom_status" NOT NULL', create_sql)

    def test_table_unique_keys_ddl(self):
        table = Table('USERS')
        table.unique_keys.append(UniqueKey('PK_USERS', column='ID', is_primary_key=True))
        table.unique_keys.append(UniqueKey('UQ_USERS_EMAIL', column='EMAIL', is_primary_key=False))

        uq_sql = table.get_unique_keys_query()
        self.assertIsNotNone(uq_sql)
        self.assertEqual(
            'ALTER TABLE "users" ADD CONSTRAINT "pk_users" PRIMARY KEY ("id"), ADD CONSTRAINT "uq_users_email" UNIQUE ("email");',
            uq_sql
        )

    def test_table_composite_unique_keys_ddl(self):
        table = Table('USER_ROLES')
        table.unique_keys.append(UniqueKey('PK_USER_ROLES', column='ROLE_ID', is_primary_key=True))
        table.unique_keys.append(UniqueKey('PK_USER_ROLES', column='USER_ID', is_primary_key=True))

        uq_sql = table.get_unique_keys_query()
        self.assertIsNotNone(uq_sql)
        self.assertEqual(
            'ALTER TABLE "user_roles" ADD CONSTRAINT "pk_user_roles" PRIMARY KEY ("role_id", "user_id");',
            uq_sql
        )

    def test_table_foreign_keys_ddl(self):
        table = Table('ORDERS')
        table.foreign_keys.append(
            ForeignKey(
                key_name='FK_ORDERS_CLIENTE',
                local_column_name='CLIENTE_ID',
                local_column_index=0,
                referenced_table_name='CLIENTES',
                referenced_column_name='ID',
                referenced_column_index=0,
            )
        )

        fk_sql = table.get_foreign_keys_query()
        self.assertIsNotNone(fk_sql)
        self.assertEqual(
            'ALTER TABLE "orders" ADD CONSTRAINT "fk_orders_cliente" FOREIGN KEY ("cliente_id") REFERENCES "clientes"("id");',
            fk_sql
        )

    def test_table_composite_foreign_keys_ddl(self):
        table = Table('ORDER_ITEMS')
        table.foreign_keys.append(
            ForeignKey(
                key_name='FK_ORDER_ITEMS_ORDER',
                local_column_name='ORDER_ID',
                local_column_index=0,
                referenced_table_name='ORDERS',
                referenced_column_name='ID',
                referenced_column_index=0,
            )
        )
        table.foreign_keys.append(
            ForeignKey(
                key_name='FK_ORDER_ITEMS_ORDER',
                local_column_name='COMPANY_ID',
                local_column_index=1,
                referenced_table_name='ORDERS',
                referenced_column_name='COMPANY_ID',
                referenced_column_index=1,
            )
        )

        fk_sql = table.get_foreign_keys_query()
        self.assertIsNotNone(fk_sql)
        self.assertEqual(
            'ALTER TABLE "order_items" ADD CONSTRAINT "fk_order_items_order" FOREIGN KEY ("company_id", "order_id") REFERENCES "orders"("company_id", "id");',
            fk_sql
        )

    def test_table_indexes_ddl(self):
        table = Table('PRODUCTS')
        table.indexes.append(
            Index(
                index_name='IDX_PRODUCTS_NAME',
                unique=False,
                inactive=False,
                column_name='NAME',
                column_index=0,
            )
        )
        table.indexes.append(
            Index(
                index_name='IDX_PRODUCTS_SKU',
                unique=True,
                inactive=False,
                column_name='SKU',
                column_index=0,
            )
        )

        idx_queries = table.get_index_queries()
        self.assertEqual(len(idx_queries), 2)
        self.assertIn('CREATE INDEX "idx_products_name" ON "products" ("name");', idx_queries)
        self.assertIn('CREATE UNIQUE INDEX "idx_products_sku" ON "products" ("sku");', idx_queries)

    def test_table_composite_indexes_ddl(self):
        table = Table('PRODUCTS')
        table.indexes.append(
            Index(
                index_name='IDX_PRODUCTS_CAT_NAME',
                unique=False,
                inactive=False,
                column_name='CATEGORY_ID',
                column_index=0,
            )
        )
        table.indexes.append(
            Index(
                index_name='IDX_PRODUCTS_CAT_NAME',
                unique=False,
                inactive=False,
                column_name='NAME',
                column_index=1,
            )
        )

        idx_queries = table.get_index_queries()
        self.assertEqual(len(idx_queries), 1)
        self.assertEqual(
            'CREATE INDEX "idx_products_cat_name" ON "products" ("category_id", "name");',
            idx_queries[0]
        )

    def test_table_inactive_indexes_ddl(self):
        table = Table('PRODUCTS')
        table.indexes.append(
            Index(
                index_name='IDX_PRODUCTS_INACTIVE',
                unique=False,
                inactive=True,
                column_name='DELETED_AT',
                column_index=0,
            )
        )
        table.indexes.append(
            Index(
                index_name='IDX_PRODUCTS_ACTIVE',
                unique=False,
                inactive=False,
                column_name='NAME',
                column_index=0,
            )
        )

        idx_queries = table.get_index_queries()
        self.assertEqual(len(idx_queries), 1)
        self.assertEqual(
            'CREATE INDEX "idx_products_active" ON "products" ("name");',
            idx_queries[0]
        )

    def test_empty_table_returns_empty_or_none(self):
        table = Table('EMPTY')
        self.assertEqual(table.get_sequence_queries(), [])
        self.assertEqual(table.get_index_queries(), [])
        self.assertIsNone(table.get_unique_keys_query())
        self.assertIsNone(table.get_foreign_keys_query())
