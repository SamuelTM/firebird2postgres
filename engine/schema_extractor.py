import re
from graphlib import TopologicalSorter, CycleError
import firebirdsql
from models import (
    Table, Column, ForeignKey, UniqueKey, Index, Sequence, CheckConstraint,
    get_postgres_type, resolve_firebird_type, resolve_pg_domain_name, build_domain_mapping
)
from transpiler import FirebirdToPostgresVisitor, validate_immutable_expression


# Official Firebird SQLCODE/GDSCODE table (fblangref appendix B.2):
_GDS_NO_PERMISSION = 335544352
_GDS_DYNAMIC_SQL_ERROR = 335544569  # isc_dsql_error: generic wrapper, NEVER sufficient alone
_GDS_COLUMN_UNKNOWN = 335544578     # isc_dsql_field_err: "Column unknown"
_SQLCODE_COLUMN_UNKNOWN = -206
_SQLCODE_NO_PERMISSION = -551


def is_column_not_found_error(e: Exception, column_name: str = "RDB$GENERATOR_INCREMENT") -> bool:
    """
    Returns True only with specific evidence that the named column does not
    exist in the Firebird catalog (e.g., older Firebird versions where
    RDB$GENERATOR_INCREMENT was not present).
    335544569 alone proves nothing: it is the generic "Dynamic SQL Error"
    wrapper also carried by syntax errors (-104), which must abort instead
    of silently falling back to increment 1. Likewise, an unknown DIFFERENT
    column, permission, connection or catalog failure returns False.
    """
    if not isinstance(e, firebirdsql.Error):
        return False
    msg = str(e).lower()
    sql_code = getattr(e, "sql_code", None)
    gds_codes = getattr(e, "gds_codes", set()) or set()

    # Permission errors must never be treated as column unknown
    if sql_code == _SQLCODE_NO_PERMISSION or _GDS_NO_PERMISSION in gds_codes \
            or "permission" in msg or "privilege" in msg:
        return False

    # Connection errors must never be treated as column unknown
    if "connection" in msg or "socket" in msg or "network" in msg or "broken pipe" in msg:
        return False

    # A known SQLCODE other than column-unknown disproves the fallback.
    if sql_code is not None and sql_code != _SQLCODE_COLUMN_UNKNOWN:
        return False

    # The evidence must name THIS column as unknown: either an unknown
    # indicator next to its name, or the specific facility code.
    col_lower = column_name.lower()
    if col_lower not in msg:
        return False
    if "unknown" not in msg and _GDS_COLUMN_UNKNOWN not in gds_codes:
        return False

    return True


