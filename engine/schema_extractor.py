import re
from graphlib import TopologicalSorter, CycleError
from models import Table, Column, ForeignKey, UniqueKey, Index, Sequence, CheckConstraint, resolve_firebird_type, resolve_pg_domain_name, build_domain_mapping
from transpiler import FirebirdToPostgresVisitor, validate_immutable_expression


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
        domain_map = self._fetch_domain_map(fb_cursor, relation_names)

        table_objs: list[Table] = []
        for table_name in tables:
            table_obj = Table(table_name)
            table_obj.columns = self._extract_columns(fb_cursor, table_name, relation_names, domain_map=domain_map)
            table_obj.foreign_keys = self._extract_foreign_keys(fb_cursor, table_name)
            table_obj.unique_keys = self._extract_unique_keys(fb_cursor, table_name)
            col_symbols = {col.name.lower(): col.column_type for col in table_obj.columns}
            table_obj.indexes = self._extract_indexes(fb_cursor, table_name, symbols=col_symbols)
            table_obj.check_constraints = self._extract_check_constraints(fb_cursor, table_name, symbols=col_symbols)
            table_objs.append(table_obj)

        self._bind_sequence_generators(fb_cursor, table_objs)
        return table_objs

    def extract_sequences(self) -> list[Sequence]:
        """
        Extracts all user-defined sequences/generators from Firebird system catalog,
        preserving their names and querying their current values.
        """
        fb_cursor = self.fb_con.cursor()
        return self._extract_sequences(fb_cursor)

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
    def _fetch_domain_map(cursor, relation_names: set[str]) -> dict[str, str]:
        """
        Fetches all user-defined domains and builds a collision-free mapping.
        """
        cursor.execute("""
            SELECT DISTINCT RDB$FIELD_NAME FROM RDB$FIELDS
            WHERE RDB$SYSTEM_FLAG = 0 AND RDB$FIELD_NAME NOT STARTING WITH 'RDB$';
        """)
        domain_names = [r[0].strip() for r in cursor.fetchall() if r[0]]
        return build_domain_mapping(domain_names, relation_names)

    @staticmethod
    def _extract_columns(cursor, table_name: str, relation_names: set[str], domain_map: dict[str, str] = None) -> list[Column]:
        """
        Extracts all columns for a given table, resolving types and domain mappings.
        """
        cursor.execute("""
            SELECT rf.RDB$FIELD_NAME, f.RDB$FIELD_TYPE, f.RDB$FIELD_SUB_TYPE, f.RDB$FIELD_LENGTH, 
                   COALESCE(rf.RDB$NULL_FLAG, f.RDB$NULL_FLAG),
                   f.RDB$FIELD_PRECISION, f.RDB$FIELD_SCALE,
                   rf.RDB$DEFAULT_SOURCE, f.RDB$DEFAULT_SOURCE,
                   rf.RDB$FIELD_SOURCE, f.RDB$COMPUTED_SOURCE
            FROM RDB$RELATION_FIELDS rf
            JOIN RDB$FIELDS f ON rf.RDB$FIELD_SOURCE = f.RDB$FIELD_NAME
            WHERE rf.RDB$RELATION_NAME = ?
            ORDER BY rf.RDB$FIELD_POSITION;
        """, (table_name,))
        raw_rows = cursor.fetchall()
        symbols = {
            row[0].strip().lower(): resolve_firebird_type(
                field_type=row[1],
                field_subtype=row[2],
                field_length=row[3],
                field_precision=row[5],
                field_scale=row[6],
            )
            for row in raw_rows
        }
        columns = []
        for column in raw_rows:
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
            computed_source = column[10].strip() if column[10] else None
            if computed_source:
                computed_source = FirebirdToPostgresVisitor.transpile_expression(computed_source, symbols=symbols)

            column_data_type = symbols.get(column_name.lower()) or resolve_firebird_type(
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
                if domain_map and field_source.upper() in domain_map:
                    domain_name = domain_map[field_source.upper()]
                else:
                    domain_name = resolve_pg_domain_name(field_source, relation_names)
                default_value = column_default
            else:
                default_value = column_default or domain_default

            if default_value:
                default_value = FirebirdToPostgresVisitor.transpile_default_clause(default_value, symbols=symbols)

            columns.append(
                Column(
                    name=column_name,
                    column_type=column_data_type,
                    nullable=nullable,
                    default_value=default_value,
                    domain_name=domain_name,
                    computed_source=computed_source,
                )
            )

        SchemaExtractor._expand_computed_column_dependencies(columns, table_name)
        return columns

    @staticmethod
    def _expand_computed_column_dependencies(columns: list[Column], table_name: str) -> None:
        """
        Inlines references between computed columns within the same table.
        PostgreSQL generated columns cannot directly reference other generated columns.
        """
        computed_cols = {col.name: col for col in columns if col.computed_source}
        if not computed_cols:
            return

        strip_literals = re.compile(r"'(?:''|[^'])*'|/\*.*?\*/|--[^\n]*", flags=re.DOTALL)
        graph = {}
        for name, col in computed_cols.items():
            clean_expr = strip_literals.sub(" ", col.computed_source)
            deps = {
                other for other in computed_cols
                if other != name and re.search(rf'\b{re.escape(other)}\b', clean_expr, re.IGNORECASE)
            }
            if re.search(rf'\b{re.escape(name)}\b', clean_expr, re.IGNORECASE):
                raise ValueError(f"Self-referencing computed column '{name}' in table '{table_name}' is not permitted.")
            graph[name] = deps

        try:
            sorter = TopologicalSorter(graph)
            order = list(sorter.static_order())
        except CycleError as e:
            raise ValueError(f"Circular dependency detected between computed columns in table '{table_name}': {e}") from e

        for name in order:
            col = computed_cols[name]
            curr_expr = col.computed_source
            for dep in graph[name]:
                dep_col = computed_cols[dep]
                curr_expr = re.sub(
                    rf'\b{re.escape(dep)}\b',
                    f"({dep_col.computed_source})",
                    curr_expr,
                    flags=re.IGNORECASE
                )
            col.computed_source = curr_expr
            validate_immutable_expression(col.computed_source, f"computed column '{name}' in table '{table_name}'")

    @staticmethod
    def _extract_foreign_keys(cursor, table_name: str) -> list[ForeignKey]:
        """
        Extracts foreign key definitions for a given table.
        """
        cursor.execute("""
            SELECT 
                rc.RDB$CONSTRAINT_NAME AS foreign_key_name,
                si.RDB$FIELD_POSITION AS column_position,
                si.RDB$FIELD_NAME AS local_column,
                rs.RDB$RELATION_NAME AS referenced_table,
                rsi.RDB$FIELD_POSITION AS referenced_column_position,
                rsi.RDB$FIELD_NAME AS referenced_column,
                refc.RDB$UPDATE_RULE AS update_rule,
                refc.RDB$DELETE_RULE AS delete_rule
            FROM RDB$RELATION_CONSTRAINTS rc
            JOIN RDB$INDEX_SEGMENTS si ON rc.RDB$INDEX_NAME = si.RDB$INDEX_NAME
            JOIN RDB$REF_CONSTRAINTS refc ON rc.RDB$CONSTRAINT_NAME = refc.RDB$CONSTRAINT_NAME
            JOIN RDB$RELATION_CONSTRAINTS rs ON refc.RDB$CONST_NAME_UQ = rs.RDB$CONSTRAINT_NAME
            JOIN RDB$INDEX_SEGMENTS rsi ON rs.RDB$INDEX_NAME = rsi.RDB$INDEX_NAME
            WHERE rc.RDB$CONSTRAINT_TYPE = 'FOREIGN KEY'
              AND rc.RDB$RELATION_NAME = ?
            ORDER BY foreign_key_name, column_position;
        """, (table_name,))
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
                    update_rule=row[6].strip() if row[6] else None,
                    delete_rule=row[7].strip() if row[7] else None,
                )
            )
        return foreign_keys

    @staticmethod
    def _extract_unique_keys(cursor, table_name: str) -> list[UniqueKey]:
        """
        Extracts primary and unique key constraints for a given table.
        Rows are ordered by segment position so composite keys preserve the original
        Firebird column order in the generated PostgreSQL DDL.
        """
        cursor.execute("""
            SELECT 
                rc.RDB$CONSTRAINT_NAME AS constraint_name,
                si.RDB$FIELD_NAME AS column_name,
                rc.RDB$CONSTRAINT_TYPE AS constraint_type
            FROM RDB$RELATION_CONSTRAINTS rc
            JOIN RDB$INDEX_SEGMENTS si ON rc.RDB$INDEX_NAME = si.RDB$INDEX_NAME
            WHERE rc.RDB$CONSTRAINT_TYPE IN ('UNIQUE', 'PRIMARY KEY')
              AND rc.RDB$RELATION_NAME = ?
            ORDER BY rc.RDB$CONSTRAINT_NAME, si.RDB$FIELD_POSITION;
        """, (table_name,))
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
    def _extract_indexes(cursor, table_name: str, symbols: dict[str, str] = None) -> list[Index]:
        """
        Extracts user-defined secondary indexes for a given table (excluding PK/UQ indexes),
        supporting both standard column-segment indexes and expression-based indexes (COMPUTED BY).
        """
        cursor.execute("""
            SELECT 
                i.RDB$INDEX_NAME AS index_name,
                i.RDB$UNIQUE_FLAG AS is_unique,
                i.RDB$INDEX_INACTIVE AS is_inactive,
                seg.RDB$FIELD_NAME AS column_name,
                seg.RDB$FIELD_POSITION AS column_position,
                i.RDB$EXPRESSION_SOURCE AS expression_source
            FROM RDB$INDICES i
            LEFT JOIN RDB$INDEX_SEGMENTS seg ON i.RDB$INDEX_NAME = seg.RDB$INDEX_NAME
            WHERE i.RDB$RELATION_NAME = ?
              AND i.RDB$INDEX_NAME NOT IN (
                  SELECT RDB$INDEX_NAME 
                  FROM RDB$RELATION_CONSTRAINTS 
                  WHERE RDB$CONSTRAINT_TYPE IN ('PRIMARY KEY', 'UNIQUE') 
                    AND RDB$INDEX_NAME IS NOT NULL
              )
            ORDER BY i.RDB$INDEX_NAME, seg.RDB$FIELD_POSITION;
        """, (table_name,))
        indexes = []
        for row in cursor.fetchall():
            raw_expr = row[5]
            expr_str = raw_expr.strip() if raw_expr else None
            if expr_str:
                expr_str = FirebirdToPostgresVisitor.transpile_expression(expr_str, symbols=symbols)
                validate_immutable_expression(expr_str, f"expression index '{row[0].strip()}' in table '{table_name}'")
            col_name = row[3].strip() if row[3] else None
            indexes.append(
                Index(
                    index_name=row[0].strip(),
                    unique=bool(row[1]),
                    inactive=bool(row[2]),
                    column_name=col_name,
                    column_index=row[4] if row[4] is not None else 0,
                    expression=expr_str,
                )
            )
        return indexes

    @staticmethod
    def _extract_check_constraints(cursor, table_name: str, symbols: dict[str, str] = None) -> list[CheckConstraint]:
        """
        Extracts table-level CHECK constraints from Firebird system catalog,
        transpiling their expressions to PostgreSQL.
        Distinguishes table checks from domain checks (domain checks are on RDB$FIELDS).
        """
        query = """
            SELECT DISTINCT
                rc.RDB$CONSTRAINT_NAME,
                t.RDB$TRIGGER_SOURCE
            FROM RDB$RELATION_CONSTRAINTS rc
            JOIN RDB$CHECK_CONSTRAINTS cc ON cc.RDB$CONSTRAINT_NAME = rc.RDB$CONSTRAINT_NAME
            JOIN RDB$TRIGGERS t ON t.RDB$TRIGGER_NAME = cc.RDB$TRIGGER_NAME
            WHERE rc.RDB$RELATION_NAME = ?
              AND rc.RDB$CONSTRAINT_TYPE = 'CHECK'
              AND t.RDB$TRIGGER_SOURCE IS NOT NULL
            ORDER BY rc.RDB$CONSTRAINT_NAME;
        """
        cursor.execute(query, (table_name,))
        rows = cursor.fetchall()
        checks: list[CheckConstraint] = []
        seen = set()
        for row in rows:
            cname = row[0].strip() if row[0] else None
            source = row[1].strip() if row[1] else None
            if not cname or not source or cname in seen:
                continue
            seen.add(cname)

            # Strip CHECK keyword and outer parentheses if present
            m = re.match(r'^\s*CHECK\s*\((.*)\)\s*$', source, re.IGNORECASE | re.DOTALL)
            if m:
                inner_expr = m.group(1).strip()
            else:
                m2 = re.match(r'^\s*CHECK\s+(.*)$', source, re.IGNORECASE | re.DOTALL)
                inner_expr = m2.group(1).strip() if m2 else source

            try:
                pg_expr = FirebirdToPostgresVisitor.transpile_expression(inner_expr, symbols=symbols)
            except Exception:
                pg_expr = inner_expr

            checks.append(CheckConstraint(name=cname, expression=pg_expr))
        return checks

    @staticmethod
    def _bind_sequence_generators(cursor, table_objs: list[Table]) -> None:
        """
        Inspects trigger bodies for GEN_ID / NEXT VALUE FOR usage and binds identified
        sequences to table columns only for genuine auto-increment / identity defaults
        on BEFORE INSERT triggers (RDB$TRIGGER_TYPE = 1).
        Ignores commented-out code, step != 1 (e.g. GEN_ID(..., 0)), non-BEFORE-INSERT triggers,
        and assignments conditioned on other columns.
        """
        cursor.execute("""
            SELECT RDB$RELATION_NAME, RDB$TRIGGER_SOURCE, RDB$TRIGGER_TYPE
            FROM RDB$TRIGGERS
            WHERE RDB$SYSTEM_FLAG = 0
              AND RDB$TRIGGER_SOURCE IS NOT NULL
              AND (RDB$TRIGGER_INACTIVE = 0 OR RDB$TRIGGER_INACTIVE IS NULL);
        """)
        triggers = cursor.fetchall()
        tables_by_name = {t.name.upper(): t for t in table_objs}

        uncond_re = re.compile(
            r"^(?:(?:AS\s+)?BEGIN\s+)?NEW\.(?:\"|\s)*([A-Za-z0-9_]+)(?:\"|\s)*=\s*(?:GEN_ID\s*\(\s*([A-Za-z0-9_]+)\s*,\s*1\s*\)|NEXT\s+VALUE\s+FOR\s+([A-Za-z0-9_]+))\s*(?:END)?$",
            re.IGNORECASE
        )
        if_re = re.compile(
            r"^(?:(?:AS\s+)?BEGIN\s+)?IF\s*\((.*?)\)\s*THEN\s*(?:BEGIN\s+)?NEW\.(?:\"|\s)*([A-Za-z0-9_]+)(?:\"|\s)*=\s*(?:GEN_ID\s*\(\s*([A-Za-z0-9_]+)\s*,\s*1\s*\)|NEXT\s+VALUE\s+FOR\s+([A-Za-z0-9_]+))\s*(?:END)?$",
            re.IGNORECASE | re.DOTALL
        )

        for trigger in triggers:
            relation_name = trigger[0].strip() if trigger[0] else None
            source = trigger[1]
            trigger_type = trigger[2] if len(trigger) > 2 else 1
            if not relation_name or not source or trigger_type != 1:
                continue

            table = tables_by_name.get(relation_name.upper())
            if not table:
                continue

            # Strip comments (-- and /* ... */)
            clean = re.sub(r"--[^\r\n]*", "", source)
            clean = re.sub(r"/\*.*?\*/", "", clean, flags=re.DOTALL)

            stmts = [s.strip() for s in clean.split(";") if s.strip()]
            for stmt in stmts:
                col_name = None
                seq_name = None

                m_uncond = uncond_re.match(stmt)
                if m_uncond:
                    col_name = m_uncond.group(1).strip()
                    seq_name = (m_uncond.group(2) or m_uncond.group(3)).strip().lower()
                else:
                    m_if = if_re.match(stmt)
                    if m_if:
                        cond = m_if.group(1).strip()
                        c = m_if.group(2).strip()
                        s = (m_if.group(3) or m_if.group(4)).strip().lower()
                        cond_cols = re.findall(r"NEW\.(?:\"|\s)*([A-Za-z0-9_]+)(?:\"|\s)*", cond, re.IGNORECASE)
                        # Verify condition only guards this same column (e.g. NEW.ID IS NULL or NEW.ID = 0)
                        if cond_cols and all(col.upper() == c.upper() for col in cond_cols):
                            col_name = c
                            seq_name = s

                if col_name and seq_name:
                    column = next((c for c in table.columns if c.name.upper() == col_name.upper()), None)
                    if column:
                        column.sequence_name = seq_name

    @staticmethod
    def _extract_sequences(cursor) -> list[Sequence]:
        """
        Queries all user-defined generators from RDB$GENERATORS and reads their current values.
        """
        cursor.execute("""
            SELECT RDB$GENERATOR_NAME
            FROM RDB$GENERATORS
            WHERE (RDB$SYSTEM_FLAG = 0 OR RDB$SYSTEM_FLAG IS NULL)
              AND RDB$GENERATOR_NAME NOT STARTING WITH 'RDB$'
              AND RDB$GENERATOR_NAME NOT STARTING WITH 'MON$';
        """)
        seq_names = [row[0].strip() for row in cursor.fetchall()]
        sequences = []
        for name in seq_names:
            safe_name = name.replace('"', '""')
            try:
                cursor.execute(f'SELECT GEN_ID("{safe_name}", 0) FROM RDB$DATABASE;')
                row = cursor.fetchone()
                if not row or row[0] is None:
                    raise RuntimeError(f"Failed to read current value for generator '{name}': no value returned")
                curr_val = int(row[0])
            except Exception as e:
                raise RuntimeError(f"Failed to read current value for generator '{name}': {e}") from e
            sequences.append(Sequence(name=name, current_value=curr_val))
        return sequences
