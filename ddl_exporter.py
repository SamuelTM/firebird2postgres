import os
import logging
from concurrent.futures import ProcessPoolExecutor
from config import DUMP_DIR, DumpFiles, get_dump_path
from database_objects import get_postgres_type
from firebird_visitor import FirebirdToPostgresVisitor
from firebird_types import resolve_firebird_type, resolve_pg_domain_name, decode_trigger_type

logger = logging.getLogger(__name__)


def _ensure_parent_dir(file_path: str):
    directory = os.path.dirname(file_path)
    if directory:
        os.makedirs(directory, exist_ok=True)


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


class DdlExporter:
    """
    Extracts Firebird domains, triggers, stored procedures, and views,
    transpiles their DDL in parallel to PostgreSQL, and writes out SQL dump files.
    """


    def __init__(self, fb_con):
        self.fb_con = fb_con

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

        with open(output_file, 'w', encoding='utf-8') as f, open(converted_file, 'w', encoding='utf-8') as conv_f:
            f.write(firebird_header)
            conv_f.write(postgres_header)

            for (item_name, fb_sql), (pg_sql, err) in zip(items, results):
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

        logger.info(f"Exported {len(items)} {object_type.lower()}s to '{output_file}' and '{converted_file}'")

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

            timing_events = decode_trigger_type(trigger_type)
            fb_sql = f"CREATE TRIGGER {trigger_name} FOR {relation_name} {timing_events}\n{source}\n\n"
            items.append((trigger_name, fb_sql))

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

                type_name = resolve_firebird_type(param[3], param[4], param[5], param[6], param[7])
                if type_name is None:
                    type_name = 'VARCHAR(255)'

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

    def export_all_firebird_ddl(self, output_dir: str = None):
        """
        Exports all Firebird domains, triggers, procedures, and views using a single shared
        ProcessPoolExecutor, saving all dump files to the specified output directory.
        """
        target_dir = output_dir or DUMP_DIR
        os.makedirs(target_dir, exist_ok=True)

        def _path(filename: str) -> str:
            return get_dump_path(filename, target_dir)

        self.export_firebird_domains(
            output_file=_path(DumpFiles.DOMAINS_FB),
            converted_file=_path(DumpFiles.DOMAINS_PG)
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

    def export_firebird_domains(self, output_file: str = None,
                                converted_file: str = None):
        """
        Extracts all user-defined domains from Firebird and saves their source code to a file
        and the PostgreSQL converted CREATE DOMAIN definitions.
        """
        out_file = output_file or get_dump_path(DumpFiles.DOMAINS_FB)
        conv_file = converted_file or get_dump_path(DumpFiles.DOMAINS_PG)

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
                RDB$NULL_FLAG,
                RDB$VALIDATION_SOURCE
            FROM RDB$FIELDS
            WHERE RDB$SYSTEM_FLAG = 0
              AND RDB$FIELD_NAME NOT STARTING WITH 'RDB$'
            ORDER BY RDB$FIELD_NAME;
        """
        fb_cursor.execute(query)
        domains = fb_cursor.fetchall()

        # Needed to detect domain names that collide with tables/views (see resolve_pg_domain_name)
        fb_cursor.execute('SELECT RDB$RELATION_NAME FROM RDB$RELATIONS WHERE RDB$SYSTEM_FLAG = 0;')
        relation_names = {r[0].strip() for r in fb_cursor.fetchall() if r[0]}

        _ensure_parent_dir(out_file)
        _ensure_parent_dir(conv_file)

        with open(out_file, 'w', encoding='utf-8') as f, open(conv_file, 'w', encoding='utf-8') as conv_f:
            f.write("-- ==========================================\n")
            f.write("-- FIREBIRD DOMAINS DUMP\n")
            f.write("-- ==========================================\n\n")

            conv_f.write("-- ==========================================\n")
            conv_f.write("-- POSTGRESQL DOMAINS DUMP (CONVERTED)\n")
            conv_f.write("-- ==========================================\n\n")

            for d in domains:
                domain_name = d[0].strip() if d[0] else 'UNKNOWN'
                default_source = d[6].strip() if d[6] else None
                not_null = (d[7] == 1)
                validation_source = d[8].strip() if d[8] else None

                fb_full_type = resolve_firebird_type(d[1], d[2], d[3], d[4], d[5])
                if fb_full_type is None:
                    fb_full_type = 'VARCHAR'
                # get_postgres_type maps base types (e.g. FLOAT -> REAL) and passes through
                # parameterized ones (e.g. NUMERIC(10,2), VARCHAR(20)) unchanged
                pg_type = get_postgres_type(fb_full_type)

                # Firebird DDL
                fb_ddl = f'CREATE DOMAIN "{domain_name}" AS {fb_full_type}'
                if default_source:
                    fb_ddl += f' {default_source}'
                if not_null:
                    fb_ddl += ' NOT NULL'
                if validation_source:
                    fb_ddl += f'\n{validation_source}'
                fb_ddl += ';\n'
                f.write(fb_ddl)

                # Rename domains whose final name collides with a table/view name
                # (see resolve_pg_domain_name). The same mapping is applied to the
                # columns that reference this domain.
                pg_domain_name = resolve_pg_domain_name(domain_name, relation_names)
                if pg_domain_name != domain_name.lower():
                    logger.info(f'  [RENAMED] Domain "{domain_name}" collides with a table/view name; '
                                f'exported as "{pg_domain_name}".')
                    conv_f.write(f'-- [RENAMED] DOMAIN "{domain_name}" -> "{pg_domain_name}" '
                                 f'(collides with a table/view name)\n')

                # PostgreSQL DDL: schema-qualified, lowercase-quoted identifier. Lowercase makes
                # unquoted references in transpiled PL/pgSQL bodies resolve correctly (PostgreSQL
                # folds unquoted identifiers to lowercase); quoting avoids keyword parse errors
                # (e.g. REAL, TIME); schema qualification prevents resolution to pg_catalog
                # built-in types (e.g. "time").
                #
                # The domain is created only if missing (PostgreSQL has no CREATE OR REPLACE
                # DOMAIN). Recreation with a fresh definition happens in the teardown phase
                # (drop_schema, before tables are rebuilt), because DROP DOMAIN ... CASCADE on
                # a domain still in use would drop the table columns referencing it.
                pg_domain_ident = f'public."{pg_domain_name}"'
                create_ddl = f'CREATE DOMAIN {pg_domain_ident} AS {pg_type}'
                if default_source:
                    create_ddl += f' {default_source}'
                if not_null:
                    create_ddl += ' NOT NULL'
                if validation_source:
                    check = validation_source
                    if not check.upper().startswith('CHECK'):
                        check = f'CHECK ({check})'
                    create_ddl += f'\n{check}'
                create_ddl += ';'

                escaped_name = pg_domain_name.replace("'", "''")
                escaped_ddl = create_ddl.replace("'", "''")
                pg_ddl = (
                    'DO $$\n'
                    'BEGIN\n'
                    '    IF NOT EXISTS (SELECT 1 FROM pg_type t\n'
                    '                   JOIN pg_namespace n ON n.oid = t.typnamespace\n'
                    "                   WHERE t.typtype = 'd' AND n.nspname = 'public'\n"
                    f"                     AND t.typname = '{escaped_name}') THEN\n"
                    f"        EXECUTE '{escaped_ddl}';\n"
                    '    END IF;\n'
                    'END $$;\n'
                )
                conv_f.write(pg_ddl)

        logger.info(f"Exported {len(domains)} domains to '{out_file}' and '{conv_file}'")
