from models import Table
from transpiler import FirebirdToPostgresVisitor
from utils import SqlRunner
from .schema_extractor import SchemaExtractor
from .schema_migrator import SchemaMigrator
from .data_migrator import DataMigrator
from .ddl_exporter import DdlExporter


class DatabaseMigrator:
    """
    Facade orchestrating the migration lifecycle between Firebird and PostgreSQL.
    Delegates specialized tasks to SchemaExtractor, SchemaMigrator, DataMigrator,
    DdlExporter, and SqlRunner.
    """

    def __init__(self, fb_con, pg_con):
        """
        Initializes the migrator with live connection objects to Firebird and PostgreSQL.
        """
        self.fb_con = fb_con
        self.pg_con = pg_con
        self.table_objs: list[Table] = []

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
        self.schema_migrator.drop_schema(self.table_objs)

    def migrate_schema(self):
        """
        Executes the generated PostgreSQL DDL to create the tables, sequences, indexes, and keys.
        """
        self._ensure_schema()
        self.schema_migrator.migrate_schema(self.table_objs)

    def import_data(self) -> bool:
        """
        Reads data from Firebird and bulk inserts into PostgreSQL with sequence synchronization.
        Returns True if successful, False if any table failed.
        """
        self._ensure_schema()
        return self.data_migrator.import_data(self.table_objs)

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

    def export_all_firebird_ddl(self, output_dir: str = None):
        """
        Exports all Firebird domains, triggers, procedures, and views using a single shared
        ProcessPoolExecutor to the specified output directory (default configured in config.DUMP_DIR).
        """
        self.ddl_exporter.export_all_firebird_ddl(output_dir=output_dir)

    def apply_sql_file(self, file_path: str, continue_on_error: bool = False) -> int:
        """
        Executes a PostgreSQL SQL file against the connected database.
        """
        return self.sql_runner.apply_file(file_path, continue_on_error=continue_on_error)
