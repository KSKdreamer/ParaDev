"""Shared Markdown helpers for generated API reference tables."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import NamedTuple, cast

from paradev._api_table import API_STANDARD_INDEXES, API_SYMBOL_FIELDS

ApiMarkdownIndex = Mapping[object, Iterable[object]]
ApiMarkdownRecord = Mapping[str, object]
ApiMarkdownRows = Iterable[ApiMarkdownRecord]


class ApiIndexSectionSpec(NamedTuple):
    title: str
    index_name: str
    label: str
    count_label: str
    values_label: str


class _ApiIndexHeaderLabels(NamedTuple):
    label: str
    count_label: str
    values_label: str


class _ApiSummaryIndexLabels(NamedTuple):
    label: str
    localized_label: str


@dataclass(frozen=True, slots=True)
class _ApiStandardIndexLabels:
    title: str
    label: str
    count_label: str
    values_label: str
    summary_label: str
    summary_localized_label: str


_API_MARKDOWN_ROW_COUNT_FIELD = "row_count"
_API_MARKDOWN_ROWS_FIELD = "rows"
_API_MARKDOWN_VALUE_FIELD = "value"
_API_FIELD_LABELS = {
    "cli_command": "CLI Command",
    "cli_commands": "CLI Commands",
    "command_key": "Command Key",
    "doc_page": "Doc Page",
    "frontend_operation_ids": "Frontend Operation IDs",
    "id": "ID",
    "index_names": "Indexes",
    "inspection_kinds": "Inspection Kinds",
    "markdown_cli_command": "Markdown CLI Command",
    "markdown_helper": "Markdown Helper",
    "payload_schema": "Payload Schema",
    "registry_seam": "Registry Seam",
    "required_inputs": "Required Inputs",
    _API_MARKDOWN_ROW_COUNT_FIELD: "Rows",
    "sdk_method": "SDK Method",
    "table_helper": "Table Helper",
    "test_anchor": "Test Anchor",
}
_API_FEATURE_INDEX_TITLE = "Feature Index / Feature 索引"
_API_KIND_INDEX_TITLE = "Kind Index / 行类型索引"
_API_MODULE_INDEX_TITLE = "Module Index / 模块索引"
_API_STANDARD_TABLE_TITLE = "API Standard Table / API 标准表"
_API_SUMMARY_TITLE = "Summary / 汇总"
_API_SURFACE_INDEX_TITLE = "Surface Index / Surface 索引"
_API_STANDARD_INDEX_LABELS: Mapping[str, _ApiStandardIndexLabels] = {
    "module_index": _ApiStandardIndexLabels(
        _API_MODULE_INDEX_TITLE,
        "Module",
        "Symbols",
        "Public Exports",
        "{module_label} modules",
        "{module_label} 模块数",
    ),
    "feature_index": _ApiStandardIndexLabels(
        _API_FEATURE_INDEX_TITLE,
        "Feature",
        "Symbols",
        "Public Exports",
        "Features",
        "Feature 数",
    ),
    "kind_index": _ApiStandardIndexLabels(
        _API_KIND_INDEX_TITLE,
        "Kind",
        "Symbols",
        "Public Exports",
        "Row kinds",
        "行类型数",
    ),
}


def _api_standard_index_labels(index_name: str) -> _ApiStandardIndexLabels:
    return _API_STANDARD_INDEX_LABELS[index_name]


def _api_standard_index_section_spec(index_name: str) -> ApiIndexSectionSpec:
    labels = _api_standard_index_labels(index_name)
    return ApiIndexSectionSpec(
        labels.title,
        index_name,
        labels.label,
        labels.count_label,
        labels.values_label,
    )


def _api_standard_summary_index_labels(index_name: str) -> _ApiSummaryIndexLabels:
    labels = _api_standard_index_labels(index_name)
    return _ApiSummaryIndexLabels(labels.summary_label, labels.summary_localized_label)


_API_STANDARD_INDEX_SECTION_SPECS: tuple[ApiIndexSectionSpec, ...] = tuple(_api_standard_index_section_spec(spec.index_name) for spec in API_STANDARD_INDEXES)


def markdown_cell(value: object) -> str:
    """Return a Markdown table-safe plain cell."""

    return str(value).replace("\n", " ").replace("|", "\\|").strip()


def code_cell(value: object) -> str:
    """Return a Markdown table-safe inline-code cell."""

    escaped = markdown_cell(value)
    return f"`{escaped}`" if escaped else ""


def code_list_cell(values: Iterable[str]) -> str:
    """Return comma-separated inline-code cells."""

    return ", ".join(
        code_cell(value)
        for value in _api_markdown_string_list(
            values,
            label="API Markdown code-list values",
            item_label="API Markdown code-list value",
        )
    )


def table_row(cells: Sequence[str]) -> str:
    """Return one Markdown table row from already-rendered cells."""

    cell_list = _api_markdown_string_list(
        cells,
        label="API Markdown table cells",
        item_label="API Markdown table cell",
    )
    return "| " + " | ".join(cell_list) + " |"


def table_rows(cell_rows: Iterable[Sequence[str]]) -> list[str]:
    """Return Markdown table rows from already-rendered cell rows."""

    row_list = _api_markdown_list_items(cell_rows, label="API Markdown table cell rows")
    return [table_row(cast(Sequence[str], cells)) for cells in row_list]


def table_header(labels: Sequence[object]) -> list[str]:
    """Return Markdown table header rows from plain labels."""

    label_list = _api_markdown_list_items(labels, label="API Markdown table labels")
    return [
        table_row([markdown_cell(label) for label in label_list]),
        table_row(["---" for _ in label_list]),
    ]


def api_table_lines(labels: Sequence[object], rows: Iterable[str]) -> list[str]:
    """Return Markdown table header rows plus already-rendered table rows."""

    row_list = _api_markdown_string_list(
        rows,
        label="API Markdown table rows",
        item_label="API Markdown table row",
    )
    return [
        *table_header(labels),
        *row_list,
    ]


def api_table_section(
    title: str,
    labels: Sequence[object],
    rows: Iterable[str],
    *,
    level: int = 2,
    body: Iterable[str] = (),
) -> list[str]:
    """Return one titled API table section from already-rendered rows."""

    title_text = _api_markdown_string_item(title, label="API Markdown section title")
    heading_level = _api_markdown_heading_level(level)
    body_lines = _api_markdown_string_list(
        body,
        label="API Markdown section body lines",
        item_label="API Markdown section body line",
    )
    lines = [
        f"{'#' * heading_level} {title_text}",
        "",
    ]
    if body_lines:
        lines.extend((*body_lines, ""))
    lines.extend(api_table_lines(labels, rows))
    return lines


def api_section_lines(sections: Iterable[Iterable[str]]) -> list[str]:
    """Return Markdown sections separated by one blank line."""

    lines: list[str] = []
    section_list = _api_markdown_line_sections(
        sections,
        sections_label="API Markdown sections",
        lines_label="API Markdown section lines",
    )
    for section in section_list:
        if lines:
            lines.append("")
        lines.extend(section)
    return lines


def api_field_label(field: str) -> str:
    """Return a generated API table column label for a row field."""

    field_name = _api_markdown_string_item(field, label="API Markdown field")
    return _API_FIELD_LABELS.get(field_name, field_name.replace("_", " ").title())


def api_field_table_header(fields: Sequence[str]) -> list[str]:
    """Return API table header rows for the selected mapping fields."""

    field_list = _api_markdown_field_names(fields)
    return table_header([api_field_label(field) for field in field_list])


def api_field_table_rows(
    rows: ApiMarkdownRows,
    fields: Sequence[str],
    *,
    list_fields: Iterable[str] = (),
    markdown_fields: Iterable[str] = (),
) -> list[str]:
    """Return API table rows by rendering the selected mapping fields."""

    row_list = _api_markdown_row_list(rows, label="API Markdown rows")
    field_list = _api_markdown_field_names(fields)
    list_names = _api_markdown_field_name_set(
        list_fields,
        label="API Markdown list fields",
        item_label="API Markdown list field",
    )
    markdown_names = _api_markdown_field_name_set(
        markdown_fields,
        label="API Markdown plain-value fields",
        item_label="API Markdown plain-value field",
    )
    cell_rows = [
        _api_markdown_field_row(
            row,
            field_list,
            list_names=list_names,
            markdown_names=markdown_names,
        )
        for row in row_list
    ]
    return table_rows(cell_rows)


def _api_markdown_field_row(
    row: ApiMarkdownRecord,
    fields: Sequence[str],
    *,
    list_names: set[str],
    markdown_names: set[str],
) -> list[str]:
    return [
        _api_markdown_field_cell(
            row,
            field,
            list_names=list_names,
            markdown_names=markdown_names,
        )
        for field in fields
    ]


def _api_markdown_field_cell(
    row: ApiMarkdownRecord,
    field: str,
    *,
    list_names: set[str],
    markdown_names: set[str],
) -> str:
    if field in list_names:
        return code_list_cell(_api_markdown_string_list_value(row, field))
    value = _api_markdown_value(row, field, label="API Markdown row")
    if field in markdown_names:
        return markdown_cell(value)
    return code_cell(value)


def _api_markdown_string_list_value(row: ApiMarkdownRecord, field: str) -> list[str]:
    return _api_markdown_string_list(
        _api_markdown_value(row, field, label="API Markdown row"),
        label=f"API Markdown field {field!r}",
        item_label=f"API Markdown field {field!r} value",
    )


def _api_markdown_list_items(value: object, *, label: str) -> list[object]:
    if isinstance(value, (str, bytes)):
        raise TypeError(f"{label} must be a list-like value, not {type(value).__name__}")
    if isinstance(value, Mapping):
        raise TypeError(f"{label} must be a list-like value, not {type(value).__name__}")
    if isinstance(value, Iterable):
        return list(value)
    raise TypeError(f"{label} must be a list-like value, not {type(value).__name__}")


def _api_markdown_string_item(value: object, *, label: str) -> str:
    if isinstance(value, str):
        return value
    raise TypeError(f"{label} must be a string value, not {type(value).__name__}")


def _api_markdown_field_names(fields: object) -> list[str]:
    return [_api_markdown_string_item(field, label="API Markdown table field") for field in _api_markdown_list_items(fields, label="API Markdown table fields")]


def _api_markdown_field_name_set(fields: object, *, label: str, item_label: str) -> set[str]:
    return {_api_markdown_string_item(field, label=item_label) for field in _api_markdown_list_items(fields, label=label)}


def _api_markdown_string_list(values: object, *, label: str, item_label: str) -> list[str]:
    return [_api_markdown_string_item(value, label=item_label) for value in _api_markdown_list_items(values, label=label)]


def _api_markdown_heading_level(level: object) -> int:
    if not isinstance(level, int) or isinstance(level, bool):
        raise TypeError(f"API Markdown section level must be an integer value, not {type(level).__name__}")
    if level < 1:
        raise ValueError(f"API Markdown section level must be at least 1, not {level}")
    return level


def _api_markdown_index_header_labels(label: object, count_label: object, values_label: object) -> _ApiIndexHeaderLabels:
    return _ApiIndexHeaderLabels(
        _api_markdown_string_item(label, label="API Markdown index label"),
        _api_markdown_string_item(count_label, label="API Markdown index count label"),
        _api_markdown_string_item(values_label, label="API Markdown index values label"),
    )


def _api_markdown_line_sections(
    sections: object,
    *,
    sections_label: str,
    lines_label: str,
) -> list[list[str]]:
    section_list = _api_markdown_list_items(sections, label=sections_label)
    line_label = lines_label[:-1] if lines_label.endswith("s") else lines_label
    return [_api_markdown_string_list(section, label=lines_label, item_label=line_label) for section in section_list]


def _api_markdown_value(row: ApiMarkdownRecord, field: str, *, label: str) -> object:
    if field in row:
        return row[field]
    raise KeyError(f"{label} missing field {field!r}")


def _api_markdown_table(table: object) -> ApiMarkdownRecord:
    return _api_markdown_string_key_mapping(table, label="API Markdown table")


def _api_markdown_mapping_value(row: ApiMarkdownRecord, field: str) -> ApiMarkdownIndex:
    value = _api_markdown_value(_api_markdown_table(row), field, label="API Markdown table")
    return _api_markdown_mapping_items(value, label=f"API Markdown index {field!r}")


def _api_markdown_rows_value(table: ApiMarkdownRecord) -> ApiMarkdownRows:
    return cast(ApiMarkdownRows, _api_markdown_value(table, _API_MARKDOWN_ROWS_FIELD, label="API Markdown table"))


def _api_markdown_row_count_line(table: ApiMarkdownRecord) -> str:
    return _api_markdown_summary_count_line(
        "API rows",
        _api_markdown_value(table, _API_MARKDOWN_ROW_COUNT_FIELD, label="API Markdown table"),
        localized_label="API 行数",
    )


def _api_markdown_summary_count_line(label: str, count: object, *, localized_label: str) -> str:
    return f"- {label} / {localized_label}: {count}"


def _api_markdown_mapping_items(value: object, *, label: str) -> ApiMarkdownIndex:
    if isinstance(value, Mapping):
        return value
    raise TypeError(f"{label} must be a mapping value, not {type(value).__name__}")


def _api_markdown_row_list(rows: object, *, label: str) -> list[ApiMarkdownRecord]:
    row_values = _api_markdown_list_items(rows, label=label)
    return [_api_markdown_row_mapping(row, label="API Markdown row") for row in row_values]


def _api_markdown_row_mapping(row: object, *, label: str) -> ApiMarkdownRecord:
    return _api_markdown_string_key_mapping(row, label=label)


def _api_markdown_string_key_mapping(value: object, *, label: str) -> ApiMarkdownRecord:
    if isinstance(value, Mapping):
        for key in value:
            if not isinstance(key, str):
                raise TypeError(f"{label} keys must be string values, not {type(key).__name__}")
        return cast(ApiMarkdownRecord, value)
    raise TypeError(f"{label} must be a mapping value, not {type(value).__name__}")


def api_field_table_section(
    title: str,
    rows: ApiMarkdownRows,
    fields: Sequence[str],
    *,
    list_fields: Iterable[str] = (),
    markdown_fields: Iterable[str] = (),
) -> list[str]:
    """Return one titled API field table Markdown section."""

    field_list = _api_markdown_field_names(fields)
    return api_table_section(
        title,
        [api_field_label(field) for field in field_list],
        api_field_table_rows(rows, field_list, list_fields=list_fields, markdown_fields=markdown_fields),
    )


def api_symbol_table_row(row: ApiMarkdownRecord) -> str:
    """Return one standard package-style API symbol table row."""

    return api_symbol_table_rows([row])[0]


def api_symbol_table_rows(rows: ApiMarkdownRows) -> list[str]:
    """Return standard package-style API symbol table rows."""

    return api_field_table_rows(rows, API_SYMBOL_FIELDS)


def api_symbol_markdown_value_table_row(row: ApiMarkdownRecord) -> str:
    """Return one standard API symbol row with a plain Markdown value cell."""

    return api_symbol_markdown_value_table_rows([row])[0]


def api_symbol_markdown_value_table_rows(rows: ApiMarkdownRows) -> list[str]:
    """Return standard API symbol rows with plain Markdown value cells."""

    return api_field_table_rows(rows, API_SYMBOL_FIELDS, markdown_fields=(_API_MARKDOWN_VALUE_FIELD,))


def api_symbol_table_header() -> list[str]:
    """Return the standard API symbol table Markdown header rows."""

    return api_field_table_header(API_SYMBOL_FIELDS)


def api_index_table_header(
    label: str,
    *,
    count_label: str = "Symbols",
    values_label: str = "Public Exports",
) -> list[str]:
    """Return the standard API index table Markdown header rows."""

    labels = _api_markdown_index_header_labels(label, count_label, values_label)
    return table_header((labels.label, labels.count_label, labels.values_label))


def api_index_section(
    title: str,
    index: ApiMarkdownIndex,
    label: str,
    *,
    count_label: str = "Symbols",
    values_label: str = "Public Exports",
) -> list[str]:
    """Return one titled API index Markdown section."""

    index_map = _api_markdown_mapping_items(index, label=f"API Markdown index {title!r}")
    labels = _api_markdown_index_header_labels(label, count_label, values_label)
    return api_table_section(
        title,
        (labels.label, labels.count_label, labels.values_label),
        index_rows(index_map),
    )


def api_index_sections(
    table: ApiMarkdownRecord,
    specs: Iterable[ApiIndexSectionSpec],
) -> list[list[str]]:
    """Return API index sections from table index specs."""

    table_map = _api_markdown_table(table)
    sections: list[list[str]] = []
    for spec in _api_markdown_index_section_specs(specs):
        index = _api_markdown_mapping_value(table_map, spec.index_name)
        sections.append(
            api_index_section(
                spec.title,
                index,
                spec.label,
                count_label=spec.count_label,
                values_label=spec.values_label,
            )
        )
    return sections


def _api_markdown_index_section_specs(specs: object) -> list[ApiIndexSectionSpec]:
    return [_api_markdown_index_section_spec(spec) for spec in _api_markdown_list_items(specs, label="API Markdown index section specs")]


def _api_markdown_index_section_spec(spec: object) -> ApiIndexSectionSpec:
    values = _api_markdown_list_items(spec, label="API Markdown index section spec")
    if len(values) != 5:
        raise ValueError(f"API Markdown index section spec must contain 5 values, not {len(values)}")
    string_values: list[str] = []
    for value in values:
        if not isinstance(value, str):
            raise TypeError(f"API Markdown index section spec must contain string values, not {type(value).__name__}")
        string_values.append(value)
    return ApiIndexSectionSpec(*string_values)


def api_indexed_reference_sections(
    *,
    summary_lines: Iterable[str],
    table: ApiMarkdownRecord,
    index_specs: Iterable[ApiIndexSectionSpec],
    fields: Sequence[str],
    table_title: str = _API_STANDARD_TABLE_TITLE,
    list_fields: Iterable[str] = (),
    markdown_fields: Iterable[str] = (),
) -> list[list[str]]:
    """Return summary, index, and standard field-table API reference sections."""

    table_map = _api_markdown_table(table)
    return [
        api_summary_section(summary_lines),
        *api_index_sections(table_map, index_specs),
        api_field_table_section(
            table_title,
            _api_markdown_rows_value(table_map),
            fields,
            list_fields=list_fields,
            markdown_fields=markdown_fields,
        ),
    ]


def api_summary_lines(table: ApiMarkdownRecord, *, module_label: str) -> list[str]:
    """Return the standard API reference summary bullet lines."""

    table_map = _api_markdown_table(table)
    module_label_text = _api_markdown_string_item(module_label, label="API Markdown module label")
    return [
        _api_markdown_row_count_line(table_map),
        *_api_standard_summary_index_lines(table_map, module_label_text=module_label_text),
    ]


def _api_standard_summary_index_lines(table: ApiMarkdownRecord, *, module_label_text: str) -> list[str]:
    lines: list[str] = []
    for spec in API_STANDARD_INDEXES:
        labels = _api_standard_summary_index_labels(spec.index_name)
        index = _api_markdown_mapping_value(table, spec.index_name)
        lines.append(
            _api_markdown_summary_count_line(
                labels.label.format(module_label=module_label_text),
                len(index),
                localized_label=labels.localized_label.format(module_label=module_label_text),
            )
        )
    return lines


def api_summary_section(lines: Iterable[str]) -> list[str]:
    """Return the standard API reference summary Markdown section."""

    line_list = _api_markdown_string_list(
        lines,
        label="API Markdown summary lines",
        item_label="API Markdown summary line",
    )
    return [
        f"## {_API_SUMMARY_TITLE}",
        "",
        *line_list,
    ]


def api_summary_reference_sections(
    summary_lines: Iterable[str],
    sections: Iterable[Iterable[str]],
) -> list[list[str]]:
    """Return summary plus custom generated API reference sections."""

    section_list = _api_markdown_line_sections(
        sections,
        sections_label="API Markdown reference sections",
        lines_label="API Markdown reference section lines",
    )
    return [
        api_summary_section(summary_lines),
        *section_list,
    ]


def api_standard_index_sections(table: ApiMarkdownRecord) -> list[str]:
    """Return the standard Module/Feature/Kind API index Markdown sections."""

    return api_section_lines(api_index_sections(table, _API_STANDARD_INDEX_SECTION_SPECS))


def api_standard_overview_sections(table: ApiMarkdownRecord, *, module_label: str) -> list[str]:
    """Return standard API summary and index Markdown sections."""

    return api_section_lines(
        (
            api_summary_section(api_summary_lines(table, module_label=module_label)),
            api_standard_index_sections(table),
        )
    )


def api_standard_table_section(rows: ApiMarkdownRows, *, markdown_value: bool = False) -> list[str]:
    """Return the standard API symbol table Markdown section."""

    markdown_fields = (_API_MARKDOWN_VALUE_FIELD,) if markdown_value else ()
    return api_field_table_section(
        _API_STANDARD_TABLE_TITLE,
        rows,
        API_SYMBOL_FIELDS,
        markdown_fields=markdown_fields,
    )


def api_standard_reference_markdown(
    *,
    title: str,
    source: str,
    regenerate_when: str,
    command: str,
    table: ApiMarkdownRecord,
    module_label: str,
    markdown_value: bool = False,
) -> str:
    """Render a complete standard API reference Markdown document."""

    table_map = _api_markdown_table(table)
    return api_reference_markdown(
        title=title,
        source=source,
        regenerate_when=regenerate_when,
        command=command,
        sections=(
            api_standard_overview_sections(table_map, module_label=module_label),
            api_standard_table_section(
                _api_markdown_rows_value(table_map),
                markdown_value=markdown_value,
            ),
        ),
    )


def api_surface_reference_markdown(
    *,
    title: str,
    source: str,
    regenerate_when: str,
    command: str,
    table: ApiMarkdownRecord,
    fields: Sequence[str],
    include_feature_index: bool = True,
    list_fields: Iterable[str] = (),
    markdown_fields: Iterable[str] = (),
) -> str:
    """Render a surface-indexed API reference Markdown document."""

    table_map = _api_markdown_table(table)
    return api_reference_markdown(
        title=title,
        source=source,
        regenerate_when=regenerate_when,
        command=command,
        sections=_api_surface_reference_sections(
            table_map,
            fields,
            include_feature_index=include_feature_index,
            list_fields=list_fields,
            markdown_fields=markdown_fields,
        ),
    )


def _api_surface_reference_sections(
    table: ApiMarkdownRecord,
    fields: Sequence[str],
    *,
    include_feature_index: bool,
    list_fields: Iterable[str],
    markdown_fields: Iterable[str],
) -> list[list[str]]:
    surface_index, feature_index = _api_surface_reference_indexes(
        table,
        include_feature_index=include_feature_index,
    )
    return [
        api_summary_section(_api_surface_reference_summary_lines(table, surface_index, feature_index)),
        *_api_surface_reference_index_sections(surface_index, feature_index),
        _api_surface_reference_table_section(
            table,
            fields,
            list_fields=list_fields,
            markdown_fields=markdown_fields,
        ),
    ]


def _api_surface_reference_indexes(
    table: ApiMarkdownRecord,
    *,
    include_feature_index: bool,
) -> tuple[ApiMarkdownIndex, ApiMarkdownIndex | None]:
    surface_index = _api_markdown_mapping_value(table, "surface_index")
    feature_index = _api_markdown_mapping_value(table, "feature_index") if include_feature_index else None
    return surface_index, feature_index


def _api_surface_reference_index_sections(
    surface_index: ApiMarkdownIndex,
    feature_index: ApiMarkdownIndex | None,
) -> list[list[str]]:
    sections: list[list[str]] = []
    if feature_index is not None:
        sections.append(_api_surface_reference_feature_index_section(feature_index))
    sections.append(_api_surface_reference_surface_index_section(surface_index))
    return sections


def _api_surface_reference_summary_lines(
    table: ApiMarkdownRecord,
    surface_index: ApiMarkdownIndex,
    feature_index: ApiMarkdownIndex | None,
) -> list[str]:
    lines = [
        _api_markdown_row_count_line(table),
        _api_markdown_summary_count_line("Surfaces", len(surface_index), localized_label="Surface 数"),
    ]
    if feature_index is not None:
        lines.append(_api_markdown_summary_count_line("Features", len(feature_index), localized_label="Feature 数"))
    return lines


def _api_surface_reference_feature_index_section(feature_index: ApiMarkdownIndex) -> list[str]:
    return api_index_section(
        _API_FEATURE_INDEX_TITLE,
        feature_index,
        "Feature",
        count_label="APIs",
        values_label="Symbols",
    )


def _api_surface_reference_surface_index_section(surface_index: ApiMarkdownIndex) -> list[str]:
    return api_index_section(
        _API_SURFACE_INDEX_TITLE,
        surface_index,
        "Surface",
        count_label="APIs",
        values_label="Symbols",
    )


def _api_surface_reference_table_section(
    table: ApiMarkdownRecord,
    fields: Sequence[str],
    *,
    list_fields: Iterable[str],
    markdown_fields: Iterable[str],
) -> list[str]:
    return api_field_table_section(
        _API_STANDARD_TABLE_TITLE,
        _api_markdown_rows_value(table),
        fields,
        list_fields=list_fields,
        markdown_fields=markdown_fields,
    )


def api_reference_markdown(
    *,
    title: str,
    source: str,
    regenerate_when: str,
    command: str,
    sections: Iterable[Iterable[str]],
) -> str:
    """Render a complete generated API reference Markdown document."""

    section_list = _api_markdown_line_sections(
        sections,
        sections_label="API Markdown reference sections",
        lines_label="API Markdown reference section lines",
    )
    intro_section = _api_reference_intro_section(
        title=title,
        source=source,
        regenerate_when=regenerate_when,
        command=command,
    )
    return "\n".join(api_section_lines((intro_section, *section_list))) + "\n"


def _api_reference_intro_section(
    *,
    title: str,
    source: str,
    regenerate_when: str,
    command: str,
) -> list[str]:
    title_text = _api_markdown_string_item(title, label="API Markdown reference title")
    return [
        f"# {title_text}",
        "",
        *api_reference_intro_lines(source=source, regenerate_when=regenerate_when, command=command),
    ]


def api_regeneration_command_block(command: str) -> list[str]:
    """Return a fenced Bash command block for API reference regeneration."""

    command_text = _api_markdown_string_item(command, label="API Markdown regeneration command")
    return [
        "```bash",
        command_text,
        "```",
    ]


def api_reference_intro_lines(
    *,
    source: str,
    regenerate_when: str,
    command: str,
) -> list[str]:
    """Return the standard generated API reference intro lines."""

    source_text = _api_markdown_string_item(source, label="API Markdown reference source")
    regenerate_text = _api_markdown_string_item(regenerate_when, label="API Markdown regeneration note")
    return [
        f"Generated from `{source_text}`.",
        "",
        regenerate_text,
        "",
        *api_regeneration_command_block(command),
    ]


def index_row(key: str, values: Iterable[str]) -> str:
    """Return a standard three-column API index table row."""

    key_text = _api_markdown_string_item(key, label="API Markdown index key")
    cells = _api_markdown_string_list(
        values,
        label=f"API Markdown index values for {key_text!r}",
        item_label=f"API Markdown index value for {key_text!r}",
    )
    return f"| {code_cell(key_text)} | {len(cells)} | {', '.join(code_cell(cell) for cell in cells)} |"


def index_rows(index: ApiMarkdownIndex) -> list[str]:
    """Return standard three-column API index table rows."""

    index_map = _api_markdown_mapping_items(index, label="API Markdown index rows")
    return [index_row(key, values) for key, values in index_map.items()]
