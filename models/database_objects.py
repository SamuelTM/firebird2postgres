class Column:
    def __init__(self, name: str, column_type: str, nullable: bool, default_value: str = None,
                 sequence_name: str = None, domain_name: str = None, computed_source: str = None):
        self.name = name
        self.column_type = column_type
        self.nullable = nullable
        self.default_value = default_value
        # PostgreSQL-side identifier (lowercase); `name` keeps the original Firebird casing,
        # which is required for quoted (case-sensitive) queries against the source database
        self.sequence_name = sequence_name.lower() if sequence_name else None
        self.domain_name = domain_name
        self.computed_source = computed_source.strip() if computed_source else None

    @property
    def pg_name(self) -> str:
        return self.name.lower()


class ForeignKey:
    def __init__(self, key_name: str, local_column_name: str, local_column_index: int, referenced_table_name: str,
                 referenced_column_name: str, referenced_column_index: int,
                 update_rule: str = None, delete_rule: str = None):
        # All identifiers here are PostgreSQL-side only, so they are normalized to lowercase
        self.referenced_column_index = referenced_column_index
        self.referenced_column_name = referenced_column_name.lower()
        self.referenced_table_name = referenced_table_name.lower()
        self.local_column_index = local_column_index
        self.local_column_name = local_column_name.lower()
        self.key_name = key_name.lower()
        self.update_rule = update_rule.strip().upper() if update_rule else None
        self.delete_rule = delete_rule.strip().upper() if delete_rule else None


class UniqueKey:
    def __init__(self, name: str, column: str, is_primary_key: bool = False):
        # PostgreSQL-side only identifiers, normalized to lowercase
        self.name = name.lower()
        self.column = column.lower()
        self.is_primary_key = is_primary_key

    def __str__(self):
        type_str = "PRIMARY KEY" if self.is_primary_key else "UNIQUE KEY"
        return f'[{type_str}] Name: {self.name} - Column: {self.column}'


class Index:
    def __init__(self, index_name: str, unique: bool, inactive: bool,
                 column_name: str = None, column_index: int = 0, expression: str = None):
        # PostgreSQL-side only identifiers, normalized to lowercase
        self.column_index = column_index
        self.column_name = column_name.lower() if column_name else None
        self.inactive = inactive
        self.unique = unique
        self.index_name = index_name.lower()
        self.expression = expression.strip() if expression else None


def get_postgres_type(firebird_type: str) -> str:
    type_mapping = {
        'SMALLINT': 'SMALLINT',
        'INTEGER': 'INTEGER',
        'FLOAT': 'REAL',
        'DATE': 'DATE',
        'TIME': 'TIME',
        'CHAR': 'CHAR',
        'BIGINT': 'BIGINT',
        'DOUBLE PRECISION': 'DOUBLE PRECISION',
        'TIMESTAMP': 'TIMESTAMP',
        'VARCHAR': 'VARCHAR',
        'BLOB SUBTYPE 1': 'TEXT',
        'BLOB SUBTYPE 0': 'BYTEA',
        'NUMERIC': 'NUMERIC'
    }

    return type_mapping.get(firebird_type, firebird_type)


