"""Shared helpers for generated API reference table data."""

from __future__ import annotations

import inspect
from collections.abc import Iterable, Mapping, MutableMapping
from typing import NamedTuple, TypeVar

_API_SYMBOL_FIELD = "symbol"
_API_SYMBOL_VALUE_FIELD = "value"
API_SYMBOL_FIELDS = (
    _API_SYMBOL_FIELD,
    "kind",
    "layer",
    "module",
    "feature",
    "import_path",
    "returns",
    _API_SYMBOL_VALUE_FIELD,
    "registry_seam",
    "surface",
    "doc_page",
    "test_anchor",
)
_API_TABLE_SCHEMA_FIELD = "schema"
_API_TABLE_ROW_COUNT_FIELD = "row_count"
_API_TABLE_ROWS_FIELD = "rows"
_API_TABLE_INDEX_SUFFIX = "_index"
_API_TABLE_PAYLOAD_FIELDS = (
    _API_TABLE_SCHEMA_FIELD,
    _API_TABLE_ROW_COUNT_FIELD,
    _API_TABLE_ROWS_FIELD,
)

IndexKey = TypeVar("IndexKey")
OuterIndexKey = TypeVar("OuterIndexKey")
IndexValue = TypeVar("IndexValue")
Index = MutableMapping[IndexKey, list[IndexValue]]
NestedIndex = MutableMapping[OuterIndexKey, Index[IndexKey, IndexValue]]
ApiIndex = MutableMapping[str, list[str]]
ApiNestedIndex = MutableMapping[str, ApiIndex]
ApiTablePayload = dict[str, object]
ApiTableRow = Mapping[str, object]
ApiTableRowPayload = dict[str, object]
ApiTableRows = Iterable[ApiTableRow]


class ApiIndexSpec(NamedTuple):
    index_name: str
    field: str


API_STANDARD_INDEXES: tuple[ApiIndexSpec, ...] = (
    ApiIndexSpec("module_index", "module"),
    ApiIndexSpec("feature_index", "feature"),
    ApiIndexSpec("kind_index", "kind"),
)


def append_index_entry(index: Index[IndexKey, IndexValue], key: IndexKey, value: IndexValue) -> None:
    """Append one value to a typed index bucket."""

    index.setdefault(key, []).append(value)


def append_nested_index_entry(
    index: NestedIndex[OuterIndexKey, IndexKey, IndexValue],
    outer_key: OuterIndexKey,
    key: IndexKey,
    value: IndexValue,
) -> None:
    """Append one value to a typed nested index bucket."""

    append_index_entry(index.setdefault(outer_key, {}), key, value)


def append_api_index_entry(index: ApiIndex, key: object, value: object) -> None:
    """Append one value to an API reference index bucket."""

    append_index_entry(index, str(key), str(value))


def append_api_nested_index_entry(index: ApiNestedIndex, outer_key: object, key: object, value: object) -> None:
    """Append one value to a nested API reference index bucket."""

    append_api_index_entry(index.setdefault(str(outer_key), {}), key, value)


def api_symbol_indexes(
    rows: ApiTableRows,
    *fields: str,
    symbol_field: str = _API_SYMBOL_FIELD,
    list_fields: Iterable[str] = (),
    skip_empty_fields: Iterable[str] = (),
) -> tuple[dict[str, list[str]], ...]:
    """Return symbol indexes for API table rows keyed by the requested fields."""

    return api_value_indexes(
        rows,
        *fields,
        value_field=symbol_field,
        list_fields=list_fields,
        skip_empty_fields=skip_empty_fields,
    )


def api_standard_table(schema: str, rows: ApiTableRows) -> ApiTablePayload:
    """Return a detached API-standard symbol table payload."""

    copied_rows = [copy_api_symbol_row(row) for row in _api_row_list(rows, label="API table rows")]
    return api_indexed_table(schema, copied_rows, API_STANDARD_INDEXES)


