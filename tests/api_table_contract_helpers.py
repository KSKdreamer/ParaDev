"""Shared helpers for API table contract tests."""

from __future__ import annotations

import ast
import importlib
import re
from collections.abc import Iterable, Mapping, Sized
from typing import NamedTuple, get_args, get_origin, get_type_hints

from heavenbase.utils import enum_files, exists_file, load_txt, pj
from typing_extensions import is_typeddict

from paradev._api_table import API_STANDARD_INDEXES, api_table_index_names
from paradev._api_table_markdown import api_summary_lines

_API_SOURCE_ROOT = "src/paradev"
_API_TABLE_SCHEMA_FIELD = "schema"
_API_TABLE_ROW_COUNT_FIELD = "row_count"
_API_TABLE_ROWS_FIELD = "rows"
_DEFAULT_API_TABLE_ROW_KEY_FIELD = "symbol"
_API_TABLE_SHARED_ROW_TEXT_FIELDS = (
    "kind",
    "layer",
    "returns",
    "surface",
    "registry_seam",
)
_API_TABLE_SHARED_ROW_OPTIONAL_INDEX_FIELDS = {
    "feature_index": "feature",
}
_API_TABLE_INDEX_LIST_FIELD_SUFFIXES = ("_ids", "s")
_API_CATALOG_TABLE_FUNCTION_NAME = "get_api_catalog_table"
_API_CATALOG_REFERENCE_ID = "api-catalog"
_USER_MANUAL_ROOT = "docs/user-manual"
_USER_MANUAL_INDEX_PAGE = "docs/user-manual/README.md"
_USER_MANUAL_REFERENCE_SUFFIX = "-reference.md"
_USER_MANUAL_API_REFERENCE_SECTION_HEADINGS = {
    "English": "## English",
    "Chinese": "## 中文",
}
_MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
_API_CATALOG_ROW_COUNT_FALLBACK_FIELDS = {
    "surface-contract-reference": "surface_count",
    "project-inspection-reference": "inspections",
}
_API_CATALOG_SUMMARY_COUNT_FIELDS = {
    "reference_count": _API_TABLE_ROW_COUNT_FIELD,
    "layer_count": "layer_index",
    "feature_count": "feature_index",
    "kind_count": "kind_index",
    "reference_group_count": "reference_groups",
    "index_count": "index_catalog",
    "owner_module_count": "owner_module_index",
    "surface_count": "surface_index",
    "cli_command_count": "cli_command_index",
    "selector_helper_count": "selector_helper_index",
    "doc_page_count": "doc_page_index",
}
_API_REFERENCE_MARKDOWN_ROW_COUNT_TITLE = "API rows / API 行数"
_API_CATALOG_ROW_INDEX_FIELDS = {
    "layer_index": "layer",
    "feature_index": "feature",
    "kind_index": "kind",
    "owner_module_index": "owner_module",
    "cli_command_index": "cli_command",
    "selector_helper_index": "selector_helper",
    "doc_page_index": "doc_page",
}
_API_CATALOG_ROW_LIST_INDEX_FIELDS = {
    "surface_index": "surfaces",
}
_API_CATALOG_OPTIONAL_ROW_INDEX_FIELDS = {"selector_helper"}
_API_CATALOG_REQUIRED_ROW_TEXT_FIELDS = (
    "id",
    "title",
    "kind",
    "layer",
    "feature",
    "owner_module",
    "schema",
    "table_helper",
    "markdown_helper",
    "cli_command",
    "markdown_cli_command",
    "doc_page",
    "test_anchor",
)
_API_CATALOG_OPTIONAL_ROW_TEXT_FIELDS = ("selector_helper",)
_API_CATALOG_REQUIRED_ROW_INT_FIELDS = ("row_count",)
_API_CATALOG_REQUIRED_ROW_LIST_FIELDS = ("index_names", "surfaces")
_API_CATALOG_UNIQUE_ROW_FIELDS = ("id", "doc_page", "markdown_cli_command")
_API_CATALOG_MARKDOWN_ROW_FIELDS = (
    "id",
    "title",
    "kind",
    "layer",
    "feature",
    "schema",
    "row_count",
    "table_helper",
    "selector_helper",
    "markdown_helper",
    "cli_command",
    "markdown_cli_command",
    "index_names",
    "surfaces",
    "doc_page",
    "test_anchor",
)
_API_CATALOG_MARKDOWN_ROW_TEXT_FIELDS = {"title", "row_count"}
_API_CATALOG_MARKDOWN_ROW_LIST_FIELDS = {"index_names", "surfaces"}
_API_CATALOG_MARKDOWN_ROW_OPTIONAL_CODE_FIELDS = {"selector_helper"}
_API_CATALOG_DIRECT_INDEX_CATALOG_IDS = {
    "id",
    "reference_group",
}
_API_CATALOG_HELPER_NAMES = {
    "id": "get_api_catalog_reference",
    "reference_group": "get_api_catalog_reference_group",
    "group": "get_api_catalog_group_reference_ids",
}
_API_CATALOG_REFERENCE_IDS_HELPER = "get_api_catalog_reference_ids"
_API_CATALOG_CLI_SURFACE = "cli"
_API_CATALOG_MCP_SURFACE = "mcp"
_API_CATALOG_REST_SURFACE = "rest"
_API_CATALOG_SURFACE_CONTRACT_REFERENCE_ID = "surface-contract-reference"
_API_CATALOG_SURFACE_CONTRACT_SURFACE_ALIASES = {
    "openapi": _API_CATALOG_REST_SURFACE,
}
_API_CATALOG_KNOWN_SURFACES = {
    "bundle",
    "cli",
    "desktop",
    "docs",
    "frontend",
    "lsp",
    "mcp",
    "rest",
    "sdk",
    "typescript",
    "vscode",
}
_API_CATALOG_REST_SELECTOR_FEATURE_REFERENCE_IDS = {
    "api-catalog": "api-catalog",
    "architecture": "architecture-api",
    "catalog": "catalog-api",
    "cli": "cli-api",
    "frontend-api": "frontend-api",
    "lsp": "lsp-api",
    "pdx": "pdx-api",
    "rest": "rest-api",
    "surface-contracts": "surface-contract-reference",
}
_API_REFERENCE_MARKDOWN_SUMMARY_HEADING = "## Summary / 汇总"
_API_REFERENCE_MARKDOWN_TABLE_HEADING = "## API Standard Table / API 标准表"
_API_REFERENCE_MARKDOWN_RENDERER_CALLS = (
    "api_reference_markdown",
    "api_standard_reference_markdown",
    "api_surface_reference_markdown",
)
_API_REFERENCE_MARKDOWN_INDEX_HEADINGS = {
    "adapter_index": "## Adapter Index / Adapter 索引",
    "cli_command_index": "## CLI Command Index / CLI 命令索引",
    "feature_index": "## Feature Index / Feature 索引",
    "frontend_operation_index": "## Frontend Operation Index / 前端操作索引",
    "inspection_kind_index": "## Inspection Kind Index / Inspection 类型索引",
    "kind_index": "## Kind Index / 行类型索引",
    "method_index": "## Method Index / Method 索引",
    "mode_index": "## Mode Index / 模式索引",
    "module_index": "## Module Index / 模块索引",
    "surface_index": "## Surface Index / Surface 索引",
}
_API_CATALOG_MARKDOWN_TABLE_HEADING = "## API Catalog Table / API Catalog 表"
_API_CATALOG_REFERENCE_GROUPS_MARKDOWN_HEADING = "## Reference Groups / Reference 分组"
_API_CATALOG_INDEX_CATALOG_MARKDOWN_HEADING = "## Index Catalog / Index 目录"
_API_CATALOG_MARKDOWN_EXTRA_HEADINGS = (
    _API_CATALOG_REFERENCE_GROUPS_MARKDOWN_HEADING,
    _API_CATALOG_INDEX_CATALOG_MARKDOWN_HEADING,
)
_API_CATALOG_MARKDOWN_INDEX_HEADINGS = {
    "cli_command_index": "## Regeneration Index / 重新生成索引",
    "doc_page_index": "## Doc Page Index / Doc Page 索引",
    "feature_index": "## Feature Index / Feature 索引",
    "group_index": "## Reference Group Index / Reference 分组索引",
    "kind_index": "## Kind Index / 类型索引",
    "layer_index": "## Layer Index / Layer 索引",
    "owner_module_index": "## Owner Module Index / Owner Module 索引",
    "selector_helper_index": "## Selector Helper Index / Selector Helper 索引",
    "surface_index": "## Surface Index / Surface 索引",
}
_CLI_API_COMMAND_KEY_FIELD = "command_key"
_MANUAL_API_TABLE_ROW_KEY_FIELDS = {
    "src/paradev/surfaces/api_catalog.py": {"get_api_catalog_table": "id"},
}
_API_SELECTION_TABLE_HELPER_EXCEPTIONS = {
    "src/paradev/sdk/frontend_api.py": {"get_frontend_api_selection"},
    "src/paradev/sdk/project_api.py": {"get_project_api_selection"},
    "src/paradev/surfaces/cli.py": {"get_cli_api_selection"},
    "src/paradev/surfaces/mcp.py": {"get_mcp_api_selection"},
    "src/paradev/surfaces/rest.py": {"get_rest_api_selection"},
}


class ApiTableFunction(NamedTuple):
    module_name: str
    function_name: str
    row_key_field: str


class ApiSummaryCountLine(NamedTuple):
    field: str
    prefix: str
    index_name: str
    index_key: str | None = None


def api_source_trees(root: str = _API_SOURCE_ROOT) -> list[tuple[str, ast.AST, str]]:
    sources: list[tuple[str, ast.AST, str]] = []
    for name in sorted(enum_files(root, ext="py")):
        path = pj(root, name).replace("\\", "/")
        text = load_txt(path, encoding="utf-8")
        sources.append((path, ast.parse(text), text))
    return sources


def function_names(tree: ast.AST) -> set[str]:
    return {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}


def api_selection_functions(tree: ast.AST) -> list[ast.FunctionDef]:
    return [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name.startswith("get_") and node.name.endswith("api_selection")]


def function_calls(node: ast.FunctionDef, name: str) -> bool:
    return any(isinstance(child, ast.Call) and isinstance(child.func, ast.Name) and child.func.id == name for child in ast.walk(node))


def api_table_functions() -> list[ApiTableFunction]:
    functions: list[ApiTableFunction] = []
    for path, tree, _text in api_source_trees():
        module_name = _api_source_module_name(path)
        for function_name, row_key_field in _api_table_function_row_keys(path, tree).items():
            functions.append(ApiTableFunction(module_name, function_name, row_key_field))
    return functions


def load_api_table(function: ApiTableFunction) -> object:
    return getattr(importlib.import_module(function.module_name), function.function_name)()


def api_table_payload_gaps(function: ApiTableFunction, table: object) -> list[str]:
    label = f"{function.module_name}.{function.function_name}"
    if not isinstance(table, Mapping):
        return [f"{label}: table is {type(table).__name__}, not a mapping"]
    row_gaps, rows = _api_table_rows(function, table)
    gaps = [*row_gaps, *_api_row_count_gaps(function, table, rows)]
    gaps.extend(_api_table_payload_field_gaps(function, table))
    gaps.extend(_api_table_typed_payload_field_gaps(function, table))
    row_keys = _api_table_row_keys(function, rows, gaps)
    gaps.extend(_api_table_index_gaps(function, table, set(row_keys)))
    return gaps


def api_table_schema_gaps(tables: list[tuple[ApiTableFunction, object]]) -> list[str]:
    gaps: list[str] = []
    seen_schemas: dict[str, str] = {}
    for function, table in tables:
        label = f"{function.module_name}.{function.function_name}"
        if not isinstance(table, Mapping):
            gaps.append(f"{label}: table is {type(table).__name__}, not a mapping")
            continue
        schema = _api_table_schema(function, table, gaps)
        if not schema:
            continue
        previous_label = seen_schemas.get(schema)
        if previous_label is not None:
            gaps.append(f"{label}: duplicate schema {schema!r} already used by {previous_label}")
            continue
        seen_schemas[schema] = label
    return gaps


def api_table_row_shape_gaps(function: ApiTableFunction, table: object) -> list[str]:
    if function.function_name == _API_CATALOG_TABLE_FUNCTION_NAME:
        return []
    label = f"{function.module_name}.{function.function_name}"
    if not isinstance(table, Mapping):
        return [f"{label}: table is {type(table).__name__}, not a mapping"]
    row_gaps, rows = _api_table_rows(function, table)
    gaps = [*row_gaps]
    _api_table_row_field_set_gaps(function, rows, gaps)
    gaps.extend(_api_table_typed_row_field_gaps(function, rows))
    required_fields = _api_table_required_row_text_fields(table)
    for index, row in enumerate(rows):
        for field in required_fields:
            _api_non_empty_row_string(function, row, index, field, gaps)
    return gaps


def api_table_index_coverage_gaps(function: ApiTableFunction, table: object) -> list[str]:
    if function.function_name == _API_CATALOG_TABLE_FUNCTION_NAME:
        return []
    label = f"{function.module_name}.{function.function_name}"
    if not isinstance(table, Mapping):
        return [f"{label}: table is {type(table).__name__}, not a mapping"]
    row_gaps, rows = _api_table_rows(function, table)
    gaps = [*row_gaps]
    row_keys = {value for row in rows if isinstance((value := row.get(function.row_key_field)), str) and value}
    gaps.extend(_api_table_index_gaps(function, table, row_keys))
    for index_name in api_table_index_names(table):
        index = table[index_name]
        if not isinstance(index, Mapping):
            gaps.append(f"{label}: {index_name} is not a mapping")
            continue
        field = _api_table_index_row_field(function, index_name, rows, gaps)
        if not field:
            continue
        expected_row_values: dict[str, set[str]] = {}
        for row_index, row in enumerate(rows):
            row_key = _api_non_empty_row_string(function, row, row_index, function.row_key_field, gaps)
            for value in _api_table_index_row_values(function, row, row_index, field, gaps):
                expected_row_values.setdefault(row_key, set()).add(value)
                _api_table_index_contains_row(function, index_name, value, row_key, index, gaps)
        _api_table_index_matches_row_fields(function, index_name, index, expected_row_values, gaps)
    return gaps


def api_table_reference_gaps(function: ApiTableFunction, table: object) -> list[str]:
    label = f"{function.module_name}.{function.function_name}"
    if not isinstance(table, Mapping):
        return [f"{label}: table is {type(table).__name__}, not a mapping"]
    row_gaps, rows = _api_table_rows(function, table)
    gaps = [*row_gaps]
    test_functions_by_path: dict[str, set[str]] = {}
    for index, row in enumerate(rows):
        _api_doc_page_gaps(function, row, index, gaps)
        _api_test_anchor_gaps(function, row, index, test_functions_by_path, gaps)
    return gaps


