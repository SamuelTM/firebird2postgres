# Firebird to PostgreSQL Migrator

This tool migrates the schema and the data of a Firebird database to PostgreSQL.
It converts Firebird structures (domains, generators, PSQL) to native PostgreSQL features.
An ANTLR-based transpiler converts triggers, stored procedures and views to PL/pgSQL.

## Features

### Schema Conversion

- Converts Firebird data types to PostgreSQL types. Keeps `NUMERIC` precision and scale.

- Recreates user domains as PostgreSQL domains with their `CHECK` constraints. Columns that use a domain keep the reference.

- Qualifies domain names with `public.` and applies lowercase (e.g. `public."varchar200"`). This prevents conflicts with reserved words such as `REAL`.

- If a domain has the same name as a table or a view, the tool adds a `_dom` suffix. PostgreSQL requires this because each relation has a composite type with the same name.

- Detects `GEN_ID` generators in triggers and converts them to sequences with `DEFAULT nextval(...)`.

- Recreates primary keys, foreign keys, unique keys and indexes. Ignores system-generated indexes.

### Data Import

- Uses multi-process parallel workers to import tables at the same time. Each worker process opens its own database connections. This bypasses the Python GIL and uses all CPU cores.

- Sorts tables by workload before the import starts (LPT scheduling). Tables with BLOB columns and more columns start first.

- Does bulk inserts with `psycopg2.extras.execute_values`.

- Adjusts the batch size for tables with BLOB columns to save memory.

- Disables triggers during the load (`DISABLE TRIGGER ALL`). No foreign-key sort is necessary.

- Removes NUL bytes (`\x00`) from text values.

- Synchronizes all sequences with `setval()` after the import.

### Transpiler

- An ANTLR4 parser reads the Firebird PSQL grammar and builds a syntax tree.

- A visitor walks the tree and generates the equivalent PL/pgSQL code.

- Each export writes two SQL files: the original Firebird source and the converted PostgreSQL DDL.

- If the transpiler cannot convert an object, it writes a `-- [TRANSPILER FAILED]` marker for manual review.

- The transpiler runs in a `ProcessPoolExecutor` for parallel conversion.

### Idempotency

- You can run the migration again at any time.

- A teardown step drops tables, sequences and domains, in this order. Tables go first: `DROP DOMAIN CASCADE` on a domain in use drops the columns that reference it.

- The domain dump creates a domain only if it does not exist. The other dumps use `DROP IF EXISTS` guards.

- Each table import does `TRUNCATE` to clear old data before insert. Each table commits separately.

### Validation

`validate_postgres_ddl.py` is an optional script that runs all converted DDL against PostgreSQL in a dry run (rollback at the end).
It shows a report for each object type (domains, procedures, views, triggers).

## Requirements

- Python 3.10 or later.

- Access to a Firebird database (source) and a PostgreSQL database (target).

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

1. Copy `.env.example` to `.env`.
2. Set the Firebird and PostgreSQL connection parameters in `.env`.

## Usage

### Run the Migration

```bash
python main.py
```

The pipeline has 8 steps:

1. **Export and transpile DDL** - Reads domains, triggers, procedures and views from Firebird. Writes the Firebird source and the converted PostgreSQL DDL to SQL files.

2. **Drop existing objects** - Drops tables, sequences and domains in PostgreSQL.

3. **Apply domains** - Creates the PostgreSQL domains.

4. **Create tables and sequences** - Creates base tables and sequences without constraints or indexes.

5. **Import data** - Imports all table data in parallel and synchronizes sequences.

6. **Create constraints and indexes** - Creates primary keys, unique keys, foreign keys and secondary indexes.

7. **Apply procedures and views** - Runs the converted procedure and view DDL.

8. **Apply triggers** - Runs the converted trigger DDL.

### Run the Tests

```bash
pytest
```

## Limitations

- The PostgreSQL user must have sufficient privileges for `ALTER TABLE ... DISABLE TRIGGER ALL`.

- The tool writes all objects to the `public` schema.

- The transpiler is still a work in progress, it may not support all Firebird PSQL constructs. Objects that fail get a `[TRANSPILER FAILED]` marker in the output file.

## License

MIT - see [LICENSE](LICENSE).
