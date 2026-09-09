import logging

from models import Table, Sequence
from transpiler import FirebirdToPostgresVisitor
from utils import SqlRunner
from .schema_extractor import SchemaExtractor
from .schema_migrator import SchemaMigrator
from .data_migrator import DataMigrator
from .ddl_exporter import DdlExporter

logger = logging.getLogger(__name__)


class DatabaseMigrator:
    """
    Facade orchestrating the migration lifecycle between Firebird and PostgreSQL.
    Delegates specialized tasks to SchemaExtractor, SchemaMigrator, DataMigrator,
    DdlExporter, and SqlRunner.
    """

    def __init__(self, fb_con, pg_con, config=None):
        """
        Initializes the migrator with live connection objects to Firebird and PostgreSQL.
        """
        from config import MigrationConfig
        self.fb_con = fb_con
        self.pg_con = pg_con
        self.config = config or MigrationConfig()
        self.table_objs: list[Table] = []
        self.sequence_objs: list[Sequence] = []
        self.verified_empty: dict[str, bool] = {}

        self.extractor = SchemaExtractor(fb_con)
        self.schema_migrator = SchemaMigrator(pg_con)
        self.data_migrator = DataMigrator(fb_con, pg_con)
        self.ddl_exporter = DdlExporter(fb_con)
        self.sql_runner = SqlRunner(pg_con)

    def _extract_schema(self):
        """
        Extracts the DDL schema from Firebird system tables into memory.
        """
        self.table_objs = self.extractor.extract_schema()
        self.sequence_objs = self.extractor.extract_sequences()

    def _ensure_schema(self):
        if not self.table_objs:
            self._extract_schema()

    @staticmethod
    def transpile_firebird_sql(firebird_sql_string: str) -> str:
        return FirebirdToPostgresVisitor.transpile(firebird_sql_string)

    def drop_schema(self):
        """
        Drops all migrated objects (tables, sequences and domains) from PostgreSQL.
        """
        self._ensure_schema()
        self.schema_migrator.drop_schema(self.table_objs, self.sequence_objs)

    def create_tables(self):
        """
        Executes the generated PostgreSQL DDL to create base tables and sequences (without constraints/indexes).
        """
        self._ensure_schema()
        self.schema_migrator.create_tables(self.table_objs, self.sequence_objs)

    def create_constraints_and_indexes(self):
        """
        Executes the generated PostgreSQL DDL to create Unique/Primary Keys, Secondary Indexes, and Foreign Keys.
        """
        self._ensure_schema()
        self.schema_migrator.create_constraints_and_indexes(self.table_objs)

    def migrate_schema(self):
        """
        Executes the generated PostgreSQL DDL to create the tables, sequences, indexes, and keys.
        """
        self._ensure_schema()
        self.schema_migrator.migrate_schema(self.table_objs, self.sequence_objs)

    def analyze_tables(self):
        """
        Updates PostgreSQL optimizer statistics by running ANALYZE on migrated tables.
        """
        self._ensure_schema()
        self.schema_migrator.analyze_tables(self.table_objs)

    def check_source_consistency(self, require_frozen: bool = None, allow_live_source: bool = None) -> dict:
        """
        Verifies source database consistency and freeze state before export and destructive operations.
        Defaults require_frozen to MigrationConfig.require_frozen_source (True).
        Defaults allow_live_source to MigrationConfig.allow_live_source (False).
        """
        req_frozen = self.config.require_frozen_source if require_frozen is None else require_frozen
        allow_live = self.config.allow_live_source if allow_live_source is None else allow_live_source
        return self.data_migrator.check_source_consistency(
            require_frozen=req_frozen,
            allow_live_source=allow_live
        )

    def _get_blob_domains(self) -> set[str]:
        """
        Retrieves user domains that are based on BLOB types (RDB$FIELD_TYPE = 261).
        """
        blob_domains = set()
        if not self.fb_con:
            return blob_domains
        try:
            cur = self.fb_con.cursor()
            cur.execute("""
                SELECT DISTINCT RDB$FIELD_NAME
                FROM RDB$FIELDS
                WHERE RDB$SYSTEM_FLAG = 0
                  AND RDB$FIELD_NAME NOT STARTING WITH 'RDB$'
                  AND (RDB$FIELD_TYPE = 261 OR RDB$CHARACTER_SET_ID = 1)
            """)
            rows = cur.fetchall()
            for r in rows:
                if r and r[0]:
                    name = r[0].strip()
                    blob_domains.add(name)
                    blob_domains.add(name.upper())
                    blob_domains.add(name.lower())
        except Exception as e:
            logger.warning(f"Could not retrieve BLOB domains from Firebird catalog: {e}")
        return blob_domains

    def _get_binary_domains(self) -> set[str]:
        """
        Retrieves user domains that represent binary data (BYTEA):
        Firebird BLOBs with SUBTYPE != 1 (binary BLOB) or CHARACTER SET OCTETS.
        """
        binary_domains = set()
        if not self.fb_con:
            return binary_domains
        try:
            cur = self.fb_con.cursor()
            cur.execute("""
                SELECT DISTINCT RDB$FIELD_NAME, RDB$FIELD_SUB_TYPE, RDB$CHARACTER_SET_ID, RDB$FIELD_TYPE
                FROM RDB$FIELDS
                WHERE RDB$SYSTEM_FLAG = 0
                  AND RDB$FIELD_NAME NOT STARTING WITH 'RDB$'
                  AND (
                      (RDB$FIELD_TYPE = 261 AND COALESCE(RDB$FIELD_SUB_TYPE, 0) != 1)
                      OR RDB$CHARACTER_SET_ID = 1
                  )
            """)
            rows = cur.fetchall()
            for r in rows:
                if r and r[0]:
                    name = r[0].strip()
                    binary_domains.add(name)
                    binary_domains.add(name.upper())
                    binary_domains.add(name.lower())
        except Exception as e:
            logger.warning(f"Could not retrieve binary domains from Firebird catalog: {e}")
        return binary_domains

    def import_data(
        self,
        max_workers: int = 4,
        require_frozen_source: bool = None,
        allow_live_source: bool = None,
        total_memory_budget: int = None,
        per_worker_budget: int = None,
        max_blob_bytes: int = None,
        blob_domains: set[str] = None,
        binary_domains: set[str] = None
    ) -> bool:
        """
        Imports data from Firebird to PostgreSQL using parallel worker pool.
        Enforces memory budgets per worker and overall, and streaming BLOB constraints.
        Returns True if successful, False if any table failed.
        """
        self._ensure_schema()
        req_frozen = self.config.require_frozen_source if require_frozen_source is None else require_frozen_source
        allow_live = self.config.allow_live_source if allow_live_source is None else allow_live_source

        tot_budget = getattr(self.config, 'total_memory_budget_bytes', None) if total_memory_budget is None else total_memory_budget
        worker_budget = getattr(self.config, 'max_buffer_bytes_per_worker', None) if per_worker_budget is None else per_worker_budget
        blob_limit = getattr(self.config, 'max_blob_bytes', None) if max_blob_bytes is None else max_blob_bytes

        domains = blob_domains if blob_domains is not None else self._get_blob_domains()
        bin_domains = binary_domains if binary_domains is not None else self._get_binary_domains()

        return self.data_migrator.import_data(
            self.table_objs,
            max_workers=max_workers,
            require_frozen_source=req_frozen,
            allow_live_source=allow_live,
            total_memory_budget=tot_budget,
            per_worker_budget=worker_budget,
            max_blob_bytes=blob_limit,
            blob_domains=domains,
            binary_domains=bin_domains
        )

    def export_firebird_triggers(self, output_file: str = None,
                                 converted_file: str = None,
                                 executor=None, chunksize: int = 4):
        self.ddl_exporter.export_firebird_triggers(output_file, converted_file, executor, chunksize)

    def export_firebird_procedures(self, output_file: str = None,
                                   converted_file: str = None,
                                   executor=None, chunksize: int = 4):
        self.ddl_exporter.export_firebird_procedures(output_file, converted_file, executor, chunksize)

    def export_firebird_views(self, output_file: str = None,
                              converted_file: str = None,
                              executor=None, chunksize: int = 4):
        self.ddl_exporter.export_firebird_views(output_file, converted_file, executor, chunksize)

    def export_firebird_domains(self, output_file: str = None,
                                converted_file: str = None):
        self.ddl_exporter.export_firebird_domains(output_file, converted_file)

    def export_firebird_generators(self, output_file: str = None,
                                   converted_file: str = None):
        self.ddl_exporter.export_firebird_generators(output_file, converted_file)


    def export_all_firebird_ddl(self, output_dir: str = None) -> dict[str, int]:
        """
        Exports all Firebird domains, triggers, procedures, and views using a single shared
        ProcessPoolExecutor to the specified output directory (default configured in config.DUMP_DIR).
        Returns a dict of exported object counts per category.
        """
        return self.ddl_exporter.export_all_firebird_ddl(output_dir=output_dir)

    def _get_domain_name_mapping(self) -> dict[str, str]:
        """
        Returns the exact source->defined domain name mapping (both uppercase)
        computed from the source catalog with build_domain_mapping, so renamed
        domains (table/view collisions) validate by identity instead of fuzzy
        suffix stripping. Returns {} when no source connection is available,
        falling back to exact matching. Catalog errors propagate: an
        unverifiable mapping must never approve a dump.
        """
        if self.fb_con is None:
            return {}
        raw = DdlExporter._fetch_domain_map(self.fb_con.cursor())
        return {str(src).upper(): str(pg).upper() for src, pg in raw.items()}

    def validate_artifacts(self, output_dir: str = None,
                           expected_counts: dict[str, int] = None,
                           expected_objects: dict[str, list[str] | set[str]] = None) -> dict[str, bool]:
        """
        Validates that all expected DDL artifact files exist and are complete
        BEFORE dropping the destination database.
        Checks objects by identity and type against source database catalog.
        Returns a dict mapping filename -> allow_empty (True if legitimately 0 objects).
        Raises FileNotFoundError or ValueError if any artifact is missing, truncated,
        or missing expected objects. Catalog query errors propagate and prevent approval.
        """
        from config import DumpFiles, get_dump_path

        target_files = [
            DumpFiles.DOMAINS_PG,
            DumpFiles.PROCEDURES_PG,
            DumpFiles.VIEWS_PG,
            DumpFiles.TRIGGERS_PG,
        ]

        category_types = {
            DumpFiles.DOMAINS_PG: 'DOMAIN',
            DumpFiles.PROCEDURES_PG: 'PROCEDURE',
            DumpFiles.VIEWS_PG: 'VIEW',
            DumpFiles.TRIGGERS_PG: 'TRIGGER',
        }

        # If neither expected_objects nor expected_counts passed, query catalog for objects
        if expected_objects is None and expected_counts is None:
            expected_objects = self.ddl_exporter.get_source_objects()

        domain_mapping: dict[str, str] | None = None

        verified_empty = {}
        for fname in target_files:
            file_path = get_dump_path(fname, output_dir)
            cat_type = category_types.get(fname)

            if expected_objects is not None:
                exp_objs = expected_objects.get(fname, [])
                if isinstance(exp_objs, int):
                    allow_empty = (exp_objs == 0)
                    self.sql_runner.validate_file(
                        file_path,
                        expected_count=exp_objs,
                        allow_empty=allow_empty,
                        object_type=cat_type
                    )
                else:
                    allow_empty = (len(exp_objs) == 0)
                    name_mapping = None
                    if fname == DumpFiles.DOMAINS_PG and len(exp_objs) > 0:
                        if domain_mapping is None:
                            domain_mapping = self._get_domain_name_mapping()
                        name_mapping = domain_mapping
                    self.sql_runner.validate_file(
                        file_path,
                        expected_objects=exp_objs,
                        allow_empty=allow_empty,
                        object_type=cat_type,
                        name_mapping=name_mapping
                    )
            elif expected_counts is not None:
                exp_val = expected_counts.get(fname, 0)
                if isinstance(exp_val, (list, set, tuple)):
                    allow_empty = (len(exp_val) == 0)
                    name_mapping = None
                    if fname == DumpFiles.DOMAINS_PG and len(exp_val) > 0:
                        if domain_mapping is None:
                            domain_mapping = self._get_domain_name_mapping()
                        name_mapping = domain_mapping
                    self.sql_runner.validate_file(
                        file_path,
                        expected_objects=exp_val,
                        allow_empty=allow_empty,
                        object_type=cat_type,
                        name_mapping=name_mapping
                    )
                else:
                    allow_empty = (exp_val == 0)
                    self.sql_runner.validate_file(
                        file_path,
                        expected_count=exp_val,
                        allow_empty=allow_empty,
                        object_type=cat_type
                    )

            verified_empty[fname] = allow_empty

        self.verified_empty = verified_empty
        return verified_empty

    def is_category_empty(self, filename: str) -> bool:
        """
        Returns True if the category corresponding to filename was verified as legitimately empty.
        """
        return self.verified_empty.get(filename, False)

    def inventory_unsupported_objects(self) -> dict[str, list[str]]:
        """
        Returns an inventory of Firebird objects requiring manual migration.
        """
        return self.ddl_exporter.inventory_unsupported_objects()

    def apply_sql_file(self, file_path: str, continue_on_error: bool = False,
                       allow_empty: bool = None, expected_count: int = None) -> int:
        """
        Executes a PostgreSQL SQL file against the connected database.
        If allow_empty is None, checks verified category status from validate_artifacts.
        """
        if allow_empty is None:
            import os
            basename = os.path.basename(file_path)
            allow_empty = self.verified_empty.get(basename, False)

        return self.sql_runner.apply_file(
            file_path,
            continue_on_error=continue_on_error,
            allow_empty=allow_empty,
            expected_count=expected_count
        )