def api_reference_markdown_gaps(function: ApiTableFunction) -> list[str]:
    label = f"{function.module_name}.{function.function_name}"
    module = importlib.import_module(function.module_name)
    renderer_name = _api_reference_renderer_name(function)
    renderer = getattr(module, renderer_name, None)
    if not callable(renderer):
        return [f"{label}: missing renderer {renderer_name}"]
    markdown = renderer()
    if not isinstance(markdown, str):
        return [f"{label}: renderer {renderer_name} returned {type(markdown).__name__}, not str"]
    table = load_api_table(function)
    gaps = _api_reference_markdown_title_gaps(function, markdown)
    gaps.extend(_api_reference_markdown_source_gaps(function, markdown))
    gaps.extend(_api_reference_markdown_regeneration_note_gaps(function, markdown))
    gaps.extend(_api_reference_markdown_regeneration_command_gaps(function, markdown))
    gaps.extend(_api_reference_markdown_heading_gaps(function, table, markdown))
    gaps.extend(_api_reference_markdown_row_gaps(function, table, markdown))
    gaps.extend(_api_reference_markdown_index_gaps(function, table, markdown))
    gaps.extend(_api_reference_markdown_summary_gaps(function, table, markdown))
    gaps.extend(_api_reference_markdown_catalog_table_gaps(function, table, markdown))
    gaps.extend(_api_reference_markdown_catalog_summary_gaps(function, table, markdown))
    gaps.extend(_api_reference_markdown_catalog_group_gaps(function, table, markdown))
    gaps.extend(_api_reference_markdown_catalog_index_catalog_gaps(function, table, markdown))
    doc_path = _api_reference_markdown_path(markdown)
    if not doc_path:
        gaps.append(f"{label}: renderer {renderer_name} does not declare a docs/user-manual output path")
        return gaps
    if not exists_file(doc_path):
        gaps.append(f"{label}: renderer {renderer_name} points at missing docs page {doc_path!r}")
        return gaps
    existing = load_txt(doc_path, encoding="utf-8")
    if existing != markdown:
        gaps.append(f"{label}: {doc_path} differs from {renderer_name}() output")
    return gaps


def api_catalog_reference_gaps() -> list[str]:
    gaps, _table, rows = _api_catalog_table_rows()
    doc_pages: set[str] = set()
    test_functions_by_path: dict[str, set[str]] = {}
    for index, row in enumerate(rows):
        doc_page = _api_catalog_row_text(row, index, "doc_page", gaps)
        if doc_page:
            doc_pages.add(doc_page)
        _api_catalog_markdown_gaps(row, index, gaps)
        _api_catalog_test_anchor_gaps(row, index, test_functions_by_path, gaps)
    gaps.extend(_api_catalog_manual_reference_gaps(doc_pages))
    return gaps


def api_manual_reference_index_gaps() -> list[str]:
    gaps, _table, rows = _api_catalog_table_rows()
    if not exists_file(_USER_MANUAL_INDEX_PAGE):
        return [f"api catalog: user manual index {_USER_MANUAL_INDEX_PAGE!r} is missing"]
    section_links = _user_manual_index_section_links(load_txt(_USER_MANUAL_INDEX_PAGE, encoding="utf-8"), gaps)
    catalog_doc_pages: set[str] = set()
    for index, row in enumerate(rows):
        row_id = _api_catalog_row_text(row, index, "id", gaps)
        doc_page = _api_catalog_row_text(row, index, "doc_page", gaps)
        if doc_page:
            catalog_doc_pages.add(doc_page)
        for section, linked_pages in section_links.items():
            if doc_page and doc_page not in linked_pages:
                gaps.append(f"api catalog {row_id}: doc_page {doc_page!r} is not linked from {_USER_MANUAL_INDEX_PAGE} {section} section")
    _user_manual_stale_reference_link_gaps(section_links, catalog_doc_pages, gaps)
    return gaps


def api_catalog_payload_metadata_gaps() -> list[str]:
    gaps, _table, rows = _api_catalog_table_rows()
    for index, row in enumerate(rows):
        _api_catalog_payload_metadata_row_gaps(row, index, gaps)
    return gaps


def api_catalog_api_table_helper_gaps(functions: list[ApiTableFunction]) -> list[str]:
    gaps, _table, rows = _api_catalog_table_rows()
    api_table_helpers: dict[object, ApiTableFunction] = {}
    for function in functions:
        helper = getattr(importlib.import_module(function.module_name), function.function_name, None)
        if callable(helper):
            api_table_helpers[helper] = function
            continue
        gaps.append(f"api catalog: missing scanned API table helper {function.module_name}.{function.function_name}")
    catalog_helpers: set[object] = set()
    for index, row in enumerate(rows):
        owner_module = _api_catalog_row_text(row, index, "owner_module", gaps)
        helper_name = _api_catalog_row_text(row, index, "table_helper", gaps)
        if not owner_module or not helper_name:
            continue
        helper = getattr(importlib.import_module(owner_module), helper_name, None)
        if helper in api_table_helpers:
            catalog_helpers.add(helper)
    for helper, function in api_table_helpers.items():
        if helper not in catalog_helpers:
            gaps.append(f"api catalog: missing API table helper {function.module_name}.{function.function_name}")
    return gaps


def api_catalog_row_shape_gaps() -> list[str]:
    gaps, _table, rows = _api_catalog_table_rows()
    seen_values: dict[str, dict[str, int]] = {field: {} for field in _API_CATALOG_UNIQUE_ROW_FIELDS}
    for index, row in enumerate(rows):
        _api_catalog_row_shape_row_gaps(row, index, seen_values, gaps)
    _api_catalog_source_id_gaps(rows, gaps)
    _api_catalog_source_order_gaps(rows, gaps)
    _api_catalog_source_metadata_gaps(rows, gaps)
    return gaps


def api_catalog_summary_group_gaps() -> list[str]:
    gaps, table, rows = _api_catalog_table_rows()
    if table is None:
        return gaps
    rows_by_id = _api_catalog_rows_by_id(rows, gaps)
    _api_catalog_summary_gaps(table, gaps)
    _api_catalog_reference_group_gaps(table, rows_by_id, gaps)
    return gaps


def api_catalog_index_coverage_gaps() -> list[str]:
    gaps, table, rows = _api_catalog_table_rows()
    if table is None:
        return gaps
    for index, row in enumerate(rows):
        _api_catalog_row_index_coverage_gaps(table, row, index, gaps)
    _api_catalog_reverse_index_coverage_gaps(table, rows, gaps)
    return gaps


def api_catalog_index_catalog_gaps() -> list[str]:
    gaps, table, _rows = _api_catalog_table_rows()
    if table is None:
        return gaps
    index_catalog = table.get("index_catalog")
    if not isinstance(index_catalog, list):
        gaps.append(f"api catalog: index_catalog is {type(index_catalog).__name__}, not a list")
        return gaps
    catalog_rows: list[Mapping[str, object]] = []
    for index, row in enumerate(index_catalog):
        if isinstance(row, Mapping):
            catalog_rows.append(row)
            continue
        gaps.append(f"api catalog: index_catalog row {index} is {type(row).__name__}, not a mapping")
    row_ids = [_api_catalog_index_catalog_text(row, index, "id", gaps) for index, row in enumerate(catalog_rows)]
    _api_catalog_index_catalog_id_gaps(table, row_ids, gaps)
    for index, row in enumerate(catalog_rows):
        _api_catalog_index_catalog_row_gaps(table, row, index, gaps)
    return gaps


def api_catalog_cli_command_gaps() -> list[str]:
    gaps, _table, rows = _api_catalog_table_rows()
    cli_gaps, cli_rows = _cli_api_rows_by_command()
    gaps.extend(cli_gaps)
    catalog_commands: set[str] = set()
    for index, row in enumerate(rows):
        catalog_commands.update(_api_catalog_cli_command_row_gaps(row, index, cli_rows, gaps))
    _api_catalog_cli_command_reverse_gaps(catalog_commands, cli_rows, gaps)
    return gaps


def api_catalog_selector_surface_gaps() -> list[str]:
    gaps, _table, rows = _api_catalog_table_rows()
    catalog_rows_by_id: dict[str, tuple[int, Mapping[str, object]]] = {}
    catalog_rows_by_selector: dict[str, list[tuple[int, Mapping[str, object]]]] = {}
    for index, row in enumerate(rows):
        row_id = _api_catalog_row_text(row, index, "id", gaps)
        selector = _api_catalog_optional_row_text(row, index, "selector_helper", gaps)
        if row_id:
            catalog_rows_by_id[row_id] = (index, row)
        if selector:
            catalog_rows_by_selector.setdefault(selector, []).append((index, row))
    _api_catalog_mcp_selector_surface_gaps(catalog_rows_by_selector, gaps)
    _api_catalog_rest_selector_surface_gaps(catalog_rows_by_id, gaps)
    return gaps


def api_catalog_surface_contract_gaps() -> list[str]:
    gaps, table, rows = _api_catalog_table_rows()
    if table is None:
        return gaps
    catalog_rows_by_id = _api_catalog_rows_by_id(rows, gaps)
    contract_surfaces = _surface_contract_catalog_surfaces(gaps)
    if not contract_surfaces:
        return gaps
    _api_catalog_surface_index_contract_gaps(table, contract_surfaces, gaps)
    _api_catalog_surface_contract_reference_gaps(catalog_rows_by_id, contract_surfaces, gaps)
    return gaps


def api_selection_table_gaps() -> list[str]:
    row_keys_by_module = _api_table_row_keys_by_module()
    gaps: list[str] = []
    for path, tree, _text in api_source_trees():
        module_name = _api_source_module_name(path)
        row_keys = row_keys_by_module.get(module_name, set())
        for node in api_selection_functions(tree):
            if node.name in _API_SELECTION_TABLE_HELPER_EXCEPTIONS.get(path, set()):
                continue
            if node.name not in row_keys:
                gaps.append(f"{module_name}.{node.name}")
    return gaps


def _api_table_row_keys_by_module() -> dict[str, set[str]]:
    row_keys_by_module: dict[str, set[str]] = {}
    for function in api_table_functions():
        table = load_api_table(function)
        if not isinstance(table, Mapping):
            continue
        rows = table.get(_API_TABLE_ROWS_FIELD, [])
        if not isinstance(rows, list):
            continue
        module_row_keys = row_keys_by_module.setdefault(function.module_name, set())
        for row in rows:
            if isinstance(row, Mapping):
                value = row.get(function.row_key_field)
                if isinstance(value, str):
                    module_row_keys.add(value)
    return row_keys_by_module


def _api_table_schema(function: ApiTableFunction, table: Mapping[str, object], gaps: list[str]) -> str:
    label = f"{function.module_name}.{function.function_name}"
    schema = table.get("schema")
    if not isinstance(schema, str) or not schema:
        gaps.append(f"{label}: schema is invalid {schema!r}")
        return ""
    if not schema.startswith("paradev.") or not schema.endswith(".v1"):
        gaps.append(f"{label}: schema {schema!r} does not use paradev.*.v1")
        return ""
    return schema


def _api_table_required_row_text_fields(table: Mapping[str, object]) -> tuple[str, ...]:
    fields = list(_API_TABLE_SHARED_ROW_TEXT_FIELDS)
    for index_name, field in _API_TABLE_SHARED_ROW_OPTIONAL_INDEX_FIELDS.items():
        if index_name in table:
            fields.append(field)
    return tuple(fields)


def _api_table_row_field_set_gaps(function: ApiTableFunction, rows: list[Mapping[str, object]], gaps: list[str]) -> None:
    expected_fields = _api_table_expected_row_fields(rows)
    if not expected_fields:
        return
    expected_field_set = set(expected_fields)
    label = f"{function.module_name}.{function.function_name}"
    for index, row in enumerate(rows):
        fields = set(row)
        for field in sorted(expected_field_set - fields):
            gaps.append(f"{label}: row {index} is missing field {field!r}")
        for field in sorted(fields - expected_field_set):
            gaps.append(f"{label}: row {index} has undocumented field {field!r}")


def _api_table_expected_row_fields(rows: list[Mapping[str, object]]) -> tuple[str, ...]:
    return tuple(rows[0]) if rows else ()


def _api_doc_page_gaps(function: ApiTableFunction, row: Mapping[str, object], index: int, gaps: list[str]) -> None:
    doc_page = row.get("doc_page")
    if not isinstance(doc_page, str) or not exists_file(doc_page):
        gaps.append(f"{function.module_name}.{function.function_name}: row {index} points at missing doc_page {doc_page!r}")
        return
    if not doc_page.startswith("docs/") or not doc_page.endswith(".md"):
        gaps.append(f"{function.module_name}.{function.function_name}: row {index} doc_page {doc_page!r} is not a docs/ markdown page")


def _api_test_anchor_gaps(
    function: ApiTableFunction,
    row: Mapping[str, object],
    index: int,
    test_functions_by_path: dict[str, set[str]],
    gaps: list[str],
) -> None:
    test_anchor = row.get("test_anchor")
    if not isinstance(test_anchor, str) or "::" not in test_anchor:
        gaps.append(f"{function.module_name}.{function.function_name}: row {index} has invalid test_anchor {test_anchor!r}")
        return
    test_path, test_name = test_anchor.split("::", 1)
    if not exists_file(test_path):
        gaps.append(f"{function.module_name}.{function.function_name}: row {index} points at missing test file {test_path!r}")
        return
    if not test_path.startswith("tests/") or not test_path.endswith(".py"):
        gaps.append(f"{function.module_name}.{function.function_name}: row {index} test_anchor {test_anchor!r} is not a tests/ Python anchor")
        return
    function_names = test_functions_by_path.setdefault(test_path, _test_function_names(test_path))
    if test_name not in function_names:
        gaps.append(f"{function.module_name}.{function.function_name}: row {index} points at missing test {test_anchor!r}")


def _test_function_names(path: str) -> set[str]:
    tree = ast.parse(load_txt(path, encoding="utf-8"))
    return {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)}


def _api_reference_renderer_name(function: ApiTableFunction) -> str:
    reference_name = function.function_name.removeprefix("get_").removesuffix("_table")
    return f"render_{reference_name}_reference_markdown"


def _api_reference_markdown_path(markdown: str) -> str:
    for line in markdown.splitlines():
        if " > docs/user-manual/" not in line:
            continue
        path = line.rsplit(" > ", 1)[-1].strip()
        if path.startswith("docs/user-manual/") and path.endswith(".md"):
            return path
    return ""


def _api_reference_markdown_source_gaps(function: ApiTableFunction, markdown: str) -> list[str]:
    label = f"{function.module_name}.{function.function_name}"
    gaps: list[str] = []
    actual = _api_reference_markdown_source_line(markdown)
    if not actual:
        return [f"{label}: markdown is missing source line"]
    catalog_row = _api_reference_markdown_catalog_row(function, label, gaps)
    if catalog_row is None:
        return gaps
    owner_module = catalog_row.get("owner_module")
    table_helper = catalog_row.get("table_helper")
    if not isinstance(owner_module, str) or not owner_module:
        gaps.append(f"{label}: API catalog row has invalid owner_module {owner_module!r}")
        return gaps
    if not isinstance(table_helper, str) or not table_helper:
        gaps.append(f"{label}: API catalog row has invalid table_helper {table_helper!r}")
        return gaps
    expected = f"Generated from `{owner_module}.{table_helper}()`."
    if actual != expected:
        gaps.append(f"{label}: source line {actual!r} != {expected!r}")
    return gaps


def _api_reference_markdown_source_line(markdown: str) -> str:
    for line in markdown.splitlines():
        if line.startswith("Generated from `") and line.endswith("`."):
            return line
    return ""


def _api_reference_markdown_regeneration_note_gaps(function: ApiTableFunction, markdown: str) -> list[str]:
    label = f"{function.module_name}.{function.function_name}"
    gaps: list[str] = []
    actual = _api_reference_markdown_regeneration_note(markdown)
    if not actual:
        return [f"{label}: markdown is missing regeneration note"]
    expected = _api_reference_markdown_renderer_keyword(function, label, "regenerate_when", gaps)
    if not expected:
        return gaps
    if actual != expected:
        gaps.append(f"{label}: regeneration note {actual!r} != {expected!r}")
    return gaps


