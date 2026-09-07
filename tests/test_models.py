import unittest
from models import (
    Table,
    Column,
    ForeignKey,
    UniqueKey,
    Index,
    Sequence,
    get_postgres_type,
    resolve_firebird_type,
    resolve_pg_domain_name,
    build_domain_mapping,
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
        self.assertEqual(get_postgres_type('BOOLEAN'), 'BOOLEAN')
        self.assertEqual(get_postgres_type('DECFLOAT(16)'), 'NUMERIC')
        self.assertEqual(get_postgres_type('DECFLOAT(34)'), 'NUMERIC')
        self.assertEqual(get_postgres_type('INT128'), 'NUMERIC(38)')
        self.assertEqual(get_postgres_type('TIME WITH TIME ZONE'), 'TIMETZ')
        self.assertEqual(get_postgres_type('TIMESTAMP WITH TIME ZONE'), 'TIMESTAMPTZ')
        self.assertEqual(get_postgres_type('CUSTOM_TYPE'), 'CUSTOM_TYPE')
        with self.assertRaises(ValueError):
            get_postgres_type(None)

    def test_resolve_firebird_type(self):
        # 7 = SMALLINT, 8 = INTEGER, 14 = CHAR, 37 = VARCHAR, 16 = BIGINT / INT64
        self.assertEqual(resolve_firebird_type(field_type=8), 'INTEGER')
        self.assertEqual(resolve_firebird_type(field_type=7), 'SMALLINT')
        self.assertEqual(resolve_firebird_type(field_type=37, field_length=50), 'VARCHAR(50)')
        self.assertEqual(resolve_firebird_type(field_type=37, field_length=40, character_length=10), 'VARCHAR(10)')
        self.assertEqual(resolve_firebird_type(field_type=14, field_length=10), 'CHAR(10)')
        self.assertEqual(resolve_firebird_type(field_type=14, field_length=40, character_length=10), 'CHAR(10)')
        # Modern FB 3/4/5 types
        self.assertEqual(resolve_firebird_type(field_type=23), 'BOOLEAN')
        self.assertEqual(resolve_firebird_type(field_type=24), 'DECFLOAT(16)')
        self.assertEqual(resolve_firebird_type(field_type=25), 'DECFLOAT(34)')
        self.assertEqual(resolve_firebird_type(field_type=26), 'INT128')
        self.assertEqual(resolve_firebird_type(field_type=26, field_subtype=1, field_precision=30, field_scale=-4),
                         'NUMERIC(30, 4)')
        self.assertEqual(resolve_firebird_type(field_type=28), 'TIME WITH TIME ZONE')
        self.assertEqual(resolve_firebird_type(field_type=29), 'TIMESTAMP WITH TIME ZONE')
        # Numeric with precision and scale
        self.assertEqual(resolve_firebird_type(field_type=16, field_subtype=1, field_precision=15, field_scale=-2),
                         'NUMERIC(15, 2)')
        self.assertEqual(resolve_firebird_type(field_type=8, field_subtype=1, field_precision=9, field_scale=0),
                         'NUMERIC(9, 0)')
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

    def test_build_domain_mapping_avoids_domain_and_table_collisions(self):
        relation_names = {'foo', 'orders'}
        domain_names = ['FOO', 'FOO_DOM', 'STATUS']
        mapping = build_domain_mapping(domain_names, relation_names)
        self.assertEqual(mapping['STATUS'], 'status')
        self.assertEqual(mapping['FOO_DOM'], 'foo_dom')
        self.assertEqual(mapping['FOO'], 'foo_dom_dom')
        self.assertNotEqual(mapping['FOO'], mapping['FOO_DOM'])

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

    def test_table_quotes_escaped(self):
        table = Table('MY_"TABLE"')
        table.columns.append(Column('COL_"A"', 'INTEGER', nullable=False, sequence_name='GEN_"SEQ"'))
        table.columns.append(Column('COL_B', 'VARCHAR(20)', nullable=True, domain_name='dom_"type"'))
        create_sql = table.get_create_table_query()
        self.assertIn('CREATE TABLE "my_""table"""', create_sql)
        self.assertIn('"col_""a""" INTEGER DEFAULT nextval(\'"gen_""seq"""\') NOT NULL', create_sql)
        self.assertIn('"col_b" public."dom_""type"""', create_sql)
        seqs = table.get_sequence_queries()
        self.assertEqual(seqs[0], 'CREATE SEQUENCE "gen_""seq""";')

    def test_table_sequence_with_apostrophe(self):
        table = Table('EMPLOYEES')
        table.columns.append(Column('ID', 'INTEGER', nullable=False, sequence_name="gen_o'brien"))
        create_sql = table.get_create_table_query()
        self.assertIn('DEFAULT nextval(\'"gen_o\'\'brien"\')', create_sql)

    def test_table_unique_keys_ddl(self):
        table = Table('USERS')
        table.unique_keys.append(UniqueKey('PK_USERS', column='ID', is_primary_key=True))
        table.unique_keys.append(UniqueKey('UQ_USERS_EMAIL', column='EMAIL', is_primary_key=False))

        uq_sql = table.get_unique_keys_query()
        self.assertIsNotNone(uq_sql)
        self.assertEqual(
            'ALTER TABLE "users" ADD CONSTRAINT "pk_users" PRIMARY KEY ("id"), '
            'ADD CONSTRAINT "uq_users_email" UNIQUE ("email");', uq_sql
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
            'ALTER TABLE "orders" ADD CONSTRAINT "fk_orders_cliente" FOREIGN KEY ("cliente_id") '
            'REFERENCES "clientes"("id");', fk_sql
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
        # Columns follow the original Firebird segment positions (ORDER_ID = 0, COMPANY_ID = 1),
        # not alphabetical order
        self.assertEqual(
            'ALTER TABLE "order_items" ADD CONSTRAINT "fk_order_items_order" FOREIGN KEY ("order_id", "company_id") '
            'REFERENCES "orders"("id", "company_id");', fk_sql
        )

    def test_table_foreign_keys_with_actions_ddl(self):
        table = Table('ORDERS')
        table.foreign_keys.append(
            ForeignKey(
                key_name='FK_ORDERS_CLIENTE',
                local_column_name='CLIENTE_ID',
                local_column_index=0,
                referenced_table_name='CLIENTES',
                referenced_column_name='ID',
                referenced_column_index=0,
                update_rule='CASCADE',
                delete_rule='SET NULL',
            )
        )
        fk_sql = table.get_foreign_keys_query()
        self.assertEqual(
            'ALTER TABLE "orders" ADD CONSTRAINT "fk_orders_cliente" FOREIGN KEY ("cliente_id") '
            'REFERENCES "clientes"("id") ON DELETE SET NULL ON UPDATE CASCADE;', fk_sql
        )

    def test_table_computed_columns_ddl(self):
        table = Table('INVOICE_ITEMS')
        table.columns.append(Column('QTD', 'INTEGER', nullable=False))
        table.columns.append(Column('PRECO', 'NUMERIC(15,2)', nullable=False))
        table.columns.append(Column('TOTAL', 'NUMERIC(15,2)', nullable=True, computed_source='QTD * PRECO'))
        table.columns.append(Column('TOTAL_LIQUIDO', 'NUMERIC(15,2)', nullable=False, domain_name='dom_moeda', computed_source='QTD * PRECO * 0.9'))
        table.columns.append(Column('SUM_VALS', 'NUMERIC(15,2)', nullable=True, computed_source='(QTD) + (PRECO)'))
        table.columns.append(Column('STR_CONCAT', 'VARCHAR(100)', nullable=True, computed_source="('(') || (')')"))

        create_sql = table.get_create_table_query()
        self.assertIn('"total" NUMERIC(15,2) GENERATED ALWAYS AS (QTD * PRECO) STORED', create_sql)
        self.assertIn('"total_liquido" public."dom_moeda" GENERATED ALWAYS AS (QTD * PRECO * 0.9) STORED NOT NULL', create_sql)
        self.assertIn('"sum_vals" NUMERIC(15,2) GENERATED ALWAYS AS ((QTD) + (PRECO)) STORED', create_sql)
        self.assertIn('"str_concat" VARCHAR(100) GENERATED ALWAYS AS ((\'(\') || (\')\')) STORED', create_sql)

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

    def test_table_expression_indexes_ddl(self):
        table = Table('CLIENTES')
        table.indexes.append(
            Index(
                index_name='IDX_CLIENTES_NOME_UPPER',
                unique=False,
                inactive=False,
                expression='(UPPER(NOME))',
            )
        )
        table.indexes.append(
            Index(
                index_name='UK_CLIENTES_DOC_CLEAN',
                unique=True,
                inactive=False,
                expression='TRIM(CNPJ)',
            )
        )
        table.indexes.append(
            Index(
                index_name='IDX_EXPR_INACTIVE',
                unique=False,
                inactive=True,
                expression='(EXTRACT(YEAR FROM DATA_CADASTRO))',
            )
        )

        table.indexes.append(
            Index(
                index_name='IDX_STR_CONCAT',
                unique=False,
                inactive=False,
                expression="('(') || (')')",
            )
        )

        idx_queries = table.get_index_queries()
        self.assertEqual(len(idx_queries), 3)
        self.assertIn('CREATE INDEX "idx_clientes_nome_upper" ON "clientes" (((UPPER(NOME))));', idx_queries)
        self.assertIn('CREATE UNIQUE INDEX "uk_clientes_doc_clean" ON "clientes" ((TRIM(CNPJ)));', idx_queries)
        self.assertIn('CREATE INDEX "idx_str_concat" ON "clientes" (((\'(\') || (\')\')));', idx_queries)

    def test_partial_index_generation(self):
        table = Table('USERS')
        table.indexes.append(
            Index(
                index_name='IDX_USERS_ACTIVE_EMAIL',
                unique=True,
                inactive=False,
                column_name='EMAIL',
                condition='active = 1'
            )
        )
        queries = table.get_index_queries()
        self.assertEqual(len(queries), 1)
        self.assertIn('CREATE UNIQUE INDEX "idx_users_active_email" ON "users" ("email") WHERE active = 1;', queries)


class TestSequenceModel(unittest.TestCase):
    def test_sequence_creation_queries(self):
        seq_zero = Sequence('GEN_TEST_ID', current_value=0)
        self.assertEqual(seq_zero.pg_name, 'gen_test_id')
        self.assertEqual(seq_zero.get_create_sequence_query(), 'CREATE SEQUENCE "gen_test_id";')
        self.assertEqual(seq_zero.get_drop_sequence_query(), 'DROP SEQUENCE IF EXISTS "gen_test_id" CASCADE;')

        seq_with_value = Sequence('GEN_TATENDIMENTOS_APAC_ID', current_value=150)
        self.assertEqual(seq_with_value.pg_name, 'gen_tatendimentos_apac_id')
        self.assertEqual(
            seq_with_value.get_create_sequence_query(),
            'CREATE SEQUENCE "gen_tatendimentos_apac_id" START WITH 151;'
        )

        seq_neg = Sequence('GEN_NEG_ID', current_value=-10)
        self.assertEqual(
            seq_neg.get_create_sequence_query(),
            'CREATE SEQUENCE "gen_neg_id" MINVALUE -9223372036854775807 START WITH -9;'
        )

        seq_minus_one = Sequence('GEN_MINUS_ONE', current_value=-1)
        self.assertEqual(
            seq_minus_one.get_create_sequence_query(),
            'CREATE SEQUENCE "gen_minus_one" MINVALUE -9223372036854775807 START WITH 0;'
        )

        seq_unknown = Sequence('GEN_UNKNOWN', current_value=None)
        with self.assertRaises(ValueError):
            seq_unknown.get_create_sequence_query()

        seq_with_inc = Sequence('GEN_INC', current_value=10, increment=5)
        self.assertEqual(
            seq_with_inc.get_create_sequence_query(),
            'CREATE SEQUENCE "gen_inc" INCREMENT BY 5 START WITH 15;'
        )

    def test_table_with_identity_column(self):
        table = Table('ORDERS')
        table.columns.append(Column('ID', 'BIGINT', nullable=False, identity_type='BY DEFAULT'))
        table.columns.append(Column('NAME', 'VARCHAR(50)', nullable=True))

        sql = table.get_create_table_query()
        self.assertIn('"id" BIGINT GENERATED BY DEFAULT AS IDENTITY NOT NULL', sql)
        self.assertEqual(table.get_sequence_queries(), [])

    def test_sequence_escapes_double_quotes(self):
        seq = Sequence('GEN_"QUOTED"', current_value=5)
        self.assertEqual(seq.get_create_sequence_query(), 'CREATE SEQUENCE "gen_""quoted""" START WITH 6;')
        self.assertEqual(seq.get_drop_sequence_query(), 'DROP SEQUENCE IF EXISTS "gen_""quoted""" CASCADE;')

    def test_check_constraint_query(self):
        from models import CheckConstraint
        table = Table('ITENS')
        self.assertIsNone(table.get_check_constraints_query())

        table.check_constraints.append(CheckConstraint('CHK_QTD', 'quantidade > 0'))
        table.check_constraints.append(CheckConstraint('CHK_PRECO', 'preco >= 0'))
        query = table.get_check_constraints_query()
        self.assertEqual(
            query,
            'ALTER TABLE "itens" ADD CONSTRAINT "chk_qtd" CHECK (quantidade > 0), ADD CONSTRAINT "chk_preco" CHECK (preco >= 0);'
        )


