import re
import psycopg2.extras
from enum import IntEnum
from concurrent.futures import ProcessPoolExecutor

from database_objects import Table, Column, ForeignKey, UniqueKey, Index, get_postgres_type
from firebird_visitor import FirebirdToPostgresVisitor


def _transpile_worker(item: tuple[str, str]) -> tuple[str | None, str | None]:
    """
    Worker function for multiprocessing pool.
    Takes (item_name, fb_sql) and returns (pg_sql, error_msg).
    Avoids returning fb_sql across IPC to minimize pickle overhead.
    """
    _, fb_sql = item
    try:
        pg_sql = FirebirdToPostgresVisitor.transpile(fb_sql)
        return pg_sql, None
    except Exception as e:
        return None, str(e)


class FirebirdDataType(IntEnum):
    SMALLINT = 7
    INTEGER = 8
    FLOAT = 10
    DATE = 12
    TIME = 13
    CHAR = 14
    BIGINT = 16
    DOUBLE_PRECISION = 27
    TIMESTAMP = 35
    VARCHAR = 37
    BLOB = 261


class DatabaseMigrator:
    def __init__(self, fb_con, pg_con):
        """
        Initializes the migrator with live connection objects to Firebird and PostgreSQL.
        """
        self.fb_con = fb_con
        self.pg_con = pg_con
        self.table_objs: list[Table] = []

    @staticmethod
    def transpile_firebird_sql(firebird_sql_string: str) -> str:
        return FirebirdToPostgresVisitor.transpile(firebird_sql_string)

    @staticmethod
    def _get_firebird_data_type_name(data_type_value: int, subtype: int = None) -> str | None:
        if data_type_value == FirebirdDataType.SMALLINT:
            return 'SMALLINT'
        elif data_type_value == FirebirdDataType.INTEGER:
            return 'INTEGER'
        elif data_type_value == FirebirdDataType.FLOAT:
            return 'FLOAT'
        elif data_type_value == FirebirdDataType.DATE:
            return 'DATE'
        elif data_type_value == FirebirdDataType.TIME:
            return 'TIME'
        elif data_type_value == FirebirdDataType.CHAR:
            return 'CHAR'
        elif data_type_value == FirebirdDataType.BIGINT:
            return 'BIGINT'
        elif data_type_value == FirebirdDataType.DOUBLE_PRECISION:
            return 'DOUBLE PRECISION'
        elif data_type_value == FirebirdDataType.TIMESTAMP:
            return 'TIMESTAMP'
        elif data_type_value == FirebirdDataType.VARCHAR:
            return 'VARCHAR'
        elif data_type_value == FirebirdDataType.BLOB:
            if subtype == 1:
                return 'BLOB SUBTYPE 1'
            return 'BLOB SUBTYPE 0'
        return None

    def _extract_schema(self):
        """
        Extracts the DDL schema from Firebird system tables into memory.
        """
        fb_cursor = self.fb_con.cursor()
        fb_cursor.execute(
            'SELECT RDB$RELATION_NAME FROM RDB$RELATIONS WHERE RDB$SYSTEM_FLAG = 0 AND RDB$VIEW_BLR IS NULL;')
        tables = fb_cursor.fetchall()

        self.table_objs = []

        for table in tables:
            table_name = table[0].strip()

            fb_cursor.execute(f"""
                   SELECT rf.RDB$FIELD_NAME, f.RDB$FIELD_TYPE, f.RDB$FIELD_SUB_TYPE, f.RDB$FIELD_LENGTH, 
                          COALESCE(rf.RDB$NULL_FLAG, f.RDB$NULL_FLAG),
                          f.RDB$FIELD_PRECISION, f.RDB$FIELD_SCALE,
                          COALESCE(rf.RDB$DEFAULT_SOURCE, f.RDB$DEFAULT_SOURCE)
                   FROM RDB$RELATION_FIELDS rf
                   JOIN RDB$FIELDS f ON rf.RDB$FIELD_SOURCE = f.RDB$FIELD_NAME
                   WHERE rf.RDB$RELATION_NAME = '{table_name}'
                   ORDER BY rf.RDB$FIELD_POSITION;
               """)

            table_obj = Table(table_name)

            for column in fb_cursor.fetchall():
                column_name = column[0].strip()
                column_type = column[1]
                column_subtype = column[2]
                column_data_type = self._get_firebird_data_type_name(column_type, column_subtype)
                column_size = int(column[3])
                nullable = column[4] is None
                precision = column[5]
                scale = abs(column[6]) if column[6] is not None else 0
                default_value = column[7].strip() if column[7] else None

                if (column_type in [FirebirdDataType.SMALLINT, FirebirdDataType.INTEGER, FirebirdDataType.BIGINT]
                        and column_subtype is not None and column_subtype > 0):
                    if precision:
                        column_data_type = f'NUMERIC({precision}, {scale})'
                    else:
                        column_data_type = 'NUMERIC'

                table_obj.columns.append(Column(column_name, column_data_type, column_size, nullable, default_value))

            foreign_keys_query = f"""
                     SELECT 
                        rc.RDB$CONSTRAINT_NAME AS foreign_key_name,
                        si.RDB$FIELD_POSITION AS column_position,
                        si.RDB$FIELD_NAME AS local_column,
                        rs.RDB$RELATION_NAME AS referenced_table,
                        rsi.RDB$FIELD_POSITION AS referenced_column_position,
                        rsi.RDB$FIELD_NAME AS referenced_column
                    FROM RDB$RELATION_CONSTRAINTS rc
                    JOIN RDB$INDEX_SEGMENTS si ON rc.RDB$INDEX_NAME = si.RDB$INDEX_NAME
                    JOIN RDB$REF_CONSTRAINTS refc ON rc.RDB$CONSTRAINT_NAME = refc.RDB$CONSTRAINT_NAME
                    JOIN RDB$RELATION_CONSTRAINTS rs ON refc.RDB$CONST_NAME_UQ = rs.RDB$CONSTRAINT_NAME
                    JOIN RDB$INDEX_SEGMENTS rsi ON rs.RDB$INDEX_NAME = rsi.RDB$INDEX_NAME
                    WHERE rc.RDB$CONSTRAINT_TYPE = 'FOREIGN KEY'
                      AND rc.RDB$RELATION_NAME = '{table_name}'
                    ORDER BY foreign_key_name, column_position;
            """

            fb_cursor.execute(foreign_keys_query)

            foreign_keys = fb_cursor.fetchall()

            if foreign_keys:
                for foreign_key in foreign_keys:
                    foreign_key_obj = ForeignKey(foreign_key[0].strip(), foreign_key[2].strip(), foreign_key[1],
                                                 foreign_key[3].strip(), foreign_key[5].strip(), foreign_key[4])

                    table_obj.foreign_keys.append(foreign_key_obj)

            unique_keys_query = f"""
                 SELECT 
                        rc.RDB$CONSTRAINT_NAME AS constraint_name,
                        si.RDB$FIELD_NAME AS column_name,
                        rc.RDB$CONSTRAINT_TYPE AS constraint_type
                    FROM RDB$RELATION_CONSTRAINTS rc
                    JOIN RDB$INDEX_SEGMENTS si ON rc.RDB$INDEX_NAME = si.RDB$INDEX_NAME
                    WHERE rc.RDB$CONSTRAINT_TYPE IN ('UNIQUE', 'PRIMARY KEY')
                      AND rc.RDB$RELATION_NAME = '{table_name}'
            """

            fb_cursor.execute(unique_keys_query)

            unique_keys = fb_cursor.fetchall()

            if unique_keys:
                for unique_key in unique_keys:
                    unique_key_column_name = unique_key[1].strip()
                    is_pk = unique_key[2].strip() == 'PRIMARY KEY'
                    unique_key_obj = UniqueKey(unique_key[0].strip(), unique_key_column_name, is_primary_key=is_pk)
                    table_obj.unique_keys.append(unique_key_obj)

            indexes_query = f"""
                SELECT 
                    i.RDB$INDEX_NAME AS index_name,
                    i.RDB$UNIQUE_FLAG AS is_unique,
                    i.RDB$INDEX_INACTIVE AS is_inactive,
                    seg.RDB$FIELD_NAME AS column_name,
                    seg.RDB$FIELD_POSITION AS column_position
                FROM RDB$INDICES i
                JOIN RDB$INDEX_SEGMENTS seg ON i.RDB$INDEX_NAME = seg.RDB$INDEX_NAME
                WHERE i.RDB$RELATION_NAME = '{table_name}'
                  AND i.RDB$INDEX_NAME NOT IN (
                      SELECT RDB$INDEX_NAME 
                      FROM RDB$RELATION_CONSTRAINTS 
                      WHERE RDB$CONSTRAINT_TYPE IN ('PRIMARY KEY', 'UNIQUE') 
                        AND RDB$INDEX_NAME IS NOT NULL
                  )
                ORDER BY i.RDB$INDEX_NAME, seg.RDB$FIELD_POSITION;
            """

            fb_cursor.execute(indexes_query)

            indexes = fb_cursor.fetchall()

            if indexes:
                for index in indexes:
                    ind = Index(index[0].strip(), index[1], index[2], index[3].strip(), index[4])
                    table_obj.indexes.append(ind)

            self.table_objs.append(table_obj)

        triggers_query = """
            SELECT RDB$RELATION_NAME, RDB$TRIGGER_SOURCE
            FROM RDB$TRIGGERS
            WHERE RDB$SYSTEM_FLAG = 0
              AND RDB$TRIGGER_SOURCE IS NOT NULL;
        """
        fb_cursor.execute(triggers_query)
        triggers = fb_cursor.fetchall()

        pattern = re.compile(r'NEW\.([A-Za-z0-9_]+)\s*=\s*GEN_ID\s*\(\s*([A-Za-z0-9_]+)\s*,\s*\d+\s*\)', re.IGNORECASE)

        for trigger in triggers:
            relation_name = trigger[0].strip() if trigger[0] else None
            source = trigger[1]
            if not relation_name or not source:
                continue

            match = pattern.search(source)
            if match:
                column_name = match.group(1).strip()
                sequence_name = match.group(2).strip()

                table = next((t for t in self.table_objs if t.name == relation_name), None)
                if table:
                    column = next((c for c in table.columns if c.name == column_name), None)
                    if column:
                        column.sequence_name = sequence_name

    def migrate_schema(self, print_queries=False):
        """
        Executes the generated PostgreSQL DDL to create the schema.
        """
        if not self.table_objs:
            self._extract_schema()

        cursor = self.pg_con.cursor()

        for table in self.table_objs:
            seq_queries = table.get_sequences_query()
            for seq_query in seq_queries:
                if print_queries:
                    print(seq_query)
                cursor.execute(seq_query)

        for table in self.table_objs:
            if print_queries:
                print(table.get_create_query())
            cursor.execute(table.get_create_query())

        for table in self.table_objs:
            uniq_query = table.get_unique_keys_query()
            if uniq_query:
                if print_queries:
                    print(uniq_query)
                cursor.execute(uniq_query)

        for table in self.table_objs:
            indexes_query = table.get_indexes_query()
            if indexes_query:
                for idx_query in indexes_query:
                    if print_queries:
                        print(idx_query)
                    cursor.execute(idx_query)

        for table in self.table_objs:
            fk_query = table.get_foreign_keys_query()
            if fk_query:
                if print_queries:
                    print(fk_query)
                cursor.execute(fk_query)

        print('Saving schema transactions...')
        self.pg_con.commit()

    def import_data(self):
        """
        Reads data from Firebird and bulk inserts into PostgreSQL.
        """
        if not self.table_objs:
            self._extract_schema()

        print('Data migration starting...')
        fb_cur = self.fb_con.cursor()
        pg_cur = self.pg_con.cursor()

        print('Disabling constraints and clearing existing data for a clean import...')
        for table in self.table_objs:
            pg_cur.execute(f'ALTER TABLE "{table.name}" DISABLE TRIGGER ALL;')
            pg_cur.execute(f'TRUNCATE TABLE "{table.name}" CASCADE;')
        self.pg_con.commit()

        for table in self.table_objs:
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
        for table in self.table_objs:
            pg_cur.execute(f'ALTER TABLE "{table.name}" ENABLE TRIGGER ALL;')
        self.pg_con.commit()

        print('Synchronizing sequences...')
        for table in self.table_objs:
            for col in table.columns:
                if col.sequence_name:
                    sync_query = f"""
                        SELECT setval('"{col.sequence_name}"', COALESCE(MAX("{col.name}"), 1))
                        FROM "{table.name}";
                    """
                    pg_cur.execute(sync_query)
        self.pg_con.commit()

        print('Data migration complete!')

    @staticmethod
    def _decode_trigger_type(trigger_type: int) -> str:
        """
        Decodes Firebird's RDB$TRIGGER_TYPE into a human-readable timing + events string.

        Firebird encodes trigger types as:
            stored_type = (phase | (slot1 << 1) | (slot2 << 3) | (slot3 << 5)) - 1
        Where phase: 0=BEFORE, 1=AFTER; slots: 1=INSERT, 2=UPDATE, 3=DELETE.
        """
        event_names = {1: 'INSERT', 2: 'UPDATE', 3: 'DELETE'}

        raw = trigger_type + 1
        phase = 'BEFORE' if (raw & 1) == 0 else 'AFTER'
        events = []
        for shift in (1, 3, 5):
            slot = (raw >> shift) & 0b11
            if slot > 0:
                events.append(event_names.get(slot, f'UNKNOWN({slot})'))

        if not events:
            return f'/* UNKNOWN TYPE {trigger_type} */'

        return f'{phase} {" OR ".join(events)}'

    def export_firebird_triggers(self, output_file: str = 'firebird_triggers_dump.sql',
                                 converted_file: str = 'postgres_triggers_dump.sql',
                                 executor: ProcessPoolExecutor = None,
                                 chunksize: int = 4):
        """
        Extracts all user-defined triggers from Firebird and saves their source code to a file
        """
        fb_cursor = self.fb_con.cursor()

        query = """
            SELECT RDB$TRIGGER_NAME, RDB$RELATION_NAME, RDB$TRIGGER_TYPE, RDB$TRIGGER_SOURCE
            FROM RDB$TRIGGERS
            WHERE RDB$SYSTEM_FLAG = 0
              AND RDB$TRIGGER_SOURCE IS NOT NULL
            ORDER BY RDB$RELATION_NAME, RDB$TRIGGER_NAME;
        """
        fb_cursor.execute(query)
        triggers = fb_cursor.fetchall()

        items = []
        for trigger in triggers:
            trigger_name = trigger[0].strip() if trigger[0] else 'UNKNOWN'
            relation_name = trigger[1].strip() if trigger[1] else 'UNKNOWN'
            trigger_type = trigger[2]
            source = trigger[3]

            timing_events = self._decode_trigger_type(trigger_type)
            fb_sql = f"CREATE TRIGGER {trigger_name} FOR {relation_name} {timing_events}\n{source}\n\n"
            items.append((trigger_name, fb_sql))

        print(f"Transpiling {len(items)} triggers in parallel...")
        if executor is not None:
            results = list(executor.map(_transpile_worker, items, chunksize=chunksize))
        else:
            with ProcessPoolExecutor() as local_executor:
                results = list(local_executor.map(_transpile_worker, items, chunksize=chunksize))

        with open(output_file, 'w', encoding='utf-8') as f, open(converted_file, 'w', encoding='utf-8') as conv_f:
            f.write("-- ==========================================\n")
            f.write("-- FIREBIRD TRIGGERS DUMP\n")
            f.write("-- ==========================================\n\n")

            conv_f.write("-- ==========================================\n")
            conv_f.write("-- POSTGRESQL TRIGGERS DUMP (CONVERTED)\n")
            conv_f.write("-- ==========================================\n\n")

            for (trigger_name, fb_sql), (pg_sql, err) in zip(items, results):
                f.write(fb_sql)
                if err is None and pg_sql:
                    conv_f.write(pg_sql)
                    conv_f.write("\n\n")
                else:
                    print(f"Failed to transpile trigger {trigger_name}: {err}")
                    conv_f.write(f"-- [TRANSPILER FAILED] TRIGGER {trigger_name}\n")
                    conv_f.write(fb_sql)

        print(f"Exported {len(triggers)} triggers to '{output_file}' and '{converted_file}'")

    def export_firebird_procedures(self, output_file: str = 'firebird_procedures_dump.sql',
                                   converted_file: str = 'postgres_procedures_dump.sql',
                                   executor: ProcessPoolExecutor = None,
                                   chunksize: int = 4):
        """
        Extracts all user-defined stored procedures from Firebird and saves their source code to a file
        """
        fb_cursor = self.fb_con.cursor()

        query = """
            SELECT RDB$PROCEDURE_NAME, RDB$PROCEDURE_SOURCE
            FROM RDB$PROCEDURES
            WHERE RDB$SYSTEM_FLAG = 0
              AND RDB$PROCEDURE_SOURCE IS NOT NULL
            ORDER BY RDB$PROCEDURE_NAME;
        """
        fb_cursor.execute(query)
        procedures = fb_cursor.fetchall()

        items = []
        for proc in procedures:
            proc_name = proc[0].strip() if proc[0] else 'UNKNOWN'
            source = proc[1]

            # Query input and output parameters for this procedure
            params_query = f"""
                SELECT
                    pp.RDB$PARAMETER_NAME,
                    pp.RDB$PARAMETER_TYPE,
                    pp.RDB$PARAMETER_NUMBER,
                    f.RDB$FIELD_TYPE,
                    f.RDB$FIELD_SUB_TYPE,
                    f.RDB$FIELD_LENGTH,
                    f.RDB$FIELD_PRECISION,
                    f.RDB$FIELD_SCALE
                FROM RDB$PROCEDURE_PARAMETERS pp
                JOIN RDB$FIELDS f ON pp.RDB$FIELD_SOURCE = f.RDB$FIELD_NAME
                WHERE pp.RDB$PROCEDURE_NAME = '{proc_name}'
                ORDER BY pp.RDB$PARAMETER_TYPE, pp.RDB$PARAMETER_NUMBER;
            """
            fb_cursor.execute(params_query)
            params = fb_cursor.fetchall()

            input_params = []
            output_params = []
            for param in params:
                param_name = param[0].strip() if param[0] else 'UNKNOWN'
                param_type_flag = param[1]  # 0=input, 1=output
                field_type = param[3]
                field_subtype = param[4]
                field_length = param[5]
                field_precision = param[6]
                field_scale = abs(param[7]) if param[7] else 0

                type_name = self._get_firebird_data_type_name(field_type, field_subtype)
                if type_name is None:
                    type_name = 'VARCHAR(255)'

                if (field_type in (FirebirdDataType.SMALLINT, FirebirdDataType.INTEGER,
                                   FirebirdDataType.BIGINT) and field_subtype is not None
                        and field_subtype > 0 and field_precision):
                    type_name = f'NUMERIC({field_precision}, {field_scale})'

                elif field_type in (FirebirdDataType.CHAR, FirebirdDataType.VARCHAR) and field_length:
                    type_name = f'{type_name}({field_length})'

                if param_type_flag == 0:
                    input_params.append(f'    {param_name} {type_name}')
                else:
                    output_params.append(f'    {param_name} {type_name}')

            # Build header
            fb_sql = f'CREATE OR ALTER PROCEDURE {proc_name}'
            if input_params:
                params_str = ",\n".join(input_params)
                fb_sql += f' (\n{params_str}\n)'
            fb_sql += '\n'
            if output_params:
                params_str = ",\n".join(output_params)
                fb_sql += f'RETURNS (\n{params_str}\n)\n'
            fb_sql += 'AS\n'
            fb_sql += f'{source};\n\n'

            items.append((proc_name, fb_sql))

        print(f"Transpiling {len(items)} procedures in parallel...")
        if executor is not None:
            results = list(executor.map(_transpile_worker, items, chunksize=chunksize))
        else:
            with ProcessPoolExecutor() as local_executor:
                results = list(local_executor.map(_transpile_worker, items, chunksize=chunksize))

        with open(output_file, 'w', encoding='utf-8') as f, open(converted_file, 'w', encoding='utf-8') as conv_f:
            f.write("-- ==========================================\n")
            f.write("-- FIREBIRD PROCEDURES DUMP\n")
            f.write("-- ==========================================\n\n")

            conv_f.write("-- ==========================================\n")
            conv_f.write("-- POSTGRESQL PROCEDURES DUMP (CONVERTED)\n")
            conv_f.write("-- ==========================================\n\n")

            for (proc_name, fb_sql), (pg_sql, err) in zip(items, results):
                f.write(fb_sql)
                if err is None and pg_sql:
                    conv_f.write(pg_sql)
                    conv_f.write('\n\n')
                else:
                    print(f"Failed to transpile procedure {proc_name}: {err}")
                    conv_f.write(f"-- [TRANSPILER FAILED] PROCEDURE {proc_name}\n")
                    conv_f.write(fb_sql)

        print(f"Exported {len(procedures)} procedures to '{output_file}' and '{converted_file}'")

    def export_firebird_views(self, output_file: str = 'firebird_views_dump.sql',
                              converted_file: str = 'postgres_views_dump.sql',
                              executor: ProcessPoolExecutor = None,
                              chunksize: int = 4):
        """
        Extracts all user-defined views from Firebird and saves their source code to a file
        """
        fb_cursor = self.fb_con.cursor()

        query = """
            SELECT RDB$RELATION_NAME, RDB$VIEW_SOURCE
            FROM RDB$RELATIONS
            WHERE RDB$SYSTEM_FLAG = 0
              AND RDB$VIEW_BLR IS NOT NULL
            ORDER BY RDB$RELATION_NAME;
        """
        fb_cursor.execute(query)
        views = fb_cursor.fetchall()

        items = []
        for view in views:
            view_name = view[0].strip() if view[0] else 'UNKNOWN'
            source = view[1]

            # Fetch view columns in order
            columns_query = f"""
                SELECT RDB$FIELD_NAME 
                FROM RDB$RELATION_FIELDS 
                WHERE RDB$RELATION_NAME = '{view_name}' 
                ORDER BY RDB$FIELD_POSITION;
            """
            fb_cursor.execute(columns_query)
            columns = fb_cursor.fetchall()

            col_names = []
            for col in columns:
                col_name = col[0].strip()
                col_names.append(f'"{col_name}"')

            col_list = ""
            if col_names:
                col_list = f" ({', '.join(col_names)})"

            fb_sql = f'CREATE OR ALTER VIEW "{view_name}"{col_list} AS\n{source}\n\n'
            items.append((view_name, fb_sql))

        print(f"Transpiling {len(items)} views in parallel...")
        if executor is not None:
            results = list(executor.map(_transpile_worker, items, chunksize=chunksize))
        else:
            with ProcessPoolExecutor() as local_executor:
                results = list(local_executor.map(_transpile_worker, items, chunksize=chunksize))

        with open(output_file, 'w', encoding='utf-8') as f, open(converted_file, 'w', encoding='utf-8') as conv_f:
            f.write("-- ==========================================\n")
            f.write("-- FIREBIRD VIEWS DUMP\n")
            f.write("-- This file contains the raw SELECT source for manual translation to PostgreSQL views\n")
            f.write("-- ==========================================\n\n")

            conv_f.write("-- ==========================================\n")
            conv_f.write("-- POSTGRESQL VIEWS DUMP (CONVERTED)\n")
            conv_f.write("-- ==========================================\n\n")

            for (view_name, fb_sql), (pg_sql, err) in zip(items, results):
                f.write(f"-- ----------------------------------------\n")
                f.write(f"-- View: {view_name}\n")
                f.write(f"-- ----------------------------------------\n")
                f.write(fb_sql)

                conv_f.write(f"-- ----------------------------------------\n")
                conv_f.write(f"-- View: {view_name}\n")
                conv_f.write(f"-- ----------------------------------------\n")

                if err is None and pg_sql:
                    conv_f.write(pg_sql)
                    conv_f.write("\n\n")
                else:
                    print(f"Failed to transpile view {view_name}: {err}")
                    conv_f.write(f"-- [TRANSPILER FAILED] VIEW {view_name}\n")
                    conv_f.write(fb_sql)

        print(f"Exported {len(views)} views to '{output_file}' and '{converted_file}'")

    def export_all_firebird_ddl(self):
        """
        Exports all Firebird domains, triggers, procedures, and views using a single shared
        ProcessPoolExecutor, avoiding the overhead of repeated process spawns and parser imports.
        """
        self.export_firebird_domains()
        with ProcessPoolExecutor() as executor:
            self.export_firebird_triggers(executor=executor)
            self.export_firebird_procedures(executor=executor)
            self.export_firebird_views(executor=executor)

    def export_firebird_domains(self, output_file: str = 'firebird_domains_dump.sql',
                                converted_file: str = 'postgres_domains_dump.sql'):
        """
        Extracts all user-defined domains from Firebird and saves their source code to a file
        and the PostgreSQL converted CREATE DOMAIN definitions.
        """
        fb_cursor = self.fb_con.cursor()

        query = """
            SELECT 
                RDB$FIELD_NAME, 
                RDB$FIELD_TYPE, 
                RDB$FIELD_SUB_TYPE, 
                RDB$FIELD_LENGTH, 
                RDB$FIELD_PRECISION, 
                RDB$FIELD_SCALE,
                RDB$DEFAULT_SOURCE,
                RDB$NULL_FLAG
            FROM RDB$FIELDS
            WHERE RDB$SYSTEM_FLAG = 0
              AND RDB$FIELD_NAME NOT STARTING WITH 'RDB$'
            ORDER BY RDB$FIELD_NAME;
        """
        fb_cursor.execute(query)
        domains = fb_cursor.fetchall()

        with open(output_file, 'w', encoding='utf-8') as f, open(converted_file, 'w', encoding='utf-8') as conv_f:
            f.write("-- ==========================================\n")
            f.write("-- FIREBIRD DOMAINS DUMP\n")
            f.write("-- ==========================================\n\n")

            conv_f.write("-- ==========================================\n")
            conv_f.write("-- POSTGRESQL DOMAINS DUMP (CONVERTED)\n")
            conv_f.write("-- ==========================================\n\n")

            for d in domains:
                domain_name = d[0].strip() if d[0] else 'UNKNOWN'
                field_type = d[1]
                field_subtype = d[2]
                field_length = d[3]
                field_precision = d[4]
                field_scale = abs(d[5]) if d[5] else 0
                default_source = d[6].strip() if d[6] else None
                not_null = (d[7] == 1)

                fb_type_name = self._get_firebird_data_type_name(field_type, field_subtype)
                if fb_type_name is None:
                    fb_type_name = 'VARCHAR'

                if (field_type in (FirebirdDataType.SMALLINT, FirebirdDataType.INTEGER,
                                   FirebirdDataType.BIGINT) and field_subtype is not None
                        and field_subtype > 0 and field_precision):
                    fb_full_type = f'NUMERIC({field_precision}, {field_scale})'
                    pg_type = fb_full_type
                elif field_type in (FirebirdDataType.CHAR, FirebirdDataType.VARCHAR) and field_length:
                    fb_full_type = f'{fb_type_name}({field_length})'
                    pg_type = fb_full_type
                else:
                    fb_full_type = fb_type_name
                    pg_type = get_postgres_type(fb_type_name)

                # Firebird DDL
                fb_ddl = f'CREATE DOMAIN "{domain_name}" AS {fb_full_type}'
                if default_source:
                    fb_ddl += f' {default_source}'
                if not_null:
                    fb_ddl += ' NOT NULL'
                fb_ddl += ';\n'
                f.write(fb_ddl)

                # PostgreSQL DDL (use unquoted identifier for case-insensitive matching in PL/pgSQL)
                pg_domain_ident = domain_name if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', domain_name) else f'"{domain_name}"'
                pg_ddl = f'CREATE DOMAIN {pg_domain_ident} AS {pg_type}'
                if default_source:
                    pg_ddl += f' {default_source}'
                if not_null:
                    pg_ddl += ' NOT NULL'
                pg_ddl += ';\n'
                conv_f.write(pg_ddl)

        print(f"Exported {len(domains)} domains to '{output_file}' and '{converted_file}'")