def _api_reference_markdown_regeneration_note(markdown: str) -> str:
    lines = markdown.splitlines()
    for index, line in enumerate(lines):
        if line != "```bash" or index < 2:
            continue
        note = lines[index - 2].strip()
        if note:
            return note
    return ""


def _api_reference_markdown_regeneration_command_gaps(function: ApiTableFunction, markdown: str) -> list[str]:
    label = f"{function.module_name}.{function.function_name}"
    gaps: list[str] = []
    command = _api_reference_markdown_regeneration_command(markdown)
    if not command:
        return [f"{label}: markdown is missing regeneration command block"]
    catalog_row = _api_reference_markdown_catalog_row(function, label, gaps)
    if catalog_row is None:
        return gaps
    markdown_cli_command = catalog_row.get("markdown_cli_command")
    doc_page = catalog_row.get("doc_page")
    if not isinstance(markdown_cli_command, str) or not markdown_cli_command:
        gaps.append(f"{label}: API catalog row has invalid markdown_cli_command {markdown_cli_command!r}")
        return gaps
    if not isinstance(doc_page, str) or not doc_page:
        gaps.append(f"{label}: API catalog row has invalid doc_page {doc_page!r}")
        return gaps
    expected = f"rtk uv run paradev {markdown_cli_command} > {doc_page}"
    if command != expected:
        gaps.append(f"{label}: regeneration command {command!r} != {expected!r}")
    return gaps


def _api_reference_markdown_regeneration_command(markdown: str) -> str:
    lines = markdown.splitlines()
    for index, line in enumerate(lines[:-2]):
        if line != "```bash" or lines[index + 2] != "```":
            continue
        command = lines[index + 1].strip()
        if command:
            return command
    return ""


def _api_reference_markdown_catalog_row(function: ApiTableFunction, label: str, gaps: list[str]) -> Mapping[str, object] | None:
    from paradev.surfaces import get_api_catalog_table

    table = get_api_catalog_table()
    rows = table.get(_API_TABLE_ROWS_FIELD)
    if not isinstance(rows, list):
        gaps.append(f"{label}: API catalog rows are invalid {type(rows).__name__}")
        return None
    matches = [row for row in rows if isinstance(row, Mapping) and row.get("table_helper") == function.function_name]
    if not matches:
        gaps.append(f"{label}: API catalog has no row for table helper {function.function_name!r}")
        return None
    if len(matches) > 1:
        gaps.append(f"{label}: API catalog has duplicate rows for table helper {function.function_name!r}")
        return None
    return matches[0]


def _api_reference_markdown_summary_gaps(function: ApiTableFunction, table: object, markdown: str) -> list[str]:
    if function.function_name == _API_CATALOG_TABLE_FUNCTION_NAME:
        return []
    label = f"{function.module_name}.{function.function_name}"
    if not isinstance(table, Mapping):
        return [f"{label}: table is {type(table).__name__}, not a mapping"]
    gaps: list[str] = []
    lines = markdown.splitlines()
    expected_summary_lines = _api_reference_markdown_expected_summary_lines(function, label, table, gaps)
    for field, line in expected_summary_lines:
        if line not in lines:
            gaps.append(f"{label}: markdown is missing summary {field} line {line!r}")
        line_prefix = _api_reference_markdown_summary_line_prefix(line)
        if line_prefix:
            _api_reference_markdown_stale_summary_line_gaps(label, markdown, line, line_prefix, field, gaps)
    _api_reference_markdown_unexpected_summary_line_gaps(label, markdown, expected_summary_lines, gaps)
    return gaps


def _api_reference_markdown_title_gaps(function: ApiTableFunction, markdown: str) -> list[str]:
    label = f"{function.module_name}.{function.function_name}"
    gaps: list[str] = []
    title = _api_reference_markdown_renderer_keyword(function, label, "title", gaps)
    if not title:
        return gaps
    expected = f"# {title}"
    lines = markdown.splitlines()
    actual = lines[0] if lines else ""
    if actual != expected:
        gaps.append(f"{label}: markdown title line {actual!r} != {expected!r}")
    return gaps


def _api_reference_markdown_renderer_keyword(function: ApiTableFunction, label: str, name: str, gaps: list[str]) -> str:
    node = _api_reference_markdown_renderer_node(function, label, gaps)
    if node is None:
        return ""
    for child in ast.walk(node):
        if not isinstance(child, ast.Call) or not isinstance(child.func, ast.Name) or child.func.id not in _API_REFERENCE_MARKDOWN_RENDERER_CALLS:
            continue
        for keyword in child.keywords:
            if keyword.arg == name and isinstance(keyword.value, ast.Constant) and isinstance(keyword.value.value, str):
                return keyword.value.value
            if keyword.arg == name and isinstance(keyword.value, ast.Name):
                value = getattr(importlib.import_module(function.module_name), keyword.value.id, None)
                if isinstance(value, str):
                    return value
        gaps.append(f"{label}: renderer {node.name} has no literal {name}")
        return ""
    gaps.append(f"{label}: renderer {node.name} does not call an API reference markdown helper")
    return ""


def _api_reference_markdown_expected_summary_lines(
    function: ApiTableFunction,
    label: str,
    table: Mapping[str, object],
    gaps: list[str],
) -> list[tuple[str, str]]:
    row_count = table.get(_API_TABLE_ROW_COUNT_FIELD)
    if not isinstance(row_count, int):
        gaps.append(f"{label}: row_count is invalid {row_count!r}")
        return []
    if not _api_reference_markdown_has_standard_indexes(table):
        surface_summary_lines = _api_reference_markdown_surface_summary_lines(function, label, table, gaps)
        if surface_summary_lines:
            return [
                (_API_TABLE_ROW_COUNT_FIELD, f"- {_API_REFERENCE_MARKDOWN_ROW_COUNT_TITLE}: {row_count}"),
                *surface_summary_lines,
            ]
        return [
            (_API_TABLE_ROW_COUNT_FIELD, f"- {_API_REFERENCE_MARKDOWN_ROW_COUNT_TITLE}: {row_count}"),
            *_api_reference_markdown_custom_summary_lines(function, label, table, gaps),
        ]
    module_label = _api_reference_markdown_renderer_module_label(function, label, gaps)
    if not module_label:
        return []
    expected_lines = api_summary_lines(table, module_label=module_label)
    fields = (_API_TABLE_ROW_COUNT_FIELD, *(spec.index_name for spec in API_STANDARD_INDEXES))
    return list(zip(fields, expected_lines, strict=False))


def _api_reference_markdown_has_standard_indexes(table: Mapping[str, object]) -> bool:
    return all(spec.index_name in table for spec in API_STANDARD_INDEXES)


def _api_reference_markdown_renderer_module_label(function: ApiTableFunction, label: str, gaps: list[str]) -> str:
    node = _api_reference_markdown_renderer_node(function, label, gaps)
    if node is None:
        return ""
    return _api_reference_markdown_renderer_call_module_label(label, node, node.name, gaps)


def _api_reference_markdown_module_path(module_name: str) -> str:
    source_path = pj("src", *module_name.split(".")).replace("\\", "/") + ".py"
    if exists_file(source_path):
        return source_path
    package_path = pj("src", *module_name.split("."), "__init__.py").replace("\\", "/")
    if exists_file(package_path):
        return package_path
    return source_path


def _api_reference_markdown_renderer_node(
    function: ApiTableFunction,
    label: str,
    gaps: list[str],
) -> ast.FunctionDef | None:
    path = _api_reference_markdown_module_path(function.module_name)
    if not exists_file(path):
        gaps.append(f"{label}: source module path {path!r} is missing")
        return None
    tree = ast.parse(load_txt(path, encoding="utf-8"))
    renderer_name = _api_reference_renderer_name(function)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == renderer_name:
            return node
    gaps.append(f"{label}: source module has no renderer {renderer_name}")
    return None


def _api_reference_markdown_renderer_call_module_label(
    label: str,
    node: ast.FunctionDef,
    renderer_name: str,
    gaps: list[str],
) -> str:
    for child in ast.walk(node):
        if not isinstance(child, ast.Call) or not isinstance(child.func, ast.Name) or child.func.id != "api_standard_reference_markdown":
            continue
        for keyword in child.keywords:
            if keyword.arg == "module_label" and isinstance(keyword.value, ast.Constant) and isinstance(keyword.value.value, str):
                return keyword.value.value
        gaps.append(f"{label}: renderer {renderer_name} has no literal module_label")
        return ""
    gaps.append(f"{label}: renderer {renderer_name} does not call api_standard_reference_markdown")
    return ""


def _api_reference_markdown_surface_summary_lines(
    function: ApiTableFunction,
    label: str,
    table: Mapping[str, object],
    gaps: list[str],
) -> list[tuple[str, str]]:
    node = _api_reference_markdown_renderer_node(function, label, gaps)
    if node is None or not _api_reference_markdown_renderer_calls(node, "api_surface_reference_markdown"):
        return []
    lines: list[tuple[str, str]] = []
    surface_index = _api_reference_markdown_summary_index(label, table, "surface_index", gaps)
    if surface_index is not None:
        lines.append(("surface_index", f"- Surfaces / Surface 数: {len(surface_index)}"))
    if "feature_index" in table:
        feature_index = _api_reference_markdown_summary_index(label, table, "feature_index", gaps)
        if feature_index is not None:
            lines.append(("feature_index", f"- Features / Feature 数: {len(feature_index)}"))
    return lines


def _api_reference_markdown_renderer_calls(node: ast.FunctionDef, name: str) -> bool:
    return any(isinstance(child, ast.Call) and isinstance(child.func, ast.Name) and child.func.id == name for child in ast.walk(node))


def _api_reference_markdown_summary_index(
    label: str,
    table: Mapping[str, object],
    index_name: str,
    gaps: list[str],
) -> Mapping[object, object] | None:
    index = table.get(index_name)
    if not isinstance(index, Mapping):
        gaps.append(f"{label}: summary {index_name} is {type(index).__name__}, not a mapping")
        return None
    return index


def _api_reference_markdown_custom_summary_lines(
    function: ApiTableFunction,
    label: str,
    table: Mapping[str, object],
    gaps: list[str],
) -> list[tuple[str, str]]:
    node = _api_reference_markdown_renderer_node(function, label, gaps)
    if node is None:
        return []
    lines: list[tuple[str, str]] = []
    for summary_node in _api_reference_markdown_custom_summary_nodes(node):
        count_line = _api_reference_markdown_custom_summary_count_line(summary_node)
        if count_line is not None:
            count = _api_reference_markdown_custom_summary_count(label, table, count_line, gaps)
            if count is not None:
                lines.append((count_line.field, f"{count_line.prefix}{count}"))
            continue
        literal_line = _api_reference_markdown_custom_summary_literal_line(summary_node)
        if literal_line is not None:
            lines.append(literal_line)
    return lines


def _api_reference_markdown_custom_summary_nodes(node: ast.FunctionDef) -> list[ast.AST]:
    for child in ast.walk(node):
        if not isinstance(child, ast.Call) or not isinstance(child.func, ast.Name):
            continue
        if child.func.id != "api_indexed_reference_sections":
            continue
        for keyword in child.keywords:
            if keyword.arg == "summary_lines" and isinstance(keyword.value, ast.List | ast.Tuple):
                return list(keyword.value.elts)
    return []


def _api_reference_markdown_custom_summary_count_line(node: ast.AST) -> ApiSummaryCountLine | None:
    if not isinstance(node, ast.JoinedStr):
        return None
    prefix_parts: list[str] = []
    count_line: ApiSummaryCountLine | None = None
    seen_count = False
    for value in node.values:
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            if seen_count and value.value:
                return None
            if not seen_count:
                prefix_parts.append(value.value)
            continue
        if not isinstance(value, ast.FormattedValue) or seen_count:
            return None
        count_line = _api_reference_markdown_len_table_count_line(value.value, "".join(prefix_parts))
        if count_line is None:
            return None
        seen_count = True
    prefix = "".join(prefix_parts)
    if not seen_count or not prefix.startswith("- ") or not prefix.endswith(": "):
        return None
    return count_line


def _api_reference_markdown_custom_summary_literal_line(node: ast.AST) -> tuple[str, str] | None:
    if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
        return None
    line = node.value
    if not line.startswith("- "):
        return None
    return _api_reference_markdown_summary_literal_field(line), line


def _api_reference_markdown_summary_literal_field(line: str) -> str:
    prefix = _api_reference_markdown_summary_line_prefix(line)
    label = prefix.removeprefix("- ").removesuffix(": ") if prefix else line.removeprefix("- ")
    english_label = label.split("/", 1)[0].strip().lower()
    field = re.sub(r"[^a-z0-9]+", "_", english_label).strip("_")
    return field or "literal"


def _api_reference_markdown_custom_summary_count(
    label: str,
    table: Mapping[str, object],
    count_line: ApiSummaryCountLine,
    gaps: list[str],
) -> int | None:
    index = _api_reference_markdown_summary_index(label, table, count_line.index_name, gaps)
    if index is None:
        return None
    if count_line.index_key is None:
        return len(index)
    bucket = index.get(count_line.index_key, [])
    if isinstance(bucket, (str, bytes)) or isinstance(bucket, Mapping) or not isinstance(bucket, Sized):
        gaps.append(f"{label}: summary {count_line.field} is {type(bucket).__name__}, not a sized bucket")
        return None
    return len(bucket)


def _api_reference_markdown_len_table_count_line(node: ast.AST, prefix: str) -> ApiSummaryCountLine | None:
    if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name) or node.func.id != "len":
        return None
    if len(node.args) != 1 or node.keywords:
        return None
    index_name = _api_reference_markdown_table_subscript_name(node.args[0])
    if index_name:
        return ApiSummaryCountLine(field=index_name, prefix=prefix, index_name=index_name)
    index_key_count = _api_reference_markdown_table_get_count(node.args[0])
    if index_key_count is None:
        return None
    index_name, index_key = index_key_count
    return ApiSummaryCountLine(
        field=f"{index_name}[{index_key!r}]",
        prefix=prefix,
        index_name=index_name,
        index_key=index_key,
    )


def _api_reference_markdown_table_subscript_name(node: ast.AST) -> str:
    if not isinstance(node, ast.Subscript) or not isinstance(node.value, ast.Name) or node.value.id != "table":
        return ""
    if not isinstance(node.slice, ast.Constant) or not isinstance(node.slice.value, str):
        return ""
    return node.slice.value


def _api_reference_markdown_table_get_count(node: ast.AST) -> tuple[str, str] | None:
    if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute) or node.func.attr != "get":
        return None
    if len(node.args) not in {1, 2} or node.keywords:
        return None
    index_name = _api_reference_markdown_table_subscript_name(node.func.value)
    if not index_name:
        return None
    key = node.args[0]
    if not isinstance(key, ast.Constant) or not isinstance(key.value, str):
        return None
    if len(node.args) == 2 and not _api_reference_markdown_empty_list(node.args[1]):
        return None
    return index_name, key.value


def _api_reference_markdown_empty_list(node: ast.AST) -> bool:
    return isinstance(node, ast.List) and not node.elts


def _api_reference_markdown_summary_line_prefix(line: str) -> str:
    if ": " not in line:
        return ""
    return line.rsplit(": ", 1)[0] + ": "


def _api_reference_markdown_heading_gaps(function: ApiTableFunction, table: object, markdown: str) -> list[str]:
    label = f"{function.module_name}.{function.function_name}"
    if not isinstance(table, Mapping):
        return [f"{label}: table is {type(table).__name__}, not a mapping"]
    lines = markdown.splitlines()
    gaps: list[str] = []
    headings = _api_reference_markdown_headings(function, table, gaps)
    for heading in headings:
        if heading not in lines:
            gaps.append(f"{label}: markdown is missing section heading {heading!r}")
    _api_reference_markdown_unexpected_heading_gaps(label, lines, headings, gaps)
    return gaps


