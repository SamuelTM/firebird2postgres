# Firebird to PostgreSQL Migrator

A script designed to automatically migrate schemas and data from Firebird databases to PostgreSQL. It handles the structural complexities of Firebird (like domains and generators) and translates them seamlessly into native PostgreSQL features.

## Key Features

### Schema Migration
- **Smart Type Mapping**: Converts Firebird data types (including `NUMERIC` precision/scale) to their PostgreSQL equivalents.
- **Domain Resolution**: Correctly resolves `NOT NULL` constraints and `DEFAULT` values even when they are hidden behind Firebird's implicit system domains.
- **Auto-Increment Intelligence**: Parses Firebird triggers via regex to detect `GEN_ID` sequences and automatically ports them to native PostgreSQL Sequences (`DEFAULT nextval(...)`).
- **Constraint Parsing**: Extracts and recreates Primary Keys, Foreign Keys, Unique Keys, and standard Indexes while properly filtering out system-generated indexes to avoid duplicates.
- **View Filtering**: Skips Views during physical table extraction to prevent unwanted data duplication.

### Data Migration
- **High-Performance Bulk Inserts**: Uses `psycopg2.extras.execute_values` to ingest thousands of rows in a single network transaction.
- **Dynamic Batch Sizing**: Automatically detects heavy BLOB columns and dynamically shrinks the batch size to prevent memory exhaustion during extraction.
- **Idempotency & Atomicity**: Before importing, the script runs `TRUNCATE CASCADE` to clear partial data from previous runs. Inserts are committed atomically per table, meaning you can restart a failed migration safely at any time.
- **Constraint Bypassing**: Temporarily disables PostgreSQL triggers and constraints (`DISABLE TRIGGER ALL`) during the data load, completely eliminating the need for complex Foreign Key dependency sorting.
- **Sequence Synchronization**: Automatically runs `setval()` on all generated sequences after the data is imported, ensuring your application won't hit duplicate key errors on its next `INSERT`.
- **Data Sanitization**: Automatically scrubs NUL bytes (`\x00`) from text fields to satisfy PostgreSQL's C-string requirements.

### Logic & Business Rules Export
Firebird's PSQL and PostgreSQL's PL/pgSQL are fundamentally different. Instead of attempting risky automated translations, the script extracts your raw business logic into organized `.sql` dump files for manual translation:
- `export_firebird_triggers()` -> `firebird_triggers_dump.sql`
- `export_firebird_procedures()` -> `firebird_procedures_dump.sql`
- `export_firebird_views()` -> `firebird_views_dump.sql`

## Requirements

- Python 3.8+
- `firebirdsql` (Pure Python Firebird driver)
- `psycopg2` (PostgreSQL driver)

## Usage

1. Configure your database connections in `main.py`:
```python
fb_connection = firebirdsql.connect(
    host='localhost',
    database='/path/to/database.fdb',
    user='sysdba',
    password='masterkey',
    charset='WIN1252' # Ensures correct decoding of Latin-1 characters
)

pg_connection = psycopg2.connect(
    host='localhost',
    dbname='target_db',
    user='postgres',
    password='password'
)
```

2. Run the migration:
```python
migrator = DatabaseMigrator(fb_connection, pg_connection)

# 1. Create tables, columns, constraints, and sequences
migrator.migrate_schema(print_queries=True)

# 2. Transfer the data
migrator.import_data()

# 3. Dump business logic for manual translation
migrator.export_firebird_triggers()
migrator.export_firebird_procedures()
migrator.export_firebird_views()
```

## Known Limitations
- The script must be run with a PostgreSQL user that has Superuser privileges (or sufficient rights to execute `ALTER TABLE ... DISABLE TRIGGER ALL`).