def fetch_all_sequence_increments(cursor) -> dict[str, int]:
    """
    Fetches all user-defined sequence/generator increments from Firebird system catalog.
    Returns a dict mapping lowercase generator name to its increment value.
    """
    query = """
        SELECT TRIM(RDB$GENERATOR_NAME), COALESCE(RDB$GENERATOR_INCREMENT, 1)
        FROM RDB$GENERATORS
        WHERE (RDB$SYSTEM_FLAG = 0 OR RDB$SYSTEM_FLAG IS NULL)
          AND RDB$GENERATOR_NAME NOT STARTING WITH 'RDB$'
          AND RDB$GENERATOR_NAME NOT STARTING WITH 'MON$';
    """
    increments = {}
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
    except firebirdsql.Error as e:
        if not is_column_not_found_error(e, "RDB$GENERATOR_INCREMENT"):
            raise RuntimeError(f"Failed to fetch sequence increments from Firebird: {e}") from e
        try:
            cursor.execute("""
                SELECT RDB$GENERATOR_NAME, 1
                FROM RDB$GENERATORS
                WHERE (RDB$SYSTEM_FLAG = 0 OR RDB$SYSTEM_FLAG IS NULL)
                  AND RDB$GENERATOR_NAME NOT STARTING WITH 'RDB$'
                  AND RDB$GENERATOR_NAME NOT STARTING WITH 'MON$';
            """)
            rows = cursor.fetchall()
        except Exception as fallback_err:
            raise RuntimeError(f"Failed to fetch sequence increments from Firebird: {fallback_err}") from fallback_err
    except Exception as e:
        raise RuntimeError(f"Failed to fetch sequence increments from Firebird: {e}") from e

    for row in rows:
        if row and row[0]:
            seq_name = str(row[0]).strip()
            val = row[1] if len(row) > 1 else 1
            if val is None:
                raise ValueError(
                    f"Invalid sequence increment None for generator '{seq_name}': sequence increment cannot be null"
                )
            try:
                inc = int(val)
            except (ValueError, TypeError) as e:
                raise ValueError(
                    f"Invalid sequence increment {val!r} for generator '{seq_name}': must be a valid integer"
                ) from e
            if inc == 0:
                raise ValueError(
                    f"Invalid sequence increment 0 for generator '{seq_name}': sequence increment cannot be zero"
                )
            increments[seq_name.lower()] = inc
    return increments


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
        seq_increments = fetch_all_sequence_increments(fb_cursor)

        table_objs: list[Table] = []
        for table_name in tables:
            table_obj = Table(table_name)
            table_obj.columns = self._extract_columns(
                fb_cursor, table_name, relation_names, domain_map=domain_map, sequence_increments=seq_increments
            )
            table_obj.foreign_keys = self._extract_foreign_keys(fb_cursor, table_name)
            table_obj.unique_keys = self._extract_unique_keys(fb_cursor, table_name)
            col_symbols = {col.name.lower(): col.column_type for col in table_obj.columns}
            table_obj.indexes = self._extract_indexes(
                fb_cursor, table_name, symbols=col_symbols, sequence_increments=seq_increments
            )
            table_obj.check_constraints = self._extract_check_constraints(
                fb_cursor, table_name, symbols=col_symbols, sequence_increments=seq_increments
            )
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
            WHERE RDB$SYSTEM_FLAG = 0 AND RDB$FIELD_NAME NOT STARTING WITH 'RDB$'
            ORDER BY RDB$FIELD_NAME;
        """)
        domain_names = [r[0].strip() for r in cursor.fetchall() if r[0]]
        return build_domain_mapping(domain_names, relation_names)

    @staticmethod
    def _extract_columns(cursor, table_name: str, relation_names: set[str],
                         domain_map: dict[str, str] = None,
                         sequence_increments: dict[str, int] = None) -> list[Column]:
        """
        Extracts all columns for a given table, resolving types and domain mappings.
        """
        try:
            cursor.execute("""
                SELECT rf.RDB$FIELD_NAME, f.RDB$FIELD_TYPE, f.RDB$FIELD_SUB_TYPE,
                       COALESCE(f.RDB$CHARACTER_LENGTH, f.RDB$FIELD_LENGTH),
                       COALESCE(rf.RDB$NULL_FLAG, f.RDB$NULL_FLAG),
                       f.RDB$FIELD_PRECISION, f.RDB$FIELD_SCALE,
                       rf.RDB$DEFAULT_SOURCE, f.RDB$DEFAULT_SOURCE,
                       rf.RDB$FIELD_SOURCE, f.RDB$COMPUTED_SOURCE,
                       rf.RDB$IDENTITY_TYPE, rf.RDB$GENERATOR_NAME,
                       f.RDB$CHARACTER_SET_ID, f.RDB$DIMENSIONS
                FROM RDB$RELATION_FIELDS rf
                JOIN RDB$FIELDS f ON rf.RDB$FIELD_SOURCE = f.RDB$FIELD_NAME
                WHERE rf.RDB$RELATION_NAME = ?
                ORDER BY rf.RDB$FIELD_POSITION;
            """, (table_name,))
            raw_rows = cursor.fetchall()
        except firebirdsql.Error:
            try:
                cursor.execute("""
                    SELECT rf.RDB$FIELD_NAME, f.RDB$FIELD_TYPE, f.RDB$FIELD_SUB_TYPE,
                           COALESCE(f.RDB$CHARACTER_LENGTH, f.RDB$FIELD_LENGTH),
                           COALESCE(rf.RDB$NULL_FLAG, f.RDB$NULL_FLAG),
                           f.RDB$FIELD_PRECISION, f.RDB$FIELD_SCALE,
                           rf.RDB$DEFAULT_SOURCE, f.RDB$DEFAULT_SOURCE,
                           rf.RDB$FIELD_SOURCE, f.RDB$COMPUTED_SOURCE,
                           rf.RDB$IDENTITY_TYPE, NULL,
                           f.RDB$CHARACTER_SET_ID, f.RDB$DIMENSIONS
                    FROM RDB$RELATION_FIELDS rf
                    JOIN RDB$FIELDS f ON rf.RDB$FIELD_SOURCE = f.RDB$FIELD_NAME
                    WHERE rf.RDB$RELATION_NAME = ?
                    ORDER BY rf.RDB$FIELD_POSITION;
                """, (table_name,))
                raw_rows = cursor.fetchall()
            except firebirdsql.Error:
                cursor.execute("""
                    SELECT rf.RDB$FIELD_NAME, f.RDB$FIELD_TYPE, f.RDB$FIELD_SUB_TYPE,
                           COALESCE(f.RDB$CHARACTER_LENGTH, f.RDB$FIELD_LENGTH),
                           COALESCE(rf.RDB$NULL_FLAG, f.RDB$NULL_FLAG),
                           f.RDB$FIELD_PRECISION, f.RDB$FIELD_SCALE,
                           rf.RDB$DEFAULT_SOURCE, f.RDB$DEFAULT_SOURCE,
                           rf.RDB$FIELD_SOURCE, f.RDB$COMPUTED_SOURCE,
                           NULL, NULL,
                           f.RDB$CHARACTER_SET_ID, f.RDB$DIMENSIONS
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
                character_set_id=row[13] if len(row) > 13 else None,
                dimensions=row[14] if len(row) > 14 else None,
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
            charset_id = column[13] if len(column) > 13 else None
            dimensions = column[14] if len(column) > 14 else None

            if dimensions is not None and dimensions > 0:
                raise NotImplementedError(
                    f"Firebird array columns are not supported (column '{column_name}' in table '{table_name}')."
                )

            if computed_source:
                try:
                    computed_source = FirebirdToPostgresVisitor.transpile_expression(
                        computed_source, symbols=symbols, sequence_increments=sequence_increments
                    )
                except Exception as e:
                    raise RuntimeError(
                        f"Failed to transpile computed column '{column_name}' in table '{table_name}': "
                        f"expression '{column[10].strip()}' could not be converted to PostgreSQL. Cause: {e}"
                    ) from e

            column_data_type = symbols.get(column_name.lower()) or resolve_firebird_type(
                field_type=field_type,
                field_subtype=field_subtype,
                field_length=field_length,
                field_precision=field_precision,
                field_scale=field_scale,
                character_set_id=charset_id,
                dimensions=dimensions,
            )

            if not column_data_type:
                raise TypeError(
                    f"Unsupported or unrecognized Firebird data type (field_type={field_type}, "
                    f"field_subtype={field_subtype}) for column '{column_name}' in table '{table_name}'."
                )

            # Preserve domains: if field_source is a user domain, retain its name
            domain_name = None
            if field_source and not field_source.startswith('RDB$'):
                clean_fs = field_source.upper()
                if domain_map and clean_fs in domain_map:
                    domain_name = domain_map[clean_fs]
                elif relation_names:
                    domain_name = resolve_pg_domain_name(field_source, relation_names)
                else:
                    domain_name = field_source.lower()
                default_value = column_default
            else:
                default_value = column_default or domain_default

            if default_value:
                try:
                    default_value = FirebirdToPostgresVisitor.transpile_default_clause(
                        default_value, symbols=symbols, sequence_increments=sequence_increments
                    )
                except Exception as e:
                    raise RuntimeError(
                        f"Failed to transpile default value for column '{column_name}' in table '{table_name}': "
                        f"expression '{default_value}' could not be converted to PostgreSQL. Cause: {e}"
                    ) from e

            identity_flag = column[11] if len(column) > 11 else None
            identity_type = None
            identity_increment = None
            identity_current = None
            if identity_flag is not None:
                identity_type = 'ALWAYS' if identity_flag == 0 else 'BY DEFAULT'
                gen_name = column[12].strip() if len(column) > 12 and column[12] else None
                if gen_name:
                    try:
                        cursor.execute("SELECT COALESCE(RDB$GENERATOR_INCREMENT, 1) FROM RDB$GENERATORS WHERE RDB$GENERATOR_NAME = ?;", (gen_name,))
                        grow = cursor.fetchone()
                        if not grow or grow[0] is None:
                            raise RuntimeError(
                                f"Generator '{gen_name}' for identity column '{column_name}' in table '{table_name}' was not found in RDB$GENERATORS."
                            )
                        identity_increment = int(grow[0])
                    except (firebirdsql.Error, ValueError, TypeError) as e:
                        raise RuntimeError(
                            f"Failed to read generator increment for identity column '{column_name}' in table '{table_name}' from generator '{gen_name}': {e}"
                        ) from e

                    try:
                        safe_gen = gen_name.replace('"', '""')
                        cursor.execute(f'SELECT GEN_ID("{safe_gen}", 0) FROM RDB$DATABASE;')
                        vrow = cursor.fetchone()
                        if not vrow or vrow[0] is None:
                            raise RuntimeError(
                                f"Failed to retrieve current value for generator '{gen_name}' of identity column '{column_name}' in table '{table_name}'."
                            )
                        identity_current = int(vrow[0])
                    except (firebirdsql.Error, ValueError, TypeError) as e:
                        raise RuntimeError(
                            f"Failed to read current generator state for identity column '{column_name}' in table '{table_name}' from generator '{gen_name}': {e}"
                        ) from e

            columns.append(
                Column(
                    name=column_name,
                    column_type=column_data_type,
                    nullable=nullable,
                    default_value=default_value,
                    domain_name=domain_name,
                    computed_source=computed_source,
                    identity_type=identity_type,
                    identity_increment=identity_increment,
                    identity_current=identity_current,
                )
            )

        SchemaExtractor._expand_computed_column_dependencies(columns, table_name)
        return columns

    @staticmethod
    def _expand_computed_column_dependencies(columns: list[Column], table_name: str) -> None:
        """
        Inlines references between computed columns within the same table.
        PostgreSQL generated columns cannot directly reference other generated columns.
        Substitutions operate strictly on column identifier references (preserving string literals
        and comments) and preserve the declared data type via explicit casts.
        """
        computed_cols = {col.name: col for col in columns if col.computed_source}
        if not computed_cols:
            return

        _ident = r'(?:"(?:""|[^"])+"|[A-Za-z0-9_$]+)'
        token_pat = re.compile(
            r"('(?:''|[^'])*'|/\*.*?\*/|--[^\n]*)"
            r"|((?:(?:" + _ident + r")\s*\.\s*)?(?:" + _ident + r"))",
            flags=re.DOTALL
        )
        split_pat = re.compile(
            r"^(?:(" + _ident + r")\s*\.\s*)?(" + _ident + r")$"
        )

        _SQL_EXPR_KEYWORDS = {
            'AND', 'OR', 'NOT', 'IS', 'NULL', 'TRUE', 'FALSE',
            'CASE', 'WHEN', 'THEN', 'ELSE', 'END',
            'BETWEEN', 'IN', 'LIKE', 'SIMILAR', 'DISTINCT',
            'ESCAPE', 'COLLATE', 'AS', 'FROM'
        }

        def _unquote_ident(ident: str) -> str:
            ident = ident.strip()
            if ident.startswith('"') and ident.endswith('"') and len(ident) >= 2:
                return ident[1:-1].replace('""', '"')
            return ident

        def _parse_ident(ident_full: str) -> tuple[str | None, str]:
            m = split_pat.match(ident_full)
            if not m:
                return None, ident_full
            tbl_raw, col_raw = m.group(1), m.group(2)
            tbl_name = _unquote_ident(tbl_raw).lower() if tbl_raw else None
            col_name = _unquote_ident(col_raw).lower()
            return tbl_name, col_name

        def is_column_ref(m: re.Match, s: str) -> bool:
            # Function call: followed by '(' (ignoring whitespace)
            rest = s[m.end():]
            if rest and rest.lstrip().startswith('('):
                return False
            # Type cast target: preceded by '::'
            prefix = s[:m.start()].rstrip()
            if prefix.endswith('::'):
                return False
            # CAST target type: preceded by AS (e.g. CAST(x AS type))
            if re.search(r'\bAS$', prefix, re.IGNORECASE):
                return False
            # Collation: preceded by COLLATE
            if re.search(r'\bCOLLATE$', prefix, re.IGNORECASE):
                return False
            # Date part in EXTRACT (e.g. EXTRACT(YEAR FROM col))
            if re.search(r'\bEXTRACT\s*\(\s*$', prefix, re.IGNORECASE):
                return False
            ident = m.group(2)
            # Unquoted SQL expression keywords are not column identifiers
            if ident and not ident.startswith('"') and '.' not in ident:
                if ident.upper() in _SQL_EXPR_KEYWORDS:
                    return False
            return True

        def find_referenced_columns(expr: str) -> set[str]:
            col_refs = set()
            for m in token_pat.finditer(expr):
                if m.group(1):
                    continue
                ident_full = m.group(2)
                if not ident_full or not is_column_ref(m, expr):
                    continue
                tbl_name, col_name = _parse_ident(ident_full)
                if tbl_name is None or tbl_name == table_name.lower():
                    col_refs.add(col_name)
            return col_refs

        def replace_col_ident(expr: str, col_target: str, repl_sql: str) -> str:
            def repl(m):
                lit = m.group(1)
                if lit:
                    return lit
                ident_full = m.group(2)
                if not ident_full or not is_column_ref(m, expr):
                    return m.group(0)
                tbl_name, col_name = _parse_ident(ident_full)
                if tbl_name is None or tbl_name == table_name.lower():
                    if col_name == col_target.lower():
                        return repl_sql
                return ident_full

            return token_pat.sub(repl, expr)

        graph = {}
        for name, col in computed_cols.items():
            refs = find_referenced_columns(col.computed_source)
            if name.lower() in refs:
                raise ValueError(f"Self-referencing computed column '{name}' in table '{table_name}' is not permitted.")
            deps = {
                other for other in computed_cols
                if other != name and other.lower() in refs
            }
            graph[name] = deps

        try:
            sorter = TopologicalSorter(graph)
            order = list(sorter.static_order())
        except CycleError as e:
            raise ValueError(f"Circular dependency detected between computed columns in table '{table_name}': {e}") from e

        for name in order:
            col = computed_cols[name]
            curr_expr = col.computed_source
            deps = [d for d in order if d in graph[name]]
            for dep in deps:
                dep_col = computed_cols[dep]
                pg_type = get_postgres_type(dep_col.column_type).lower() if dep_col.column_type else ""
                type_cast = f"::{pg_type}" if pg_type else ""
                replacement = f"(({dep_col.computed_source}){type_cast})"
                curr_expr = replace_col_ident(curr_expr, dep, replacement)
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
    def _extract_indexes(cursor, table_name: str, symbols: dict[str, str] = None,
                         sequence_increments: dict[str, int] = None) -> list[Index]:
        """
        Extracts user-defined secondary indexes for a given table (excluding PK/UQ indexes),
        supporting both standard column-segment indexes and expression-based indexes (COMPUTED BY).
        """
        try:
            cursor.execute("""
                SELECT 
                    i.RDB$INDEX_NAME AS index_name,
                    i.RDB$UNIQUE_FLAG AS is_unique,
                    i.RDB$INDEX_INACTIVE AS is_inactive,
                    seg.RDB$FIELD_NAME AS column_name,
                    seg.RDB$FIELD_POSITION AS column_position,
                    i.RDB$EXPRESSION_SOURCE AS expression_source,
                    i.RDB$CONDITION_SOURCE AS condition_source
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
            rows = cursor.fetchall()
        except firebirdsql.Error:
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
            rows = cursor.fetchall()

        indexes = []
        for row in rows:
            raw_expr = row[5]
            expr_str = raw_expr.strip() if raw_expr else None
            if expr_str:
                try:
                    expr_str = FirebirdToPostgresVisitor.transpile_expression(
                        expr_str, symbols=symbols, sequence_increments=sequence_increments
                    )
                except Exception as e:
                    raise RuntimeError(
                        f"Failed to transpile expression index '{row[0].strip()}' on table '{table_name}': "
                        f"expression '{raw_expr.strip()}' could not be converted to PostgreSQL. Cause: {e}"
                    ) from e
                validate_immutable_expression(expr_str, f"expression index '{row[0].strip()}' in table '{table_name}'")
            raw_cond = row[6] if len(row) > 6 else None
            cond_str = raw_cond.strip() if raw_cond else None
            if cond_str:
                try:
                    cond_str = FirebirdToPostgresVisitor.transpile_expression(
                        cond_str, symbols=symbols, sequence_increments=sequence_increments
                    )
                except Exception as e:
                    raise RuntimeError(
                        f"Failed to transpile partial index condition for index '{row[0].strip()}' in table '{table_name}': "
                        f"expression '{raw_cond.strip()}' could not be converted to PostgreSQL. Cause: {e}"
                    ) from e
            col_name = row[3].strip() if row[3] else None
            indexes.append(
                Index(
                    index_name=row[0].strip(),
                    unique=bool(row[1]),
                    inactive=bool(row[2]),
                    column_name=col_name,
                    column_index=row[4] if row[4] is not None else 0,
                    expression=expr_str,
                    condition=cond_str,
                )
            )
        return indexes

    @staticmethod
    def _extract_check_constraints(cursor, table_name: str, symbols: dict[str, str] = None,
                                   sequence_increments: dict[str, int] = None) -> list[CheckConstraint]:
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
                pg_expr = FirebirdToPostgresVisitor.transpile_expression(
                    inner_expr, symbols=symbols, sequence_increments=sequence_increments
                )
            except Exception as e:
                raise RuntimeError(
                    f"Failed to transpile CHECK constraint '{cname}' on table '{table_name}': "
                    f"expression '{inner_expr}' could not be converted to PostgreSQL. Cause: {e}"
                ) from e

            checks.append(CheckConstraint(name=cname, expression=pg_expr))
        return checks

    @staticmethod
    def _strip_outer_parens(s: str) -> str:
        s = s.strip()
        while s.startswith("(") and s.endswith(")"):
            depth = 0
            enclosing = True
            for ch in s[:-1]:
                if ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
                    if depth == 0:
                        enclosing = False
                        break
            if enclosing and depth == 1:
                s = s[1:-1].strip()
            else:
                break
        return s

    @classmethod
    def _is_equivalent_absent_condition(cls, cond: str, col_name: str) -> bool:
        if not cond:
            return False
        cond = cls._strip_outer_parens(cond)
        # Disallow AND conjunctions (any AND restricts the generation to a subset of cases)
        if re.search(r"\bAND\b", cond, re.IGNORECASE):
            return False
        # Disallow NOT (negations)
        if re.search(r"\bNOT\b", cond, re.IGNORECASE):
            return False
        # Disallow inequality operators
        if re.search(r"!=|<>|>", cond):
            return False
        # Disallow user/context variables or functions (e.g. CURRENT_USER = 'ADMIN')
        if re.search(r"\b(CURRENT_USER|CURRENT_ROLE|USER|CURRENT_DATE|CURRENT_TIME|CURRENT_TIMESTAMP)\b", cond, re.IGNORECASE):
            return False

        col_esc = re.escape(col_name)
        col_ref_pat = rf'(?:\"?NEW\"?\s*\.\s*\"?{col_esc}\"?)'
        null_branch_patterns = [
            rf'^{col_ref_pat}\s+IS\s+NULL$',
            rf'^COALESCE\s*\(\s*{col_ref_pat}\s*,\s*0\s*\)\s*(?:<=?|=)\s*0$',
            rf'^COALESCE\s*\(\s*{col_ref_pat}\s*,\s*0\s*\)\s*<\s*1$',
        ]
        zero_branch_patterns = [
            rf'^{col_ref_pat}\s*(?:<=?|=)\s*0$',
            rf'^{col_ref_pat}\s*<\s*1$',
        ]

        branches = re.split(r"\bOR\b", cond, flags=re.IGNORECASE)
        if not branches:
            return False

        has_null_cover = False
        for b in branches:
            b_clean = cls._strip_outer_parens(b)
            if any(re.match(p, b_clean, re.IGNORECASE) for p in null_branch_patterns):
                has_null_cover = True
            elif not any(re.match(p, b_clean, re.IGNORECASE) for p in zero_branch_patterns):
                return False

        return has_null_cover

    @classmethod
    def _bind_sequence_generators(cls, cursor, table_objs: list[Table]) -> None:
        """
        Inspects trigger bodies for GEN_ID / NEXT VALUE FOR usage and binds identified
        sequences to table columns only for genuine auto-increment / identity defaults
        on BEFORE INSERT triggers (RDB$TRIGGER_TYPE = 1).
        Ignores commented-out code, step != 1 (e.g. GEN_ID(..., 0)), non-BEFORE-INSERT triggers,
        conditional triggers dependent on user/context or other columns, unconditional triggers,
        triggers with preceding or procedural commands, and columns affected by multiple triggers.
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

        if_re = re.compile(
            r"^(?:(?:AS\s+)?BEGIN\s+)?IF\s*(?:\((.*)\)|(.*?))\s+THEN\s*(?:BEGIN\s+)?NEW\.(?:\"|\s)*([A-Za-z0-9_]+)(?:\"|\s)*=\s*(?:GEN_ID\s*\(\s*([A-Za-z0-9_]+)\s*,\s*1\s*\)|NEXT\s+VALUE\s+FOR\s+([A-Za-z0-9_]+))\s*(?:END)?$",
            re.IGNORECASE | re.DOTALL
        )

        # Group BEFORE INSERT triggers by table
        table_triggers: dict[str, list[tuple[str, str]]] = {}
        for trigger in triggers:
            relation_name = trigger[0].strip() if trigger[0] else None
            source = trigger[1]
            trigger_type = trigger[2] if len(trigger) > 2 else 1
            if not relation_name or not source or trigger_type != 1:
                continue
            if relation_name.upper() in tables_by_name:
                clean = re.sub(r"--[^\r\n]*", "", source)
                clean = re.sub(r"/\*.*?\*/", "", clean, flags=re.DOTALL).strip()
                table_triggers.setdefault(relation_name.upper(), []).append((source, clean))

        for rel_name_upper, trg_list in table_triggers.items():
            table = tables_by_name[rel_name_upper]

            for idx, (source, clean) in enumerate(trg_list):
                # Split clean source into meaningful statements
                raw_stmts = [s.strip() for s in clean.split(";") if s.strip()]
                stmts = []
                for s in raw_stmts:
                    # Ignore pure block boundary keywords
                    s_no_kw = re.sub(r"\b(BEGIN|END)\b", "", s, flags=re.IGNORECASE).strip()
                    if s_no_kw:
                        stmts.append(s)

                if not stmts:
                    continue

                # If the trigger contains any statement other than an auto-increment assignment,
                # it is not a pure auto-increment trigger (commands/logic present)
                candidates = []
                is_pure = True
                for stmt in stmts:
                    m_if = if_re.match(stmt)
                    if m_if:
                        cond = (m_if.group(1) or m_if.group(2)).strip()
                        c = m_if.group(3).strip()
                        s = (m_if.group(4) or m_if.group(5)).strip().lower()
                        if cls._is_equivalent_absent_condition(cond, c):
                            candidates.append((c, s))
                        else:
                            is_pure = False
                            break
                    else:
                        is_pure = False
                        break

                if not is_pure or not candidates:
                    continue

                # For each candidate column, verify no other BEFORE INSERT trigger on this table
                # references or modifies NEW.<col>
                other_triggers = [c_src for i, (_, c_src) in enumerate(trg_list) if i != idx]
                for col_name, seq_name in candidates:
                    col_pat = re.compile(rf'\bNEW\s*\.\s*"?{re.escape(col_name)}"?\b', re.IGNORECASE)
                    if any(col_pat.search(other_clean) for other_clean in other_triggers):
                        # Another trigger references this column; do not promote to default
                        continue

                    column = next((col for col in table.columns if col.name.upper() == col_name.upper()), None)
                    if column:
                        column.sequence_name = seq_name

    @staticmethod
    def _extract_sequences(cursor) -> list[Sequence]:
        """
        Queries all user-defined generators from RDB$GENERATORS and reads their current values and increments.
        """
        try:
            cursor.execute("""
                SELECT RDB$GENERATOR_NAME, COALESCE(RDB$GENERATOR_INCREMENT, 1)
                FROM RDB$GENERATORS
                WHERE (RDB$SYSTEM_FLAG = 0 OR RDB$SYSTEM_FLAG IS NULL)
                  AND RDB$GENERATOR_NAME NOT STARTING WITH 'RDB$'
                  AND RDB$GENERATOR_NAME NOT STARTING WITH 'MON$';
            """)
            seq_rows = cursor.fetchall()
        except firebirdsql.Error as e:
            if not is_column_not_found_error(e, "RDB$GENERATOR_INCREMENT"):
                raise RuntimeError(f"Failed to query sequences from Firebird: {e}") from e
            try:
                cursor.execute("""
                    SELECT RDB$GENERATOR_NAME, 1
                    FROM RDB$GENERATORS
                    WHERE (RDB$SYSTEM_FLAG = 0 OR RDB$SYSTEM_FLAG IS NULL)
                      AND RDB$GENERATOR_NAME NOT STARTING WITH 'RDB$'
                      AND RDB$GENERATOR_NAME NOT STARTING WITH 'MON$';
                """)
                seq_rows = cursor.fetchall()
            except Exception as fallback_err:
                raise RuntimeError(f"Failed to query sequences from Firebird: {fallback_err}") from fallback_err
        except Exception as e:
            raise RuntimeError(f"Failed to query sequences from Firebird: {e}") from e
        sequences = []
        for row in seq_rows:
            name = row[0].strip()
            val = row[1] if len(row) > 1 else 1
            if val is None:
                raise ValueError(
                    f"Invalid sequence increment None for generator '{name}': sequence increment cannot be null"
                )
            try:
                increment = int(val)
            except (ValueError, TypeError) as e:
                raise ValueError(
                    f"Invalid sequence increment {val!r} for generator '{name}': must be a valid integer"
                ) from e
            if increment == 0:
                raise ValueError(
                    f"Invalid sequence increment 0 for generator '{name}': sequence increment cannot be zero"
                )
            safe_name = name.replace('"', '""')
            try:
                cursor.execute(f'SELECT GEN_ID("{safe_name}", 0) FROM RDB$DATABASE;')
                r = cursor.fetchone()
                if not r or r[0] is None:
                    raise RuntimeError(f"Failed to read current value for generator '{name}': no value returned")
                curr_val = int(r[0])
            except Exception as e:
                raise RuntimeError(f"Failed to read current value for generator '{name}': {e}") from e
            sequences.append(Sequence(name=name, current_value=curr_val, increment=increment))
        return sequences