def _api_reference_markdown_unexpected_heading_gaps(
    label: str,
    lines: list[str],
    expected_headings: list[str],
    gaps: list[str],
) -> None:
    expected = set(expected_headings)
    seen: set[str] = set()
    for line in lines:
        if not line.startswith("## "):
            continue
        if line in seen:
            gaps.append(f"{label}: markdown has duplicate section heading {line!r}")
            continue
        seen.add(line)
        if line not in expected:
            gaps.append(f"{label}: markdown has unexpected section heading {line!r}")


def _api_reference_markdown_headings(function: ApiTableFunction, table: Mapping[str, object], gaps: list[str]) -> list[str]:
    label = f"{function.module_name}.{function.function_name}"
    if function.function_name == _API_CATALOG_TABLE_FUNCTION_NAME:
        return [
            _API_REFERENCE_MARKDOWN_SUMMARY_HEADING,
            *_API_CATALOG_MARKDOWN_EXTRA_HEADINGS,
            *_api_reference_markdown_index_headings(table, _API_CATALOG_MARKDOWN_INDEX_HEADINGS, label, gaps),
            _API_CATALOG_MARKDOWN_TABLE_HEADING,
        ]
    return [
        _API_REFERENCE_MARKDOWN_SUMMARY_HEADING,
        *_api_reference_markdown_index_headings(table, _API_REFERENCE_MARKDOWN_INDEX_HEADINGS, label, gaps),
        _API_REFERENCE_MARKDOWN_TABLE_HEADING,
    ]


def _api_reference_markdown_index_headings(
    table: Mapping[str, object],
    headings: Mapping[str, str],
    label: str,
    gaps: list[str],
) -> list[str]:
    expected_headings: list[str] = []
    for index_name in api_table_index_names(table):
        heading = headings.get(index_name)
        if heading is None:
            gaps.append(f"{label}: markdown has no configured section heading for index {index_name!r}")
            continue
        expected_headings.append(heading)
    return expected_headings


def _api_reference_markdown_row_gaps(function: ApiTableFunction, table: object, markdown: str) -> list[str]:
    if function.function_name == _API_CATALOG_TABLE_FUNCTION_NAME:
        return []
    label = f"{function.module_name}.{function.function_name}"
    if not isinstance(table, Mapping):
        return [f"{label}: table is {type(table).__name__}, not a mapping"]
    row_gaps, rows = _api_table_rows(function, table)
    gaps = [*row_gaps]
    expected_key_cells: set[str] = set()
    lines = markdown.splitlines()
    for index, row in enumerate(rows):
        row_key = _api_non_empty_row_string(function, row, index, function.row_key_field, gaps)
        if row_key:
            expected_key_cells.add(_api_reference_markdown_code_cell(row_key))
        expected_rows = _api_reference_markdown_row_candidates(function, row, index, label, gaps)
        if row_key and expected_rows and not any(expected_row in lines for expected_row in expected_rows):
            gaps.append(f"{label}: markdown is missing complete table row {row_key!r}")
    _api_reference_markdown_stale_table_row_gaps(label, markdown, expected_key_cells, gaps)
    return gaps


def _api_reference_markdown_row_candidates(
    function: ApiTableFunction,
    row: Mapping[str, object],
    index: int,
    label: str,
    gaps: list[str],
) -> list[str]:
    cell_rows: list[list[str]] = [[]]
    for field in _api_reference_markdown_row_fields(function, row):
        value = row.get(field)
        cell_candidates = _api_reference_markdown_cell_candidates(field, value, index, label, gaps)
        if not cell_candidates:
            return []
        cell_rows = [cells + [candidate] for cells in cell_rows for candidate in cell_candidates]
    return ["| " + " | ".join(cells) + " |" for cells in cell_rows]


def _api_reference_markdown_stale_table_row_gaps(
    label: str,
    markdown: str,
    expected_key_cells: set[str],
    gaps: list[str],
    *,
    heading: str = _API_REFERENCE_MARKDOWN_TABLE_HEADING,
    row_label: str = "table row",
    context: str = "",
) -> None:
    for line in _api_reference_markdown_section_table_rows(markdown, heading):
        cells = _api_reference_markdown_table_cells(line)
        if not cells:
            continue
        key_cell = cells[0]
        if key_cell.startswith("`") and key_cell.endswith("`") and key_cell not in expected_key_cells:
            context_text = f" in {context}" if context else ""
            gaps.append(f"{label}: markdown has stale {row_label} {key_cell}{context_text}")


def _api_reference_markdown_section_table_rows(markdown: str, heading: str) -> list[str]:
    rows: list[str] = []
    in_section = False
    for line in markdown.splitlines():
        if line == heading:
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section and line.startswith("| ") and line.endswith(" |"):
            rows.append(line)
    return rows


def _api_reference_markdown_section_bullets(markdown: str, heading: str) -> list[str]:
    bullets: list[str] = []
    in_section = False
    for line in markdown.splitlines():
        if line == heading:
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section and line.startswith("- "):
            bullets.append(line)
    return bullets


def _api_reference_markdown_stale_summary_line_gaps(
    label: str,
    markdown: str,
    expected_line: str,
    line_prefix: str,
    field: str,
    gaps: list[str],
) -> None:
    for line in _api_reference_markdown_section_bullets(markdown, _API_REFERENCE_MARKDOWN_SUMMARY_HEADING):
        if line.startswith(line_prefix) and line != expected_line:
            gaps.append(f"{label}: markdown has stale summary {field} line {line!r}")


def _api_reference_markdown_unexpected_summary_line_gaps(
    label: str,
    markdown: str,
    expected_summary_lines: list[tuple[str, str]],
    gaps: list[str],
) -> None:
    expected_lines = {line for _field, line in expected_summary_lines}
    expected_prefixes = {prefix for _field, line in expected_summary_lines if (prefix := _api_reference_markdown_summary_line_prefix(line))}
    for line in _api_reference_markdown_section_bullets(markdown, _API_REFERENCE_MARKDOWN_SUMMARY_HEADING):
        if line in expected_lines or any(line.startswith(prefix) for prefix in expected_prefixes):
            continue
        gaps.append(f"{label}: markdown has unexpected summary line {line!r}")


def _api_reference_markdown_table_cells(line: str) -> list[str]:
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    if not cells or all(set(cell) <= {"-"} for cell in cells):
        return []
    return cells


def _api_reference_markdown_row_fields(function: ApiTableFunction, row: Mapping[str, object]) -> tuple[str, ...]:
    module = importlib.import_module(function.module_name)
    constant_name = f"_{function.function_name.removeprefix('get_').removesuffix('_table').upper()}_STANDARD_FIELDS"
    fields = getattr(module, constant_name, None)
    if _api_reference_markdown_field_tuple(fields, row):
        return tuple(fields)
    return tuple(row)


def _api_reference_markdown_field_tuple(value: object, row: Mapping[str, object]) -> bool:
    return isinstance(value, tuple) and all(isinstance(field, str) and field in row for field in value)


def _api_reference_markdown_cell_candidates(field: str, value: object, index: int, label: str, gaps: list[str]) -> list[str]:
    values = _api_reference_markdown_string_values(value)
    if values is not None:
        return [_api_reference_markdown_code_list(values)]
    if field == "value":
        return list(dict.fromkeys((_api_reference_markdown_code_cell(value), _api_reference_markdown_cell(value))))
    if isinstance(value, str):
        return [_api_reference_markdown_code_cell(value)]
    gaps.append(f"{label}: row {index} has invalid markdown field {field} {value!r}")
    return []


def _api_reference_markdown_string_values(value: object) -> list[str] | None:
    if isinstance(value, (str, bytes)) or isinstance(value, Mapping):
        return None
    if not isinstance(value, Iterable):
        return None
    values = list(value)
    if all(isinstance(item, str) for item in values):
        return values
    return None


def _api_reference_markdown_index_gaps(function: ApiTableFunction, table: object, markdown: str) -> list[str]:
    label = f"{function.module_name}.{function.function_name}"
    if not isinstance(table, Mapping):
        return [f"{label}: table is {type(table).__name__}, not a mapping"]
    gaps: list[str] = []
    lines = markdown.splitlines()
    headings = _api_reference_markdown_index_heading_map(function)
    for index_name in api_table_index_names(table):
        index = table[index_name]
        if not isinstance(index, Mapping):
            gaps.append(f"{label}: {index_name} is not a mapping")
            continue
        expected_key_cells: set[str] = set()
        for key, values in index.items():
            if isinstance(key, str) and key:
                expected_key_cells.add(_api_reference_markdown_code_cell(key))
            expected_row = _api_reference_markdown_index_row(label, index_name, key, values, gaps)
            if expected_row and expected_row not in lines:
                gaps.append(f"{label}: markdown is missing {index_name} index row {key!r}")
        heading = headings.get(index_name)
        if heading:
            _api_reference_markdown_stale_table_row_gaps(
                label,
                markdown,
                expected_key_cells,
                gaps,
                heading=heading,
                row_label="index row",
                context=index_name,
            )
    return gaps


def _api_reference_markdown_index_heading_map(function: ApiTableFunction) -> Mapping[str, str]:
    if function.function_name == _API_CATALOG_TABLE_FUNCTION_NAME:
        return _API_CATALOG_MARKDOWN_INDEX_HEADINGS
    return _API_REFERENCE_MARKDOWN_INDEX_HEADINGS


def _api_reference_markdown_index_row(label: str, index_name: str, key: object, values: object, gaps: list[str]) -> str:
    if not isinstance(key, str) or not key:
        gaps.append(f"{label}: {index_name} has invalid index key {key!r}")
        return ""
    value_list = _api_reference_markdown_string_values(values)
    if value_list is None:
        gaps.append(f"{label}: {index_name} key {key!r} has invalid values {values!r}")
        return ""
    cells = ", ".join(_api_reference_markdown_code_cell(value) for value in value_list)
    return f"| {_api_reference_markdown_code_cell(key)} | {len(value_list)} | {cells} |"


def _api_reference_markdown_catalog_table_gaps(function: ApiTableFunction, table: object, markdown: str) -> list[str]:
    if function.function_name != _API_CATALOG_TABLE_FUNCTION_NAME:
        return []
    label = f"{function.module_name}.{function.function_name}"
    if not isinstance(table, Mapping):
        return [f"{label}: table is {type(table).__name__}, not a mapping"]
    row_gaps, rows = _api_table_rows(function, table)
    gaps = [*row_gaps]
    expected_key_cells: set[str] = set()
    lines = markdown.splitlines()
    for index, row in enumerate(rows):
        expected_row = _api_reference_markdown_catalog_table_row(row, index, label, gaps)
        if not expected_row:
            continue
        row_id = row["id"]
        expected_key_cells.add(_api_reference_markdown_code_cell(row_id))
        if expected_row not in lines:
            gaps.append(f"{label}: markdown is missing catalog table row {row_id!r}")
    _api_reference_markdown_stale_table_row_gaps(
        label,
        markdown,
        expected_key_cells,
        gaps,
        heading=_API_CATALOG_MARKDOWN_TABLE_HEADING,
        row_label="catalog table row",
    )
    return gaps


def _api_reference_markdown_catalog_table_row(row: Mapping[str, object], index: int, label: str, gaps: list[str]) -> str:
    cells: list[str] = []
    for field in _API_CATALOG_MARKDOWN_ROW_FIELDS:
        cell = _api_reference_markdown_catalog_table_cell(row, index, field, label, gaps)
        if cell is None:
            return ""
        cells.append(cell)
    return "| " + " | ".join(cells) + " |"


def _api_reference_markdown_catalog_table_cell(
    row: Mapping[str, object],
    index: int,
    field: str,
    label: str,
    gaps: list[str],
) -> str | None:
    value = row.get(field)
    if field in _API_CATALOG_MARKDOWN_ROW_LIST_FIELDS:
        values = _api_reference_markdown_string_list(value)
        if values:
            return _api_reference_markdown_code_list(values)
        gaps.append(f"{label}: catalog table row {index} has invalid {field} {value!r}")
        return None
    if field in _API_CATALOG_MARKDOWN_ROW_TEXT_FIELDS:
        if isinstance(value, str) and value:
            return _api_reference_markdown_cell(value)
        if isinstance(value, int):
            return _api_reference_markdown_cell(value)
        gaps.append(f"{label}: catalog table row {index} has invalid {field} {value!r}")
        return None
    if isinstance(value, str) and (value or field in _API_CATALOG_MARKDOWN_ROW_OPTIONAL_CODE_FIELDS):
        return _api_reference_markdown_code_cell(value)
    gaps.append(f"{label}: catalog table row {index} has invalid {field} {value!r}")
    return None


def _api_reference_markdown_catalog_summary_gaps(function: ApiTableFunction, table: object, markdown: str) -> list[str]:
    if function.function_name != _API_CATALOG_TABLE_FUNCTION_NAME:
        return []
    label = f"{function.module_name}.{function.function_name}"
    if not isinstance(table, Mapping):
        return [f"{label}: table is {type(table).__name__}, not a mapping"]
    summary = table.get("summary")
    if not isinstance(summary, Mapping):
        return [f"{label}: summary is {type(summary).__name__}, not a mapping"]
    gaps: list[str] = []
    for field, title in _api_reference_markdown_catalog_summary_fields().items():
        value = summary.get(field)
        if not isinstance(value, int):
            gaps.append(f"{label}: summary {field} is invalid {value!r}")
            continue
        line = f"- {title}: {value}"
        if line not in markdown.splitlines():
            gaps.append(f"{label}: markdown is missing summary {field} line {line!r}")
        _api_reference_markdown_stale_summary_line_gaps(
            label,
            markdown,
            line,
            f"- {title}: ",
            field,
            gaps,
        )
    return gaps


def _api_reference_markdown_catalog_summary_fields() -> Mapping[str, str]:
    return {
        "reference_count": "References / Reference 数",
        "layer_count": "Layers / Layer 数",
        "feature_count": "Features / Feature 数",
        "kind_count": "Kinds / 类型数",
        "reference_group_count": "Reference groups / Reference 分组数",
        "index_count": "Index dimensions / Index 维度数",
        "owner_module_count": "Owner modules / Owner Module 数",
        "surface_count": "Surfaces / Surface 数",
        "cli_command_count": "CLI commands / CLI 命令数",
        "selector_helper_count": "Selector helpers / Selector helper 数",
        "doc_page_count": "Doc pages / Doc page 数",
    }


def _api_reference_markdown_catalog_group_gaps(function: ApiTableFunction, table: object, markdown: str) -> list[str]:
    if function.function_name != _API_CATALOG_TABLE_FUNCTION_NAME:
        return []
    label = f"{function.module_name}.{function.function_name}"
    if not isinstance(table, Mapping):
        return [f"{label}: table is {type(table).__name__}, not a mapping"]
    reference_groups = table.get("reference_groups")
    if not isinstance(reference_groups, list):
        return [f"{label}: reference_groups is {type(reference_groups).__name__}, not a list"]
    gaps: list[str] = []
    expected_key_cells: set[str] = set()
    lines = markdown.splitlines()
    for index, row in enumerate(reference_groups):
        if not isinstance(row, Mapping):
            gaps.append(f"{label}: reference_groups row {index} is {type(row).__name__}, not a mapping")
            continue
        expected_row = _api_reference_markdown_catalog_group_row(row, index, label, gaps)
        if not expected_row:
            continue
        group_id = row["id"]
        expected_key_cells.add(_api_reference_markdown_code_cell(group_id))
        if expected_row not in lines:
            gaps.append(f"{label}: markdown is missing reference group row {group_id!r}")
    _api_reference_markdown_stale_table_row_gaps(
        label,
        markdown,
        expected_key_cells,
        gaps,
        heading=_API_CATALOG_REFERENCE_GROUPS_MARKDOWN_HEADING,
        row_label="reference group row",
    )
    return gaps


