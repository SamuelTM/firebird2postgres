import psycopg2.extras
from database_objects import Table


class DataMigrator:
    """
    Handles streaming data from Firebird and bulk-inserting into PostgreSQL
    with string sanitization, adaptive batching, trigger toggling, and sequence synchronization.
    """

    def __init__(self, fb_con, pg_con):
        self.fb_con = fb_con
        self.pg_con = pg_con

    def import_data(self, table_objs: list[Table]):
        """
        Reads data from Firebird and bulk inserts into PostgreSQL.
        """
        print('Data migration starting...')
        fb_cur = self.fb_con.cursor()
        pg_cur = self.pg_con.cursor()

        print('Disabling constraints and clearing existing data for a clean import...')
        for table in table_objs:
            pg_cur.execute(f'ALTER TABLE "{table.name}" DISABLE TRIGGER ALL;')
            pg_cur.execute(f'TRUNCATE TABLE "{table.name}" CASCADE;')
        self.pg_con.commit()

        for table in table_objs:
            print(f'Importing data for {table.name}...')

            try:
                blob_count = sum(1 for col in table.columns if 'BLOB' in col.column_type)
                batch_size = 10000
                if blob_count > 0:
                    batch_size = max(500, 10000 // (blob_count * 5))
                    print(f'  Found {blob_count} BLOB columns. Adjusted batch size to {batch_size}.')

                # Explicitly list columns to ensure it perfectly matches the postgres insert order
                fb_column_names = [f'"{col.name}"' for col in table.columns]
                fb_columns_str = ", ".join(fb_column_names)

                fb_cur.execute(f'SELECT {fb_columns_str} FROM "{table.name}"')

                insert_query = f'INSERT INTO "{table.name}" ({fb_columns_str}) VALUES %s'

                total_rows = 0
                while True:
                    rows = fb_cur.fetchmany(batch_size)
                    if not rows:
                        break

                    # Sanitize strings because postgres does not allow NUL (\x00) bytes in TEXT/VARCHAR
                    sanitized_rows = []
                    for row in rows:
                        sanitized_row = []
                        for val in row:
                            if isinstance(val, str):
                                sanitized_row.append(val.replace('\x00', ''))
                            else:
                                sanitized_row.append(val)
                        sanitized_rows.append(tuple(sanitized_row))

                    psycopg2.extras.execute_values(pg_cur, insert_query, sanitized_rows)
                    total_rows += len(rows)

                self.pg_con.commit()
                print(f'  -> Imported {total_rows} rows.')

            except Exception as e:
                self.pg_con.rollback()
                print(f'  [CRITICAL ERROR] Failed to import the following table: {table.name}: {e}')
                print('  Ignoring and carrying on with the next table...')
                continue

        print('Re-enabling constraints in PostgreSQL...')
        for table in table_objs:
            pg_cur.execute(f'ALTER TABLE "{table.name}" ENABLE TRIGGER ALL;')
        self.pg_con.commit()

        print('Synchronizing sequences...')
        for table in table_objs:
            for col in table.columns:
                if col.sequence_name:
                    sync_query = f"""
                        SELECT setval('"{col.sequence_name}"', COALESCE(MAX("{col.name}"), 1))
                        FROM "{table.name}";
                    """
                    pg_cur.execute(sync_query)
        self.pg_con.commit()

        print('Data migration complete!')
