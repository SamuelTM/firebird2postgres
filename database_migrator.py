from database_objects import Table
from firebird_visitor import FirebirdToPostgresVisitor
from schema_extractor import SchemaExtractor
from schema_migrator import SchemaMigrator
from data_migrator import DataMigrator
from ddl_exporter import DdlExporter
from sql_runner import SqlRunner


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

    def drop_schema(self, print_queries: bool = False):
        """
        Drops all migrated objects (tables, sequences and domains) from PostgreSQL.
        """
        self._ensure_schema()
        self.schema_migrator.drop_schema(self.table_objs, print_queries=print_queries)

    def migrate_schema(self, print_queries: bool = False):
        """
        Executes the generated PostgreSQL DDL to create the tables, sequences, indexes, and keys.
        """
        self._ensure_schema()
        self.schema_migrator.migrate_schema(self.table_objs, print_queries=print_queries)

    def import_data(self):
        """
        Reads data from Firebird and bulk inserts into PostgreSQL with sequence synchronization.
        """
        self._ensure_schema()
        self.data_migrator.import_data(self.table_objs)

    def export_firebird_triggers(self, output_file: str = 'firebird_triggers_dump.sql',
                                 converted_file: str = 'postgres_triggers_dump.sql',
                                 executor=None, chunksize: int = 4):
        self.ddl_exporter.export_firebird_triggers(output_file, converted_file, executor, chunksize)

    def export_firebird_procedures(self, output_file: str = 'firebird_procedures_dump.sql',
                                   converted_file: str = 'postgres_procedures_dump.sql',
                                   executor=None, chunksize: int = 4):
        self.ddl_exporter.export_firebird_procedures(output_file, converted_file, executor, chunksize)

    def export_firebird_views(self, output_file: str = 'firebird_views_dump.sql',
                              converted_file: str = 'postgres_views_dump.sql',
                              executor=None, chunksize: int = 4):
        self.ddl_exporter.export_firebird_views(output_file, converted_file, executor, chunksize)

    def export_firebird_domains(self, output_file: str = 'firebird_domains_dump.sql',
                                converted_file: str = 'postgres_domains_dump.sql'):
        self.ddl_exporter.export_firebird_domains(output_file, converted_file)

    def export_all_firebird_ddl(self):
        """
        Exports all Firebird domains, triggers, procedures, and views using a single shared
        ProcessPoolExecutor.
        """
        self.ddl_exporter.export_all_firebird_ddl()

    def apply_sql_file(self, file_path: str, continue_on_error: bool = False) -> int:
        """
        Executes a PostgreSQL SQL file against the connected database.
        """
        return self.sql_runner.apply_file(file_path, continue_on_error=continue_on_error)