def _api_reference_markdown_catalog_group_row(row: Mapping[str, object], index: int, label: str, gaps: list[str]) -> str:
    group_id = row.get("id")
    title = row.get("title")
    reference_count = row.get("reference_count")
    kinds = row.get("kinds")
    reference_ids = row.get("reference_ids")
    usage = row.get("usage")
    if not isinstance(group_id, str) or not group_id or not isinstance(title, str) or not title:
        gaps.append(f"{label}: reference_groups row {index} has invalid id/title")
        return ""
    if not isinstance(reference_count, int):
        gaps.append(f"{label}: reference_groups row {index} has invalid reference_count {reference_count!r}")
        return ""
    if not _api_reference_markdown_string_list(kinds) or not _api_reference_markdown_string_list(reference_ids):
        gaps.append(f"{label}: reference_groups row {index} has invalid kinds/reference_ids")
        return ""
    if not isinstance(usage, str) or not usage:
        gaps.append(f"{label}: reference_groups row {index} has invalid usage {usage!r}")
        return ""
    return (
        f"| `{group_id}` | {title} | {reference_count} | "
        f"{_api_reference_markdown_code_list(kinds)} | {_api_reference_markdown_code_list(reference_ids)} | {usage} |"
    )


def _api_reference_markdown_string_list(value: object) -> list[str]:
    if isinstance(value, list) and all(isinstance(item, str) and item for item in value):
        return list(value)
    return []


def _api_reference_markdown_code_list(value: object) -> str:
    return ", ".join(f"`{item}`" for item in _api_reference_markdown_string_list(value))


def _api_reference_markdown_cell(value: object) -> str:
    return str(value).replace("\n", " ").replace("|", "\\|").strip()


def _api_reference_markdown_code_cell(value: object) -> str:
    text = _api_reference_markdown_cell(value)
    return f"`{text}`" if text else ""


def _api_reference_markdown_catalog_index_catalog_gaps(function: ApiTableFunction, table: object, markdown: str) -> list[str]:
    if function.function_name != _API_CATALOG_TABLE_FUNCTION_NAME:
        return []
    label = f"{function.module_name}.{function.function_name}"
    if not isinstance(table, Mapping):
        return [f"{label}: table is {type(table).__name__}, not a mapping"]
    index_catalog = table.get("index_catalog")
    if not isinstance(index_catalog, list):
        return [f"{label}: index_catalog is {type(index_catalog).__name__}, not a list"]
    gaps: list[str] = []
    expected_key_cells: set[str] = set()
    lines = markdown.splitlines()
    for index, row in enumerate(index_catalog):
        if not isinstance(row, Mapping):
            gaps.append(f"{label}: index_catalog row {index} is {type(row).__name__}, not a mapping")
            continue
        expected_row = _api_reference_markdown_catalog_index_catalog_row(row, index, label, gaps)
        if not expected_row:
            continue
        row_id = row["id"]
        expected_key_cells.add(_api_reference_markdown_code_cell(row_id))
        if expected_row not in lines:
            gaps.append(f"{label}: markdown is missing index_catalog row {row_id!r}")
    _api_reference_markdown_stale_table_row_gaps(
        label,
        markdown,
        expected_key_cells,
        gaps,
        heading=_API_CATALOG_INDEX_CATALOG_MARKDOWN_HEADING,
        row_label="index_catalog row",
    )
    return gaps


def _api_reference_markdown_catalog_index_catalog_row(row: Mapping[str, object], index: int, label: str, gaps: list[str]) -> str:
    row_id = row.get("id")
    table_path = row.get("table_path")
    python_helper = row.get("python_helper")
    usage = row.get("usage")
    if not isinstance(row_id, str) or not row_id:
        gaps.append(f"{label}: index_catalog row {index} has invalid id {row_id!r}")
        return ""
    if not isinstance(table_path, str) or not table_path:
        gaps.append(f"{label}: index_catalog row {index} has invalid table_path {table_path!r}")
        return ""
    if not isinstance(python_helper, str) or not python_helper:
        gaps.append(f"{label}: index_catalog row {index} has invalid python_helper {python_helper!r}")
        return ""
    if not isinstance(usage, str) or not usage:
        gaps.append(f"{label}: index_catalog row {index} has invalid usage {usage!r}")
        return ""
    return f"| `{row_id}` | `{table_path}` | `{python_helper}` | {usage} |"


def _api_catalog_table_rows() -> tuple[list[str], Mapping[str, object] | None, list[Mapping[str, object]]]:
    from paradev.surfaces import get_api_catalog_table

    table = get_api_catalog_table()
    if not isinstance(table, Mapping):
        return [f"api catalog: table is {type(table).__name__}, not a mapping"], None, []
    rows = table.get(_API_TABLE_ROWS_FIELD)
    if not isinstance(rows, list):
        return [f"api catalog: rows is {type(rows).__name__}, not a list"], table, []
    gaps: list[str] = []
    row_list: list[Mapping[str, object]] = []
    for index, row in enumerate(rows):
        if isinstance(row, Mapping):
            row_list.append(row)
            continue
        gaps.append(f"api catalog: row {index} is {type(row).__name__}, not a mapping")
    return gaps, table, row_list


def _api_catalog_rows_by_id(rows: list[Mapping[str, object]], gaps: list[str]) -> dict[str, tuple[int, Mapping[str, object]]]:
    rows_by_id: dict[str, tuple[int, Mapping[str, object]]] = {}
    for index, row in enumerate(rows):
        row_id = _api_catalog_row_text(row, index, "id", gaps)
        if row_id:
            rows_by_id[row_id] = (index, row)
    return rows_by_id


def _api_catalog_markdown_gaps(row: Mapping[str, object], index: int, gaps: list[str]) -> None:
    row_id = _api_catalog_row_text(row, index, "id", gaps)
    owner_module = _api_catalog_row_text(row, index, "owner_module", gaps)
    markdown_helper = _api_catalog_row_text(row, index, "markdown_helper", gaps)
    doc_page = _api_catalog_row_text(row, index, "doc_page", gaps)
    label = row_id or f"row {index}"
    if not owner_module or not markdown_helper or not doc_page:
        return
    module = importlib.import_module(owner_module)
    renderer = getattr(module, markdown_helper, None)
    if not callable(renderer):
        gaps.append(f"api catalog {label}: missing callable {owner_module}.{markdown_helper}")
        return
    markdown = renderer()
    if not isinstance(markdown, str):
        gaps.append(f"api catalog {label}: {owner_module}.{markdown_helper} returned {type(markdown).__name__}, not str")
        return
    if not exists_file(doc_page):
        gaps.append(f"api catalog {label}: markdown helper points at missing docs page {doc_page!r}")
        return
    existing = load_txt(doc_page, encoding="utf-8")
    if existing != markdown:
        gaps.append(f"api catalog {label}: {doc_page} differs from {owner_module}.{markdown_helper}() output")


def _api_catalog_test_anchor_gaps(
    row: Mapping[str, object],
    index: int,
    test_functions_by_path: dict[str, set[str]],
    gaps: list[str],
) -> None:
    row_id = _api_catalog_row_text(row, index, "id", gaps)
    label = row_id or f"row {index}"
    test_anchor = row.get("test_anchor")
    if not isinstance(test_anchor, str) or "::" not in test_anchor:
        gaps.append(f"api catalog {label}: row {index} has invalid test_anchor {test_anchor!r}")
        return
    test_path, test_name = test_anchor.split("::", 1)
    if not exists_file(test_path):
        gaps.append(f"api catalog {label}: row {index} points at missing test file {test_path!r}")
        return
    if not test_path.startswith("tests/") or not test_path.endswith(".py"):
        gaps.append(f"api catalog {label}: row {index} test_anchor {test_anchor!r} is not a tests/ Python anchor")
        return
    function_names = test_functions_by_path.setdefault(test_path, _test_function_names(test_path))
    if test_name not in function_names:
        gaps.append(f"api catalog {label}: row {index} points at missing test {test_anchor!r}")


def _api_catalog_payload_metadata_row_gaps(row: Mapping[str, object], index: int, gaps: list[str]) -> None:
    row_id = _api_catalog_row_text(row, index, "id", gaps)
    payload = _api_catalog_source_helper_payload(row, index, gaps)
    if not row_id or payload is None:
        return
    _api_catalog_payload_field_gaps(
        row,
        index,
        "schema",
        _api_catalog_payload_schema(payload),
        gaps,
    )
    _api_catalog_payload_field_gaps(
        row,
        index,
        "row_count",
        _api_catalog_payload_row_count(row_id, payload),
        gaps,
    )
    _api_catalog_payload_field_gaps(
        row,
        index,
        "index_names",
        _api_catalog_payload_index_names(payload),
        gaps,
    )
    _api_catalog_payload_surface_gaps(row, index, row_id, payload, gaps)


def _api_catalog_row_shape_row_gaps(
    row: Mapping[str, object],
    index: int,
    seen_values: dict[str, dict[str, int]],
    gaps: list[str],
) -> None:
    _api_catalog_row_field_set_gaps(row, index, gaps)
    for field in _API_CATALOG_REQUIRED_ROW_TEXT_FIELDS:
        _api_catalog_row_text(row, index, field, gaps)
    for field in _API_CATALOG_OPTIONAL_ROW_TEXT_FIELDS:
        _api_catalog_optional_row_text(row, index, field, gaps)
    for field in _API_CATALOG_REQUIRED_ROW_INT_FIELDS:
        _api_catalog_row_non_negative_int(row, index, field, gaps)
    for field in _API_CATALOG_REQUIRED_ROW_LIST_FIELDS:
        values = _api_catalog_row_non_empty_string_list(row, index, field, gaps)
        if field == "surfaces":
            _api_catalog_row_surface_token_gaps(index, values, gaps)
    for field in _API_CATALOG_UNIQUE_ROW_FIELDS:
        value = _api_catalog_row_text(row, index, field, gaps)
        if value:
            _api_catalog_unique_row_field_gaps(field, value, index, seen_values[field], gaps)


def _api_catalog_row_field_set_gaps(row: Mapping[str, object], index: int, gaps: list[str]) -> None:
    expected_fields = set(_API_CATALOG_REQUIRED_ROW_TEXT_FIELDS)
    expected_fields.update(_API_CATALOG_OPTIONAL_ROW_TEXT_FIELDS)
    expected_fields.update(_API_CATALOG_REQUIRED_ROW_INT_FIELDS)
    expected_fields.update(_API_CATALOG_REQUIRED_ROW_LIST_FIELDS)
    fields = set(row)
    for field in sorted(expected_fields - fields):
        gaps.append(f"api catalog: row {index} is missing field {field!r}")
    for field in sorted(fields - expected_fields):
        gaps.append(f"api catalog: row {index} has undocumented field {field!r}")


def _api_catalog_row_non_negative_int(row: Mapping[str, object], index: int, field: str, gaps: list[str]) -> int:
    value = row.get(field)
    if isinstance(value, int) and value >= 0:
        return value
    gaps.append(f"api catalog: row {index} has invalid {field} {value!r}")
    return 0


def _api_catalog_row_non_empty_string_list(row: Mapping[str, object], index: int, field: str, gaps: list[str]) -> list[str]:
    value = _api_catalog_row_string_list(row, index, field, gaps)
    if value:
        return value
    gaps.append(f"api catalog: row {index} has empty {field}")
    return []


def _api_catalog_row_surface_token_gaps(index: int, surfaces: list[str], gaps: list[str]) -> None:
    for surface in surfaces:
        if surface not in _API_CATALOG_KNOWN_SURFACES:
            gaps.append(f"api catalog: row {index} has unknown surface {surface!r}")


def _api_catalog_unique_row_field_gaps(
    field: str,
    value: str,
    index: int,
    seen_values: dict[str, int],
    gaps: list[str],
) -> None:
    previous_index = seen_values.get(value)
    if previous_index is not None:
        gaps.append(f"api catalog: rows {previous_index} and {index} share {field} {value!r}")
        return
    seen_values[value] = index


def _api_catalog_source_id_gaps(rows: list[Mapping[str, object]], gaps: list[str]) -> None:
    source_ids = {row["id"] for row in _api_catalog_source_rows()}
    row_ids = {row_id for index, row in enumerate(rows) if (row_id := _api_catalog_row_text(row, index, "id", gaps))}
    for row_id in sorted(source_ids - row_ids):
        gaps.append(f"api catalog: missing source id {row_id!r}")
    for row_id in sorted(row_ids - source_ids):
        gaps.append(f"api catalog: unknown source id {row_id!r}")


def _api_catalog_source_order_gaps(rows: list[Mapping[str, object]], gaps: list[str]) -> None:
    source_ids = [row["id"] for row in _api_catalog_source_rows()]
    row_ids = [row_id for index, row in enumerate(rows) if (row_id := _api_catalog_row_text(row, index, "id", gaps))]
    if row_ids != source_ids:
        gaps.append(f"api catalog: source order {row_ids!r} != {source_ids!r}")


def _api_catalog_source_metadata_gaps(rows: list[Mapping[str, object]], gaps: list[str]) -> None:
    sources_by_id = {row["id"]: row for row in _api_catalog_source_rows()}
    for index, row in enumerate(rows):
        row_id = _api_catalog_row_text(row, index, "id", gaps)
        source = sources_by_id.get(row_id)
        if source is None:
            continue
        for field, expected in source.items():
            value = row.get(field)
            if value != expected:
                gaps.append(f"api catalog {row_id}: {field} {value!r} != source row {expected!r}")


def _api_catalog_source_rows() -> list[Mapping[str, object]]:
    module = importlib.import_module("paradev.surfaces.api_catalog")
    return list(module.API_CATALOG_SOURCE_ROWS)


def _api_catalog_source_helper_payload(row: Mapping[str, object], index: int, gaps: list[str]) -> Mapping[str, object] | None:
    row_id = _api_catalog_row_text(row, index, "id", gaps)
    owner_module = _api_catalog_row_text(row, index, "owner_module", gaps)
    table_helper = _api_catalog_row_text(row, index, "table_helper", gaps)
    label = row_id or f"row {index}"
    if not owner_module or not table_helper:
        return None
    if row_id == _API_CATALOG_REFERENCE_ID:
        module = importlib.import_module("paradev.surfaces.api_catalog")
        return module.get_api_catalog_table()
    module = importlib.import_module(owner_module)
    helper = getattr(module, table_helper, None)
    if not callable(helper):
        gaps.append(f"api catalog {label}: missing callable {owner_module}.{table_helper}")
        return None
    payload = helper()
    if isinstance(payload, Mapping):
        return payload
    gaps.append(f"api catalog {label}: {owner_module}.{table_helper} returned {type(payload).__name__}, not mapping")
    return None


def _api_catalog_payload_field_gaps(row: Mapping[str, object], index: int, field: str, expected: object, gaps: list[str]) -> None:
    value = row.get(field)
    if value == expected:
        return
    row_id = row.get("id", f"row {index}")
    gaps.append(f"api catalog {row_id}: {field} {value!r} != source helper {expected!r}")


