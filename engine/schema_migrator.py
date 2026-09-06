import logging
import psycopg2
from models import Table, Sequence, pg_quote_ident

logger = logging.getLogger(__name__)


class SchemaMigrator:
    """
    Manages PostgreSQL structural DDL operations: dropping old tables/sequences/domains
    and creating new sequences, tables, unique keys, indexes, and foreign keys.
    """

    def __init__(self, pg_con):
        self.pg_con = pg_con

    @staticmethod
    def _drop_tables_and_sequences(cursor, table_objs: list[Table], sequences: list[Sequence] = None):
        """
        Drops migrated tables (CASCADE also removes their constraints, indexes, triggers
        and dependent views) and sequences. Domains are NOT dropped here, because the
        tables being (re)created reference them.
        """
        for table in table_objs:
            drop_query = f'DROP TABLE IF EXISTS {pg_quote_ident(table.pg_name)} CASCADE;'
            logger.debug(drop_query)
            cursor.execute(drop_query)

        seq_names = set()
        if sequences:
            for s in sequences:
                seq_names.add(s.pg_name)
        for table in table_objs:
            for col in table.columns:
                if col.sequence_name:
                    seq_names.add(col.sequence_name)

        for seq_name in sorted(seq_names):
            drop_seq_query = f'DROP SEQUENCE IF EXISTS {pg_quote_ident(seq_name)} CASCADE;'
            logger.debug(drop_seq_query)
            cursor.execute(drop_seq_query)

    def drop_schema(self, table_objs: list[Table], sequences: list[Sequence] = None):
        """
        Drops all migrated objects (tables, sequences and domains) from PostgreSQL,
        so that a re-run always rebuilds the current Firebird schema from scratch.

        Tables MUST be dropped before domains: DROP DOMAIN ... CASCADE on a domain that
        is still in use drops the table columns referencing it (and their data).
        """
        logger.info("Dropping existing tables, sequences, and domains in PostgreSQL...")
        cursor = self.pg_con.cursor()

        self._drop_tables_and_sequences(cursor, table_objs, sequences)

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
            drop_domain_query = f'DROP DOMAIN {pg_quote_ident(schema_name)}.{pg_quote_ident(domain_name)} CASCADE;'
            logger.debug(drop_domain_query)
            cursor.execute(drop_domain_query)

        self.pg_con.commit()
        logger.info("Existing schema teardown completed.")

    def create_tables(self, table_objs: list[Table], sequences: list[Sequence] = None):
        """
        Creates base tables and sequences in PostgreSQL without indexes or constraints.
        This enables optimal bulk data loading performance.
        """
        logger.info(f"Creating base schema for {len(table_objs)} tables in PostgreSQL...")
        cursor = self.pg_con.cursor()

        # Teardown of tables/sequences only - domains must already exist (STEP 3), since the
        # tables created here reference them
        self._drop_tables_and_sequences(cursor, table_objs, sequences)

        created_seqs = set()
        if sequences:
            for seq in sequences:
                if seq.pg_name not in created_seqs:
                    query = seq.get_create_sequence_query()
                    logger.debug(query)
                    cursor.execute(query)
                    created_seqs.add(seq.pg_name)

        for table in table_objs:
            for col in table.columns:
                if col.sequence_name and col.sequence_name not in created_seqs:
                    query = f'CREATE SEQUENCE {pg_quote_ident(col.sequence_name)};'
                    logger.debug(query)
                    cursor.execute(query)
                    created_seqs.add(col.sequence_name)

        for table in table_objs:
            create_query = table.get_create_table_query()
            logger.debug(create_query)
            cursor.execute(create_query)

        logger.info("Saving base table schema transactions...")
        self.pg_con.commit()
        logger.info(f"Successfully created {len(table_objs)} base tables and sequences.")

    def create_constraints_and_indexes(self, table_objs: list[Table]):
        """
        Creates Unique/Primary Keys, Secondary Indexes, and Foreign Keys in PostgreSQL.
        Running this after data insertion allows PostgreSQL to build indexes via parallel sort
        and validates foreign keys efficiently in a single pass.
        """
        logger.info(f"Creating constraints and indexes for {len(table_objs)} tables in PostgreSQL...")
        cursor = self.pg_con.cursor()

        cursor.execute("SET synchronous_commit = OFF;")
        try:
            for table in table_objs:
                uniq_query = table.get_unique_keys_query()
                if uniq_query:
                    logger.debug(uniq_query)
                    cursor.execute(uniq_query)

            for table in table_objs:
                for idx_query in table.get_index_queries():
                    logger.debug(idx_query)
                    cursor.execute(idx_query)

            for table in table_objs:
                fk_query = table.get_foreign_keys_query()
                if fk_query:
                    logger.debug(fk_query)
                    cursor.execute(fk_query)

            for table in table_objs:
                chk_query = table.get_check_constraints_query()
                if chk_query:
                    logger.debug(chk_query)
                    cursor.execute(chk_query)

            self.pg_con.commit()
            logger.info("Constraints (PK, UK, FK, CHECK) and indexes created successfully.")
        except Exception:
            # Discard the partial constraints transaction explicitly: without this rollback
            # the connection stays aborted and every following statement fails with
            # InFailedSqlTransaction (the RESET below would also fail silently)
            self.pg_con.rollback()
            logger.error("Constraint/index creation failed; transaction rolled back.")
            raise
        finally:
            try:
                # On the failure path the rollback above already restored the session default;
                # on success this clears the session-wide synchronous_commit = OFF
                cursor.execute("RESET synchronous_commit;")
                self.pg_con.commit()
            except (psycopg2.Error, OSError):
                pass

    def migrate_schema(self, table_objs: list[Table], sequences: list[Sequence] = None):
        """
        Convenience method executing both table creation and constraints/indexes creation.
        """
        self.create_tables(table_objs, sequences)
        self.create_constraints_and_indexes(table_objs)

    def analyze_tables(self, table_objs: list[Table] = None):
        """
        Runs ANALYZE on migrated tables to update PostgreSQL optimizer statistics
        immediately following data load and index creation.
        """
        logger.info("Updating PostgreSQL optimizer statistics (ANALYZE)...")
        cursor = self.pg_con.cursor()
        if table_objs:
            for table in table_objs:
                logger.debug(f'ANALYZE {pg_quote_ident(table.pg_name)};')
                cursor.execute(f'ANALYZE {pg_quote_ident(table.pg_name)};')
        else:
            cursor.execute("ANALYZE;")
        self.pg_con.commit()
        logger.info("Optimizer statistics updated successfully.")
