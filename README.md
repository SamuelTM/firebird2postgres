# Firebird to PostgreSQL Migrator

This tool migrates the schema and the data of a Firebird database to PostgreSQL. It converts Firebird structures (domains, generators, PSQL) to native PostgreSQL features. An ANTLR-based transpiler converts triggers, stored procedures and views to PL/pgSQL.

## Features

### Schema
- Converts Firebird data types to PostgreSQL types, with `NUMERIC` precision and scale.

- Recreates user domains as PostgreSQL domains, with their `CHECK` constraints. Columns that use a domain keep the reference to it. Domain names are lowercase and schema-qualified (`public."varchar200"`). Thus keyword names (`REAL`) and unquoted references in PL/pgSQL resolve correctly.

- Detects `GEN_ID` generators in triggers and converts them to sequences with `DEFAULT nextval(...)`.

- Recreates primary keys, foreign keys, unique keys and indexes. Ignores system-generated indexes.

### Data
- Does bulk inserts with `psycopg2.extras.execute_values`.

- Decreases the batch size for tables with BLOB columns to save memory.

- Disables triggers and constraints during the load (`DISABLE TRIGGER ALL`). Thus no foreign-key sort is necessary.

- Synchronizes the sequences with `setval()` after the import.

- Removes NUL bytes from text values.

### Idempotency
- You can run the migration again at any time.

- A teardown phase drops tables, sequences and domains, in this order. Tables go first: `DROP DOMAIN ... CASCADE` on a domain in use drops the columns that reference it.

- The domains dump creates a domain only if it does not exist. The other dumps use `DROP IF EXISTS` guards.

- `TRUNCATE CASCADE` clears partial data before each import. Each table commits atomically.

### Transpilation
Each export writes two files: the Firebird source and the converted PostgreSQL DDL. If the transpiler cannot convert an object, it writes the object with a `-- [TRANSPILER FAILED]` marker for manual review.

### Validation
`validate_postgres_ddl.py` executes all converted DDL against PostgreSQL in a dry run (rollback at the end). It prints a report for each object type.

## Requirements

Python 3.10 or later.

```bash
pip install -r requirements.txt
```

## Configuration

1. Copy `.env.example` to `.env`.
2. Set the Firebird and PostgreSQL connection parameters.

## Usage

Run the migration:

```bash
python main.py
```

The pipeline does 7 steps:

1. Export and transpile the Firebird DDL (domains, triggers, procedures, views).
2. Drop the migrated objects in PostgreSQL (tables, sequences, domains).
3. Apply the domains.
4. Create the tables, sequences, keys and indexes.
5. Import the data and synchronize the sequences.
6. Apply the procedures and the views.
7. Apply the triggers.

To validate the converted DDL first (dry run, no changes):

```bash
python validate_postgres_ddl.py
```

## Limitations

- The PostgreSQL user needs sufficient rights for `ALTER TABLE ... DISABLE TRIGGER ALL`.
- A domain with the same name as a table or a view gets a `_dom` suffix. This is because each PostgreSQL relation owns a composite type with the same name.
- The migration writes to the `public` schema.
