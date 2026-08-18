import re
from models import Table, Column, ForeignKey, UniqueKey, Index, resolve_firebird_type, resolve_pg_domain_name


class SchemaExtractor:
    """
    Extracts table schemas, column types, domains, constraints, indexes,
    and sequence bindings from Firebird database system catalogs into memory.
    """

    def __init__(self, fb_con):
        self.fb_con = fb_con

    def extract_schema(self) -> list[Table]:
        """
        Extracts the full relational schema from Firebird system tables into a list of Table objects.
        """
        fb_cursor = self.fb_con.cursor()
        fb_cursor.execute(
            'SELECT RDB$RELATION_NAME FROM RDB$RELATIONS WHERE RDB$SYSTEM_FLAG = 0 AND RDB$VIEW_BLR IS NULL;'
        )
        tables = fb_cursor.fetchall()

        # Needed to detect domain names that collide with tables/views (see resolve_pg_domain_name)
        fb_cursor.execute('SELECT RDB$RELATION_NAME FROM RDB$RELATIONS WHERE RDB$SYSTEM_FLAG = 0;')
        relation_names = {r[0].strip() for r in fb_cursor.fetchall() if r[0]}

        table_objs: list[Table] = []

        for table in tables:
            table_name = table[0].strip()

            fb_cursor.execute(f"""
                SELECT rf.RDB$FIELD_NAME, f.RDB$FIELD_TYPE, f.RDB$FIELD_SUB_TYPE, f.RDB$FIELD_LENGTH, 
                       COALESCE(rf.RDB$NULL_FLAG, f.RDB$NULL_FLAG),
                       f.RDB$FIELD_PRECISION, f.RDB$FIELD_SCALE,
                       rf.RDB$DEFAULT_SOURCE, f.RDB$DEFAULT_SOURCE,
                       rf.RDB$FIELD_SOURCE
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
                nullable = column[4] is None
                column_default = column[7].strip() if column[7] else None
                domain_default = column[8].strip() if column[8] else None
                field_source = column[9].strip() if column[9] else None

                column_data_type = resolve_firebird_type(column_type, column_subtype,
                                                         field_length=column[3],
                                                         field_precision=column[5],
                                                         field_scale=column[6])

                # RDB$FIELD_SOURCE starting with 'RDB$' is an implicit system domain, meaning the
                # column was declared with a raw type. Anything else is a user-defined domain,
                # which the column must reference in PostgreSQL to preserve the original design.
                domain_name = None
                if field_source and not field_source.startswith('RDB$'):
                    domain_name = resolve_pg_domain_name(field_source, relation_names)
                    # Only column-level overrides go inline; the domain carries its own default
                    default_value = column_default
                else:
                    default_value = column_default or domain_default

                table_obj.columns.append(
                    Column(column_name, column_data_type, nullable, default_value,
                           domain_name=domain_name)
                )

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

            table_objs.append(table_obj)

        triggers_query = """
            SELECT RDB$RELATION_NAME, RDB$TRIGGER_SOURCE
            FROM RDB$TRIGGERS
            WHERE RDB$SYSTEM_FLAG = 0
              AND RDB$TRIGGER_SOURCE IS NOT NULL;
        """
        fb_cursor.execute(triggers_query)
        triggers = fb_cursor.fetchall()

        pattern = re.compile(
            r'NEW\.([A-Za-z0-9_]+)\s*=\s*GEN_ID\s*\(\s*([A-Za-z0-9_]+)\s*,\s*\d+\s*\)',
            re.IGNORECASE
        )

        for trigger in triggers:
            relation_name = trigger[0].strip() if trigger[0] else None
            source = trigger[1]
            if not relation_name or not source:
                continue

            match = pattern.search(source)
            if match:
                column_name = match.group(1).strip()
                sequence_name = match.group(2).strip()

                table = next((t for t in table_objs if t.name == relation_name), None)
                if table:
                    column = next((c for c in table.columns if c.name == column_name), None)
                    if column:
                        column.sequence_name = sequence_name

        return table_objs