def api_indexed_table(
    schema: str,
    rows: ApiTableRows,
    indexes: Iterable[ApiIndexSpec],
    *,
    value_field: str = _API_SYMBOL_FIELD,
    index_list_fields: Iterable[str] = (),
    index_skip_empty_fields: Iterable[str] = (),
    row_list_fields: Iterable[str] = (),
) -> ApiTablePayload:
    """Return a detached API table payload with named indexes."""

    row_list = _api_row_list(rows, label="API table rows")
    index_list = _api_index_specs(indexes)
    payload = _api_table_payload(schema, len(row_list))
    index_values = api_value_indexes(
        row_list,
        *_api_index_fields(index_list),
        value_field=value_field,
        list_fields=index_list_fields,
        skip_empty_fields=index_skip_empty_fields,
    )
    for spec, index in zip(index_list, index_values):
        payload[spec.index_name] = index
    payload[_API_TABLE_ROWS_FIELD] = [copy_api_row(row, list_fields=row_list_fields) for row in row_list]
    return payload


def api_table_index_names(table: ApiTableRow) -> list[str]:
    """Return ordered index payload names from an API table."""

    table_map = _api_row_mapping(table, label="API table")
    return [key for key, value in table_map.items() if key.endswith(_API_TABLE_INDEX_SUFFIX) and isinstance(value, Mapping)]


def api_table_row(
    table: ApiTableRow,
    key_field: str,
    key: str,
    *,
    row_list_fields: Iterable[str] = (),
) -> ApiTableRowPayload:
    """Return one detached API table row by a selected row key field."""

    table_map = _api_row_mapping(table, label="API table")
    field_name = _api_name(key_field, label="API table row key field")
    key_name = _api_name(key, label="API table row key")
    rows = _api_row_list(_api_row_value(table_map, _API_TABLE_ROWS_FIELD), label="API table rows")
    choices: list[str] = []
    for row in rows:
        row_key = str(_api_row_value(row, field_name))
        choices.append(row_key)
        if row_key == key_name:
            return copy_api_row(row, list_fields=row_list_fields)
    raise KeyError(f"unknown API table {field_name} {key_name!r}; expected one of: {', '.join(choices)}")


def api_table_index_values(
    table: ApiTableRow,
    index_name: str,
    key: str,
    *,
    index_names: Iterable[str] | None = None,
) -> list[str]:
    """Return one detached value list from an API table index."""

    table_map = _api_row_mapping(table, label="API table")
    selected_index = _api_name(index_name, label="API table index")
    key_name = _api_name(key, label="API table index key")
    supported_indexes = api_table_index_names(table_map) if index_names is None else _api_name_list(index_names, label="API table indexes")
    if selected_index not in supported_indexes:
        raise ValueError(f"unsupported API table index {selected_index!r}; expected one of: {', '.join(supported_indexes)}")
    index = _api_row_mapping(_api_row_value(table_map, selected_index), label=f"API table index {selected_index!r}")
    try:
        return _api_name_list(index[key_name], label=f"API table index {selected_index!r} values")
    except KeyError as error:
        raise ValueError(f"unknown API table {selected_index} key {key_name!r}; expected one of: {', '.join(index)}") from error


def api_table_selection(
    table: ApiTableRow,
    *,
    row_key_field: str = _API_SYMBOL_FIELD,
    row_key: str | None = None,
    index_name: str | None = None,
    key: str | None = None,
    row_list_fields: Iterable[str] = (),
    index_names: Iterable[str] | None = None,
) -> ApiTablePayload | ApiTableRowPayload | list[str]:
    """Return an API table, one row, or one index projection."""

    field_name = _api_name(row_key_field, label="API table row key field")
    index_lookup = index_name is not None or key is not None
    if row_key is not None and index_lookup:
        raise ValueError(f"Pass only one API table selector: {field_name} or index_name/key.")
    if index_lookup and (index_name is None or key is None):
        raise ValueError("index_name requires key, and key requires index_name.")
    if row_key is not None:
        return api_table_row(table, field_name, row_key, row_list_fields=row_list_fields)
    if index_name is not None and key is not None:
        return api_table_index_values(table, index_name, key, index_names=index_names)
    return _api_table_copy(table, row_list_fields=row_list_fields)


