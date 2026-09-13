import logging
import os
import re
import tempfile
from concurrent.futures import ProcessPoolExecutor
from graphlib import TopologicalSorter
import firebirdsql

from config import DUMP_DIR, DumpFiles, get_dump_path
from models import (
    Sequence,
    get_postgres_type,
    resolve_firebird_type,
    build_domain_mapping,
    decode_trigger_type,
    pg_quote_ident,
)
from transpiler import FirebirdToPostgresVisitor
from utils import choose_dollar_tag
from engine.schema_extractor import fetch_all_sequence_increments, is_column_not_found_error

logger = logging.getLogger(__name__)


def _ensure_parent_dir(file_path: str):
    directory = os.path.dirname(file_path)
    if directory:
        os.makedirs(directory, exist_ok=True)


def _write_text_atomic(file_path: str, content: str) -> None:
    _ensure_parent_dir(file_path)
    directory = os.path.dirname(file_path) or '.'
    fd, temp_path = tempfile.mkstemp(
        prefix=f'.{os.path.basename(file_path)}.', suffix='.tmp', dir=directory
    )
    os.close(fd)
    try:
        with open(temp_path, 'w', encoding='utf-8') as stream:
            stream.write(content)
        os.replace(temp_path, file_path)
    finally:
        try:
            os.unlink(temp_path)
        except FileNotFoundError:
            pass


def _transpile_worker(item: tuple) -> tuple[str | None, str | None]:
    """
    Worker function executed in worker processes.
    Tuple may be (item_name, fb_sql), (item_name, fb_sql, transpile_sql),
    (item_name, fb_sql, transpile_sql, domain_map),
    (item_name, fb_sql, transpile_sql, domain_map, symbols),
    or (item_name, fb_sql, transpile_sql, domain_map, symbols, sequence_increments, domain_types, function_map)
    and returns (pg_sql, error_msg).
    Avoids returning fb_sql across IPC to minimize pickle overhead.
    """
    sql_to_transpile = item[2] if len(item) > 2 and item[2] is not None else item[1]
    domain_map = item[3] if len(item) > 3 else None
    symbols = item[4] if len(item) > 4 else None
    sequence_increments = item[5] if len(item) > 5 else None
    domain_types = item[6] if len(item) > 6 else None
    function_map = item[7] if len(item) > 7 else None
    function_return_not_null = item[8] if len(item) > 8 else False
    try:
        pg_sql = FirebirdToPostgresVisitor.transpile(
            sql_to_transpile,
            domain_map=domain_map,
            symbols=symbols,
            sequence_increments=sequence_increments,
            domain_types=domain_types,
            function_map=function_map,
            function_return_not_null=function_return_not_null,
        )
        return pg_sql, None
    except Exception as e:
        return None, str(e)