def _api_catalog_payload_schema(payload: Mapping[str, object]) -> str:
    value = payload.get("schema")
    return value if isinstance(value, str) else ""


def _api_catalog_payload_row_count(row_id: str, payload: Mapping[str, object]) -> int:
    count = _api_catalog_int_payload_field(payload, _API_TABLE_ROW_COUNT_FIELD)
    if count is not None:
        return count
    summary = payload.get("summary")
    if isinstance(summary, Mapping):
        count = _api_catalog_int_payload_field(summary, "operation_count")
        if count is not None:
            return count
    fallback_field = _API_CATALOG_ROW_COUNT_FALLBACK_FIELDS.get(row_id)
    return _api_catalog_payload_field_count(payload, fallback_field) if fallback_field else 0


def _api_catalog_int_payload_field(payload: Mapping[str, object], field: str) -> int | None:
    value = payload.get(field)
    return value if isinstance(value, int) else None


def _api_catalog_payload_field_count(payload: Mapping[str, object], field: str) -> int:
    value = payload.get(field)
    if isinstance(value, int):
        return value
    return len(value) if isinstance(value, list) else 0


def _api_catalog_payload_index_names(payload: Mapping[str, object]) -> list[str]:
    names = sorted(key for key, value in payload.items() if key.endswith("_index") and isinstance(value, Mapping))
    index = payload.get("index")
    if not isinstance(index, Mapping):
        return names
    if all(not isinstance(value, (Mapping, list, tuple, set)) for value in index.values()):
        names.append("index")
        return names
    names.extend(f"index.{key}" for key in sorted(str(key) for key in index))
    return names


def _api_catalog_payload_surface_gaps(row: Mapping[str, object], index: int, row_id: str, payload: Mapping[str, object], gaps: list[str]) -> None:
    if row_id == _API_CATALOG_REFERENCE_ID:
        return
    surface_index = payload.get("surface_index")
    if not isinstance(surface_index, Mapping):
        return
    payload_surfaces = {surface for surface in surface_index if isinstance(surface, str) and surface}
    catalog_surfaces = set(_api_catalog_row_string_list(row, index, "surfaces", gaps))
    for surface in sorted(payload_surfaces - catalog_surfaces):
        gaps.append(f"api catalog {row_id}: surfaces is missing payload surface {surface!r}")


def _api_catalog_summary_gaps(table: Mapping[str, object], gaps: list[str]) -> None:
    summary = table.get("summary")
    if not isinstance(summary, Mapping):
        gaps.append(f"api catalog: summary is {type(summary).__name__}, not a mapping")
        return
    for summary_field, table_field in _API_CATALOG_SUMMARY_COUNT_FIELDS.items():
        expected = _api_catalog_table_count(table, table_field, gaps)
        value = summary.get(summary_field)
        if value != expected:
            gaps.append(f"api catalog: summary {summary_field} {value!r} != {expected!r}")


def _api_catalog_table_count(table: Mapping[str, object], field: str, gaps: list[str]) -> int:
    value = table.get(field)
    if isinstance(value, int):
        return value
    if isinstance(value, Mapping | list):
        return len(value)
    gaps.append(f"api catalog: {field} is {type(value).__name__}, not a countable table field")
    return 0


def _api_catalog_reference_group_gaps(
    table: Mapping[str, object],
    rows_by_id: Mapping[str, tuple[int, Mapping[str, object]]],
    gaps: list[str],
) -> None:
    group_index = table.get("group_index")
    if not isinstance(group_index, Mapping):
        gaps.append(f"api catalog: group_index is {type(group_index).__name__}, not a mapping")
        return
    reference_groups = table.get("reference_groups")
    if not isinstance(reference_groups, list):
        gaps.append(f"api catalog: reference_groups is {type(reference_groups).__name__}, not a list")
        return
    seen_groups: set[str] = set()
    assigned_ids: list[str] = []
    for index, row in enumerate(reference_groups):
        if not isinstance(row, Mapping):
            gaps.append(f"api catalog: reference_groups row {index} is {type(row).__name__}, not a mapping")
            continue
        group_id = _api_catalog_reference_group_text(row, index, "id", gaps)
        _api_catalog_reference_group_text(row, index, "title", gaps)
        _api_catalog_reference_group_text(row, index, "usage", gaps)
        reference_ids = _api_catalog_reference_group_string_list(row, index, "reference_ids", gaps)
        kinds = _api_catalog_reference_group_string_list(row, index, "kinds", gaps)
        expected_kinds = _api_catalog_reference_group_kinds(reference_ids, rows_by_id, gaps)
        if group_id:
            if group_id in seen_groups:
                gaps.append(f"api catalog: duplicate reference group {group_id!r}")
            seen_groups.add(group_id)
            expected = group_index.get(group_id)
            if reference_ids != expected:
                gaps.append(f"api catalog: reference group {group_id!r} ids {reference_ids!r} != group_index {expected!r}")
            if kinds != expected_kinds:
                gaps.append(f"api catalog: reference group {group_id!r} kinds {kinds!r} != {expected_kinds!r}")
        if row.get("reference_count") != len(reference_ids):
            gaps.append(f"api catalog: reference group {group_id or index!r} reference_count {row.get('reference_count')!r} != {len(reference_ids)}")
        assigned_ids.extend(reference_ids)
    _api_catalog_reference_group_key_gaps(group_index, seen_groups, gaps)
    _api_catalog_reference_group_assignment_gaps(set(rows_by_id), assigned_ids, gaps)


def _api_catalog_reference_group_key_gaps(
    group_index: Mapping[object, object],
    reference_group_ids: set[str],
    gaps: list[str],
) -> None:
    group_index_ids: set[str] = set()
    for group_id in group_index:
        if isinstance(group_id, str):
            group_index_ids.add(group_id)
            continue
        gaps.append(f"api catalog: group_index key {group_id!r} is not a string")
    for group_id in sorted(group_index_ids - reference_group_ids):
        gaps.append(f"api catalog: group_index contains {group_id!r} without a reference_groups row")
    for group_id in sorted(reference_group_ids - group_index_ids):
        gaps.append(f"api catalog: reference_groups contains {group_id!r} without a group_index key")


def _api_catalog_reference_group_assignment_gaps(row_ids: set[str], assigned_ids: list[str], gaps: list[str]) -> None:
    assigned_id_set = set(assigned_ids)
    duplicate_ids = sorted({row_id for row_id in assigned_ids if assigned_ids.count(row_id) > 1})
    for row_id in duplicate_ids:
        gaps.append(f"api catalog: reference id {row_id!r} is assigned to multiple reference groups")
    for row_id in sorted(row_ids - assigned_id_set):
        gaps.append(f"api catalog: reference id {row_id!r} is not assigned to any reference group")
    for row_id in sorted(assigned_id_set - row_ids):
        gaps.append(f"api catalog: reference groups point at unknown reference id {row_id!r}")


def _api_catalog_reference_group_kinds(
    reference_ids: list[str],
    rows_by_id: Mapping[str, tuple[int, Mapping[str, object]]],
    gaps: list[str],
) -> list[str]:
    kinds: list[str] = []
    for reference_id in reference_ids:
        catalog_row = rows_by_id.get(reference_id)
        if catalog_row is None:
            continue
        index, row = catalog_row
        kind = _api_catalog_row_text(row, index, "kind", gaps)
        if kind and kind not in kinds:
            kinds.append(kind)
    return kinds


def _api_catalog_reference_group_text(row: Mapping[str, object], index: int, field: str, gaps: list[str]) -> str:
    value = row.get(field)
    if isinstance(value, str) and value:
        return value
    gaps.append(f"api catalog: reference_groups row {index} has invalid {field} {value!r}")
    return ""


def _api_catalog_reference_group_string_list(row: Mapping[str, object], index: int, field: str, gaps: list[str]) -> list[str]:
    value = row.get(field)
    if isinstance(value, list) and all(isinstance(item, str) and item for item in value):
        return list(value)
    gaps.append(f"api catalog: reference_groups row {index} has invalid {field} {value!r}")
    return []


def _api_catalog_row_index_coverage_gaps(table: Mapping[str, object], row: Mapping[str, object], index: int, gaps: list[str]) -> None:
    row_id = _api_catalog_row_text(row, index, "id", gaps)
    if not row_id:
        return
    for index_name, field in _API_CATALOG_ROW_INDEX_FIELDS.items():
        if field in _API_CATALOG_OPTIONAL_ROW_INDEX_FIELDS and not row.get(field):
            continue
        value = _api_catalog_row_text(row, index, field, gaps)
        if value:
            _api_catalog_index_contains(table, index_name, value, row_id, gaps)
    for index_name, field in _API_CATALOG_ROW_LIST_INDEX_FIELDS.items():
        for value in _api_catalog_row_string_list(row, index, field, gaps):
            _api_catalog_index_contains(table, index_name, value, row_id, gaps)


def _api_catalog_index_contains(table: Mapping[str, object], index_name: str, key: str, row_id: str, gaps: list[str]) -> None:
    index = table.get(index_name)
    if not isinstance(index, Mapping):
        gaps.append(f"api catalog: {index_name} is {type(index).__name__}, not a mapping")
        return
    values = index.get(key)
    if not isinstance(values, list):
        gaps.append(f"api catalog: {index_name}[{key!r}] is {type(values).__name__}, not a list")
        return
    if row_id not in values:
        gaps.append(f"api catalog: {index_name}[{key!r}] does not include {row_id!r}")


def _api_catalog_reverse_index_coverage_gaps(
    table: Mapping[str, object],
    rows: list[Mapping[str, object]],
    gaps: list[str],
) -> None:
    row_ids = {row_id for index, row in enumerate(rows) if (row_id := _api_catalog_row_text(row, index, "id", gaps))}
    for index_name, field in _API_CATALOG_ROW_INDEX_FIELDS.items():
        _api_catalog_reverse_index_reference_id_gaps(table, index_name, row_ids, gaps)
        expected_row_values = _api_catalog_expected_index_values(rows, field, list_field=False, gaps=gaps)
        _api_catalog_reverse_index_field_match_gaps(table, index_name, expected_row_values, gaps)
    for index_name, field in _API_CATALOG_ROW_LIST_INDEX_FIELDS.items():
        _api_catalog_reverse_index_reference_id_gaps(table, index_name, row_ids, gaps)
        expected_row_values = _api_catalog_expected_index_values(rows, field, list_field=True, gaps=gaps)
        _api_catalog_reverse_index_field_match_gaps(table, index_name, expected_row_values, gaps)


def _api_catalog_expected_index_values(
    rows: list[Mapping[str, object]],
    field: str,
    *,
    list_field: bool,
    gaps: list[str],
) -> dict[str, set[str]]:
    expected: dict[str, set[str]] = {}
    for index, row in enumerate(rows):
        row_id = _api_catalog_row_text(row, index, "id", gaps)
        if not row_id:
            continue
        if field in _API_CATALOG_OPTIONAL_ROW_INDEX_FIELDS and not row.get(field):
            continue
        if list_field:
            values = _api_catalog_row_string_list(row, index, field, gaps)
        else:
            value = _api_catalog_row_text(row, index, field, gaps)
            values = [value] if value else []
        for value in values:
            expected.setdefault(row_id, set()).add(value)
    return expected


def _api_catalog_reverse_index_reference_id_gaps(
    table: Mapping[str, object],
    index_name: str,
    row_ids: set[str],
    gaps: list[str],
) -> None:
    index = table.get(index_name)
    if not isinstance(index, Mapping):
        gaps.append(f"api catalog: {index_name} is {type(index).__name__}, not a mapping")
        return
    for key, values in index.items():
        if not isinstance(key, str) or not key:
            gaps.append(f"api catalog: {index_name} has invalid key {key!r}")
            continue
        if not isinstance(values, list):
            gaps.append(f"api catalog: {index_name}[{key!r}] is {type(values).__name__}, not a list")
            continue
        for row_id in values:
            if not isinstance(row_id, str) or not row_id:
                gaps.append(f"api catalog: {index_name}[{key!r}] has invalid reference id {row_id!r}")
                continue
            if row_id not in row_ids:
                gaps.append(f"api catalog: {index_name}[{key!r}] points at unknown reference id {row_id!r}")


def _api_catalog_reverse_index_field_match_gaps(
    table: Mapping[str, object],
    index_name: str,
    expected_row_values: Mapping[str, set[str]],
    gaps: list[str],
) -> None:
    index = table.get(index_name)
    if not isinstance(index, Mapping):
        return
    for key, values in index.items():
        if not isinstance(key, str) or not isinstance(values, list):
            continue
        for row_id in values:
            if not isinstance(row_id, str):
                continue
            if row_id in expected_row_values and key not in expected_row_values[row_id]:
                gaps.append(f"api catalog: {index_name}[{key!r}] includes {row_id!r} without matching row field")


def _api_catalog_index_catalog_id_gaps(table: Mapping[str, object], row_ids: list[str], gaps: list[str]) -> None:
    expected_ids = _api_catalog_expected_index_catalog_ids(table)
    row_id_set = {row_id for row_id in row_ids if row_id}
    duplicate_ids = sorted({row_id for row_id in row_ids if row_ids.count(row_id) > 1})
    for row_id in duplicate_ids:
        gaps.append(f"api catalog: duplicate index_catalog id {row_id!r}")
    for row_id in sorted(expected_ids - row_id_set):
        gaps.append(f"api catalog: index_catalog is missing documented index {row_id!r}")
    for row_id in sorted(row_id_set - expected_ids):
        gaps.append(f"api catalog: index_catalog documents unknown index {row_id!r}")


def _api_catalog_expected_index_catalog_ids(table: Mapping[str, object]) -> set[str]:
    index_ids = set(_API_CATALOG_DIRECT_INDEX_CATALOG_IDS)
    for field, value in table.items():
        if field.endswith("_index") and isinstance(value, Mapping):
            index_ids.add(field.removesuffix("_index"))
    return index_ids


def _api_catalog_index_catalog_row_gaps(table: Mapping[str, object], row: Mapping[str, object], index: int, gaps: list[str]) -> None:
    row_id = _api_catalog_index_catalog_text(row, index, "id", gaps)
    table_path = _api_catalog_index_catalog_text(row, index, "table_path", gaps)
    helper_text = _api_catalog_index_catalog_text(row, index, "python_helper", gaps)
    _api_catalog_index_catalog_text(row, index, "usage", gaps)
    if not row_id:
        return
    _api_catalog_index_catalog_path_gaps(row_id, table_path, gaps)
    helper_name = _api_catalog_index_catalog_helper_name(row_id, helper_text, gaps)
    if helper_name:
        _api_catalog_index_catalog_helper_text_gaps(row_id, helper_name, helper_text, gaps)
        _api_catalog_index_catalog_helper_gaps(table, row_id, helper_name, gaps)


def _api_catalog_index_catalog_path_gaps(row_id: str, table_path: str, gaps: list[str]) -> None:
    if row_id == "id":
        _api_catalog_index_catalog_path_tokens(row_id, table_path, ('table["rows"]', '["id"]'), gaps)
        return
    if row_id == "reference_group":
        _api_catalog_index_catalog_path_tokens(row_id, table_path, ('table["reference_groups"]', '["id"]'), gaps)
        return
    _api_catalog_index_catalog_path_tokens(row_id, table_path, (f'table["{row_id}_index"]',), gaps)


def _api_catalog_index_catalog_path_tokens(row_id: str, table_path: str, tokens: tuple[str, ...], gaps: list[str]) -> None:
    for token in tokens:
        if token in table_path:
            continue
        gaps.append(f"api catalog index_catalog {row_id!r}: table_path {table_path!r} is missing {token!r}")


