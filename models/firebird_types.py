from collections.abc import Iterable
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
                          field_scale: int = None, character_length: int = None) -> str | None:
    """
    Resolves the full Firebird type declaration for a field, column or parameter:
    NUMERIC precision/scale for integer-based numeric subtypes, and length for
    CHAR/VARCHAR (prefers character_length over byte field_length).
    Returns the base type name otherwise (None if unknown).
    """
    type_name = get_firebird_data_type_name(field_type, field_subtype)

    if (field_type in (FirebirdDataType.SMALLINT, FirebirdDataType.INTEGER, FirebirdDataType.BIGINT)
            and field_subtype is not None and field_subtype > 0):
        if field_precision:
            scale = abs(field_scale) if field_scale else 0
            return f'NUMERIC({field_precision}, {scale})'
        return 'NUMERIC'

    eff_length = character_length or field_length
    if field_type in (FirebirdDataType.CHAR, FirebirdDataType.VARCHAR) and eff_length:
        return f'{type_name}({eff_length})'

    return type_name


def resolve_pg_domain_name(domain_name: str, relation_names: set[str], allocated_names: set[str] | None = None) -> str:
    """
    Resolves the final PostgreSQL name for a Firebird domain.

    Domains are created lowercase-quoted (e.g. public."varchar200") because transpiled
    PL/pgSQL bodies reference domain names unquoted, and PostgreSQL folds unquoted
    identifiers to lowercase. Quoting avoids keyword parse errors (e.g. REAL, TIME).

    Every PostgreSQL table/view implicitly owns a composite type with the exact same
    (case-sensitive) name, so in the case of a collision with a relation or an already
    allocated domain name, the domain is renamed with a '_dom' suffix.
    """
    pg_name = domain_name.lower()
    lower_relations = {r.lower() for r in relation_names}
    lower_allocated = {a.lower() for a in allocated_names} if allocated_names else set()
    while pg_name in lower_relations or pg_name in lower_allocated:
        pg_name = f'{pg_name}_dom'
    if allocated_names is not None:
        allocated_names.add(pg_name)
    return pg_name


def build_domain_mapping(domain_names: Iterable[str], relation_names: set[str]) -> dict[str, str]:
    """
    Builds a collision-free mapping from Firebird domain name (case-insensitive) to PostgreSQL domain name.
    1. Domains that do not collide with table/view names keep their lowercase name (unless duplicated).
    2. Domains that collide with table/view names (or other domains) receive unique suffixed names.
    """
    relation_set = {r.lower() for r in relation_names}
    mapping: dict[str, str] = {}
    allocated: set[str] = set()

    clean_domains = [d.strip() for d in domain_names if d and d.strip()]

    # Pass 1: Original names that don't collide with relations
    for d in clean_domains:
        d_upper = d.upper()
        d_lower = d.lower()
        if d_lower not in relation_set and d_lower not in allocated:
            mapping[d_upper] = d_lower
            allocated.add(d_lower)

    # Pass 2: Domains that collide with relations or other domains
    for d in clean_domains:
        d_upper = d.upper()
        if d_upper in mapping:
            continue
        d_lower = d.lower()
        cand = f"{d_lower}_dom"
        while cand in relation_set or cand in allocated:
            cand = f"{cand}_dom"
        mapping[d_upper] = cand
        allocated.add(cand)

    return mapping


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