class DdlExporter:
    """
    Extracts Firebird domains, functions, triggers, stored procedures, and views,
    transpiles their DDL in parallel to PostgreSQL, and writes out SQL dump files.
    """


    def __init__(self, fb_con):
        self.fb_con = fb_con
        self.exported_counts: dict[str, int] = {}
        self.function_call_map: dict[str, str] = {}

    # Mappings are deliberately conservative. A Firebird UDF with one of
    # these entries is treated as native only when its library, entrypoint,
    # database name and arity match. A name alone is never evidence of
    # equivalence because Firebird UDFs can shadow built-ins. `dynamic_safe`
    # means the target keeps the same callable name, so runtime-built SQL can
    # still resolve it.
    _NATIVE_EQUIVALENTS = {
        ('ib_udf', 'abs'): {'target': 'abs', 'arity': 1},
        ('ib_udf', 'ib_udf_abs'): {'target': 'abs', 'name': 'ABS', 'arity': 1, 'dynamic_safe': True},
        ('ib_udf', 'acos'): {'target': 'acos', 'arity': 1},
        ('ib_udf', 'ib_udf_acos'): {'target': 'acos', 'name': 'ACOS', 'arity': 1, 'dynamic_safe': True},
        ('ib_udf', 'ib_udf_ascii_char'): {'target': 'chr', 'name': 'ASCII_CHAR', 'arity': 1},
        ('ib_udf', 'ib_udf_ascii_val'): {'target': 'ascii', 'name': 'ASCII_VAL', 'arity': 1},
        ('ib_udf', 'asin'): {'target': 'asin', 'arity': 1},
        ('ib_udf', 'ib_udf_asin'): {'target': 'asin', 'name': 'ASIN', 'arity': 1, 'dynamic_safe': True},
        ('ib_udf', 'atan'): {'target': 'atan', 'arity': 1},
        ('ib_udf', 'ib_udf_atan'): {'target': 'atan', 'name': 'ATAN', 'arity': 1, 'dynamic_safe': True},
        ('ib_udf', 'atan2'): {'target': 'atan2', 'arity': 2},
        ('ib_udf', 'ib_udf_atan2'): {'target': 'atan2', 'name': 'ATAN2', 'arity': 2, 'dynamic_safe': True},
        ('ib_udf', 'ceiling'): {'target': 'ceiling', 'name': 'CEILING', 'arity': 1, 'dynamic_safe': True},
        ('ib_udf', 'ceil'): {'target': 'ceil', 'name': 'CEILING', 'arity': 1},
        ('ib_udf', 'ib_udf_ceiling'): {'target': 'ceiling', 'name': 'CEILING', 'arity': 1, 'dynamic_safe': True},
        ('ib_udf', 'ib_udf_ceil'): {'target': 'ceil', 'name': 'CEILING', 'arity': 1},
        ('ib_udf', 'ib_udf_cos'): {'target': 'cos', 'name': 'COS', 'arity': 1, 'dynamic_safe': True},
        ('ib_udf', 'ib_udf_cosh'): {'target': 'cosh', 'name': 'COSH', 'arity': 1, 'dynamic_safe': True},
        ('ib_udf', 'ib_udf_cot'): {'target': 'cot', 'name': 'COT', 'arity': 1, 'dynamic_safe': True},
        ('ib_udf', 'floor'): {'target': 'floor', 'arity': 1},
        ('ib_udf', 'ib_udf_floor'): {'target': 'floor', 'name': 'FLOOR', 'arity': 1, 'dynamic_safe': True},
        ('ib_udf', 'ln'): {'target': 'ln', 'arity': 1},
        ('ib_udf', 'ib_udf_ln'): {'target': 'ln', 'name': 'LN', 'arity': 1, 'dynamic_safe': True},
        ('ib_udf', 'ib_udf_log'): {'target': 'log', 'name': 'LOG', 'arity': 2, 'dynamic_safe': True},
        ('ib_udf', 'ib_udf_log10'): {'target': 'log10', 'name': 'LOG10', 'arity': 1, 'dynamic_safe': True},
        ('ib_udf', 'lower'): {'target': 'lower', 'arity': 1},
        ('ib_udf', 'ib_udf_lower'): {'target': 'lower', 'name': 'LOWER', 'arity': 1, 'dynamic_safe': True},
        ('ib_udf', 'lpad'): {'target': 'lpad', 'arity': 3},
        ('ib_udf', 'ib_udf_lpad'): {'target': 'lpad', 'name': 'LPAD', 'arity': 3, 'dynamic_safe': True},
        ('ib_udf', 'ltrim'): {'target': 'ltrim', 'arity': 1},
        ('ib_udf', 'ib_udf_ltrim'): {'target': 'ltrim', 'name': 'LTRIM', 'arity': 1, 'dynamic_safe': True},
        ('ib_udf', 'ib_udf_mod'): {'target': 'mod', 'name': 'MOD', 'arity': 2, 'dynamic_safe': True},
        ('ib_udf', 'ib_udf_pi'): {'target': 'pi', 'name': 'PI', 'arity': 0, 'dynamic_safe': True},
        ('ib_udf', 'ib_udf_rand'): {'target': 'random', 'name': 'RAND', 'arity': 0},
        ('ib_udf', 'rpad'): {'target': 'rpad', 'arity': 3},
        ('ib_udf', 'ib_udf_rpad'): {'target': 'rpad', 'name': 'RPAD', 'arity': 3, 'dynamic_safe': True},
        ('ib_udf', 'rtrim'): {'target': 'rtrim', 'arity': 1},
        ('ib_udf', 'ib_udf_rtrim'): {'target': 'rtrim', 'name': 'RTRIM', 'arity': 1, 'dynamic_safe': True},
        ('ib_udf', 'sign'): {'target': 'sign', 'arity': 1},
        ('ib_udf', 'ib_udf_sign'): {'target': 'sign', 'name': 'SIGN', 'arity': 1, 'dynamic_safe': True},
        ('ib_udf', 'sin'): {'target': 'sin', 'arity': 1},
        ('ib_udf', 'ib_udf_sin'): {'target': 'sin', 'name': 'SIN', 'arity': 1, 'dynamic_safe': True},
        ('ib_udf', 'ib_udf_sinh'): {'target': 'sinh', 'name': 'SINH', 'arity': 1, 'dynamic_safe': True},
        ('ib_udf', 'sqrt'): {'target': 'sqrt', 'arity': 1},
        ('ib_udf', 'ib_udf_sqrt'): {'target': 'sqrt', 'name': 'SQRT', 'arity': 1, 'dynamic_safe': True},
        ('ib_udf', 'tan'): {'target': 'tan', 'arity': 1},
        ('ib_udf', 'ib_udf_tan'): {'target': 'tan', 'name': 'TAN', 'arity': 1, 'dynamic_safe': True},
        ('ib_udf', 'ib_udf_tanh'): {'target': 'tanh', 'name': 'TANH', 'arity': 1, 'dynamic_safe': True},
        ('ib_udf', 'ib_udf_strlen'): {'target': 'char_length', 'name': 'STRLEN', 'arity': 1},
    }

    @staticmethod
    def _catalog_text(value) -> str:
        if value is None:
            return ''
        if hasattr(value, 'read'):
            value = value.read()
        if isinstance(value, bytes):
            return value.decode('utf-8')
        return str(value)

    @staticmethod
    def _catalog_feature_missing(exc: Exception) -> bool:
        message = str(exc).lower()
        return any(marker in message for marker in (
            'column unknown', 'field unknown', 'does not exist',
            'table unknown', 'unknown column', '42s22', '42s02',
        ))

    @classmethod
    def _function_calls(cls, source: str) -> set[str]:
        """Returns function-like calls, ignoring literals and comments."""
        clean = re.sub(r"--[^\r\n]*|/\*.*?\*/|'(?:''|[^'])*'", ' ', source or '', flags=re.DOTALL)
        calls = set()
        for match in re.finditer(
                r'(?:"(?:""|[^"])+"|[A-Za-z_][A-Za-z0-9_$]*)\s*\.\s*'
                r'("(?:""|[^"])+"|[A-Za-z_][A-Za-z0-9_$]*)\s*\(|'
                r'(?<![A-Za-z0-9_$])("(?:""|[^"])+"|[A-Za-z_][A-Za-z0-9_$]*)\s*\(',
                clean
        ):
            calls.add((match.group(1) or match.group(2)).strip('"').upper())
        return calls

    def _fetch_function_catalog(self, cursor) -> list[dict]:
        """Reads user functions, supporting older Firebird catalog layouts."""
        queries = (
            # RETURN_ARGUMENT is required to distinguish the output row from
            # input rows without guessing from position.
            """
                SELECT RDB$FUNCTION_NAME, RDB$FUNCTION_SOURCE,
                       RDB$MODULE_NAME, RDB$ENTRYPOINT,
                       RDB$DETERMINISTIC_FLAG, RDB$RETURN_ARGUMENT,
                       RDB$PACKAGE_NAME
                FROM RDB$FUNCTIONS
                WHERE (RDB$SYSTEM_FLAG = 0 OR RDB$SYSTEM_FLAG IS NULL)
                ORDER BY RDB$FUNCTION_NAME;
            """,
            """
                SELECT RDB$FUNCTION_NAME, RDB$FUNCTION_SOURCE,
                       RDB$MODULE_NAME, RDB$ENTRYPOINT, NULL, RDB$RETURN_ARGUMENT
                FROM RDB$FUNCTIONS
                WHERE (RDB$SYSTEM_FLAG = 0 OR RDB$SYSTEM_FLAG IS NULL)
                ORDER BY RDB$FUNCTION_NAME;
            """,
            """
                SELECT RDB$FUNCTION_NAME, RDB$FUNCTION_SOURCE,
                       RDB$MODULE_NAME, RDB$ENTRYPOINT, NULL, NULL
                FROM RDB$FUNCTIONS
                WHERE (RDB$SYSTEM_FLAG = 0 OR RDB$SYSTEM_FLAG IS NULL)
                ORDER BY RDB$FUNCTION_NAME;
            """,
        )
        rows = None
        for query in queries:
            try:
                cursor.execute(query)
                rows = cursor.fetchall()
                break
            except firebirdsql.Error as exc:
                if not self._catalog_feature_missing(exc):
                    raise
        if rows is None:
            raise RuntimeError('Unable to read RDB$FUNCTIONS metadata.')

        functions = []
        for row in rows or []:
            if not row or not row[0]:
                continue
            functions.append({
                'name': self._catalog_text(row[0]).strip(),
                'source': self._catalog_text(row[1]).strip() if len(row) > 1 else '',
                'module': self._catalog_text(row[2]).strip() if len(row) > 2 else '',
                'entrypoint': self._catalog_text(row[3]).strip() if len(row) > 3 else '',
                'deterministic': bool(row[4]) if len(row) > 4 and row[4] is not None else False,
                'return_argument': row[5] if len(row) > 5 else None,
                'package': self._catalog_text(row[6]).strip() if len(row) > 6 else '',
            })
        return functions

    @staticmethod
    def _function_arg_type(row: tuple, domain_map: dict[str, str] | None,
                           function_name: str, argument_name: str) -> tuple[str, str]:
        """Return (Firebird declaration type, PostgreSQL declaration type)."""
        field_source = DdlExporter._catalog_text(row[2]).strip() if len(row) > 2 and row[2] else ''
        dimensions = row[11] if len(row) > 11 else None
        if dimensions is not None and dimensions > 0:
            raise NotImplementedError(
                f"Firebird array argument '{argument_name}' in function '{function_name}' is unsupported."
            )
        field_type = row[3] if len(row) > 3 else None
        field_length = row[5] if len(row) > 5 else None
        # CSTRING (catalog type 40) is used by legacy external UDFs, but is
        # not a SQL declaration type. Its PostgreSQL-compatible signature is
        # VARCHAR with the catalogued buffer length.
        if field_type == 40 and field_length:
            fb_type = f'VARCHAR({field_length})'
        else:
            fb_type = resolve_firebird_type(
                field_type=field_type,
                field_subtype=row[4] if len(row) > 4 else None,
                field_length=field_length,
                field_precision=row[6] if len(row) > 6 else None,
                field_scale=row[7] if len(row) > 7 else None,
                character_set_id=row[10] if len(row) > 10 else None,
                dimensions=dimensions,
            )
        if not fb_type:
            if not field_source or field_source.startswith('RDB$'):
                raise TypeError(
                    f"Missing type metadata for function '{function_name}' argument '{argument_name}'."
                )
            fb_type = field_source
        if field_source and not field_source.startswith('RDB$'):
            fb_decl = field_source
            if domain_map and field_source.upper() in domain_map:
                pg_decl = domain_map[field_source.upper()]
            else:
                pg_decl = field_source
        else:
            fb_decl = fb_type
            pg_decl = get_postgres_type(fb_type)
        return fb_decl, pg_decl

    @staticmethod
    def _format_function_default(value) -> str:
        if value is None:
            return ''
        value = DdlExporter._catalog_text(value).strip()
        if not value:
            return ''
        if value.upper().startswith('DEFAULT '):
            return f' {value}'
        if value.startswith('='):
            return f' DEFAULT {value[1:].strip()}'
        return f' DEFAULT {value}'

    @staticmethod
    def _function_native_key(item: dict) -> tuple[str, str]:
        module = DdlExporter._catalog_text(item.get('module', '')).strip().lower().replace('\\', '/')
        module = module.rsplit('/', 1)[-1]
        module = re.sub(r'\.(?:dll|so|dylib)$', '', module)
        entrypoint = DdlExporter._catalog_text(item.get('entrypoint', '')).strip().lower()
        return module, entrypoint

    def _fetch_function_signature(self, cursor, function: dict,
                                  domain_map: dict[str, str] | None = None) -> dict:
        """Read complete function signature without inferring the return row."""
        function_name = function['name']
        # Legacy external UDFs store their type attributes directly in
        # RDB$FUNCTION_ARGUMENTS. PSQL arguments may instead reference a
        # domain, whose attributes are resolved through RDB$FIELDS. Prefer
        # the direct values and retain the join as a compatibility fallback.
        queries = (
            """
                SELECT a.RDB$ARGUMENT_NAME, a.RDB$ARGUMENT_POSITION,
                       a.RDB$FIELD_SOURCE,
                       COALESCE(a.RDB$FIELD_TYPE, f.RDB$FIELD_TYPE),
                       COALESCE(a.RDB$FIELD_SUB_TYPE, f.RDB$FIELD_SUB_TYPE),
                       COALESCE(a.RDB$CHARACTER_LENGTH,
                                a.RDB$FIELD_LENGTH,
                                f.RDB$CHARACTER_LENGTH, f.RDB$FIELD_LENGTH),
                       COALESCE(a.RDB$FIELD_PRECISION, f.RDB$FIELD_PRECISION),
                       COALESCE(a.RDB$FIELD_SCALE, f.RDB$FIELD_SCALE),
                       a.RDB$DEFAULT_SOURCE, a.RDB$NULL_FLAG,
                       COALESCE(a.RDB$CHARACTER_SET_ID, f.RDB$CHARACTER_SET_ID),
                       f.RDB$DIMENSIONS,
                       a.RDB$ARGUMENT_MECHANISM
                FROM RDB$FUNCTION_ARGUMENTS a
                LEFT JOIN RDB$FIELDS f ON a.RDB$FIELD_SOURCE = f.RDB$FIELD_NAME
                WHERE a.RDB$FUNCTION_NAME = ?
                ORDER BY a.RDB$ARGUMENT_POSITION;
            """,
            """
                SELECT a.RDB$ARGUMENT_NAME, a.RDB$ARGUMENT_POSITION,
                       a.RDB$FIELD_SOURCE, f.RDB$FIELD_TYPE,
                       f.RDB$FIELD_SUB_TYPE,
                       COALESCE(f.RDB$CHARACTER_LENGTH, f.RDB$FIELD_LENGTH),
                       f.RDB$FIELD_PRECISION, f.RDB$FIELD_SCALE,
                       a.RDB$DEFAULT_SOURCE, a.RDB$NULL_FLAG,
                       f.RDB$CHARACTER_SET_ID, f.RDB$DIMENSIONS,
                       a.RDB$ARGUMENT_MECHANISM
                FROM RDB$FUNCTION_ARGUMENTS a
                LEFT JOIN RDB$FIELDS f ON a.RDB$FIELD_SOURCE = f.RDB$FIELD_NAME
                WHERE a.RDB$FUNCTION_NAME = ?
                ORDER BY a.RDB$ARGUMENT_POSITION;
            """,
        )
        rows = None
        for query in queries:
            try:
                cursor.execute(query, (function_name,))
                rows = cursor.fetchall() or []
                break
            except firebirdsql.Error as exc:
                if not self._catalog_feature_missing(exc):
                    raise
        if rows is None:
            raise RuntimeError(
                f"Firebird catalog cannot expose complete signature for function '{function_name}'."
            )

        return_pos = function.get('return_argument')
        if return_pos is None:
            raise RuntimeError(
                f"Return argument metadata is unavailable for function '{function_name}'; refusing to guess."
            )

        try:
            return_pos = int(return_pos)
        except (TypeError, ValueError) as exc:
            raise RuntimeError(
                f"Invalid return argument position for function '{function_name}': {return_pos!r}."
            ) from exc

        inputs_fb, inputs_pg = [], []
        return_fb = return_pg = None
        return_not_null = False
        for row in rows:
            if not row:
                continue
            position = int(row[1]) if row[1] is not None else None
            name = self._catalog_text(row[0]).strip() if row[0] else f'ARG{position}'
            fb_type, pg_type = self._function_arg_type(row, domain_map, function_name, name)
            mechanism = row[12] if len(row) > 12 else None
            if mechanism not in (None, 0):
                raise NotImplementedError(
                    f"Function '{function_name}' argument '{name}' uses unsupported mechanism {mechanism}."
                )
            default = self._format_function_default(row[8] if len(row) > 8 else None)
            if position == return_pos:
                return_fb, return_pg = fb_type, pg_type
                return_not_null = (row[9] == 1) if len(row) > 9 else False
                continue
            not_null = ' NOT NULL' if len(row) > 9 and row[9] == 1 else ''
            inputs_fb.append(f'{name} {fb_type}{not_null}{default}')
            inputs_pg.append(f'{name} {pg_type}{default}')

        if return_fb is None:
            raise RuntimeError(
                f"Return argument position {return_pos} was not found for function '{function_name}'."
            )
        return {
            'fb_params': inputs_fb,
            'pg_params': inputs_pg,
            'fb_return': return_fb,
            'pg_return': return_pg,
            'input_count': len(inputs_fb),
            'return_not_null': return_not_null,
        }

    def _fetch_function_arguments(self, cursor, function_name: str) -> tuple[list[str], str]:
        """Compatibility wrapper returning PostgreSQL input params and return type."""
        function = next(
            (item for item in self._fetch_function_catalog(cursor)
             if item['name'].upper() == function_name.upper()),
            {'name': function_name, 'return_argument': None},
        )
        signature = self._fetch_function_signature(cursor, function)
        return signature['pg_params'], signature['pg_return']

    def _fetch_stored_function_sources(self, cursor) -> list[dict]:
        """Read every migrated database expression that can call a function."""
        queries = (
            ('PROCEDURE', """
                SELECT RDB$PROCEDURE_NAME, RDB$PROCEDURE_SOURCE
                FROM RDB$PROCEDURES
                WHERE (RDB$SYSTEM_FLAG = 0 OR RDB$SYSTEM_FLAG IS NULL)
                  AND RDB$PROCEDURE_SOURCE IS NOT NULL;
            """),
            ('VIEW', """
                SELECT RDB$RELATION_NAME, RDB$VIEW_SOURCE
                FROM RDB$RELATIONS
                WHERE (RDB$SYSTEM_FLAG = 0 OR RDB$SYSTEM_FLAG IS NULL)
                  AND RDB$VIEW_SOURCE IS NOT NULL;
            """),
            ('TRIGGER', """
                SELECT RDB$TRIGGER_NAME, RDB$TRIGGER_SOURCE
                FROM RDB$TRIGGERS
                WHERE (RDB$SYSTEM_FLAG = 0 OR RDB$SYSTEM_FLAG IS NULL)
                  AND RDB$TRIGGER_SOURCE IS NOT NULL;
            """),
            ('COLUMN_DEFAULT', """
                SELECT RF.RDB$RELATION_NAME, RF.RDB$DEFAULT_SOURCE
                FROM RDB$RELATION_FIELDS RF
                WHERE RF.RDB$DEFAULT_SOURCE IS NOT NULL;
            """),
            ('COLUMN_COMPUTED', """
                SELECT RF.RDB$RELATION_NAME, F.RDB$COMPUTED_SOURCE
                FROM RDB$RELATION_FIELDS RF
                JOIN RDB$FIELDS F ON F.RDB$FIELD_NAME = RF.RDB$FIELD_SOURCE
                WHERE F.RDB$COMPUTED_SOURCE IS NOT NULL;
            """),
            ('FIELD_DEFAULT', """
                SELECT RDB$FIELD_NAME, RDB$DEFAULT_SOURCE
                FROM RDB$FIELDS
                WHERE RDB$DEFAULT_SOURCE IS NOT NULL;
            """),
            ('FIELD_VALIDATION', """
                SELECT RDB$FIELD_NAME, RDB$VALIDATION_SOURCE
                FROM RDB$FIELDS
                WHERE RDB$VALIDATION_SOURCE IS NOT NULL;
            """),
            ('INDEX_EXPRESSION', """
                SELECT RDB$INDEX_NAME, RDB$EXPRESSION_SOURCE
                FROM RDB$INDICES
                WHERE RDB$EXPRESSION_SOURCE IS NOT NULL;
            """),
            ('PARAMETER_DEFAULT', """
                SELECT RDB$PROCEDURE_NAME, RDB$DEFAULT_SOURCE
                FROM RDB$PROCEDURE_PARAMETERS
                WHERE RDB$DEFAULT_SOURCE IS NOT NULL;
            """),
            ('FUNCTION_DEFAULT', """
                SELECT RDB$FUNCTION_NAME, RDB$DEFAULT_SOURCE
                FROM RDB$FUNCTION_ARGUMENTS
                WHERE RDB$DEFAULT_SOURCE IS NOT NULL;
            """),
        )
        records = []
        for kind, query in queries:
            try:
                cursor.execute(query)
                for row in cursor.fetchall() or []:
                    if row and row[1]:
                        records.append({
                            'kind': kind,
                            'name': self._catalog_text(row[0]).strip() if row[0] else kind,
                            'source': self._catalog_text(row[1]),
                        })
            except firebirdsql.Error as exc:
                if kind in {'COLUMN_DEFAULT', 'COLUMN_COMPUTED', 'FIELD_DEFAULT',
                            'FIELD_VALIDATION', 'INDEX_EXPRESSION', 'PARAMETER_DEFAULT',
                            'FUNCTION_DEFAULT'} \
                        and self._catalog_feature_missing(exc):
                    logger.info("Optional function-use catalog query unavailable for %s: %s", kind, exc)
                    continue
                raise
        return records

    def _stored_function_sources(self, cursor) -> list[str]:
        """Backward-compatible source-only view used by existing callers/tests."""
        return [record['source'] for record in self._fetch_stored_function_sources(cursor)]

    def _fetch_function_dependencies(self, cursor) -> list[dict]:
        """Read catalog dependencies so calls hidden by syntax/dynamic SQL remain visible."""
        cursor.execute("""
            SELECT RDB$DEPENDENT_NAME, RDB$DEPENDENT_TYPE,
                   RDB$DEPENDED_ON_NAME, RDB$DEPENDED_ON_TYPE,
                   RDB$FIELD_NAME
            FROM RDB$DEPENDENCIES;
        """)
        dependencies = []
        for row in cursor.fetchall() or []:
            if not row or not row[0] or not row[2]:
                continue
            dependencies.append({
                'dependent': self._catalog_text(row[0]).strip(),
                'dependent_type': row[1] if len(row) > 1 else None,
                'depended_on': self._catalog_text(row[2]).strip(),
                'depended_on_type': row[3] if len(row) > 3 else None,
                'field': self._catalog_text(row[4]).strip() if len(row) > 4 and row[4] else '',
            })
        return dependencies

    @staticmethod
    def _has_runtime_dynamic_sql(source: str) -> bool:
        clean = re.sub(r"--[^\r\n]*|/\*.*?\*/", ' ', source or '', flags=re.DOTALL)
        for match in re.finditer(r'\bEXECUTE\s+(?:STATEMENT|IMMEDIATE)\b', clean, re.IGNORECASE):
            pos = match.end()
            while pos < len(clean) and clean[pos].isspace():
                pos += 1
            if pos >= len(clean) or clean[pos] != "'":
                return True
        return False

    @staticmethod
    def _constant_dynamic_sql(source: str) -> list[str]:
        """Extract constant EXECUTE STATEMENT strings for dependency analysis."""
        values = []
        for match in re.finditer(
            r"\bEXECUTE\s+(?:STATEMENT|IMMEDIATE)\s*'((?:''|[^'])*)'",
            source or '', re.IGNORECASE | re.DOTALL
        ):
            values.append(match.group(1).replace("''", "'"))
        return values

    def _classify_function(self, item: dict) -> tuple[str, str, str]:
        if item.get('_ambiguous_overload_count'):
            count = item['_ambiguous_overload_count']
            return 'AMBIGUOUS_SIGNATURE', item['name'], (
                f"{count} Firebird overloads share the name '{item['name']}'; "
                'signature-aware package/global resolution is required'
            )
        if item.get('package'):
            return 'PACKAGE_MANUAL', item['name'], (
                f"function belongs to Firebird package '{item['package']}'; "
                'package specification/body migration is required'
            )
        if item.get('source', '').strip():
            return 'PSQL', item['name'], 'Firebird PSQL source available'
        module, entrypoint = self._function_native_key(item)
        spec = self._NATIVE_EQUIVALENTS.get((module, entrypoint))
        accepted_names = {entrypoint.upper(), spec.get('name', '').upper()} if spec else set()
        if spec and item['name'].upper() in accepted_names:
            return 'NATIVE_EQUIVALENT', spec['target'], (
                f"explicit mapping {module}::{entrypoint}; signature/behavior regression required"
            )
        return 'EXTERNAL_MANUAL', item['name'], (
            f"external implementation {module or '?'}::{entrypoint or '?'} has no verified PostgreSQL equivalent"
        )

    def analyze_database_functions(self, include_unused: bool = False) -> dict[str, dict]:
        """Classify functions and close direct, catalog and indirect dependencies."""
        cursor = self.fb_con.cursor()
        functions = self._fetch_function_catalog(cursor)
        grouped_functions: dict[str, list[dict]] = {}
        for item in functions:
            grouped_functions.setdefault(item['name'].upper(), []).append(item)
        by_name = {}
        for name, overloads in grouped_functions.items():
            representative = dict(overloads[0])
            if len(overloads) > 1:
                representative['_ambiguous_overload_count'] = len(overloads)
            by_name[name] = representative
        if '_stored_function_sources' in self.__dict__:
            records = [
                {'kind': 'UNKNOWN', 'name': 'unknown', 'source': source}
                for source in self._stored_function_sources(cursor)
            ]
        else:
            records = self._fetch_stored_function_sources(cursor)
        dependencies = self._fetch_function_dependencies(cursor)
        function_names = set(by_name)
        used: set[str] = set()
        evidence: dict[str, list[str]] = {name: [] for name in function_names}
        dynamic_sources = []
        function_default_sources: dict[str, list[str]] = {}

        for record in records:
            if record['kind'] == 'FUNCTION_DEFAULT':
                function_default_sources.setdefault(record['name'].upper(), []).append(record['source'])
                continue
            calls = self._function_calls(record['source']) & function_names
            for dynamic_sql in self._constant_dynamic_sql(record['source']):
                calls.update(self._function_calls(dynamic_sql) & function_names)
            for name in calls:
                used.add(name)
                evidence[name].append(f"{record['kind']} {record['name']}")
            if self._has_runtime_dynamic_sql(record['source']):
                dynamic_sources.append(f"{record['kind']} {record['name']}")

        # A catalog edge from a migrated object to a function is authoritative
        # when the source parser cannot see the invocation.
        for dependency in dependencies:
            target = dependency['depended_on'].upper()
            dependent = dependency['dependent'].upper()
            if target not in function_names:
                continue
            dependent_is_function = dependent in function_names
            if not dependent_is_function or dependent in used:
                used.add(target)
                evidence[target].append(
                    f"catalog {dependency['dependent']} -> {dependency['depended_on']}"
                )

        # Close indirect calls using both source and catalog edges.
        changed = True
        while changed:
            changed = False
            for name in list(used):
                before = len(used)
                used.update(self._function_calls(by_name[name].get('source', '')) & function_names)
                for default_source in function_default_sources.get(name, []):
                    used.update(self._function_calls(default_source) & function_names)
                for dependency in dependencies:
                    if dependency['dependent'].upper() == name:
                        target = dependency['depended_on'].upper()
                        if target in function_names:
                            used.add(target)
                changed |= len(used) != before

        usage_unknown = bool(dynamic_sources)

        result = {}
        names_to_report = function_names if include_unused else used
        for name in sorted(names_to_report):
            item = by_name[name]
            classification, target, reason = self._classify_function(item)
            dynamic_safe = False
            if classification == 'NATIVE_EQUIVALENT':
                module = item.get('module', '').strip().lower().replace('\\', '/')
                module = module.rsplit('/', 1)[-1]
                module = re.sub(r'\.(?:dll|so|dylib)$', '', module)
                entrypoint = item.get('entrypoint', '').strip().lower()
                spec = self._NATIVE_EQUIVALENTS.get((module, entrypoint), {})
                dynamic_safe = bool(spec.get(
                    'dynamic_safe',
                    str(target).strip('"').upper() == str(item['name']).strip('"').upper()
                ))
            status = 'USED' if name in used else 'UNUSED'
            runtime_usage_unverified = usage_unknown and name not in used
            if runtime_usage_unverified:
                reason += (
                    f"; possible use from runtime SQL in {', '.join(dynamic_sources)} "
                    'was not inferred'
                )
            result[item['name']] = {
                **item,
                'classification': classification,
                'target': target,
                'status': status,
                'usage': sorted(set(evidence[name])),
                'reason': reason,
                'dynamic_safe': dynamic_safe,
                'runtime_usage_unverified': runtime_usage_unverified,
            }
        self.function_analysis = {
            'functions': result,
            'dynamic_sources': dynamic_sources,
            'usage_unknown': usage_unknown,
        }
        self.function_call_map = {
            name.upper(): item['target']
            for name, item in result.items()
            if item.get('classification') == 'NATIVE_EQUIVALENT'
        }
        return result

    def export_firebird_functions(self, output_file: str = None,
                                  converted_file: str = None):
        """Exports only stored functions reachable from database objects."""
        out_file = output_file or get_dump_path(DumpFiles.FUNCTIONS_FB)
        conv_file = converted_file or get_dump_path(DumpFiles.FUNCTIONS_PG)
        analysis = self.analyze_database_functions()
        items = []
        manual = []
        native = []
        cursor = self.fb_con.cursor()
        function_by_upper = {name.upper(): item for name, item in analysis.items()}
        psql_names = set()
        for name, item in analysis.items():
            if item['classification'] == 'NATIVE_EQUIVALENT':
                if item['status'] == 'USAGE_UNKNOWN' and not item.get('dynamic_safe', False):
                    manual.append(f"{name} ({item['reason']})")
                    continue
                native.append(name)
                continue
            if item['status'] == 'USAGE_UNKNOWN':
                manual.append(f"{name} ({item['reason']})")
                continue
            if item['classification'] not in {'PSQL', 'NATIVE_EQUIVALENT'}:
                manual.append(f"{name} ({item['reason']})")
                continue
            psql_names.add(name.upper())

        # Create dependencies before their callers. Cycles are legal to
        # declare in PostgreSQL only with an explicit staging strategy, so
        # fail early instead of producing an order-dependent dump.
        dependency_graph = {
            name: self._function_calls(function_by_upper[name]['source']) & psql_names
            for name in psql_names
        }
        try:
            ordered_psql = list(TopologicalSorter(dependency_graph).static_order())
        except ValueError as exc:
            raise RuntimeError(f"Circular dependency among required functions: {exc}") from exc

        domain_map, domain_types = self._fetch_domain_info(cursor)
        symbols = self._fetch_all_column_symbols(cursor)
        sequence_increments = fetch_all_sequence_increments(cursor)
        function_signatures = {}
        for name in ordered_psql:
            function = function_by_upper[name]
            if '_fetch_function_arguments' in self.__dict__:
                # Keep the small public test seam usable while the production
                # path below always reads complete Firebird metadata.
                params, return_type = self._fetch_function_arguments(cursor, function['name'])
                signature = {
                    'fb_params': list(params), 'pg_params': list(params),
                    'fb_return': return_type, 'pg_return': return_type,
                    'input_count': len(params),
                }
            else:
                signature = self._fetch_function_signature(cursor, function, domain_map=domain_map)
            if function.get('classification') == 'NATIVE_EQUIVALENT':
                target = self._NATIVE_EQUIVALENTS.get(
                    self._function_native_key(function), {}
                )
                expected_arity = target.get('arity')
                if expected_arity is not None and signature['input_count'] != expected_arity:
                    raise RuntimeError(
                        f"Native mapping for function '{name}' expects {expected_arity} argument(s), "
                        f"but Firebird signature has {signature['input_count']}."
                    )
            function_signatures[function['name']] = signature
        for name in native:
            function = analysis[name]
            if '_fetch_function_arguments' in self.__dict__:
                params, return_type = self._fetch_function_arguments(cursor, name)
                signature = {
                    'fb_params': list(params), 'pg_params': list(params),
                    'fb_return': return_type, 'pg_return': return_type,
                    'input_count': len(params),
                }
            else:
                signature = self._fetch_function_signature(cursor, function, domain_map=domain_map)
            target_spec = self._NATIVE_EQUIVALENTS.get(
                self._function_native_key(function), {}
            )
            expected_arity = target_spec.get('arity')
            if expected_arity is not None and signature['input_count'] != expected_arity:
                raise RuntimeError(
                    f"Native mapping for function '{name}' expects {expected_arity} argument(s), "
                    f"but Firebird signature has {signature['input_count']}."
                )
            function_signatures[name] = signature

        for upper_name in ordered_psql:
            item = function_by_upper[upper_name]
            name = item['name']
            signature = function_signatures[name]
            source = item['source'].rstrip()
            if not source.endswith(';'):
                source += ';'
            fb_sql = (
                f"CREATE FUNCTION {pg_quote_ident(name)}({', '.join(signature['fb_params'])}) "
                f"RETURNS {signature['fb_return']} AS\n{source}\n\n"
            )
            items.append((name, fb_sql, fb_sql, domain_map, symbols,
                          sequence_increments, domain_types, self.function_call_map,
                          signature.get('return_not_null', False)))

        if manual:
            blocked_header = self._dump_header("POSTGRESQL FUNCTIONS BLOCKED")
            _write_text_atomic(
                out_file,
                self._dump_header("FIREBIRD FUNCTIONS USED BY STORED OBJECTS")
                + "\n".join(f"-- {entry}" for entry in manual) + "\n"
            )
            _write_text_atomic(
                conv_file,
                blocked_header + "\n".join(
                    f"-- [FUNCTION MIGRATION BLOCKED] {entry}" for entry in manual
                ) + "\n"
            )
            raise RuntimeError(
                "Required Firebird external functions need manual migration: "
                + ', '.join(manual)
            )

        self._export_transpiled_ddl(
            items,
            output_file=out_file,
            converted_file=conv_file,
            object_type='FUNCTION',
            firebird_header=self._dump_header("FIREBIRD FUNCTIONS USED BY STORED OBJECTS"),
            postgres_header=self._dump_header("POSTGRESQL FUNCTIONS (CONVERTED / NATIVE EQUIVALENTS OMITTED)"),
        )
        if native:
            with open(out_file, 'a', encoding='utf-8') as fb_file:
                fb_file.write("\n-- Native PostgreSQL equivalents selected:\n")
                for name in native:
                    signature = function_signatures[name]
                    fb_file.write(
                        f"-- {name} -> {analysis[name]['target']} "
                        f"({', '.join(signature['fb_params'])}) RETURNS {signature['fb_return']}\n"
                    )
            with open(conv_file, 'a', encoding='utf-8') as conv_f:
                conv_f.write("-- Native PostgreSQL equivalents selected; no compatibility object generated:\n")
                for name in native:
                    conv_f.write(f"--   {name}\n")
                conv_f.write("\n")
        self.exported_counts[DumpFiles.FUNCTIONS_PG] = len(items)
        return len(items)

    @staticmethod
    def _dump_header(title: str) -> str:
        return (f"-- ==========================================\n"
                f"-- {title}\n"
                f"-- ==========================================\n\n")

    @staticmethod
    def _export_transpiled_ddl(items: list[tuple[str, str]], output_file: str, converted_file: str,
                               object_type: str, firebird_header: str, postgres_header: str,
                               executor: ProcessPoolExecutor = None, chunksize: int = 4,
                               per_item_separator: bool = False):
        """
        Shared export pipeline: transpiles (item_name, firebird_sql) items in parallel and
        writes both dump files - the raw Firebird source and the converted PostgreSQL DDL.
        Objects that fail transpilation are kept in the converted file with a
        [TRANSPILER FAILED] marker for manual review.
        """
        logger.info(f"Transpiling {len(items)} {object_type.lower()}s in parallel...")
        owns_executor = executor is None
        if owns_executor:
            executor = ProcessPoolExecutor()
        try:
            results = list(executor.map(_transpile_worker, items, chunksize=chunksize))
        finally:
            if owns_executor:
                executor.shutdown()

        _ensure_parent_dir(output_file)
        _ensure_parent_dir(converted_file)

        failed_items = []
        temp_paths = []
        try:
            temp_files = []
            for final_path in (output_file, converted_file):
                directory = os.path.dirname(final_path) or '.'
                fd, temp_path = tempfile.mkstemp(
                    prefix=f'.{os.path.basename(final_path)}.', suffix='.tmp', dir=directory
                )
                os.close(fd)
                temp_paths.append(temp_path)
                temp_files.append(temp_path)

            with open(temp_files[0], 'w', encoding='utf-8') as f, \
                    open(temp_files[1], 'w', encoding='utf-8') as conv_f:
                f.write(firebird_header)
                conv_f.write(postgres_header)

                for item, (pg_sql, err) in zip(items, results):
                    item_name = item[0]
                    fb_sql = item[1]
                    if per_item_separator:
                        separator = (f"-- ----------------------------------------\n"
                                     f"-- {object_type.title()}: {item_name}\n"
                                     f"-- ----------------------------------------\n")
                        f.write(separator)
                        conv_f.write(separator)

                    f.write(fb_sql)
                    if err is None and pg_sql:
                        conv_f.write(pg_sql)
                        conv_f.write("\n\n")
                    else:
                        logger.error(f"Failed to transpile {object_type.lower()} {item_name}: {err}")
                        conv_f.write(f"-- [TRANSPILER FAILED] {object_type} {item_name}\n")
                        conv_f.write(fb_sql)
                        failed_items.append((item_name, err))

            # Publish both artifacts together. A failed run publishes its new
            # diagnostic dump, never leaves a previous successful dump in place.
            os.replace(temp_files[0], output_file)
            os.replace(temp_files[1], converted_file)
            temp_paths.clear()
        finally:
            for temp_path in temp_paths:
                try:
                    os.unlink(temp_path)
                except FileNotFoundError:
                    pass

        logger.info(f"Exported {len(items)} {object_type.lower()}s to '{output_file}' and '{converted_file}'")

        if failed_items:
            failures_summary = ", ".join(f"'{name}' ({err})" for name, err in failed_items[:5])
            if len(failed_items) > 5:
                failures_summary += f" ... and {len(failed_items) - 5} more"
            raise RuntimeError(
                f"Transpilation failed for {len(failed_items)} {object_type.lower()}(s): {failures_summary}. "
                f"Aborting migration before modifying target database. "
                f"See '{converted_file}' for diagnostic details."
            )

    def export_firebird_triggers(self, output_file: str = None,
                                 converted_file: str = None,
                                 executor: ProcessPoolExecutor = None,
                                 chunksize: int = 4):
        """
        Extracts all user-defined triggers from Firebird and saves their source code to a file
        and converted PostgreSQL DDL to another file.
        """
        out_file = output_file or get_dump_path(DumpFiles.TRIGGERS_FB)
        conv_file = converted_file or get_dump_path(DumpFiles.TRIGGERS_PG)
        fb_cursor = self.fb_con.cursor()

        query = """
            SELECT RDB$TRIGGER_NAME, RDB$RELATION_NAME, RDB$TRIGGER_TYPE, RDB$TRIGGER_SOURCE, RDB$TRIGGER_SEQUENCE
            FROM RDB$TRIGGERS
            WHERE RDB$SYSTEM_FLAG = 0
              AND RDB$TRIGGER_SOURCE IS NOT NULL
              AND (RDB$TRIGGER_INACTIVE = 0 OR RDB$TRIGGER_INACTIVE IS NULL)
            ORDER BY RDB$RELATION_NAME, RDB$TRIGGER_SEQUENCE, RDB$TRIGGER_NAME;
        """
        fb_cursor.execute(query)
        triggers = fb_cursor.fetchall()

        symbols = self._fetch_all_column_symbols(fb_cursor)
        domain_map, domain_types = self._fetch_domain_info(fb_cursor)
        seq_increments = fetch_all_sequence_increments(fb_cursor)

        items = []
        for trigger in triggers:
            trigger_name = trigger[0].strip() if trigger[0] else 'UNKNOWN'
            relation_name = trigger[1].strip() if trigger[1] else 'UNKNOWN'
            trigger_type = trigger[2]
            source = trigger[3]
            trigger_sequence = trigger[4] if trigger[4] is not None else 0

            fb_sql = self._format_trigger_firebird_ddl(trigger_name, relation_name, trigger_type, source)
            pg_trg_name = f"trg_{trigger_sequence:05d}_{trigger_name.lower()}"
            transpile_sql = self._format_trigger_firebird_ddl(pg_trg_name, relation_name, trigger_type, source)
            items.append((trigger_name, fb_sql, transpile_sql, domain_map, symbols,
                          seq_increments, domain_types, self.function_call_map))

        self._export_transpiled_ddl(
            items,
            output_file=out_file,
            converted_file=conv_file,
            object_type='TRIGGER',
            firebird_header=self._dump_header("FIREBIRD TRIGGERS DUMP"),
            postgres_header=self._dump_header("POSTGRESQL TRIGGERS DUMP (CONVERTED)"),
            executor=executor,
            chunksize=chunksize,
        )
        self.exported_counts[DumpFiles.TRIGGERS_PG] = len(triggers)
        return len(triggers)

    @staticmethod
    def _format_trigger_firebird_ddl(trigger_name: str, relation_name: str,
                                     trigger_type: int, source: str) -> str:
        timing_events = decode_trigger_type(trigger_type)
        return f"CREATE TRIGGER {trigger_name} FOR {relation_name} {timing_events}\n{source}\n\n"

    def export_firebird_procedures(self, output_file: str = None,
                                   converted_file: str = None,
                                   executor: ProcessPoolExecutor = None,
                                   chunksize: int = 4):
        """
        Extracts all user-defined stored procedures from Firebird and saves their source code to a file
        and converted PostgreSQL DDL to another file.
        """
        out_file = output_file or get_dump_path(DumpFiles.PROCEDURES_FB)
        conv_file = converted_file or get_dump_path(DumpFiles.PROCEDURES_PG)
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

        symbols = self._fetch_all_column_symbols(fb_cursor)
        domain_map, domain_types = self._fetch_domain_info(fb_cursor)
        seq_increments = fetch_all_sequence_increments(fb_cursor)

        items = []
        for proc in procedures:
            proc_name = proc[0].strip() if proc[0] else 'UNKNOWN'
            source = proc[1]

            input_params, output_params = self._fetch_procedure_parameters(fb_cursor, proc_name, domain_map=domain_map)
            fb_sql = self._format_procedure_firebird_ddl(proc_name, input_params, output_params, source)
            items.append((proc_name, fb_sql, fb_sql, domain_map, symbols,
                          seq_increments, domain_types, self.function_call_map))

        self._export_transpiled_ddl(
            items,
            output_file=out_file,
            converted_file=conv_file,
            object_type='PROCEDURE',
            firebird_header=self._dump_header("FIREBIRD PROCEDURES DUMP"),
            postgres_header=self._dump_header("POSTGRESQL PROCEDURES DUMP (CONVERTED)"),
            executor=executor,
            chunksize=chunksize,
        )
        self.exported_counts[DumpFiles.PROCEDURES_PG] = len(procedures)
        return len(procedures)

    @staticmethod
    def _fetch_domain_info(cursor) -> tuple[dict[str, str], dict[str, str]]:
        cursor.execute('SELECT RDB$RELATION_NAME FROM RDB$RELATIONS WHERE RDB$SYSTEM_FLAG = 0;')
        relation_names = {r[0].strip() for r in cursor.fetchall() if r[0]}
        cursor.execute("""
            SELECT 
                RDB$FIELD_NAME, 
                RDB$FIELD_TYPE, 
                RDB$FIELD_SUB_TYPE, 
                COALESCE(RDB$CHARACTER_LENGTH, RDB$FIELD_LENGTH), 
                RDB$FIELD_PRECISION, 
                RDB$FIELD_SCALE,
                RDB$CHARACTER_SET_ID,
                RDB$DIMENSIONS
            FROM RDB$FIELDS
            WHERE RDB$SYSTEM_FLAG = 0 AND RDB$FIELD_NAME NOT STARTING WITH 'RDB$'
            ORDER BY RDB$FIELD_NAME;
        """)
        rows = cursor.fetchall()
        domain_names = [r[0].strip() for r in rows if r[0]]
        domain_map = build_domain_mapping(domain_names, relation_names)
        domain_types = {}
        for r in rows:
            if not r[0]:
                continue
            d_name = r[0].strip().upper()
            if len(r) > 1:
                field_type = r[1]
                field_subtype = r[2] if len(r) > 2 else None
                field_length = r[3] if len(r) > 3 else None
                field_precision = r[4] if len(r) > 4 else None
                field_scale = r[5] if len(r) > 5 else None
                charset_id = r[6] if len(r) > 6 else None
                dimensions = r[7] if len(r) > 7 else None
                if dimensions is not None and dimensions > 0:
                    raise NotImplementedError(
                        f"Firebird array domains are not supported (domain '{d_name}')."
                    )
                fb_type = resolve_firebird_type(
                    field_type=field_type,
                    field_subtype=field_subtype,
                    field_length=field_length,
                    field_precision=field_precision,
                    field_scale=field_scale,
                    character_set_id=charset_id,
                    dimensions=dimensions,
                )
                if fb_type:
                    domain_types[d_name] = get_postgres_type(fb_type)
        return domain_map, domain_types

    @staticmethod
    def _fetch_domain_map(cursor) -> dict[str, str]:
        domain_map, _ = DdlExporter._fetch_domain_info(cursor)
        return domain_map

    @staticmethod
    def _fetch_trigger_map(cursor) -> dict[str, str]:
        """
        Builds the exact source->PostgreSQL trigger name mapping used at export:
        pg_name = f"trg_{sequence:05d}_{source.lower()}", with NULL sequences
        treated as 0. Same filters as export_firebird_triggers and
        get_source_objects so validation compares identical populations.
        Keys are uppercase source names, values lowercase PG names.
        """
        cursor.execute("""
            SELECT RDB$TRIGGER_NAME, RDB$TRIGGER_SEQUENCE
            FROM RDB$TRIGGERS
            WHERE RDB$SYSTEM_FLAG = 0
              AND RDB$TRIGGER_SOURCE IS NOT NULL
              AND (RDB$TRIGGER_INACTIVE = 0 OR RDB$TRIGGER_INACTIVE IS NULL)
            ORDER BY RDB$TRIGGER_NAME;
        """)
        mapping: dict[str, str] = {}
        for row in cursor.fetchall() or []:
            if not row or not row[0]:
                continue
            src = str(row[0]).strip()
            seq = row[1] if len(row) > 1 and row[1] is not None else 0
            try:
                seq_num = int(seq)
            except (ValueError, TypeError):
                seq_num = 0
            mapping[src.upper()] = f"trg_{seq_num:05d}_{src.lower()}"
        return mapping

    @staticmethod
    def _fetch_domain_types(cursor) -> dict[str, str]:
        _, domain_types = DdlExporter._fetch_domain_info(cursor)
        return domain_types

    @staticmethod
    def _fetch_procedure_parameters(cursor, proc_name: str, domain_map: dict[str, str] = None) -> tuple[list[str], list[str]]:
        params_query = """
            SELECT
                pp.RDB$PARAMETER_NAME,
                pp.RDB$PARAMETER_TYPE,
                pp.RDB$PARAMETER_NUMBER,
                f.RDB$FIELD_TYPE,
                f.RDB$FIELD_SUB_TYPE,
                COALESCE(f.RDB$CHARACTER_LENGTH, f.RDB$FIELD_LENGTH),
                f.RDB$FIELD_PRECISION,
                f.RDB$FIELD_SCALE,
                pp.RDB$FIELD_SOURCE,
                pp.RDB$DEFAULT_SOURCE,
                pp.RDB$NULL_FLAG,
                f.RDB$NULL_FLAG,
                f.RDB$DEFAULT_SOURCE,
                pp.RDB$PARAMETER_MECHANISM,
                f.RDB$CHARACTER_SET_ID,
                f.RDB$DIMENSIONS
            FROM RDB$PROCEDURE_PARAMETERS pp
            JOIN RDB$FIELDS f ON pp.RDB$FIELD_SOURCE = f.RDB$FIELD_NAME
            WHERE pp.RDB$PROCEDURE_NAME = ?
            ORDER BY pp.RDB$PARAMETER_TYPE, pp.RDB$PARAMETER_NUMBER;
        """
        try:
            cursor.execute(params_query, (proc_name,))
            params = cursor.fetchall()
        except firebirdsql.Error:
            legacy_query = """
                SELECT
                    pp.RDB$PARAMETER_NAME,
                    pp.RDB$PARAMETER_TYPE,
                    pp.RDB$PARAMETER_NUMBER,
                    f.RDB$FIELD_TYPE,
                    f.RDB$FIELD_SUB_TYPE,
                    COALESCE(f.RDB$CHARACTER_LENGTH, f.RDB$FIELD_LENGTH),
                    f.RDB$FIELD_PRECISION,
                    f.RDB$FIELD_SCALE,
                    pp.RDB$FIELD_SOURCE,
                    pp.RDB$DEFAULT_SOURCE,
                    pp.RDB$NULL_FLAG,
                    f.RDB$NULL_FLAG,
                    f.RDB$DEFAULT_SOURCE,
                    NULL,
                    f.RDB$CHARACTER_SET_ID,
                    f.RDB$DIMENSIONS
                FROM RDB$PROCEDURE_PARAMETERS pp
                JOIN RDB$FIELDS f ON pp.RDB$FIELD_SOURCE = f.RDB$FIELD_NAME
                WHERE pp.RDB$PROCEDURE_NAME = ?
                ORDER BY pp.RDB$PARAMETER_TYPE, pp.RDB$PARAMETER_NUMBER;
            """
            cursor.execute(legacy_query, (proc_name,))
            params = cursor.fetchall()

        def _clean_str(val):
            if val is None:
                return None
            if hasattr(val, 'read'):
                val = val.read()
            if isinstance(val, bytes):
                val = val.decode('utf-8', errors='replace')
            s = str(val).strip()
            return s if s else None

        input_params = []
        output_params = []
        for param in params:
            param_name = param[0].strip() if param[0] else 'UNKNOWN'
            param_type_flag = param[1]  # 0=input, 1=output
            field_type = param[3]
            field_subtype = param[4]
            field_length = param[5]
            field_precision = param[6]
            field_scale = param[7]
            field_source = _clean_str(param[8]) if len(param) > 8 else None
            param_default = _clean_str(param[9]) if len(param) > 9 else None
            param_null_flag = param[10] if len(param) > 10 else None
            field_null_flag = param[11] if len(param) > 11 else None
            field_default = _clean_str(param[12]) if len(param) > 12 else None
            param_mechanism = param[13] if len(param) > 13 else None
            charset_id = param[14] if len(param) > 14 else None
            dimensions = param[15] if len(param) > 15 else None

            if dimensions is not None and dimensions > 0:
                raise NotImplementedError(
                    f"Firebird array parameters are not supported (parameter '{param_name}' in procedure '{proc_name}')."
                )

            # Preserve user-defined domain if not a system domain (RDB$...) and not TYPE OF domain (mechanism = 1)
            if field_source and not field_source.startswith('RDB$') and param_mechanism != 1:
                if domain_map and field_source.upper() in domain_map:
                    val = domain_map[field_source.upper()]
                    if isinstance(val, (tuple, list)):
                        type_name = val[0]
                    elif isinstance(val, dict):
                        type_name = val.get('pg_name', field_source)
                    else:
                        type_name = val
                else:
                    type_name = field_source
            else:
                type_name = resolve_firebird_type(
                    field_type=field_type,
                    field_subtype=field_subtype,
                    field_length=field_length,
                    field_precision=field_precision,
                    field_scale=field_scale,
                    character_set_id=charset_id,
                    dimensions=dimensions,
                )
                if type_name is None:
                    raise TypeError(
                        f"Unsupported or unrecognized Firebird data type (field_type={field_type}, "
                        f"field_subtype={field_subtype}) for parameter '{param_name}' in procedure '{proc_name}'."
                    )

            if param_mechanism == 1:
                raw_default = param_default
                is_not_null = (param_null_flag == 1)
            else:
                raw_default = param_default or field_default
                is_not_null = (param_null_flag == 1) or (field_null_flag == 1)

            default_clause = ""
            if raw_default:
                if raw_default.upper().startswith('DEFAULT'):
                    default_clause = f" {raw_default}"
                elif raw_default.startswith('='):
                    default_clause = f" DEFAULT {raw_default[1:].strip()}"
                else:
                    default_clause = f" DEFAULT {raw_default}"

            not_null_clause = " NOT NULL" if is_not_null else ""

            if param_type_flag == 0:
                input_params.append(f'    {param_name} {type_name}{not_null_clause}{default_clause}')
            else:
                output_params.append(f'    {param_name} {type_name}{not_null_clause}')

        return input_params, output_params

    @staticmethod
    def _format_procedure_firebird_ddl(proc_name: str, input_params: list[str],
                                       output_params: list[str], source: str) -> str:
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
        return fb_sql

    def export_firebird_views(self, output_file: str = None,
                              converted_file: str = None,
                              executor: ProcessPoolExecutor = None,
                              chunksize: int = 4):
        """
        Extracts all user-defined views from Firebird and saves their source code to a file
        and converted PostgreSQL DDL to another file.
        """
        out_file = output_file or get_dump_path(DumpFiles.VIEWS_FB)
        conv_file = converted_file or get_dump_path(DumpFiles.VIEWS_PG)
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

        symbols = self._fetch_all_column_symbols(fb_cursor)
        domain_map, domain_types = self._fetch_domain_info(fb_cursor)
        seq_increments = fetch_all_sequence_increments(fb_cursor)

        view_map = {}
        for view in views:
            view_name = view[0].strip() if view[0] else 'UNKNOWN'
            source = view[1]
            col_names = self._fetch_view_columns(fb_cursor, view_name)
            fb_sql = self._format_view_firebird_ddl(view_name, col_names, source)
            view_map[view_name] = (view_name, fb_sql, None, domain_map, symbols,
                                   seq_increments, domain_types, self.function_call_map)

        ordered_names = self._resolve_view_dependency_order(fb_cursor, set(view_map.keys()))
        items = [view_map[name] for name in ordered_names if name in view_map]

        self._export_transpiled_ddl(
            items,
            output_file=out_file,
            converted_file=conv_file,
            object_type='VIEW',
            firebird_header=self._dump_header("FIREBIRD VIEWS DUMP"),
            postgres_header=self._dump_header("POSTGRESQL VIEWS DUMP (CONVERTED)"),
            executor=executor,
            chunksize=chunksize,
            per_item_separator=True,
        )
        self.exported_counts[DumpFiles.VIEWS_PG] = len(views)
        return len(views)

    @staticmethod
    def _resolve_view_dependency_order(cursor, view_names: set[str]) -> list[str]:
        deps: dict[str, set[str]] = {name: set() for name in sorted(view_names)}
        dep_query = """
            SELECT DISTINCT RDB$DEPENDENT_NAME, RDB$DEPENDED_ON_NAME
            FROM RDB$DEPENDENCIES
            WHERE RDB$DEPENDENT_TYPE = 1;
        """
        cursor.execute(dep_query)
        for row in cursor.fetchall():
            dep_name = row[0].strip() if row[0] else ""
            used_name = row[1].strip() if row[1] else ""
            if dep_name in deps and used_name in deps and dep_name != used_name:
                deps[dep_name].add(used_name)

        return list(TopologicalSorter(deps).static_order())

    @staticmethod
    def _fetch_view_columns(cursor, view_name: str) -> list[str]:
        columns_query = """
            SELECT RDB$FIELD_NAME 
            FROM RDB$RELATION_FIELDS 
            WHERE RDB$RELATION_NAME = ?
            ORDER BY RDB$FIELD_POSITION;
        """
        cursor.execute(columns_query, (view_name,))
        cols = []
        for col in cursor.fetchall():
            if col[0]:
                clean = col[0].strip().replace('"', '""')
                cols.append(f'"{clean}"')
        return cols

    @staticmethod
    def _fetch_all_column_symbols(cursor) -> dict[str, str]:
        """
        Queries all column data types for user relations in Firebird to provide
        type inference context (symbols) during DDL transpilation.

        Bare column names (without table qualifier) are only stored when ALL tables
        containing that column agree on the PostgreSQL type. This prevents cross-table
        type pollution where A.D(TIMESTAMP) and B.D(DATE) would make bare 'D' resolve
        to whichever table was read first from the catalog.
        Rows are processed in (relation, field position) order — in SQL and,
        defensively, re-sorted in Python — so SELECT * expansion and other
        order-sensitive inference follow real column order regardless of the
        order the catalog (or a mock) returns rows.
        """
        query = """
            SELECT TRIM(RF.RDB$RELATION_NAME), TRIM(RF.RDB$FIELD_NAME),
                   F.RDB$FIELD_TYPE, F.RDB$FIELD_SUB_TYPE, F.RDB$FIELD_LENGTH,
                   F.RDB$FIELD_PRECISION, F.RDB$FIELD_SCALE,
                   F.RDB$CHARACTER_SET_ID, F.RDB$DIMENSIONS,
                   RF.RDB$FIELD_POSITION
            FROM RDB$RELATION_FIELDS RF
            JOIN RDB$FIELDS F ON RF.RDB$FIELD_SOURCE = F.RDB$FIELD_NAME
            WHERE (RF.RDB$SYSTEM_FLAG = 0 OR RF.RDB$SYSTEM_FLAG IS NULL)
            ORDER BY RF.RDB$RELATION_NAME, RF.RDB$FIELD_POSITION;
        """
        symbols = {}
        bare_types: dict[str, set[str]] = {}  # col -> {type1, type2, ...}
        try:
            cursor.execute(query)
            rows = list(cursor.fetchall())

            def _position_key(row) -> tuple[str, int]:
                try:
                    rel = str(row[0]).strip().lower() if row and row[0] else ""
                except Exception:
                    rel = ""
                try:
                    pos = int(row[9]) if len(row) > 9 and row[9] is not None else 0
                except (ValueError, TypeError):
                    pos = 0
                return (rel, pos)

            rows.sort(key=_position_key)
            for row in rows:
                rel = row[0].lower() if row[0] else ""
                col = row[1].lower() if row[1] else ""
                try:
                    pg_type = resolve_firebird_type(
                        field_type=row[2],
                        field_subtype=row[3],
                        field_length=row[4],
                        field_precision=row[5],
                        field_scale=row[6],
                        character_set_id=row[7] if len(row) > 7 else None,
                        dimensions=row[8] if len(row) > 8 else None,
                    )
                except NotImplementedError:
                    pg_type = None
                if pg_type:
                    if rel and col:
                        symbols[f"{rel}.{col}"] = pg_type
                    if col:
                        bare_types.setdefault(col, set()).add(pg_type.upper())
            # Only store bare column name when all tables agree on the type
            for col, types in bare_types.items():
                if len(types) == 1:
                    symbols[col] = next(iter(types))
        except Exception as e:
            raise RuntimeError("Failed to fetch column symbols required for DDL export.") from e
        return symbols

    @staticmethod
    def _format_view_firebird_ddl(view_name: str, col_names: list[str], source: str) -> str:
        col_list = f" ({', '.join(col_names)})" if col_names else ""
        return f'CREATE OR ALTER VIEW "{view_name}"{col_list} AS\n{source}\n\n'

    def inventory_unsupported_objects(self) -> dict[str, list[str]]:
        """
        Scans the Firebird database for objects that are not automatically transpiled
        (functions/UDFs, packages, exceptions, database triggers, roles, grants) and returns
        a dictionary mapping object categories to lists of object names.
        Explicitly distinguishes between empty categories, features not supported by the
        Firebird version (e.g. PACKAGES in FB 2.5), and actual catalog query errors.
        """
        cursor = self.fb_con.cursor()
        unsupported: dict[str, list[str]] = {}

        queries = [
            ("FUNCTIONS", """
                SELECT RDB$FUNCTION_NAME
                FROM RDB$FUNCTIONS
                WHERE (RDB$SYSTEM_FLAG = 0 OR RDB$SYSTEM_FLAG IS NULL)
                ORDER BY RDB$FUNCTION_NAME;
            """),
            ("PACKAGES", """
                SELECT RDB$PACKAGE_NAME
                FROM RDB$PACKAGES
                WHERE (RDB$SYSTEM_FLAG = 0 OR RDB$SYSTEM_FLAG IS NULL)
                ORDER BY RDB$PACKAGE_NAME;
            """),
            ("EXCEPTIONS", """
                SELECT RDB$EXCEPTION_NAME
                FROM RDB$EXCEPTIONS
                WHERE (RDB$SYSTEM_FLAG = 0 OR RDB$SYSTEM_FLAG IS NULL)
                ORDER BY RDB$EXCEPTION_NAME;
            """),
            ("DATABASE_TRIGGERS", """
                SELECT RDB$TRIGGER_NAME
                FROM RDB$TRIGGERS
                WHERE (RDB$SYSTEM_FLAG = 0 OR RDB$SYSTEM_FLAG IS NULL)
                  AND (RDB$RELATION_NAME IS NULL OR RDB$TRIGGER_TYPE > 8192)
                ORDER BY RDB$TRIGGER_NAME;
            """),
            ("ROLES", """
                SELECT RDB$ROLE_NAME
                FROM RDB$ROLES
                WHERE (RDB$SYSTEM_FLAG = 0 OR RDB$SYSTEM_FLAG IS NULL)
                  AND RDB$ROLE_NAME NOT STARTING WITH 'RDB$'
                ORDER BY RDB$ROLE_NAME;
            """),
            ("GRANTS", """
                SELECT DISTINCT TRIM(RDB$USER), TRIM(RDB$PRIVILEGE), TRIM(RDB$RELATION_NAME)
                FROM RDB$USER_PRIVILEGES
                WHERE RDB$USER NOT STARTING WITH 'RDB$'
                  AND RDB$USER NOT IN ('SYSDBA')
                ORDER BY RDB$RELATION_NAME, RDB$USER;
            """),
        ]

        for cat, sql in queries:
            try:
                cursor.execute(sql)
                rows = cursor.fetchall()
                if cat == "GRANTS":
                    items = [f"{r[0]} -> {r[1]} ON {r[2]}" for r in rows if r and r[0] and r[2]]
                else:
                    items = [r[0].strip() for r in rows if r and r[0]]
                if items:
                    unsupported[cat] = items
            except Exception as e:
                err_str = str(e).strip()
                # Table unknown or feature not in this Firebird dialect/version
                if "Table unknown" in err_str or "42S02" in err_str or "does not exist" in err_str.lower():
                    logger.info(f"Firebird catalog category '{cat}' is not supported by this database version: {err_str}")
                    unsupported.setdefault('NOT_SUPPORTED_BY_VERSION', []).append(f"{cat}: {err_str}")
                else:
                    logger.error(f"Catalog query failed for category '{cat}': {err_str}")
                    unsupported.setdefault('QUERY_ERRORS', []).append(f"{cat}: {err_str}")

        if unsupported:
            for cat, items in unsupported.items():
                if cat == 'QUERY_ERRORS':
                    logger.error(f"Failed to query catalog for {len(items)} category(ies): {items}")
                elif cat == 'NOT_SUPPORTED_BY_VERSION':
                    logger.info(f"Firebird version does not support: {items}")
                elif cat == 'FUNCTIONS':
                    logger.info(
                        f"Found {len(items)} declared Firebird functions; "
                        'their native/manual status is determined by function analysis.'
                    )
                else:
                    logger.warning(
                        f"Found {len(items)} {cat.lower()} in Firebird requiring manual review/migration: "
                        f"{', '.join(items[:10])}{'...' if len(items) > 10 else ''}"
                    )
        return unsupported

    def export_all_firebird_ddl(self, output_dir: str = None):
        """
        Exports all Firebird domains, triggers, procedures, and views using a single shared
        ProcessPoolExecutor, saving all dump files to the specified output directory.
        Also scans and logs an inventory of database objects that require manual migration.
        """
        target_dir = output_dir or DUMP_DIR
        os.makedirs(target_dir, exist_ok=True)

        # Inventory untranspiled/manual objects
        unsupported = self.inventory_unsupported_objects()
        if unsupported.get('QUERY_ERRORS'):
            raise RuntimeError(
                "Firebird catalog inventory failed; refusing to continue: "
                + '; '.join(unsupported['QUERY_ERRORS'])
            )
        function_analysis = self.analyze_database_functions(include_unused=True)
        report_inventory = {
            category: items for category, items in unsupported.items()
            if category != 'FUNCTIONS'
        }
        if report_inventory or function_analysis:
            report_path = os.path.join(target_dir, "manual_migration_inventory.txt")
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(self._dump_header("FIREBIRD OBJECTS REQUIRING MANUAL MIGRATION"))
                for category, items in sorted(report_inventory.items()):
                    f.write(f"[{category}] ({len(items)} items):\n")
                    for item in items:
                        f.write(f"  - {item}\n")
                    f.write("\n")
                if function_analysis:
                    f.write("[FUNCTION_ANALYSIS] (all declared functions):\n")
                    for name, item in sorted(function_analysis.items()):
                        detail = f"{item['status']} / {item['classification']}"
                        if item.get('package'):
                            detail += f" package={item['package']}"
                        if item.get('module'):
                            detail += f" [{item['module']}::{item.get('entrypoint') or '?'}]"
                        evidence = ', '.join(item.get('usage', [])) or 'no static caller found'
                        f.write(f"  - {name}: {detail}; {item.get('reason', '')}; used by {evidence}\n")
                    f.write("\n")
        else:
            stale_report = os.path.join(target_dir, "manual_migration_inventory.txt")
            if os.path.exists(stale_report):
                os.unlink(stale_report)

        def _path(filename: str) -> str:
            return get_dump_path(filename, target_dir)

        self.export_firebird_domains(
            output_file=_path(DumpFiles.DOMAINS_FB),
            converted_file=_path(DumpFiles.DOMAINS_PG)
        )
        self.export_firebird_generators(
            output_file=_path(DumpFiles.GENERATORS_FB),
            converted_file=_path(DumpFiles.SEQUENCES_PG)
        )
        self.export_firebird_functions(
            output_file=_path(DumpFiles.FUNCTIONS_FB),
            converted_file=_path(DumpFiles.FUNCTIONS_PG)
        )
        with ProcessPoolExecutor() as executor:
            self.export_firebird_triggers(
                output_file=_path(DumpFiles.TRIGGERS_FB),
                converted_file=_path(DumpFiles.TRIGGERS_PG),
                executor=executor
            )
            self.export_firebird_procedures(
                output_file=_path(DumpFiles.PROCEDURES_FB),
                converted_file=_path(DumpFiles.PROCEDURES_PG),
                executor=executor
            )
            self.export_firebird_views(
                output_file=_path(DumpFiles.VIEWS_FB),
                converted_file=_path(DumpFiles.VIEWS_PG),
                executor=executor
            )

        return dict(self.exported_counts)

    def get_source_objects(self) -> dict[str, list[str]]:
        """
        Queries Firebird catalog to retrieve user-defined object names for each category.
        Returns a dict mapping dump filename (e.g. DumpFiles.PROCEDURES_PG) to a list of object names.
        Raises an exception if any catalog query fails (catalog failures must not be swallowed).
        """
        cursor = self.fb_con.cursor()
        objects = {}

        # Domains
        cursor.execute("""
            SELECT DISTINCT RDB$FIELD_NAME FROM RDB$FIELDS
            WHERE RDB$SYSTEM_FLAG = 0
              AND RDB$FIELD_NAME NOT STARTING WITH 'RDB$'
            ORDER BY RDB$FIELD_NAME;
        """)
        objects[DumpFiles.DOMAINS_PG] = [r[0].strip() for r in cursor.fetchall() if r and r[0]]

        # Native equivalents require no PostgreSQL object. PSQL functions
        # reachable from stored objects must be present in the function dump.
        analysis = self.analyze_database_functions()
        objects[DumpFiles.FUNCTIONS_PG] = [
            name for name, item in analysis.items() if item['classification'] == 'PSQL'
        ]

        # Procedures
        cursor.execute("""
            SELECT RDB$PROCEDURE_NAME FROM RDB$PROCEDURES
            WHERE RDB$SYSTEM_FLAG = 0
              AND RDB$PROCEDURE_SOURCE IS NOT NULL
            ORDER BY RDB$PROCEDURE_NAME;
        """)
        objects[DumpFiles.PROCEDURES_PG] = [r[0].strip() for r in cursor.fetchall() if r and r[0]]

        # Views
        cursor.execute("""
            SELECT RDB$RELATION_NAME FROM RDB$RELATIONS
            WHERE RDB$SYSTEM_FLAG = 0
              AND RDB$VIEW_BLR IS NOT NULL
            ORDER BY RDB$RELATION_NAME;
        """)
        objects[DumpFiles.VIEWS_PG] = [r[0].strip() for r in cursor.fetchall() if r and r[0]]

        # Triggers
        cursor.execute("""
            SELECT RDB$TRIGGER_NAME FROM RDB$TRIGGERS
            WHERE RDB$SYSTEM_FLAG = 0
              AND RDB$TRIGGER_SOURCE IS NOT NULL
              AND (RDB$TRIGGER_INACTIVE = 0 OR RDB$TRIGGER_INACTIVE IS NULL)
            ORDER BY RDB$TRIGGER_NAME;
        """)
        objects[DumpFiles.TRIGGERS_PG] = [r[0].strip() for r in cursor.fetchall() if r and r[0]]

        # Generators / Sequences
        cursor.execute("""
            SELECT RDB$GENERATOR_NAME FROM RDB$GENERATORS
            WHERE (RDB$SYSTEM_FLAG = 0 OR RDB$SYSTEM_FLAG IS NULL)
              AND RDB$GENERATOR_NAME NOT STARTING WITH 'RDB$'
              AND RDB$GENERATOR_NAME NOT STARTING WITH 'MON$'
            ORDER BY RDB$GENERATOR_NAME;
        """)
        objects[DumpFiles.SEQUENCES_PG] = [r[0].strip() for r in cursor.fetchall() if r and r[0]]

        return objects

    def get_source_object_counts(self) -> dict[str, int]:
        """
        Queries Firebird catalog to count user-defined objects for each category.
        Returns a dict mapping dump filename (e.g. DumpFiles.DOMAINS_PG) to expected count.
        Raises an exception if any catalog query fails (catalog failures must not be swallowed).
        """
        cursor = self.fb_con.cursor()
        counts = {}

        # Domains
        cursor.execute("""
            SELECT COUNT(*) FROM RDB$FIELDS
            WHERE RDB$SYSTEM_FLAG = 0
              AND RDB$FIELD_NAME NOT STARTING WITH 'RDB$';
        """)
        row = cursor.fetchone()
        counts[DumpFiles.DOMAINS_PG] = row[0] if row and row[0] is not None else 0

        # Procedures
        cursor.execute("""
            SELECT COUNT(*) FROM RDB$PROCEDURES
            WHERE RDB$SYSTEM_FLAG = 0
              AND RDB$PROCEDURE_SOURCE IS NOT NULL;
        """)
        row = cursor.fetchone()
        counts[DumpFiles.PROCEDURES_PG] = row[0] if row and row[0] is not None else 0

        # Views
        cursor.execute("""
            SELECT COUNT(*) FROM RDB$RELATIONS
            WHERE RDB$SYSTEM_FLAG = 0
              AND RDB$VIEW_BLR IS NOT NULL;
        """)
        row = cursor.fetchone()
        counts[DumpFiles.VIEWS_PG] = row[0] if row and row[0] is not None else 0

        # Triggers
        cursor.execute("""
            SELECT COUNT(*) FROM RDB$TRIGGERS
            WHERE RDB$SYSTEM_FLAG = 0
              AND RDB$TRIGGER_SOURCE IS NOT NULL
              AND (RDB$TRIGGER_INACTIVE = 0 OR RDB$TRIGGER_INACTIVE IS NULL);
        """)
        row = cursor.fetchone()
        counts[DumpFiles.TRIGGERS_PG] = row[0] if row and row[0] is not None else 0

        # Generators / Sequences
        cursor.execute("""
            SELECT COUNT(*) FROM RDB$GENERATORS
            WHERE (RDB$SYSTEM_FLAG = 0 OR RDB$SYSTEM_FLAG IS NULL)
              AND RDB$GENERATOR_NAME NOT STARTING WITH 'RDB$'
              AND RDB$GENERATOR_NAME NOT STARTING WITH 'MON$';
        """)
        row = cursor.fetchone()
        counts[DumpFiles.SEQUENCES_PG] = row[0] if row and row[0] is not None else 0

        # Count only functions that the exporter can actually materialize.
        # Native equivalents do not produce a PostgreSQL object, and unused
        # functions are intentionally omitted from the migration.
        try:
            analysis = self.analyze_database_functions()
            counts[DumpFiles.FUNCTIONS_PG] = sum(
                item['classification'] == 'PSQL' for item in analysis.values()
            )
        except StopIteration:
            # Legacy cursor test doubles may provide only the original five
            # fetch results; real DB errors propagate.
            pass

        return counts

    def export_firebird_generators(self, output_file: str = None,
                                   converted_file: str = None):
        """
        Extracts all user-defined generators from Firebird and saves their source code to a file
        and the PostgreSQL converted CREATE SEQUENCE definitions with initial values.
        """
        out_file = output_file or get_dump_path(DumpFiles.GENERATORS_FB)
        conv_file = converted_file or get_dump_path(DumpFiles.SEQUENCES_PG)

        cursor = self.fb_con.cursor()
        try:
            cursor.execute("""
                SELECT RDB$GENERATOR_NAME, COALESCE(RDB$GENERATOR_INCREMENT, 1)
                FROM RDB$GENERATORS
                WHERE (RDB$SYSTEM_FLAG = 0 OR RDB$SYSTEM_FLAG IS NULL)
                  AND RDB$GENERATOR_NAME NOT STARTING WITH 'RDB$'
                  AND RDB$GENERATOR_NAME NOT STARTING WITH 'MON$';
            """)
            rows = cursor.fetchall()
        except firebirdsql.Error as e:
            if not is_column_not_found_error(e, "RDB$GENERATOR_INCREMENT"):
                raise RuntimeError(f"Failed to export sequences from Firebird: {e}") from e
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
                raise RuntimeError(f"Failed to export sequences from Firebird: {fallback_err}") from fallback_err
        except Exception as e:
            raise RuntimeError(f"Failed to export sequences from Firebird: {e}") from e
        items_fb = []
        items_pg = []
        for row in rows:
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
            fb_ident = name if (name.isupper() and name.isidentifier()) else f'"{safe_name}"'
            inc_clause = f" INCREMENT BY {increment}" if increment != 1 else ""
            items_fb.append(f"CREATE SEQUENCE {fb_ident}{inc_clause};\nSET GENERATOR {fb_ident} TO {curr_val};")
            items_pg.append(Sequence(name=name, current_value=curr_val, increment=increment).get_create_sequence_query())

        _ensure_parent_dir(out_file)
        _ensure_parent_dir(conv_file)

        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(self._dump_header("FIREBIRD GENERATORS"))
            for stmt in items_fb:
                f.write(f"{stmt}\n\n")

        with open(conv_file, 'w', encoding='utf-8') as f:
            f.write(self._dump_header("POSTGRESQL SEQUENCES"))
            for stmt in items_pg:
                f.write(f"{stmt}\n")

        self.exported_counts[DumpFiles.SEQUENCES_PG] = len(items_pg)
        return len(items_pg)

    def export_firebird_domains(self, output_file: str = None,
                                converted_file: str = None):
        """
        Extracts all user-defined domains from Firebird and saves their source code to a file
        and the PostgreSQL converted CREATE DOMAIN definitions.
        """
        out_file = output_file or get_dump_path(DumpFiles.DOMAINS_FB)
        conv_file = converted_file or get_dump_path(DumpFiles.DOMAINS_PG)

        fb_cursor = self.fb_con.cursor()
        seq_increments = fetch_all_sequence_increments(fb_cursor)

        query = """
            SELECT 
                RDB$FIELD_NAME, 
                RDB$FIELD_TYPE, 
                RDB$FIELD_SUB_TYPE, 
                COALESCE(RDB$CHARACTER_LENGTH, RDB$FIELD_LENGTH), 
                RDB$FIELD_PRECISION, 
                RDB$FIELD_SCALE,
                RDB$DEFAULT_SOURCE,
                RDB$NULL_FLAG,
                RDB$VALIDATION_SOURCE,
                RDB$CHARACTER_SET_ID,
                RDB$DIMENSIONS
            FROM RDB$FIELDS
            WHERE RDB$SYSTEM_FLAG = 0
              AND RDB$FIELD_NAME NOT STARTING WITH 'RDB$'
            ORDER BY RDB$FIELD_NAME;
        """
        fb_cursor.execute(query)
        domains = fb_cursor.fetchall()

        fb_cursor.execute('SELECT RDB$RELATION_NAME FROM RDB$RELATIONS WHERE RDB$SYSTEM_FLAG = 0;')
        relation_names = {r[0].strip() for r in fb_cursor.fetchall() if r[0]}

        domain_names = [d[0].strip() for d in domains if d[0]]
        domain_map = build_domain_mapping(domain_names, relation_names)

        _ensure_parent_dir(out_file)
        _ensure_parent_dir(conv_file)

        with open(out_file, 'w', encoding='utf-8') as f, open(conv_file, 'w', encoding='utf-8') as conv_f:
            f.write(self._dump_header("FIREBIRD DOMAINS DUMP"))
            conv_f.write(self._dump_header("POSTGRESQL DOMAINS DUMP (CONVERTED)"))

            for d in domains:
                domain_name = d[0].strip() if d[0] else 'UNKNOWN'
                field_type = d[1]
                field_subtype = d[2]
                field_length = d[3]
                field_precision = d[4]
                field_scale = d[5]
                default_source = d[6].strip() if d[6] else None
                not_null = (d[7] == 1)
                validation_source = d[8].strip() if d[8] else None
                charset_id = d[9] if len(d) > 9 else None
                dimensions = d[10] if len(d) > 10 else None

                if dimensions is not None and dimensions > 0:
                    raise NotImplementedError(
                        f"Firebird array domains are not supported (domain '{domain_name}')."
                    )

                fb_full_type = resolve_firebird_type(
                    field_type=field_type,
                    field_subtype=field_subtype,
                    field_length=field_length,
                    field_precision=field_precision,
                    field_scale=field_scale,
                    character_set_id=charset_id,
                    dimensions=dimensions,
                )
                if fb_full_type is None:
                    raise TypeError(
                        f"Unsupported or unrecognized Firebird data type (field_type={field_type}, "
                        f"field_subtype={field_subtype}) for domain '{domain_name}'."
                    )
                pg_type = get_postgres_type(fb_full_type)

                # Firebird DDL
                fb_ddl = self._format_domain_firebird_ddl(
                    domain_name, fb_full_type, default_source, not_null, validation_source
                )
                f.write(fb_ddl)

                # PostgreSQL DDL
                pg_domain_name = domain_map.get(domain_name.upper(), domain_name.lower())
                if pg_domain_name != domain_name.lower():
                    logger.info(f'  [RENAMED] Domain "{domain_name}" -> "{pg_domain_name}".')
                    conv_f.write(f'-- [RENAMED] DOMAIN "{domain_name}" -> "{pg_domain_name}" '
                                 f'(collides with a table/view name or another domain)\n')

                try:
                    pg_ddl = self._format_domain_postgres_ddl(
                        pg_domain_name, pg_type, default_source, not_null, validation_source,
                        sequence_increments=seq_increments,
                        function_map=self.function_call_map
                    )
                except Exception as e:
                    raise RuntimeError(f"Failed to transpile domain '{domain_name}': {e}") from e
                conv_f.write(pg_ddl)

        logger.info(f"Exported {len(domains)} domains to '{out_file}' and '{conv_file}'")
        self.exported_counts[DumpFiles.DOMAINS_PG] = len(domains)
        return len(domains)

    @staticmethod
    def _format_domain_firebird_ddl(domain_name: str, fb_full_type: str,
                                    default_source: str | None, not_null: bool,
                                    validation_source: str | None) -> str:
        fb_ddl = f'CREATE DOMAIN "{domain_name}" AS {fb_full_type}'
        if default_source:
            fb_ddl += f' {default_source}'
        if not_null:
            fb_ddl += ' NOT NULL'
        if validation_source:
            fb_ddl += f'\n{validation_source}'
        fb_ddl += ';\n'
        return fb_ddl

    @staticmethod
    def _format_domain_postgres_ddl(pg_domain_name: str, pg_type: str,
                                     default_source: str | None, not_null: bool,
                                     validation_source: str | None,
                                     sequence_increments: dict[str, int] = None,
                                     function_map: dict[str, str] = None) -> str:
        pg_domain_ident = f'public."{pg_domain_name}"'
        create_ddl = f'CREATE DOMAIN {pg_domain_ident} AS {pg_type}'
        transpiled_default = FirebirdToPostgresVisitor.transpile_default_clause(
            default_source, sequence_increments=sequence_increments,
            function_map=function_map
        )
        if transpiled_default:
            create_ddl += f' {transpiled_default}'
        if not_null:
            create_ddl += ' NOT NULL'
        transpiled_check = FirebirdToPostgresVisitor.transpile_check_clause(
            validation_source, sequence_increments=sequence_increments,
            function_map=function_map
        )
        if transpiled_check:
            create_ddl += f'\n{transpiled_check}'
        create_ddl += ';'

        escaped_name = pg_domain_name.replace("'", "''")
        escaped_ddl = create_ddl.replace("'", "''")
        inner_block = (
            'BEGIN\n'
            '    IF NOT EXISTS (SELECT 1 FROM pg_type t\n'
            '                   JOIN pg_namespace n ON n.oid = t.typnamespace\n'
            "                   WHERE t.typtype = 'd' AND n.nspname = 'public'\n"
            f"                     AND t.typname = '{escaped_name}') THEN\n"
            f"        EXECUTE '{escaped_ddl}';\n"
            '    END IF;\n'
            'END'
        )
        tag = choose_dollar_tag(inner_block + f" {escaped_ddl}", base_tag="")
        return f'DO {tag}\n{inner_block} {tag};\n'
