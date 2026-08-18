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
        tables = self._fetch_user_tables(fb_cursor)
        relation_names = self._fetch_relation_names(fb_cursor)

        table_objs: list[Table] = []
        for table_name in tables:
            table_obj = Table(table_name)
            table_obj.columns = self._extract_columns(fb_cursor, table_name, relation_names)
            table_obj.foreign_keys = self._extract_foreign_keys(fb_cursor, table_name)
            table_obj.unique_keys = self._extract_unique_keys(fb_cursor, table_name)
            table_obj.indexes = self._extract_indexes(fb_cursor, table_name)
            table_objs.append(table_obj)

        self._bind_sequence_generators(fb_cursor, table_objs)
        return table_objs

    @staticmethod
    def _fetch_user_tables(cursor) -> list[str]:
        """
        Fetches all user-defined table names (excluding system tables and views).
        """
        cursor.execute(
            'SELECT RDB$RELATION_NAME FROM RDB$RELATIONS WHERE RDB$SYSTEM_FLAG = 0 AND RDB$VIEW_BLR IS NULL;'
        )
        return [r[0].strip() for r in cursor.fetchall() if r[0]]

    @staticmethod
    def _fetch_relation_names(cursor) -> set[str]:
        """
        Fetches all relation names (tables/views) to detect domain naming collisions.
        """
        cursor.execute('SELECT RDB$RELATION_NAME FROM RDB$RELATIONS WHERE RDB$SYSTEM_FLAG = 0;')
        return {r[0].strip() for r in cursor.fetchall() if r[0]}

    @staticmethod
    def _extract_columns(cursor, table_name: str, relation_names: set[str]) -> list[Column]:
        """
        Extracts all columns for a given table, resolving types and domain mappings.
        """
        cursor.execute(f"""
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
        columns = []
        for column in cursor.fetchall():
            column_name = column[0].strip()
            field_type = column[1]
            field_subtype = column[2]
            field_length = column[3]
            nullable = column[4] is None
            field_precision = column[5]
            field_scale = column[6]
            column_default = column[7].strip() if column[7] else None
            domain_default = column[8].strip() if column[8] else None
            field_source = column[9].strip() if column[9] else None

            column_data_type = resolve_firebird_type(
                field_type=field_type,
                field_subtype=field_subtype,
                field_length=field_length,
                field_precision=field_precision,
                field_scale=field_scale,
            )

            # RDB$FIELD_SOURCE starting with 'RDB$' is an implicit system domain (raw type).
            # Anything else is a user-defined domain, referenced in PostgreSQL.
            domain_name = None
            if field_source and not field_source.startswith('RDB$'):
                domain_name = resolve_pg_domain_name(field_source, relation_names)
                default_value = column_default
            else:
                default_value = column_default or domain_default

            columns.append(
                Column(
                    name=column_name,
                    column_type=column_data_type,
                    nullable=nullable,
                    default_value=default_value,
                    domain_name=domain_name,
                )
            )
        return columns

    @staticmethod
    def _extract_foreign_keys(cursor, table_name: str) -> list[ForeignKey]:
        """
        Extracts foreign key definitions for a given table.
        """
        cursor.execute(f"""
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
        """)
        foreign_keys = []
        for row in cursor.fetchall():
            foreign_keys.append(
                ForeignKey(
                    key_name=row[0].strip(),
                    local_column_name=row[2].strip(),
                    local_column_index=row[1],
                    referenced_table_name=row[3].strip(),
                    referenced_column_name=row[5].strip(),
                    referenced_column_index=row[4],
                )
            )
        return foreign_keys

    @staticmethod
    def _extract_unique_keys(cursor, table_name: str) -> list[UniqueKey]:
        """
        Extracts primary and unique key constraints for a given table.
        """
        cursor.execute(f"""
            SELECT 
                rc.RDB$CONSTRAINT_NAME AS constraint_name,
                si.RDB$FIELD_NAME AS column_name,
                rc.RDB$CONSTRAINT_TYPE AS constraint_type
            FROM RDB$RELATION_CONSTRAINTS rc
            JOIN RDB$INDEX_SEGMENTS si ON rc.RDB$INDEX_NAME = si.RDB$INDEX_NAME
            WHERE rc.RDB$CONSTRAINT_TYPE IN ('UNIQUE', 'PRIMARY KEY')
              AND rc.RDB$RELATION_NAME = '{table_name}';
        """)
        unique_keys = []
        for row in cursor.fetchall():
            unique_key_column_name = row[1].strip()
            is_pk = row[2].strip() == 'PRIMARY KEY'
            unique_keys.append(
                UniqueKey(
                    name=row[0].strip(),
                    column=unique_key_column_name,
                    is_primary_key=is_pk,
                )
            )
        return unique_keys

    @staticmethod
    def _extract_indexes(cursor, table_name: str) -> list[Index]:
        """
        Extracts user-defined secondary indexes for a given table (excluding PK/UQ indexes).
        """
        cursor.execute(f"""
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
        """)
        indexes = []
        for row in cursor.fetchall():
            indexes.append(
                Index(
                    index_name=row[0].strip(),
                    unique=bool(row[1]),
                    inactive=bool(row[2]),
                    column_name=row[3].strip(),
                    column_index=row[4],
                )
            )
        return indexes

    @staticmethod
    def _bind_sequence_generators(cursor, table_objs: list[Table]) -> None:
        """
        Inspects trigger bodies for GEN_ID usage and binds identified sequences to table columns.
        """
        cursor.execute("""
            SELECT RDB$RELATION_NAME, RDB$TRIGGER_SOURCE
            FROM RDB$TRIGGERS
            WHERE RDB$SYSTEM_FLAG = 0
              AND RDB$TRIGGER_SOURCE IS NOT NULL;
        """)
        triggers = cursor.fetchall()
        pattern = re.compile(
            r'NEW\.([A-Za-z0-9_]+)\s*=\s*GEN_ID\s*\(\s*([A-Za-z0-9_]+)\s*,\s*\d+\s*\)',
            re.IGNORECASE
        )
        tables_by_name = {t.name: t for t in table_objs}

        for trigger in triggers:
            relation_name = trigger[0].strip() if trigger[0] else None
            source = trigger[1]
            if not relation_name or not source:
                continue

            match = pattern.search(source)
            if match:
                column_name = match.group(1).strip()
                sequence_name = match.group(2).strip()

                table = tables_by_name.get(relation_name)
                if table:
                    column = next((c for c in table.columns if c.name == column_name), None)
                    if column:
                        column.sequence_name = sequence_name