class Table:
    def __init__(self, name: str):
        self.name = name
        self.columns: list[Column] = []
        self.foreign_keys: list[ForeignKey] = []
        self.unique_keys: list[UniqueKey] = []
        self.indexes: list[Index] = []

    @property
    def pg_name(self) -> str:
        # PostgreSQL-side identifier (lowercase); `name` keeps the original Firebird casing,
        # which is required for quoted (case-sensitive) queries against the source database
        return self.name.lower()

    def get_sequence_queries(self) -> list[str]:
        """
        Returns a list of CREATE SEQUENCE statements for all sequence-bound columns.
        """
        return [f'CREATE SEQUENCE "{col.sequence_name}";'
                for col in self.columns if col.sequence_name]

    def get_create_table_query(self) -> str:
        """
        Returns the single CREATE TABLE statement with column definitions and constraints.
        """
        query = f'CREATE TABLE "{self.pg_name}" ('

        for i, col in enumerate(self.columns):
            type_decl = f'public."{col.domain_name}"' if col.domain_name else get_postgres_type(col.column_type)
            escaped_name = f'"{col.pg_name}"'

            if col.computed_source:
                expr = col.computed_source
                if not expr.startswith('(') or not expr.endswith(')'):
                    expr = f"({expr})"
                col_def = f'{escaped_name} {type_decl} GENERATED ALWAYS AS {expr} STORED'
            else:
                col_def = f'{escaped_name} {type_decl}'

            if not col.computed_source:
                if col.sequence_name:
                    col_def += f" DEFAULT nextval('\"{col.sequence_name}\"')"
                elif col.default_value:
                    col_def += f' {col.default_value}'

            if not col.nullable:
                col_def += ' NOT NULL'

            query += col_def

            if i < len(self.columns) - 1:
                query += ', '

        query += ');'

        return query

    def get_foreign_keys_query(self) -> str | None:
        """
        Returns an ALTER TABLE statement with all ADD CONSTRAINT FOREIGN KEY clauses,
        or None if the table has no foreign keys.
        """
        if not self.foreign_keys:
            return None

        foreign_keys_grouped_by_name: dict[str, list[ForeignKey]] = {}

        for foreign_key in self.foreign_keys:
            if foreign_key.key_name not in foreign_keys_grouped_by_name:
                foreign_keys_grouped_by_name[foreign_key.key_name] = [foreign_key]
            else:
                foreign_keys_grouped_by_name[foreign_key.key_name].append(foreign_key)

        query = f'ALTER TABLE "{self.pg_name}" ADD '

        for foreign_key_index, foreign_key_name in enumerate(foreign_keys_grouped_by_name):
            foreign_keys = foreign_keys_grouped_by_name[foreign_key_name]
            first_fk = foreign_keys[0]

            action_clause = ""
            if first_fk.delete_rule and first_fk.delete_rule not in ('RESTRICT', 'NO ACTION'):
                action_clause += f" ON DELETE {first_fk.delete_rule}"
            if first_fk.update_rule and first_fk.update_rule not in ('RESTRICT', 'NO ACTION'):
                action_clause += f" ON UPDATE {first_fk.update_rule}"

            if len(foreign_keys) > 1:
                # The catalog join yields a local x referenced segment cross product; keep
                # only the position-matched pairs, indexed by the real column position so
                # composite keys preserve the original Firebird column order
                pairs_by_position: dict[int, tuple[str, str]] = {}
                for foreign_key in foreign_keys:
                    if foreign_key.local_column_index == foreign_key.referenced_column_index:
                        pairs_by_position[foreign_key.local_column_index] = (
                            foreign_key.local_column_name, foreign_key.referenced_column_name)

                ordered_pairs = [pairs_by_position[pos] for pos in sorted(pairs_by_position)]

                local_columns_str = ", ".join([f'"{item}"' for item, _ in ordered_pairs])
                referenced_columns_str = ", ".join([f'"{item}"' for _, item in ordered_pairs])

                query += (f'CONSTRAINT "{foreign_key_name}" FOREIGN KEY ({local_columns_str}) '
                          f'REFERENCES "{first_fk.referenced_table_name}"({referenced_columns_str}){action_clause}')
            else:
                foreign_key = foreign_keys[0]
                query += (f'CONSTRAINT "{foreign_key.key_name}" FOREIGN KEY ("{foreign_key.local_column_name}") '
                          f'REFERENCES "{foreign_key.referenced_table_name}"("{foreign_key.referenced_column_name}"){action_clause}')

            if foreign_key_index < len(foreign_keys_grouped_by_name) - 1:
                query += ', ADD '

        query += ';'

        return query

    def get_unique_keys_query(self) -> str | None:
        """
        Returns an ALTER TABLE statement with all ADD CONSTRAINT PRIMARY KEY / UNIQUE clauses,
        or None if the table has no unique/primary keys.
        """
        if not self.unique_keys:
            return None

        unique_keys_grouped_by_name: dict[str, tuple[bool, list[str]]] = {}

        for unique_key in self.unique_keys:
            if unique_key.name not in unique_keys_grouped_by_name:
                unique_keys_grouped_by_name[unique_key.name] = (unique_key.is_primary_key, [unique_key.column])
            else:
                unique_keys_grouped_by_name[unique_key.name][1].append(unique_key.column)

        query = f'ALTER TABLE "{self.pg_name}" ADD '

        for unique_key_index, unique_key_name in enumerate(unique_keys_grouped_by_name):
            is_primary_key, column_names = unique_keys_grouped_by_name[unique_key_name]
            # Column order follows the original Firebird segment positions (guaranteed by
            # the extraction ORDER BY)

            columns_constraint = ', '.join([f'"{column_name}"' for column_name in column_names])
            constraint_type = "PRIMARY KEY" if is_primary_key else "UNIQUE"
            query += f'CONSTRAINT "{unique_key_name}" {constraint_type} ({columns_constraint})'

            if unique_key_index < len(unique_keys_grouped_by_name) - 1:
                query += ', ADD '

        query += ';'

        return query

    def get_index_queries(self) -> list[str]:
        """
        Returns a list of CREATE INDEX / CREATE UNIQUE INDEX statements for all secondary indexes.
        """
        if not self.indexes:
            return []

        indexes_grouped_by_name: dict[str, list[Index]] = {}

        for index in self.indexes:
            if index.index_name not in indexes_grouped_by_name:
                indexes_grouped_by_name[index.index_name] = [index]
            else:
                indexes_grouped_by_name[index.index_name].append(index)

        queries = []

        for index_name in indexes_grouped_by_name:
            first_idx = indexes_grouped_by_name[index_name][0]
            if first_idx.inactive:
                continue
            if first_idx.unique:
                query = f'CREATE UNIQUE INDEX "{index_name}" ON "{self.pg_name}" '
            else:
                query = f'CREATE INDEX "{index_name}" ON "{self.pg_name}" '

            if first_idx.expression:
                expr = first_idx.expression
                if not expr.startswith('(') or not expr.endswith(')'):
                    expr = f"({expr})"
                query += f'({expr});'
            else:
                column_names = ', '.join([f'"{idx.column_name}"' for idx in indexes_grouped_by_name[index_name] if idx.column_name])
                query += f'({column_names});'

            queries.append(query)

        return queries