def _api_table_copy(
    table: ApiTableRow,
    *,
    row_list_fields: Iterable[str] = (),
) -> ApiTablePayload:
    table_map = _api_row_mapping(table, label="API table")
    index_names = set(api_table_index_names(table_map))
    copied: ApiTablePayload = {}
    for field, value in table_map.items():
        if field == _API_TABLE_ROWS_FIELD:
            copied[field] = [copy_api_row(row, list_fields=row_list_fields) for row in _api_row_list(value, label="API table rows")]
        elif field in index_names:
            copied[field] = _api_table_copy_index(field, value)
        else:
            copied[field] = value
    return copied


def _api_table_copy_index(field: str, value: object) -> dict[str, list[str]]:
    index = _api_row_mapping(value, label=f"API table index {field!r}")
    return {str(key): _api_name_list(values, label=f"API table index {field!r} values") for key, values in index.items()}


def _api_table_payload(schema: object, row_count: int) -> ApiTablePayload:
    return {
        _API_TABLE_SCHEMA_FIELD: _api_name(schema, label="API table schema"),
        _API_TABLE_ROW_COUNT_FIELD: row_count,
    }


def _api_index_specs(indexes: Iterable[ApiIndexSpec]) -> list[ApiIndexSpec]:
    index_list = [_api_index_spec(spec) for spec in _api_list_items(indexes, label="API table indexes")]
    _api_validate_index_names(index_list)
    return index_list


def _api_index_fields(indexes: Iterable[ApiIndexSpec]) -> tuple[str, ...]:
    return tuple(spec.field for spec in indexes)


def _api_index_spec(spec: object) -> ApiIndexSpec:
    values = _api_name_list(spec, label="API table index spec")
    if len(values) != 2:
        raise ValueError(f"API table index spec must contain 2 values, not {len(values)}")
    return ApiIndexSpec(values[0], values[1])


def _api_validate_index_names(indexes: Iterable[ApiIndexSpec]) -> None:
    seen: set[str] = set()
    reserved = set(_API_TABLE_PAYLOAD_FIELDS)
    for spec in indexes:
        if spec.index_name in reserved:
            raise ValueError(f"API table index {spec.index_name!r} is reserved")
        if spec.index_name in seen:
            raise ValueError(f"duplicate API table index {spec.index_name!r}")
        seen.add(spec.index_name)


def copy_api_symbol_row(row: ApiTableRow) -> ApiTableRowPayload:
    """Return one detached API-standard symbol row with canonical fields."""

    return copy_api_row(row, API_SYMBOL_FIELDS)


def copy_api_row(
    row: ApiTableRow,
    fields: Iterable[str] | None = None,
    *,
    list_fields: Iterable[str] = (),
) -> ApiTableRowPayload:
    """Return one detached API table row, copying mutable list fields."""

    row_map = _api_row_mapping(row, label="API table row")
    list_names = _api_name_set(list_fields, label="API table list fields")
    field_names = row_map if fields is None else _api_name_list(fields, label="API table row fields")
    copied: dict[str, object] = {}
    for field in field_names:
        copied[field] = _api_row_payload_value(row_map, field, list_names)
    return copied


def api_annotation_text(
    value: object,
    *,
    strip_string_quotes: bool = False,
    prefer_builtins_qualname: bool = False,
    use_name: bool = True,
    drop_collections_abc: bool = False,
) -> str:
    """Return a stable API-reference label for a Python annotation."""

    if value is inspect.Signature.empty:
        return ""
    if isinstance(value, str):
        return value.strip("'\"") if strip_string_quotes else value
    if value is None:
        return "None"
    if prefer_builtins_qualname:
        module = getattr(value, "__module__", "")
        qualname = getattr(value, "__qualname__", "")
        if module == "builtins" and qualname:
            return qualname
    if use_name:
        name = getattr(value, "__name__", "")
        if name:
            return name
    text = str(value).replace("typing.", "")
    if drop_collections_abc:
        return text.replace("collections.abc.", "")
    return text


