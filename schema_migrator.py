from database_objects import Table


class SchemaMigrator:
    """
    Manages PostgreSQL structural DDL operations: dropping old tables/sequences/domains
    and creating new sequences, tables, unique keys, indexes, and foreign keys.
    """

    def __init__(self, pg_con):
        self.pg_con = pg_con

    @staticmethod
    def _drop_tables_and_sequences(cursor, table_objs: list[Table], print_queries: bool = False):
        """
        Drops migrated tables (CASCADE also removes their constraints, indexes, triggers
        and dependent views) and sequences. Domains are NOT dropped here, because the
        tables being (re)created reference them.
        """
        for table in table_objs:
            drop_query = f'DROP TABLE IF EXISTS "{table.name}" CASCADE;'
            if print_queries:
                print(drop_query)
            cursor.execute(drop_query)

        for table in table_objs:
            for col in table.columns:
                if col.sequence_name:
                    drop_seq_query = f'DROP SEQUENCE IF EXISTS "{col.sequence_name}" CASCADE;'
                    if print_queries:
                        print(drop_seq_query)
                    cursor.execute(drop_seq_query)

    def drop_schema(self, table_objs: list[Table], print_queries: bool = False):
        """
        Drops all migrated objects (tables, sequences and domains) from PostgreSQL,
        so that a re-run always rebuilds the current Firebird schema from scratch.

        Tables MUST be dropped before domains: DROP DOMAIN ... CASCADE on a domain that
        is still in use drops the table columns referencing it (and their data).
        """
        cursor = self.pg_con.cursor()

        self._drop_tables_and_sequences(cursor, table_objs, print_queries=print_queries)

        # Drop every domain in the current schema (covers orphaned variants left by earlier
        # migration runs). Schema-qualify the DROP: unqualified names that match a pg_catalog
        # type (e.g. "time") would resolve to the built-in type instead of our domain.
        cursor.execute("""
            SELECT n.nspname, t.typname
            FROM pg_type t
            JOIN pg_namespace n ON n.oid = t.typnamespace
            WHERE t.typtype = 'd' AND n.nspname = current_schema();
        """)
        for schema_name, domain_name in cursor.fetchall():
            drop_domain_query = f'DROP DOMAIN "{schema_name}"."{domain_name}" CASCADE;'
            if print_queries:
                print(drop_domain_query)
            cursor.execute(drop_domain_query)

        self.pg_con.commit()

    def migrate_schema(self, table_objs: list[Table], print_queries: bool = False):
        """
        Executes the generated PostgreSQL DDL to create the schema.
        """
        cursor = self.pg_con.cursor()

        # Teardown of tables/sequences only - domains must already exist (STEP 3), since the
        # tables created here reference them
        self._drop_tables_and_sequences(cursor, table_objs, print_queries=print_queries)

        for table in table_objs:
            seq_queries = table.get_sequences_query()
            for seq_query in seq_queries:
                if print_queries:
                    print(seq_query)
                cursor.execute(seq_query)

        for table in table_objs:
            if print_queries:
                print(table.get_create_query())
            cursor.execute(table.get_create_query())

        for table in table_objs:
            uniq_query = table.get_unique_keys_query()
            if uniq_query:
                if print_queries:
                    print(uniq_query)
                cursor.execute(uniq_query)

        for table in table_objs:
            indexes_query = table.get_indexes_query()
            if indexes_query:
                for idx_query in indexes_query:
                    if print_queries:
                        print(idx_query)
                    cursor.execute(idx_query)

        for table in table_objs:
            fk_query = table.get_foreign_keys_query()
            if fk_query:
                if print_queries:
                    print(fk_query)
                cursor.execute(fk_query)

        print('Saving schema transactions...')
        self.pg_con.commit()