def _api_catalog_index_catalog_helper_name(row_id: str, helper_text: str, gaps: list[str]) -> str:
    helper_name, separator, _arguments = helper_text.partition("(")
    if separator and helper_name.isidentifier():
        return helper_name
    gaps.append(f"api catalog index_catalog {row_id!r}: invalid python_helper {helper_text!r}")
    return ""


def _api_catalog_index_catalog_helper_text_gaps(row_id: str, helper_name: str, helper_text: str, gaps: list[str]) -> None:
    expected_helper = _api_catalog_expected_helper_name(row_id)
    if helper_name != expected_helper:
        gaps.append(f"api catalog index_catalog {row_id!r}: python_helper {helper_text!r} should call {expected_helper}")
    if row_id not in _API_CATALOG_HELPER_NAMES and not _api_catalog_index_literal_in_helper(row_id, helper_text):
        gaps.append(f"api catalog index_catalog {row_id!r}: python_helper {helper_text!r} is missing index literal {row_id!r}")


def _api_catalog_expected_helper_name(row_id: str) -> str:
    return _API_CATALOG_HELPER_NAMES.get(row_id, _API_CATALOG_REFERENCE_IDS_HELPER)


def _api_catalog_index_literal_in_helper(row_id: str, helper_text: str) -> bool:
    return f"'{row_id}'" in helper_text or f'"{row_id}"' in helper_text


def _api_catalog_index_catalog_helper_gaps(table: Mapping[str, object], row_id: str, helper_name: str, gaps: list[str]) -> None:
    module = importlib.import_module("paradev.surfaces")
    helper = getattr(module, helper_name, None)
    if not callable(helper):
        gaps.append(f"api catalog index_catalog {row_id!r}: missing callable paradev.surfaces.{helper_name}")
        return
    if row_id == "id":
        _api_catalog_index_catalog_reference_helper_gaps(table, helper, gaps)
        return
    if row_id == "reference_group":
        _api_catalog_index_catalog_reference_group_helper_gaps(table, helper, gaps)
        return
    if row_id == "group":
        _api_catalog_index_catalog_group_helper_gaps(table, helper, gaps)
        return
    _api_catalog_index_catalog_reference_ids_helper_gaps(table, row_id, helper, gaps)


def _api_catalog_index_catalog_reference_helper_gaps(table: Mapping[str, object], helper: object, gaps: list[str]) -> None:
    row = _api_catalog_first_mapping_row(table, "rows", gaps)
    if row is None:
        return
    reference_id = row.get("id")
    if not isinstance(reference_id, str) or not reference_id:
        gaps.append(f"api catalog index_catalog 'id': first row has invalid id {reference_id!r}")
        return
    payload = _api_catalog_call_helper(helper, reference_id, gaps=gaps, row_id="id")
    if not isinstance(payload, Mapping) or payload.get("id") != reference_id:
        gaps.append(f"api catalog index_catalog 'id': helper returned {payload!r} for {reference_id!r}")


def _api_catalog_index_catalog_reference_group_helper_gaps(table: Mapping[str, object], helper: object, gaps: list[str]) -> None:
    row = _api_catalog_first_mapping_row(table, "reference_groups", gaps)
    if row is None:
        return
    group_id = row.get("id")
    if not isinstance(group_id, str) or not group_id:
        gaps.append(f"api catalog index_catalog 'reference_group': first group has invalid id {group_id!r}")
        return
    payload = _api_catalog_call_helper(helper, group_id, gaps=gaps, row_id="reference_group")
    if not isinstance(payload, Mapping) or payload.get("id") != group_id:
        gaps.append(f"api catalog index_catalog 'reference_group': helper returned {payload!r} for {group_id!r}")


def _api_catalog_index_catalog_group_helper_gaps(table: Mapping[str, object], helper: object, gaps: list[str]) -> None:
    key, expected = _api_catalog_first_index_entry(table, "group_index", gaps)
    if not key:
        return
    payload = _api_catalog_call_helper(helper, key, gaps=gaps, row_id="group")
    if payload != expected:
        gaps.append(f"api catalog index_catalog 'group': helper returned {payload!r} for {key!r}, expected {expected!r}")


def _api_catalog_index_catalog_reference_ids_helper_gaps(table: Mapping[str, object], row_id: str, helper: object, gaps: list[str]) -> None:
    index_name = f"{row_id}_index"
    key, expected = _api_catalog_first_index_entry(table, index_name, gaps)
    if not key:
        return
    payload = _api_catalog_call_helper(helper, row_id, key, gaps=gaps, row_id=row_id)
    if payload != expected:
        gaps.append(f"api catalog index_catalog {row_id!r}: helper returned {payload!r} for {key!r}, expected {expected!r}")


def _api_catalog_first_mapping_row(table: Mapping[str, object], field: str, gaps: list[str]) -> Mapping[str, object] | None:
    rows = table.get(field)
    if not isinstance(rows, list):
        gaps.append(f"api catalog: {field} is {type(rows).__name__}, not a list")
        return None
    for index, row in enumerate(rows):
        if isinstance(row, Mapping):
            return row
        gaps.append(f"api catalog: {field} row {index} is {type(row).__name__}, not a mapping")
    return None


def _api_catalog_first_index_entry(table: Mapping[str, object], index_name: str, gaps: list[str]) -> tuple[str, list[str]]:
    index = table.get(index_name)
    if not isinstance(index, Mapping):
        gaps.append(f"api catalog: {index_name} is {type(index).__name__}, not a mapping")
        return "", []
    for key, values in index.items():
        if not isinstance(key, str) or not key:
            gaps.append(f"api catalog: {index_name} has invalid key {key!r}")
            return "", []
        if isinstance(values, list) and all(isinstance(value, str) and value for value in values):
            return key, list(values)
        gaps.append(f"api catalog: {index_name}[{key!r}] has invalid values {values!r}")
        return "", []
    return "", []


def _api_catalog_call_helper(helper: object, *args: str, gaps: list[str], row_id: str) -> object:
    if not callable(helper):
        gaps.append(f"api catalog index_catalog {row_id!r}: helper is not callable")
        return None
    try:
        return helper(*args)
    except Exception as error:
        gaps.append(f"api catalog index_catalog {row_id!r}: helper raised {type(error).__name__}: {error}")
        return None


def _api_catalog_index_catalog_text(row: Mapping[str, object], index: int, field: str, gaps: list[str]) -> str:
    value = row.get(field)
    if isinstance(value, str) and value:
        return value
    gaps.append(f"api catalog: index_catalog row {index} has invalid {field} {value!r}")
    return ""


def _api_catalog_cli_command_row_gaps(
    row: Mapping[str, object],
    index: int,
    cli_rows: Mapping[str, Mapping[str, object]],
    gaps: list[str],
) -> set[str]:
    surfaces = _api_catalog_row_string_list(row, index, "surfaces", gaps)
    row_id = _api_catalog_row_text(row, index, "id", gaps)
    cli_command = _api_catalog_row_text(row, index, "cli_command", gaps)
    markdown_command = _api_catalog_row_text(row, index, "markdown_cli_command", gaps)
    selector_helper = _api_catalog_optional_row_text(row, index, "selector_helper", gaps)
    markdown_helper = _api_catalog_row_text(row, index, "markdown_helper", gaps)
    if (cli_command or markdown_command) and _API_CATALOG_CLI_SURFACE not in surfaces:
        gaps.append(f"api catalog {row_id}: CLI commands require surface {_API_CATALOG_CLI_SURFACE!r}")
    if cli_command:
        _api_catalog_cli_command_adapter_gaps(row_id, cli_command, selector_helper, cli_rows, gaps)
    if markdown_command:
        _api_catalog_cli_command_adapter_gaps(row_id, markdown_command, markdown_helper, cli_rows, gaps)
    return {command for command in (cli_command, markdown_command) if command}


def _api_catalog_cli_command_reverse_gaps(
    catalog_commands: set[str],
    cli_rows: Mapping[str, Mapping[str, object]],
    gaps: list[str],
) -> None:
    for command, row in sorted(cli_rows.items()):
        if command in catalog_commands or not _api_catalog_generated_cli_api_command(command):
            continue
        gaps.append(f"CLI API table generated command_key {command!r} adapter {row.get('adapter')!r} is missing from the API catalog")


def _api_catalog_generated_cli_api_command(command: str) -> bool:
    base_command = command.removesuffix(" --markdown")
    if command not in {base_command, f"{base_command} --markdown"}:
        return False
    return " " not in base_command and base_command.endswith("-api")


def _api_catalog_cli_command_adapter_gaps(
    row_id: str,
    command: str,
    expected_adapter: str,
    cli_rows: Mapping[str, Mapping[str, object]],
    gaps: list[str],
) -> None:
    row = cli_rows.get(command)
    if row is None:
        gaps.append(f"api catalog {row_id}: CLI API table is missing command_key {command!r}")
        return
    if expected_adapter and row.get("adapter") != expected_adapter:
        gaps.append(f"api catalog {row_id}: CLI API command {command!r} adapter {row.get('adapter')!r} != {expected_adapter!r}")


def _api_catalog_mcp_selector_surface_gaps(
    catalog_rows_by_selector: Mapping[str, list[tuple[int, Mapping[str, object]]]],
    gaps: list[str],
) -> None:
    from paradev.surfaces.mcp import get_mcp_api_table

    rows = _surface_api_table_rows("MCP API table", get_mcp_api_table(), gaps)
    for index, row in enumerate(rows):
        sdk_method = _surface_api_row_text("MCP API table", row, index, "sdk_method", gaps)
        if not _api_catalog_selection_helper_name(sdk_method, catalog_rows_by_selector):
            continue
        catalog_entry = catalog_rows_by_selector.get(sdk_method)
        if catalog_entry is None:
            gaps.append(f"MCP API table row {index} uses selector helper {sdk_method!r} missing from the API catalog")
            continue
        _api_catalog_selector_surface_marker_gaps(catalog_entry, _API_CATALOG_MCP_SURFACE, sdk_method, gaps)


def _api_catalog_rest_selector_surface_gaps(
    catalog_rows_by_id: Mapping[str, tuple[int, Mapping[str, object]]],
    gaps: list[str],
) -> None:
    from paradev.surfaces.rest import get_rest_api_table

    rows = _surface_api_table_rows("REST API table", get_rest_api_table(), gaps)
    seen_features: set[str] = set()
    for index, row in enumerate(rows):
        feature = _surface_api_row_text("REST API table", row, index, "feature", gaps)
        reference_id = _API_CATALOG_REST_SELECTOR_FEATURE_REFERENCE_IDS.get(feature)
        if reference_id is None:
            if _api_catalog_rest_selector_path(row, index, gaps):
                gaps.append(f"REST API table row {index} selector feature {feature!r} is missing an API catalog reference mapping")
            continue
        seen_features.add(feature)
        catalog_entry = catalog_rows_by_id.get(reference_id)
        if catalog_entry is None:
            gaps.append(f"REST API table row {index} feature {feature!r} points at missing API catalog reference {reference_id!r}")
            continue
        catalog_index, catalog_row = catalog_entry
        _api_catalog_surface_marker_gaps(catalog_row, catalog_index, _API_CATALOG_REST_SURFACE, feature, gaps)
    for feature, reference_id in _API_CATALOG_REST_SELECTOR_FEATURE_REFERENCE_IDS.items():
        if feature not in seen_features:
            gaps.append(f"REST API table is missing selector feature {feature!r} for API catalog reference {reference_id!r}")


def _api_catalog_rest_selector_path(row: Mapping[str, object], index: int, gaps: list[str]) -> bool:
    path = _surface_api_row_text("REST API table", row, index, "path", gaps)
    return path in {"/api-catalog", "/surface-contracts"} or path.endswith("-api")


def _api_catalog_selection_helper_name(helper_name: str, catalog_rows_by_selector: Mapping[str, list[tuple[int, Mapping[str, object]]]]) -> bool:
    return helper_name in catalog_rows_by_selector or (helper_name.startswith("get_") and helper_name.endswith("_selection"))


def _api_catalog_selector_surface_marker_gaps(
    catalog_entries: list[tuple[int, Mapping[str, object]]],
    surface: str,
    source_label: str,
    gaps: list[str],
) -> None:
    row_ids: list[str] = []
    for catalog_index, catalog_row in catalog_entries:
        row_id = _api_catalog_row_text(catalog_row, catalog_index, "id", gaps)
        surfaces = _api_catalog_row_string_list(catalog_row, catalog_index, "surfaces", gaps)
        row_ids.append(row_id)
        if surface in surfaces:
            return
    gaps.append(f"api catalog selector {source_label!r}: references {row_ids!r} are missing surface {surface!r}")


def _api_catalog_surface_marker_gaps(
    catalog_row: Mapping[str, object],
    catalog_index: int,
    surface: str,
    source_label: str,
    gaps: list[str],
) -> None:
    row_id = _api_catalog_row_text(catalog_row, catalog_index, "id", gaps)
    surfaces = _api_catalog_row_string_list(catalog_row, catalog_index, "surfaces", gaps)
    if surface not in surfaces:
        gaps.append(f"api catalog {row_id}: {source_label!r} is exposed by {surface!r} but surfaces is missing {surface!r}")


def _api_catalog_surface_index_contract_gaps(table: Mapping[str, object], contract_surfaces: set[str], gaps: list[str]) -> None:
    surface_index = table.get("surface_index")
    if not isinstance(surface_index, Mapping):
        gaps.append(f"api catalog: surface_index is {type(surface_index).__name__}, not a mapping")
        return
    for surface in sorted(contract_surfaces):
        values = surface_index.get(surface)
        if not isinstance(values, list):
            gaps.append(f"api catalog: surface_index[{surface!r}] is {type(values).__name__}, not a list")
            continue
        if _API_CATALOG_SURFACE_CONTRACT_REFERENCE_ID not in values:
            gaps.append("api catalog: " f"surface_index[{surface!r}] is missing {_API_CATALOG_SURFACE_CONTRACT_REFERENCE_ID!r}")


def _api_catalog_surface_contract_reference_gaps(
    catalog_rows_by_id: Mapping[str, tuple[int, Mapping[str, object]]],
    contract_surfaces: set[str],
    gaps: list[str],
) -> None:
    catalog_entry = catalog_rows_by_id.get(_API_CATALOG_SURFACE_CONTRACT_REFERENCE_ID)
    if catalog_entry is None:
        gaps.append(f"api catalog: missing {_API_CATALOG_SURFACE_CONTRACT_REFERENCE_ID!r} row")
        return
    row_index, row = catalog_entry
    surfaces = set(_api_catalog_row_string_list(row, row_index, "surfaces", gaps))
    for surface in sorted(contract_surfaces - surfaces):
        gaps.append(f"api catalog {_API_CATALOG_SURFACE_CONTRACT_REFERENCE_ID}: surfaces is missing {surface!r}")


def _surface_contract_catalog_surfaces(gaps: list[str]) -> set[str]:
    from paradev.surfaces import get_surface_contract_summary

    summary = get_surface_contract_summary()
    if not isinstance(summary, Mapping):
        gaps.append(f"surface contract summary is {type(summary).__name__}, not a mapping")
        return set()
    rows = summary.get("rows")
    if not isinstance(rows, list):
        gaps.append(f"surface contract summary rows is {type(rows).__name__}, not a list")
        return set()
    surfaces: set[str] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            gaps.append(f"surface contract summary row {index} is {type(row).__name__}, not a mapping")
            continue
        identifier = _surface_contract_row_text(row, index, "identifier", gaps)
        if identifier:
            surfaces.add(_API_CATALOG_SURFACE_CONTRACT_SURFACE_ALIASES.get(identifier, identifier))
    return surfaces


