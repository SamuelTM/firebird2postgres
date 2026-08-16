class Column:
    def __init__(self, name: str, column_type: str, size: int, nullable: bool, default_value: str = None,
                 sequence_name: str = None, domain_name: str = None):
        self.name = name
        self.column_type = column_type
        self.size = size
        self.nullable = nullable
        self.default_value = default_value
        self.sequence_name = sequence_name
        self.domain_name = domain_name


class ForeignKey:
    def __init__(self, key_name: str, local_column_name: str, local_column_index: int, referenced_table_name: str,
                 referenced_column_name: str, referenced_column_index: int):
        self.referenced_column_index = referenced_column_index
        self.referenced_column_name = referenced_column_name
        self.referenced_table_name = referenced_table_name
        self.local_column_index = local_column_index
        self.local_column_name = local_column_name
        self.key_name = key_name


class UniqueKey:
    def __init__(self, name: str, column: str, is_primary_key: bool = False):
        self.name = name
        self.column = column
        self.is_primary_key = is_primary_key

    def __str__(self):
        type_str = "PRIMARY KEY" if self.is_primary_key else "UNIQUE KEY"
        return f'[{type_str}] Name: {self.name} - Column: {self.column}'


class Index:
    def __init__(self, index_name: str, unique: bool, inactive: bool, column_name: str, column_index: int):
        self.column_index = column_index
        self.column_name = column_name
        self.inactive = inactive
        self.unique = unique
        self.index_name = index_name


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

    def get_sequences_query(self):
        queries = []
        for col in self.columns:
            if col.sequence_name:
                queries.append(f'CREATE SEQUENCE "{col.sequence_name}";')
        return queries

    def get_create_query(self):
        query = f'CREATE TABLE "{self.name}" ('

        for i, col in enumerate(self.columns):
            converted_type = get_postgres_type(col.column_type)
            escaped_name = f'"{col.name}"'

            if col.domain_name:
                # Column declared with a user domain: reference it (schema-qualified, lowercase)
                # to preserve the original semantics and bypass pg_catalog name shadowing
                col_def = f'{escaped_name} public."{col.domain_name}"'
            elif 'char' in col.column_type.lower().strip():
                col_def = f'{escaped_name} {converted_type}({col.size})'
            else:
                col_def = f'{escaped_name} {converted_type}'

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

    def get_foreign_keys_query(self):
        if len(self.foreign_keys) > 0:
            foreign_keys_grouped_by_name: dict[str, list[ForeignKey]] = {}

            for foreign_key in self.foreign_keys:
                if foreign_key.key_name not in foreign_keys_grouped_by_name:
                    foreign_keys_grouped_by_name[foreign_key.key_name] = [foreign_key]
                else:
                    foreign_keys_grouped_by_name[foreign_key.key_name].append(foreign_key)

            query = f'ALTER TABLE "{self.name}" ADD '

            for foreign_key_index, foreign_key_name in enumerate(foreign_keys_grouped_by_name):
                foreign_keys = foreign_keys_grouped_by_name[foreign_key_name]
                if len(foreign_keys) > 1:
                    local_referenced_pairs = set()

                    for foreign_key in foreign_keys:
                        if foreign_key.local_column_index == foreign_key.referenced_column_index:
                            local_referenced_pairs.add(
                                (foreign_key.local_column_name, foreign_key.referenced_column_name))

                    ordered_pairs = sorted(local_referenced_pairs, key=lambda x: x[1])

                    local_columns = [x[0] for x in ordered_pairs]
                    referenced_columns = [x[1] for x in ordered_pairs]

                    local_columns_str = ", ".join([f'"{item}"' for item in local_columns])
                    referenced_columns_str = ", ".join([f'"{item}"' for item in referenced_columns])

                    query += (f'CONSTRAINT "{foreign_key_name}" FOREIGN KEY ({local_columns_str}) '
                              f'REFERENCES "{foreign_keys[0].referenced_table_name}"({referenced_columns_str})')
                else:
                    foreign_key = foreign_keys[0]
                    query += (f'CONSTRAINT "{foreign_key.key_name}" FOREIGN KEY ("{foreign_key.local_column_name}") '
                              f'REFERENCES "{foreign_key.referenced_table_name}"("{foreign_key.referenced_column_name}")')

                if foreign_key_index < len(foreign_keys_grouped_by_name) - 1:
                    query += ', ADD '

            query += ';'

            return query

        return None

    def get_unique_keys_query(self):
        if len(self.unique_keys) > 0:
            unique_keys_grouped_by_name: dict[str, tuple[bool, list[str]]] = {}

            for unique_key in self.unique_keys:
                if unique_key.name not in unique_keys_grouped_by_name:
                    unique_keys_grouped_by_name[unique_key.name] = (unique_key.is_primary_key, [unique_key.column])
                else:
                    unique_keys_grouped_by_name[unique_key.name][1].append(unique_key.column)

            query = f'ALTER TABLE "{self.name}" ADD '

            for unique_key_index, unique_key_name in enumerate(unique_keys_grouped_by_name):

                is_primary_key, column_names = unique_keys_grouped_by_name[unique_key_name]
                ordered_column_names = list(column_names)
                ordered_column_names.sort()

                columns_constraint = ', '.join(
                    [f'"{column_name}"' for column_name in ordered_column_names])

                constraint_type = "PRIMARY KEY" if is_primary_key else "UNIQUE"
                query += f'CONSTRAINT "{unique_key_name}" {constraint_type} ({columns_constraint})'

                if unique_key_index < len(unique_keys_grouped_by_name) - 1:
                    query += ', ADD '

            query += ';'

            return query

        return None

    def get_indexes_query(self):
        if len(self.indexes) > 0:
            indexes_grouped_by_name: dict[str, list[Index]] = {}

            for index in self.indexes:
                if index.index_name not in indexes_grouped_by_name:
                    indexes_grouped_by_name[index.index_name] = [index]
                else:
                    indexes_grouped_by_name[index.index_name].append(index)

            queries = []

            for index_name in indexes_grouped_by_name:
                unique = indexes_grouped_by_name[index_name][0].unique
                if unique:
                    query = f'CREATE UNIQUE INDEX "{index_name}" ON "{self.name}" '
                else:
                    query = f'CREATE INDEX "{index_name}" ON "{self.name}" '

                column_names = ', '.join(
                    [f'"{idx.column_name}"' for idx in indexes_grouped_by_name[index_name]])

                query += f'({column_names});'

                queries.append(query)

            return queries
        return None