def api_value_indexes(
    rows: ApiTableRows,
    *fields: str,
    value_field: str,
    list_fields: Iterable[str] = (),
    skip_empty_fields: Iterable[str] = (),
) -> tuple[dict[str, list[str]], ...]:
    """Return value indexes for API table rows keyed by the requested fields."""

    row_list = _api_row_list(rows, label="API table rows")
    field_names = _api_name_list(fields, label="API table index fields")
    value_name = _api_name(value_field, label="API table value field")
    list_field_names = _api_name_set(list_fields, label="API table list fields")
    skip_empty_field_names = _api_name_set(skip_empty_fields, label="API table skip-empty fields")
    indexes: list[dict[str, list[str]]] = [{} for _ in field_names]
    for row in row_list:
        value = str(_api_row_value(row, value_name))
        for field, index in zip(field_names, indexes):
            keys = _api_index_keys(row, field, list_field_names)
            for key in keys:
                if field in skip_empty_field_names and not key:
                    continue
                append_api_index_entry(index, key, value)
    return tuple(indexes)


def _api_index_keys(row: ApiTableRow, field: str, list_field_names: set[str]) -> Iterable[object]:
    if field in list_field_names:
        return _api_string_list_value(row, field)
    return (_api_row_value(row, field),)


def _api_row_payload_value(row: ApiTableRow, field: str, list_field_names: set[str]) -> object:
    if field in list_field_names:
        return _api_string_list_value(row, field)
    return _api_row_value(row, field)


def _api_name(value: object, *, label: str) -> str:
    if isinstance(value, str):
        return value
    raise TypeError(f"{label} must be a string value, not {type(value).__name__}")


def _api_name_list(values: object, *, label: str) -> list[str]:
    items = _api_list_items(values, label=label)
    names: list[str] = []
    for value in items:
        if not isinstance(value, str):
            raise TypeError(f"{label} must contain string values, not {type(value).__name__}")
        names.append(value)
    return names


def _api_list_items(values: object, *, label: str) -> list[object]:
    if isinstance(values, (str, bytes)):
        raise TypeError(f"{label} must be a list-like value, not {type(values).__name__}")
    if isinstance(values, Mapping):
        raise TypeError(f"{label} must be a list-like value, not {type(values).__name__}")
    if isinstance(values, Iterable):
        return list(values)
    raise TypeError(f"{label} must be a list-like value, not {type(values).__name__}")


def _api_name_set(values: object, *, label: str) -> set[str]:
    return set(_api_name_list(values, label=label))


def _api_row_list(rows: object, *, label: str) -> list[ApiTableRow]:
    return [_api_row_mapping(row, label="API table row") for row in _api_list_items(rows, label=label)]


def _api_row_mapping(row: object, *, label: str) -> ApiTableRow:
    if isinstance(row, Mapping):
        for key in row:
            if not isinstance(key, str):
                raise TypeError(f"{label} keys must be string values, not {type(key).__name__}")
        return row
    raise TypeError(f"{label} must be a mapping value, not {type(row).__name__}")


def _api_row_value(row: ApiTableRow, field: str) -> object:
    if field in row:
        return row[field]
    raise KeyError(f"API table row missing field {field!r}")


def _api_list_value(row: ApiTableRow, field: str) -> list[object]:
    return _api_list_items(_api_row_value(row, field), label=f"API table field {field!r}")


def _api_string_list_value(row: ApiTableRow, field: str) -> list[str]:
    return _api_name_list(_api_list_value(row, field), label=f"API table field {field!r}")