def _surface_contract_row_text(row: Mapping[str, object], index: int, field: str, gaps: list[str]) -> str:
    value = row.get(field)
    if isinstance(value, str) and value:
        return value
    gaps.append(f"surface contract summary row {index} has invalid {field} {value!r}")
    return ""


def _surface_api_table_rows(table_name: str, table: object, gaps: list[str]) -> list[Mapping[str, object]]:
    if not isinstance(table, Mapping):
        gaps.append(f"{table_name} is {type(table).__name__}, not a mapping")
        return []
    rows = table.get(_API_TABLE_ROWS_FIELD)
    if not isinstance(rows, list):
        gaps.append(f"{table_name} rows is {type(rows).__name__}, not a list")
        return []
    row_list: list[Mapping[str, object]] = []
    for index, row in enumerate(rows):
        if isinstance(row, Mapping):
            row_list.append(row)
            continue
        gaps.append(f"{table_name} row {index} is {type(row).__name__}, not a mapping")
    return row_list


def _surface_api_row_text(table_name: str, row: Mapping[str, object], index: int, field: str, gaps: list[str]) -> str:
    value = row.get(field)
    if isinstance(value, str) and value:
        return value
    gaps.append(f"{table_name} row {index} has invalid {field} {value!r}")
    return ""


def _cli_api_rows_by_command() -> tuple[list[str], dict[str, Mapping[str, object]]]:
    from paradev.surfaces.cli import get_cli_api_table

    table = get_cli_api_table()
    if not isinstance(table, Mapping):
        return [f"CLI API table is {type(table).__name__}, not a mapping"], {}
    rows = table.get(_API_TABLE_ROWS_FIELD)
    if not isinstance(rows, list):
        return [f"CLI API table rows is {type(rows).__name__}, not a list"], {}
    gaps: list[str] = []
    rows_by_command: dict[str, Mapping[str, object]] = {}
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            gaps.append(f"CLI API table row {index} is {type(row).__name__}, not a mapping")
            continue
        command = _cli_api_row_text(row, index, _CLI_API_COMMAND_KEY_FIELD, gaps)
        if not command:
            continue
        if command in rows_by_command:
            gaps.append(f"CLI API table has duplicate command_key {command!r}")
            continue
        rows_by_command[command] = row
    return gaps, rows_by_command


def _cli_api_row_text(row: Mapping[str, object], index: int, field: str, gaps: list[str]) -> str:
    value = row.get(field)
    if isinstance(value, str) and value:
        return value
    gaps.append(f"CLI API table row {index} has invalid {field} {value!r}")
    return ""


def _api_catalog_row_string_list(row: Mapping[str, object], index: int, field: str, gaps: list[str]) -> list[str]:
    value = row.get(field)
    if isinstance(value, list) and all(isinstance(item, str) and item for item in value):
        return list(value)
    gaps.append(f"api catalog: row {index} has invalid {field} {value!r}")
    return []


def _api_catalog_manual_reference_gaps(doc_pages: set[str]) -> list[str]:
    reference_pages = {
        pj(_USER_MANUAL_ROOT, name).replace("\\", "/") for name in enum_files(_USER_MANUAL_ROOT, ext="md") if name.endswith(_USER_MANUAL_REFERENCE_SUFFIX)
    }
    gaps: list[str] = []
    for path in sorted(reference_pages - doc_pages):
        gaps.append(f"api catalog: generated manual reference page {path!r} is not listed in get_api_catalog_table()")
    for path in sorted(doc_pages - reference_pages):
        gaps.append(f"api catalog: catalog doc_page {path!r} is not a generated manual reference page")
    return gaps


def _user_manual_index_links(markdown: str) -> set[str]:
    links: set[str] = set()
    for match in _MARKDOWN_LINK_PATTERN.finditer(markdown):
        target = _user_manual_index_link_target(match.group(1))
        if target:
            links.add(target)
    return links


def _user_manual_index_section_links(markdown: str, gaps: list[str]) -> dict[str, set[str]]:
    links: dict[str, set[str]] = {}
    for label, heading in _USER_MANUAL_API_REFERENCE_SECTION_HEADINGS.items():
        section = _user_manual_index_section(markdown, heading)
        if not section:
            gaps.append(f"api catalog: user manual index {_USER_MANUAL_INDEX_PAGE!r} is missing {label} section {heading!r}")
        links[label] = _user_manual_index_links(section)
    return links


def _user_manual_index_section(markdown: str, heading: str) -> str:
    lines = markdown.splitlines()
    try:
        start = lines.index(heading) + 1
    except ValueError:
        return ""
    end = next((index for index in range(start, len(lines)) if lines[index].startswith("## ")), len(lines))
    return "\n".join(lines[start:end])


def _user_manual_stale_reference_link_gaps(section_links: Mapping[str, set[str]], catalog_doc_pages: set[str], gaps: list[str]) -> None:
    for section, linked_pages in section_links.items():
        for path in sorted(linked_pages - catalog_doc_pages):
            if not path.endswith(_USER_MANUAL_REFERENCE_SUFFIX):
                continue
            gaps.append(
                f"API catalog: user manual index {_USER_MANUAL_INDEX_PAGE!r} {section} section links generated reference {path!r} not listed in get_api_catalog_table()"
            )


def _user_manual_index_link_target(target: str) -> str:
    path = target.split("#", 1)[0].strip()
    if not path or "://" in path or not path.endswith(".md"):
        return ""
    if path.startswith(f"{_USER_MANUAL_ROOT}/"):
        return path
    return pj(_USER_MANUAL_ROOT, path).replace("\\", "/")


def _api_catalog_row_text(row: Mapping[str, object], index: int, field: str, gaps: list[str]) -> str:
    value = row.get(field)
    if isinstance(value, str) and value:
        return value
    gaps.append(f"api catalog: row {index} has invalid {field} {value!r}")
    return ""


def _api_catalog_optional_row_text(row: Mapping[str, object], index: int, field: str, gaps: list[str]) -> str:
    value = row.get(field)
    if isinstance(value, str):
        return value
    gaps.append(f"api catalog: row {index} has invalid {field} {value!r}")
    return ""


def _api_source_module_name(path: str) -> str:
    module_name = path.removesuffix(".py").replace("/", ".").removeprefix("src.")
    return module_name.removesuffix(".__init__")


def _api_table_function_row_keys(path: str, tree: ast.AST) -> dict[str, str]:
    row_keys = {
        node.name: _DEFAULT_API_TABLE_ROW_KEY_FIELD
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name.startswith("get_") and node.name.endswith("api_table")
    }
    row_keys.update(_MANUAL_API_TABLE_ROW_KEY_FIELDS.get(path, {}))
    return row_keys


def _api_table_rows(function: ApiTableFunction, table: Mapping[str, object]) -> tuple[list[str], list[Mapping[str, object]]]:
    rows = table.get(_API_TABLE_ROWS_FIELD)
    label = f"{function.module_name}.{function.function_name}"
    if not isinstance(rows, list):
        return [f"{label}: rows is {type(rows).__name__}, not a list"], []
    if not rows:
        return [f"{label}: rows is empty"], []
    row_list: list[Mapping[str, object]] = []
    gaps: list[str] = []
    for index, row in enumerate(rows):
        if isinstance(row, Mapping):
            row_list.append(row)
            continue
        gaps.append(f"{label}: row {index} is {type(row).__name__}, not a mapping")
    return gaps, row_list


def _api_row_count_gaps(function: ApiTableFunction, table: Mapping[str, object], rows: list[Mapping[str, object]]) -> list[str]:
    expected = table.get(_API_TABLE_ROW_COUNT_FIELD)
    if not isinstance(expected, int) or isinstance(expected, bool):
        return [f"{function.module_name}.{function.function_name}: row_count {expected!r} is not an int"]
    if expected == len(rows):
        return []
    return [f"{function.module_name}.{function.function_name}: row_count {expected!r} != {len(rows)} rows"]


def _api_table_payload_field_gaps(function: ApiTableFunction, table: Mapping[str, object]) -> list[str]:
    if function.function_name == _API_CATALOG_TABLE_FUNCTION_NAME:
        return []
    index_names = api_table_index_names(table)
    expected_fields = {
        _API_TABLE_SCHEMA_FIELD,
        _API_TABLE_ROW_COUNT_FIELD,
        _API_TABLE_ROWS_FIELD,
        *index_names,
    }
    gaps: list[str] = []
    if not index_names:
        gaps.append(f"{function.module_name}.{function.function_name}: missing index fields")
    for field in sorted(set(table) - expected_fields):
        gaps.append(f"{function.module_name}.{function.function_name}: has undocumented table field {field!r}")
    return gaps


def _api_table_typed_payload_field_gaps(function: ApiTableFunction, table: Mapping[str, object]) -> list[str]:
    table_type = _api_table_return_type(function)
    if not is_typeddict(table_type):
        return []
    typed_fields = set(get_type_hints(table_type))
    table_fields = set(table)
    label = f"{function.module_name}.{function.function_name}"
    type_name = table_type.__name__
    gaps: list[str] = []
    for field in sorted(table_fields - typed_fields):
        gaps.append(f"{label}: {type_name} is missing typed field {field!r}")
    for field in sorted(typed_fields - table_fields):
        gaps.append(f"{label}: {type_name} declares stale typed field {field!r}")
    return gaps


def _api_table_typed_row_field_gaps(function: ApiTableFunction, rows: list[Mapping[str, object]]) -> list[str]:
    row_type = _api_table_row_type(function)
    if not is_typeddict(row_type):
        return []
    typed_fields = set(get_type_hints(row_type))
    row_fields = {field for row in rows for field in row}
    label = f"{function.module_name}.{function.function_name}"
    type_name = row_type.__name__
    gaps: list[str] = []
    for field in sorted(row_fields - typed_fields):
        gaps.append(f"{label}: {type_name} is missing typed row field {field!r}")
    for field in sorted(typed_fields - row_fields):
        gaps.append(f"{label}: {type_name} declares stale typed row field {field!r}")
    return gaps


def _api_table_return_type(function: ApiTableFunction) -> object:
    helper = getattr(importlib.import_module(function.module_name), function.function_name)
    return get_type_hints(helper).get("return")


def _api_table_row_type(function: ApiTableFunction) -> object:
    table_type = _api_table_return_type(function)
    if not is_typeddict(table_type):
        return None
    rows_type = get_type_hints(table_type).get(_API_TABLE_ROWS_FIELD)
    if get_origin(rows_type) is not list:
        return None
    row_args = get_args(rows_type)
    return row_args[0] if row_args else None


def _api_table_row_keys(function: ApiTableFunction, rows: list[Mapping[str, object]], gaps: list[str]) -> list[str]:
    row_keys: list[str] = []
    for index, row in enumerate(rows):
        key = _api_non_empty_row_string(function, row, index, function.row_key_field, gaps)
        if key:
            row_keys.append(key)
        _api_non_empty_row_string(function, row, index, "doc_page", gaps)
        _api_non_empty_row_string(function, row, index, "test_anchor", gaps)
    duplicates = sorted({key for key in row_keys if row_keys.count(key) > 1})
    for key in duplicates:
        gaps.append(f"{function.module_name}.{function.function_name}: duplicate {function.row_key_field} {key!r}")
    return row_keys


def _api_non_empty_row_string(
    function: ApiTableFunction,
    row: Mapping[str, object],
    index: int,
    field: str,
    gaps: list[str],
) -> str:
    value = row.get(field)
    if isinstance(value, str) and value:
        return value
    gaps.append(f"{function.module_name}.{function.function_name}: row {index} has invalid {field} {value!r}")
    return ""


def _api_table_index_gaps(function: ApiTableFunction, table: Mapping[str, object], row_keys: set[str]) -> list[str]:
    gaps: list[str] = []
    for index_name in api_table_index_names(table):
        index = table[index_name]
        if not isinstance(index, Mapping):
            gaps.append(f"{function.module_name}.{function.function_name}: {index_name} is not a mapping")
            continue
        for key, values in index.items():
            gaps.extend(_api_table_index_value_gaps(function, index_name, key, values, row_keys))
    return gaps


def _api_table_index_row_field(
    function: ApiTableFunction,
    index_name: str,
    rows: list[Mapping[str, object]],
    gaps: list[str],
) -> str:
    field = index_name.removesuffix("_index")
    candidates = (field, *(f"{field}{suffix}" for suffix in _API_TABLE_INDEX_LIST_FIELD_SUFFIXES))
    for candidate in candidates:
        if any(candidate in row for row in rows):
            return candidate
    gaps.append(f"{function.module_name}.{function.function_name}: {index_name} has no matching row field")
    return ""


def _api_table_index_row_values(
    function: ApiTableFunction,
    row: Mapping[str, object],
    index: int,
    field: str,
    gaps: list[str],
) -> list[str]:
    value = row.get(field)
    if isinstance(value, str) and value:
        return [value]
    if isinstance(value, list) and all(isinstance(item, str) and item for item in value):
        return list(value)
    if value == "" or value == []:
        return []
    gaps.append(f"{function.module_name}.{function.function_name}: row {index} has invalid indexed field {field} {value!r}")
    return []


def _api_table_index_contains_row(
    function: ApiTableFunction,
    index_name: str,
    value: str,
    row_key: str,
    index: Mapping[object, object],
    gaps: list[str],
) -> None:
    row_keys = index.get(value)
    if not isinstance(row_keys, list):
        gaps.append(f"{function.module_name}.{function.function_name}: {index_name}[{value!r}] is not a list")
        return
    if row_key not in row_keys:
        gaps.append(f"{function.module_name}.{function.function_name}: {index_name}[{value!r}] is missing row {row_key!r}")


def _api_table_index_matches_row_fields(
    function: ApiTableFunction,
    index_name: str,
    index: Mapping[object, object],
    expected_row_values: Mapping[str, set[str]],
    gaps: list[str],
) -> None:
    for key, values in index.items():
        if not isinstance(key, str) or not isinstance(values, list):
            continue
        for row_key in values:
            if not isinstance(row_key, str):
                continue
            if row_key in expected_row_values and key not in expected_row_values[row_key]:
                gaps.append(f"{function.module_name}.{function.function_name}: {index_name}[{key!r}] includes row {row_key!r} without matching row field")


def _api_table_index_value_gaps(
    function: ApiTableFunction,
    index_name: str,
    key: object,
    values: object,
    row_keys: set[str],
) -> list[str]:
    gaps: list[str] = []
    if not isinstance(key, str) or not key:
        gaps.append(f"{function.module_name}.{function.function_name}: {index_name} has invalid key {key!r}")
    if not isinstance(values, list):
        gaps.append(f"{function.module_name}.{function.function_name}: {index_name}[{key!r}] is not a list")
        return gaps
    if not values:
        gaps.append(f"{function.module_name}.{function.function_name}: {index_name}[{key!r}] has empty rows")
        return gaps
    seen_values: set[str] = set()
    for value in values:
        if not isinstance(value, str) or not value:
            gaps.append(f"{function.module_name}.{function.function_name}: {index_name}[{key!r}] has invalid row {value!r}")
            continue
        if value in seen_values:
            gaps.append(f"{function.module_name}.{function.function_name}: {index_name}[{key!r}] has duplicate row {value!r}")
            continue
        seen_values.add(value)
        if value not in row_keys:
            gaps.append(f"{function.module_name}.{function.function_name}: {index_name}[{key!r}] points at unknown row {value!r}")
    return gaps
