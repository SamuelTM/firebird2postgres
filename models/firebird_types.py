from enum import IntEnum


class FirebirdDataType(IntEnum):
    SMALLINT = 7
    INTEGER = 8
    FLOAT = 10
    DATE = 12
    TIME = 13
    CHAR = 14
    BIGINT = 16
    DOUBLE_PRECISION = 27
    TIMESTAMP = 35
    VARCHAR = 37
    BLOB = 261


_TYPE_MAP: dict[int, str] = {
    FirebirdDataType.SMALLINT: 'SMALLINT',
    FirebirdDataType.INTEGER: 'INTEGER',
    FirebirdDataType.FLOAT: 'FLOAT',
    FirebirdDataType.DATE: 'DATE',
    FirebirdDataType.TIME: 'TIME',
    FirebirdDataType.CHAR: 'CHAR',
    FirebirdDataType.BIGINT: 'BIGINT',
    FirebirdDataType.DOUBLE_PRECISION: 'DOUBLE PRECISION',
    FirebirdDataType.TIMESTAMP: 'TIMESTAMP',
    FirebirdDataType.VARCHAR: 'VARCHAR',
}


def get_firebird_data_type_name(data_type_value: int, subtype: int = None) -> str | None:
    """
    Returns the standard SQL/Firebird type name for a given Firebird data type value.
    """
    if data_type_value == FirebirdDataType.BLOB:
        return 'BLOB SUBTYPE 1' if subtype == 1 else 'BLOB SUBTYPE 0'
    return _TYPE_MAP.get(data_type_value)


def resolve_firebird_type(field_type: int, field_subtype: int = None,
                          field_length: int = None, field_precision: int = None,
                          field_scale: int = None) -> str | None:
    """
    Resolves the full Firebird type declaration for a field, column or parameter:
    NUMERIC precision/scale for integer-based numeric subtypes, and length for
    CHAR/VARCHAR. Returns the base type name otherwise (None if unknown).
    """
    type_name = get_firebird_data_type_name(field_type, field_subtype)

    if (field_type in (FirebirdDataType.SMALLINT, FirebirdDataType.INTEGER, FirebirdDataType.BIGINT)
            and field_subtype is not None and field_subtype > 0):
        if field_precision:
            scale = abs(field_scale) if field_scale else 0
            return f'NUMERIC({field_precision}, {scale})'
        return 'NUMERIC'

    if field_type in (FirebirdDataType.CHAR, FirebirdDataType.VARCHAR) and field_length:
        return f'{type_name}({field_length})'

    return type_name


def resolve_pg_domain_name(domain_name: str, relation_names: set[str]) -> str:
    """
    Resolves the final PostgreSQL name for a Firebird domain.

    Domains are created lowercase-quoted (e.g. public."varchar200") because transpiled
    PL/pgSQL bodies reference domain names unquoted, and PostgreSQL folds unquoted
    identifiers to lowercase. Quoting avoids keyword parse errors (e.g. REAL, TIME).

    Every PostgreSQL table/view implicitly owns a composite type with the exact same
    (case-sensitive) name, so in the unlikely case of an exact-case collision with a
    relation, the domain is renamed with a '_dom' suffix.
    """
    pg_name = domain_name.lower()
    lower_relations = {r.lower() for r in relation_names}
    while pg_name in lower_relations:
        pg_name = f'{pg_name}_dom'
    return pg_name


def decode_trigger_type(trigger_type: int) -> str:
    """
    Decodes Firebird's RDB$TRIGGER_TYPE into a human-readable timing + events string.

    Firebird encodes trigger types as:
        stored_type = (phase | (slot1 << 1) | (slot2 << 3) | (slot3 << 5)) - 1
    Where phase: 0=BEFORE, 1=AFTER; slots: 1=INSERT, 2=UPDATE, 3=DELETE.
    """
    event_names = {1: 'INSERT', 2: 'UPDATE', 3: 'DELETE'}

    raw = trigger_type + 1
    phase = 'BEFORE' if (raw & 1) == 0 else 'AFTER'
    events = []
    for shift in (1, 3, 5):
        slot = (raw >> shift) & 0b11
        if slot > 0:
            events.append(event_names.get(slot, f'UNKNOWN({slot})'))

    if not events:
        return f'/* UNKNOWN TYPE {trigger_type} */'

    return f'{phase} {" OR ".join(events)}'
