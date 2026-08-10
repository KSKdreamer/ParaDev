import api_table_contract_helpers as api_contracts
from api_table_contract_helpers import (
    api_catalog_api_table_helper_gaps,
    api_catalog_cli_command_gaps,
    api_catalog_index_catalog_gaps,
    api_catalog_index_coverage_gaps,
    api_catalog_payload_metadata_gaps,
    api_catalog_reference_gaps,
    api_catalog_row_shape_gaps,
    api_catalog_selector_surface_gaps,
    api_catalog_surface_contract_gaps,
    api_catalog_summary_group_gaps,
    api_manual_reference_index_gaps,
    api_selection_functions,
    api_source_trees,
    api_selection_table_gaps,
    api_table_functions,
    api_table_index_coverage_gaps,
    api_table_payload_gaps,
    api_table_reference_gaps,
    api_table_row_shape_gaps,
    api_table_schema_gaps,
    api_reference_markdown_gaps,
    function_calls,
    function_names,
    load_api_table,
)
import importlib

import paradev.sdk as sdk
import paradev.surfaces as surfaces
import paradev.surfaces.cli as cli
import paradev.surfaces.rest as rest

_MANUAL_API_SELECTION_HELPERS = {
    "src/paradev/sdk/frontend_api.py": {"get_frontend_api_selection"},
}


def test_api_table_modules_expose_selection_helpers() -> None:
    gaps: list[str] = []
    for path, tree, text in api_source_trees():
        functions = function_names(tree)
        if not any(name.startswith("get_") and name.endswith("api_table") for name in functions):
            continue
        if any(name.startswith("get_") and name.endswith("api_selection") for name in functions):
            continue
        if "api_table_selection" in text:
            continue
        gaps.append(path)

    assert gaps == []


def test_standard_api_selection_helpers_use_shared_selector() -> None:
    gaps: list[str] = []
    seen_manual: dict[str, set[str]] = {path: set() for path in _MANUAL_API_SELECTION_HELPERS}
    for path, tree, _text in api_source_trees():
        for node in api_selection_functions(tree):
            if node.name in _MANUAL_API_SELECTION_HELPERS.get(path, set()):
                seen_manual[path].add(node.name)
                continue
            if function_calls(node, "api_table_selection"):
                continue
            gaps.append(f"{path}:{node.name}")

    assert gaps == []
    assert seen_manual == _MANUAL_API_SELECTION_HELPERS


def test_api_tables_have_auditable_reference_payloads() -> None:
    gaps: list[str] = []
    for function in api_table_functions():
        gaps.extend(api_table_payload_gaps(function, load_api_table(function)))

    assert gaps == []


def test_api_table_payload_contract_flags_non_string_index_keys() -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_rest_api_table")
    table = load_api_table(function)
    row_key = table["rows"][0][function.row_key_field]
    patched_table = {
        **table,
        "method_index": {**table["method_index"], 42: [row_key]},
    }

    gaps = api_table_payload_gaps(function, patched_table)

    assert any("method_index" in gap and "42" in gap for gap in gaps)


def test_api_table_payload_contract_flags_duplicate_index_values() -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_rest_api_table")
    table = load_api_table(function)
    first_row = table["rows"][0]
    method = first_row["method"]
    row_key = first_row[function.row_key_field]
    patched_table = {
        **table,
        "method_index": {key: list(values) for key, values in table["method_index"].items()},
    }
    patched_table["method_index"][method].append(row_key)

    gaps = api_table_payload_gaps(function, patched_table)

    assert any("duplicate" in gap and "method_index" in gap and row_key in gap for gap in gaps)


def test_api_table_payload_contract_flags_empty_index_values() -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_rest_api_table")
    table = load_api_table(function)
    patched_table = {
        **table,
        "method_index": {**table["method_index"], "STALE": []},
    }

    gaps = api_table_payload_gaps(function, patched_table)

    assert any("method_index" in gap and "STALE" in gap and "empty" in gap for gap in gaps)


def test_api_table_payload_contract_flags_non_integer_row_count() -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_rest_api_table")
    table = load_api_table(function)
    patched_table = {**table, "row_count": float(table["row_count"])}

    gaps = api_table_payload_gaps(function, patched_table)

    assert any("row_count" in gap and "int" in gap for gap in gaps)


def test_api_table_payload_contract_flags_empty_rows() -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_rest_api_table")
    table = load_api_table(function)
    patched_table = {
        **table,
        "row_count": 0,
        "method_index": {},
        "feature_index": {},
        "frontend_operation_index": {},
        "rows": [],
    }

    gaps = api_table_payload_gaps(function, patched_table)

    assert any("rows" in gap and "empty" in gap for gap in gaps)


def test_api_table_payload_contract_flags_undocumented_table_field() -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_rest_api_table")
    table = load_api_table(function)
    patched_table = {**table, "stale_metadata": {"row_count": table["row_count"]}}

    gaps = api_table_payload_gaps(function, patched_table)

    assert any("stale_metadata" in gap and "undocumented table field" in gap for gap in gaps)


def test_api_table_payload_contract_flags_missing_index_fields() -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_rest_api_table")
    table = load_api_table(function)
    patched_table = {key: value for key, value in table.items() if not key.endswith("_index")}

    gaps = api_table_payload_gaps(function, patched_table)

    assert any("index" in gap and "missing" in gap for gap in gaps)


def test_api_table_payload_contract_flags_missing_typed_index_field(monkeypatch) -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_rest_api_table")
    module = importlib.import_module(function.module_name)
    monkeypatch.delitem(module.RestApiTable.__annotations__, "method_index")

    gaps = api_table_payload_gaps(function, load_api_table(function))

    assert any("RestApiTable" in gap and "method_index" in gap and "missing typed field" in gap for gap in gaps)


def test_api_table_payload_contract_flags_stale_typed_index_field(monkeypatch) -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_rest_api_table")
    module = importlib.import_module(function.module_name)
    monkeypatch.setitem(module.RestApiTable.__annotations__, "stale_index", dict[str, list[str]])

    gaps = api_table_payload_gaps(function, load_api_table(function))

    assert any("RestApiTable" in gap and "stale_index" in gap and "stale typed field" in gap for gap in gaps)


def test_api_table_row_shape_flags_missing_typed_row_field(monkeypatch) -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_rest_api_table")
    module = importlib.import_module(function.module_name)
    monkeypatch.delitem(module.RestApiRow.__annotations__, "method")

    gaps = api_table_row_shape_gaps(function, load_api_table(function))

    assert any("RestApiRow" in gap and "method" in gap and "missing typed row field" in gap for gap in gaps)


def test_api_table_row_shape_flags_stale_typed_row_field(monkeypatch) -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_rest_api_table")
    module = importlib.import_module(function.module_name)
    monkeypatch.setitem(module.RestApiRow.__annotations__, "stale_field", str)

    gaps = api_table_row_shape_gaps(function, load_api_table(function))

    assert any("RestApiRow" in gap and "stale_field" in gap and "stale typed row field" in gap for gap in gaps)


def test_api_tables_have_unique_stable_schemas() -> None:
    tables = [(function, load_api_table(function)) for function in api_table_functions()]

    assert api_table_schema_gaps(tables) == []


def test_api_tables_flag_duplicate_schema() -> None:
    tables = [(function, load_api_table(function)) for function in api_table_functions()]
    first_function, first_table = tables[0]
    second_function, second_table = tables[1]
    patched_second_table = {**second_table, "schema": first_table["schema"]}

    gaps = api_table_schema_gaps([(first_function, first_table), (second_function, patched_second_table)])

    assert any("duplicate schema" in gap for gap in gaps)


def test_standard_api_tables_have_stable_row_shape() -> None:
    gaps: list[str] = []
    for function in api_table_functions():
        gaps.extend(api_table_row_shape_gaps(function, load_api_table(function)))

    assert gaps == []


def test_standard_api_table_indexes_cover_row_fields() -> None:
    gaps: list[str] = []
    for function in api_table_functions():
        gaps.extend(api_table_index_coverage_gaps(function, load_api_table(function)))

    assert gaps == []


def test_standard_api_table_index_coverage_flags_missing_row_value() -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_rest_api_table")
    table = load_api_table(function)
    first_row = table["rows"][0]
    method = first_row["method"]
    row_key = first_row[function.row_key_field]
    patched_table = {
        **table,
        "method_index": {key: list(values) for key, values in table["method_index"].items()},
    }
    patched_table["method_index"][method] = [value for value in patched_table["method_index"][method] if value != row_key]

    gaps = api_table_index_coverage_gaps(function, patched_table)

    assert any("method_index" in gap and row_key in gap for gap in gaps)


def test_standard_api_table_index_coverage_flags_unknown_row_value() -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_rest_api_table")
    table = load_api_table(function)
    first_method, row_keys = next(iter(table["method_index"].items()))
    patched_table = {
        **table,
        "method_index": {
            **table["method_index"],
            first_method: [*row_keys, "stale-rest-api-row"],
        },
    }

    gaps = api_table_index_coverage_gaps(function, patched_table)

    assert any("method_index" in gap and "stale-rest-api-row" in gap and "unknown" in gap for gap in gaps)


def test_standard_api_table_index_coverage_flags_wrong_index_key() -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_rest_api_table")
    table = load_api_table(function)
    get_row_key = table["method_index"]["GET"][0]
    patched_table = {
        **table,
        "method_index": {
            **table["method_index"],
            "POST": [*table["method_index"]["POST"], get_row_key],
        },
    }

    gaps = api_table_index_coverage_gaps(function, patched_table)

    assert any("method_index" in gap and "POST" in gap and get_row_key in gap and "matching row field" in gap for gap in gaps)


def test_standard_api_tables_flag_empty_shared_row_field() -> None:
    function = next(function for function in api_table_functions() if function.function_name != "get_api_catalog_table")
    table = load_api_table(function)
    patched_table = {
        **table,
        "rows": [dict(row) for row in table["rows"]],
    }
    patched_table["rows"][0]["surface"] = ""

    gaps = api_table_row_shape_gaps(function, patched_table)

    assert any("surface" in gap for gap in gaps)


def test_standard_api_tables_flag_row_field_set_drift() -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_rest_api_table")
    table = load_api_table(function)
    patched_rows = [dict(row) for row in table["rows"]]
    patched_rows[1].pop("inputs")
    patched_rows[1]["stale_field"] = "not documented"
    patched_table = {**table, "rows": patched_rows}

    gaps = api_table_row_shape_gaps(function, patched_table)

    assert any("missing field" in gap and "inputs" in gap for gap in gaps)
    assert any("undocumented field" in gap and "stale_field" in gap for gap in gaps)


def test_standard_api_tables_list_selection_helpers() -> None:
    assert api_selection_table_gaps() == []


def test_api_tables_reference_existing_docs_and_tests() -> None:
    gaps: list[str] = []
    for function in api_table_functions():
        gaps.extend(api_table_reference_gaps(function, load_api_table(function)))

    assert gaps == []


def test_api_table_reference_contract_flags_non_docs_doc_page() -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_rest_api_table")
    table = load_api_table(function)
    row = dict(table["rows"][0])
    row["doc_page"] = "README.md"
    patched_table = {**table, "rows": [row, *table["rows"][1:]]}

    gaps = api_table_reference_gaps(function, patched_table)

    assert any("doc_page" in gap and "docs/" in gap and "README.md" in gap for gap in gaps)


def test_api_table_reference_contract_flags_non_tests_anchor() -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_rest_api_table")
    table = load_api_table(function)
    row = dict(table["rows"][0])
    row["test_anchor"] = "src/paradev/cli.py::main"
    patched_table = {**table, "rows": [row, *table["rows"][1:]]}

    gaps = api_table_reference_gaps(function, patched_table)

    assert any("test_anchor" in gap and "tests/" in gap and "src/paradev/cli.py::main" in gap for gap in gaps)


def test_api_reference_markdown_matches_renderers() -> None:
    gaps: list[str] = []
    for function in api_table_functions():
        gaps.extend(api_reference_markdown_gaps(function))

    assert gaps == []


def test_api_reference_markdown_contract_flags_missing_title(monkeypatch) -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_rest_api_table")
    module = importlib.import_module(function.module_name)
    original_renderer = module.render_rest_api_reference_markdown
    title = "# REST API Reference"
    patched_markdown = "\n".join(line for line in original_renderer().splitlines() if line != title)
    monkeypatch.setattr(module, "render_rest_api_reference_markdown", lambda: patched_markdown)

    gaps = api_reference_markdown_gaps(function)

    assert any("title" in gap and "REST API Reference" in gap and "markdown" in gap for gap in gaps)


def test_api_reference_markdown_contract_flags_stale_source(monkeypatch) -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_rest_api_table")
    module = importlib.import_module(function.module_name)
    original_renderer = module.render_rest_api_reference_markdown
    expected = "Generated from `paradev.surfaces.rest.get_rest_api_table()`."
    stale = "Generated from `paradev.surfaces.rest.get_stale_rest_api_table()`."
    patched_markdown = original_renderer().replace(expected, stale, 1)
    monkeypatch.setattr(module, "render_rest_api_reference_markdown", lambda: patched_markdown)

    gaps = api_reference_markdown_gaps(function)

    assert any("source" in gap and expected in gap and stale in gap for gap in gaps)


def test_api_reference_markdown_contract_flags_stale_regeneration_note(monkeypatch) -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_rest_api_table")
    module = importlib.import_module(function.module_name)
    original_renderer = module.render_rest_api_reference_markdown
    expected = "Regenerate this file whenever the REST/OpenAPI route table changes:"
    stale = "Regenerate this file whenever stale REST routes change:"
    patched_markdown = original_renderer().replace(expected, stale, 1)
    monkeypatch.setattr(module, "render_rest_api_reference_markdown", lambda: patched_markdown)

    gaps = api_reference_markdown_gaps(function)

    assert any("regeneration note" in gap and expected in gap and stale in gap for gap in gaps)


def test_api_reference_markdown_contract_flags_stale_regeneration_command(monkeypatch) -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_rest_api_table")
    module = importlib.import_module(function.module_name)
    original_renderer = module.render_rest_api_reference_markdown
    expected = "rtk uv run paradev rest-api --markdown > docs/user-manual/rest-api-reference.md"
    stale = "rtk uv run paradev stale-rest-api --markdown > docs/user-manual/rest-api-reference.md"
    patched_markdown = original_renderer().replace(expected, stale, 1)
    monkeypatch.setattr(module, "render_rest_api_reference_markdown", lambda: patched_markdown)

    gaps = api_reference_markdown_gaps(function)

    assert any("regeneration command" in gap and expected in gap and stale in gap for gap in gaps)


def test_api_reference_markdown_contract_flags_missing_standard_summary_row_count(monkeypatch) -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_rest_api_table")
    table = load_api_table(function)
    summary_line = f"- API rows / API 行数: {table['row_count']}"
    module = importlib.import_module(function.module_name)
    original_renderer = module.render_rest_api_reference_markdown
    patched_markdown = "\n".join(line for line in original_renderer().splitlines() if line != summary_line)
    monkeypatch.setattr(module, "render_rest_api_reference_markdown", lambda: patched_markdown)

    gaps = api_reference_markdown_gaps(function)

    assert any("summary" in gap and "row_count" in gap and "markdown" in gap for gap in gaps)


def test_api_reference_markdown_contract_flags_stale_standard_summary_row_count(monkeypatch) -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_rest_api_table")
    table = load_api_table(function)
    summary_line = f"- API rows / API 行数: {table['row_count']}"
    stale_line = f"- API rows / API 行数: {table['row_count'] + 1}"
    module = importlib.import_module(function.module_name)
    original_renderer = module.render_rest_api_reference_markdown
    patched_lines: list[str] = []
    for line in original_renderer().splitlines():
        patched_lines.append(line)
        if line == summary_line:
            patched_lines.append(stale_line)
    monkeypatch.setattr(module, "render_rest_api_reference_markdown", lambda: "\n".join(patched_lines))

    gaps = api_reference_markdown_gaps(function)

    assert any(stale_line in gap and "stale summary row_count" in gap for gap in gaps)


def test_api_reference_markdown_contract_flags_unexpected_summary_line(monkeypatch) -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_rest_api_table")
    table = load_api_table(function)
    summary_line = f"- API rows / API 行数: {table['row_count']}"
    unexpected_line = "- Stale summary / Stale 汇总: ghost"
    module = importlib.import_module(function.module_name)
    original_renderer = module.render_rest_api_reference_markdown
    patched_lines: list[str] = []
    for line in original_renderer().splitlines():
        patched_lines.append(line)
        if line == summary_line:
            patched_lines.append(unexpected_line)
    monkeypatch.setattr(module, "render_rest_api_reference_markdown", lambda: "\n".join(patched_lines))

    gaps = api_reference_markdown_gaps(function)

    assert any(unexpected_line in gap and "unexpected summary" in gap for gap in gaps)


def test_api_reference_markdown_contract_flags_missing_standard_summary_index_count(monkeypatch) -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_package_api_table")
    table = load_api_table(function)
    summary_line = f"- Package modules / Package 模块数: {len(table['module_index'])}"
    module = importlib.import_module(function.module_name)
    original_renderer = module.render_package_api_reference_markdown
    patched_markdown = "\n".join(line for line in original_renderer().splitlines() if line != summary_line)
    monkeypatch.setattr(module, "render_package_api_reference_markdown", lambda: patched_markdown)

    gaps = api_reference_markdown_gaps(function)

    assert any("summary" in gap and "module_index" in gap and "markdown" in gap for gap in gaps)


def test_api_reference_markdown_contract_flags_missing_custom_summary_index_count(monkeypatch) -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_rest_api_table")
    table = load_api_table(function)
    summary_line = f"- Methods / Method 数: {len(table['method_index'])}"
    module = importlib.import_module(function.module_name)
    original_renderer = module.render_rest_api_reference_markdown
    patched_markdown = "\n".join(line for line in original_renderer().splitlines() if line != summary_line)
    monkeypatch.setattr(module, "render_rest_api_reference_markdown", lambda: patched_markdown)

    gaps = api_reference_markdown_gaps(function)

    assert any("summary" in gap and "method_index" in gap and "markdown" in gap for gap in gaps)


def test_api_reference_markdown_contract_flags_missing_surface_summary_index_count(monkeypatch) -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_catalog_api_table")
    table = load_api_table(function)
    summary_line = f"- Surfaces / Surface 数: {len(table['surface_index'])}"
    module = importlib.import_module(function.module_name)
    original_renderer = module.render_catalog_api_reference_markdown
    patched_markdown = "\n".join(line for line in original_renderer().splitlines() if line != summary_line)
    monkeypatch.setattr(module, "render_catalog_api_reference_markdown", lambda: patched_markdown)

    gaps = api_reference_markdown_gaps(function)

    assert any("summary" in gap and "surface_index" in gap and "markdown" in gap for gap in gaps)


def test_api_reference_markdown_contract_flags_missing_custom_summary_index_key_count(monkeypatch) -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_mcp_api_table")
    table = load_api_table(function)
    summary_line = f"- Read tools / 读取工具数: {len(table['mode_index'].get('read', []))}"
    module = importlib.import_module(function.module_name)
    original_renderer = module.render_mcp_api_reference_markdown
    patched_markdown = "\n".join(line for line in original_renderer().splitlines() if line != summary_line)
    monkeypatch.setattr(module, "render_mcp_api_reference_markdown", lambda: patched_markdown)

    gaps = api_reference_markdown_gaps(function)

    assert any("summary" in gap and "mode_index" in gap and "read" in gap and "markdown" in gap for gap in gaps)


def test_api_reference_markdown_contract_flags_missing_custom_summary_literal(monkeypatch) -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_rest_api_table")
    module = importlib.import_module(function.module_name)
    original_renderer = module.render_rest_api_reference_markdown
    summary_line = next(
        line for line in original_renderer().splitlines() if line.startswith("- Selector helper / Selector helper: Use `get_rest_api_selection")
    )
    patched_markdown = "\n".join(line for line in original_renderer().splitlines() if line != summary_line)
    monkeypatch.setattr(module, "render_rest_api_reference_markdown", lambda: patched_markdown)

    gaps = api_reference_markdown_gaps(function)

    assert any("summary" in gap and "selector_helper" in gap and "markdown" in gap for gap in gaps)


def test_api_reference_markdown_contract_flags_missing_section_heading(monkeypatch) -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_rest_api_table")
    module = importlib.import_module(function.module_name)
    original_renderer = module.render_rest_api_reference_markdown
    heading = "## Feature Index / Feature 索引"
    patched_markdown = "\n".join(line for line in original_renderer().splitlines() if line != heading)
    monkeypatch.setattr(module, "render_rest_api_reference_markdown", lambda: patched_markdown)

    gaps = api_reference_markdown_gaps(function)

    assert any("section heading" in gap and heading in gap for gap in gaps)


def test_api_reference_markdown_contract_flags_unexpected_section_heading(monkeypatch) -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_rest_api_table")
    module = importlib.import_module(function.module_name)
    original_renderer = module.render_rest_api_reference_markdown
    heading = "## Stale Section / Stale Section"
    patched_markdown = original_renderer().replace("## API Standard Table / API 标准表", f"{heading}\n\n## API Standard Table / API 标准表", 1)
    monkeypatch.setattr(module, "render_rest_api_reference_markdown", lambda: patched_markdown)

    gaps = api_reference_markdown_gaps(function)

    assert any("unexpected section heading" in gap and heading in gap for gap in gaps)


def test_api_reference_markdown_contract_flags_duplicate_section_heading(monkeypatch) -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_rest_api_table")
    module = importlib.import_module(function.module_name)
    original_renderer = module.render_rest_api_reference_markdown
    heading = "## Summary / 汇总"
    patched_markdown = original_renderer().replace("## API Standard Table / API 标准表", f"{heading}\n\n## API Standard Table / API 标准表", 1)
    monkeypatch.setattr(module, "render_rest_api_reference_markdown", lambda: patched_markdown)

    gaps = api_reference_markdown_gaps(function)

    assert any("duplicate section heading" in gap and heading in gap for gap in gaps)


def test_api_reference_markdown_contract_flags_unmapped_index_heading(monkeypatch) -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_rest_api_table")
    table = load_api_table(function)
    row_key = table["rows"][0][function.row_key_field]
    module = importlib.import_module(function.module_name)
    patched_table = {**table, "custom_index": {"custom": [row_key]}}
    monkeypatch.setattr(module, function.function_name, lambda: patched_table)

    gaps = api_reference_markdown_gaps(function)

    assert any("custom_index" in gap and "section heading" in gap for gap in gaps)


def test_api_reference_markdown_contract_flags_missing_table_row(monkeypatch) -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_rest_api_table")
    table = load_api_table(function)
    row_key = table["rows"][0][function.row_key_field]
    module = importlib.import_module(function.module_name)
    original_renderer = module.render_rest_api_reference_markdown
    patched_markdown = "\n".join(line for line in original_renderer().splitlines() if f"`{row_key}`" not in line)
    monkeypatch.setattr(module, "render_rest_api_reference_markdown", lambda: patched_markdown)

    gaps = api_reference_markdown_gaps(function)

    assert any(row_key in gap and "markdown" in gap for gap in gaps)


def test_api_reference_markdown_contract_flags_stale_standard_table_row(monkeypatch) -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_rest_api_table")
    module = importlib.import_module(function.module_name)
    original_renderer = module.render_rest_api_reference_markdown
    original_lines = original_renderer().splitlines()
    source_row = next(line for line in original_lines if line.startswith("| `GET /health` |"))
    stale_row = source_row.replace("`GET /health`", "`STALE /ghost`", 1)
    patched_lines: list[str] = []
    for line in original_lines:
        patched_lines.append(line)
        if line == source_row:
            patched_lines.append(stale_row)
    monkeypatch.setattr(module, "render_rest_api_reference_markdown", lambda: "\n".join(patched_lines))

    gaps = api_reference_markdown_gaps(function)

    assert any("STALE /ghost" in gap and "stale table row" in gap for gap in gaps)


def test_api_reference_markdown_contract_flags_incomplete_standard_table_row(monkeypatch) -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_package_api_table")
    table = load_api_table(function)
    row = table["rows"][0]
    module = importlib.import_module(function.module_name)
    original_renderer = module.render_package_api_reference_markdown
    row_prefix = f"| `{row['symbol']}` | `{row['kind']}` |"
    test_anchor_cell = f"`{row['test_anchor']}` |"
    patched_lines = [f"{line.removesuffix(test_anchor_cell)} |" if line.startswith(row_prefix) else line for line in original_renderer().splitlines()]
    monkeypatch.setattr(module, "render_package_api_reference_markdown", lambda: "\n".join(patched_lines))

    gaps = api_reference_markdown_gaps(function)

    assert any(row["symbol"] in gap and "complete table row" in gap and "markdown" in gap for gap in gaps)


def test_api_reference_markdown_contract_flags_incomplete_catalog_table_row(monkeypatch) -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_api_catalog_table")
    table = load_api_table(function)
    row = next(row for row in table["rows"] if row["id"] == "api-catalog")
    module = importlib.import_module(function.module_name)
    original_renderer = module.render_api_catalog_reference_markdown
    row_prefix = f"| `{row['id']}` | {row['title']} |"
    test_anchor_cell = f"`{row['test_anchor']}` |"
    patched_lines = [f"{line.removesuffix(test_anchor_cell)} |" if line.startswith(row_prefix) else line for line in original_renderer().splitlines()]
    monkeypatch.setattr(module, "render_api_catalog_reference_markdown", lambda: "\n".join(patched_lines))

    gaps = api_reference_markdown_gaps(function)

    assert any(row["id"] in gap and "catalog table row" in gap and "markdown" in gap for gap in gaps)


def test_api_reference_markdown_contract_flags_stale_catalog_table_row(monkeypatch) -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_api_catalog_table")
    module = importlib.import_module(function.module_name)
    original_renderer = module.render_api_catalog_reference_markdown
    original_lines = original_renderer().splitlines()
    source_row = next(line for line in original_lines if line.startswith("| `api-catalog` | API Catalog Reference |"))
    stale_row = source_row.replace("`api-catalog`", "`stale-api-reference`", 1)
    patched_lines: list[str] = []
    for line in original_lines:
        patched_lines.append(line)
        if line == source_row:
            patched_lines.append(stale_row)
    monkeypatch.setattr(module, "render_api_catalog_reference_markdown", lambda: "\n".join(patched_lines))

    gaps = api_reference_markdown_gaps(function)

    assert any("stale-api-reference" in gap and "stale catalog table row" in gap for gap in gaps)


def test_api_reference_markdown_contract_flags_missing_index_key(monkeypatch) -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_rest_api_table")
    table = load_api_table(function)
    method = next(iter(table["method_index"]))
    module = importlib.import_module(function.module_name)
    original_renderer = module.render_rest_api_reference_markdown
    patched_markdown = "\n".join(line for line in original_renderer().splitlines() if not line.startswith(f"| `{method}` |"))
    monkeypatch.setattr(module, "render_rest_api_reference_markdown", lambda: patched_markdown)

    gaps = api_reference_markdown_gaps(function)

    assert any(method in gap and "method_index" in gap for gap in gaps)


def test_api_reference_markdown_contract_flags_incomplete_index_row(monkeypatch) -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_rest_api_table")
    table = load_api_table(function)
    method = next(iter(table["method_index"]))
    module = importlib.import_module(function.module_name)
    original_renderer = module.render_rest_api_reference_markdown
    row_prefix = f"| `{method}` | {len(table['method_index'][method])} |"
    patched_lines = [f"{row_prefix} |" if line.startswith(row_prefix) else line for line in original_renderer().splitlines()]
    monkeypatch.setattr(module, "render_rest_api_reference_markdown", lambda: "\n".join(patched_lines))

    gaps = api_reference_markdown_gaps(function)

    assert any(method in gap and "method_index" in gap and "index row" in gap for gap in gaps)


def test_api_reference_markdown_contract_flags_stale_index_row(monkeypatch) -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_rest_api_table")
    table = load_api_table(function)
    method = next(iter(table["method_index"]))
    module = importlib.import_module(function.module_name)
    original_renderer = module.render_rest_api_reference_markdown
    original_lines = original_renderer().splitlines()
    source_row = next(line for line in original_lines if line.startswith(f"| `{method}` |"))
    stale_row = source_row.replace(f"`{method}`", "`STALE_METHOD`", 1)
    patched_lines: list[str] = []
    for line in original_lines:
        patched_lines.append(line)
        if line == source_row:
            patched_lines.append(stale_row)
    monkeypatch.setattr(module, "render_rest_api_reference_markdown", lambda: "\n".join(patched_lines))

    gaps = api_reference_markdown_gaps(function)

    assert any("STALE_METHOD" in gap and "method_index" in gap and "stale index row" in gap for gap in gaps)


def test_api_reference_markdown_contract_flags_missing_catalog_group_row(monkeypatch) -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_api_catalog_table")
    table = load_api_table(function)
    reference_group = table["reference_groups"][0]
    module = importlib.import_module(function.module_name)
    original_renderer = module.render_api_catalog_reference_markdown
    row_prefix = f"| `{reference_group['id']}` | {reference_group['title']} |"
    patched_markdown = "\n".join(line for line in original_renderer().splitlines() if not line.startswith(row_prefix))
    monkeypatch.setattr(module, "render_api_catalog_reference_markdown", lambda: patched_markdown)

    gaps = api_reference_markdown_gaps(function)

    assert any(reference_group["id"] in gap and "reference group" in gap and "markdown" in gap for gap in gaps)


def test_api_reference_markdown_contract_flags_incomplete_catalog_group_row(monkeypatch) -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_api_catalog_table")
    table = load_api_table(function)
    reference_group = table["reference_groups"][0]
    module = importlib.import_module(function.module_name)
    original_renderer = module.render_api_catalog_reference_markdown
    row_prefix = f"| `{reference_group['id']}` | {reference_group['title']} |"
    patched_lines = [
        f"{line.removesuffix(reference_group['usage'] + ' |')} |" if line.startswith(row_prefix) else line for line in original_renderer().splitlines()
    ]
    monkeypatch.setattr(module, "render_api_catalog_reference_markdown", lambda: "\n".join(patched_lines))

    gaps = api_reference_markdown_gaps(function)

    assert any(reference_group["id"] in gap and "reference group" in gap and "markdown" in gap for gap in gaps)


def test_api_reference_markdown_contract_flags_stale_catalog_group_row(monkeypatch) -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_api_catalog_table")
    table = load_api_table(function)
    reference_group = table["reference_groups"][0]
    module = importlib.import_module(function.module_name)
    original_renderer = module.render_api_catalog_reference_markdown
    original_lines = original_renderer().splitlines()
    source_row = next(line for line in original_lines if line.startswith(f"| `{reference_group['id']}` | {reference_group['title']} |"))
    stale_row = source_row.replace(f"`{reference_group['id']}`", "`stale-reference-group`", 1)
    patched_lines: list[str] = []
    for line in original_lines:
        patched_lines.append(line)
        if line == source_row:
            patched_lines.append(stale_row)
    monkeypatch.setattr(module, "render_api_catalog_reference_markdown", lambda: "\n".join(patched_lines))

    gaps = api_reference_markdown_gaps(function)

    assert any("stale-reference-group" in gap and "stale reference group row" in gap for gap in gaps)


def test_api_reference_markdown_contract_flags_incomplete_catalog_index_catalog_row(monkeypatch) -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_api_catalog_table")
    table = load_api_table(function)
    index_row = next(row for row in table["index_catalog"] if row["id"] == "surface")
    module = importlib.import_module(function.module_name)
    original_renderer = module.render_api_catalog_reference_markdown
    row_prefix = f"| `{index_row['id']}` | `{index_row['table_path']}` | `{index_row['python_helper']}` |"
    patched_lines = [f"{line.removesuffix(index_row['usage'] + ' |')} |" if line.startswith(row_prefix) else line for line in original_renderer().splitlines()]
    monkeypatch.setattr(module, "render_api_catalog_reference_markdown", lambda: "\n".join(patched_lines))

    gaps = api_reference_markdown_gaps(function)

    assert any(index_row["id"] in gap and "index_catalog" in gap and "markdown" in gap for gap in gaps)


def test_api_reference_markdown_contract_flags_stale_catalog_index_catalog_row(monkeypatch) -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_api_catalog_table")
    table = load_api_table(function)
    index_row = next(row for row in table["index_catalog"] if row["id"] == "surface")
    module = importlib.import_module(function.module_name)
    original_renderer = module.render_api_catalog_reference_markdown
    original_lines = original_renderer().splitlines()
    row_prefix = f"| `{index_row['id']}` | `{index_row['table_path']}` | `{index_row['python_helper']}` |"
    source_row = next(line for line in original_lines if line.startswith(row_prefix))
    stale_row = source_row.replace(f"`{index_row['id']}`", "`stale-index-catalog`", 1)
    patched_lines: list[str] = []
    for line in original_lines:
        patched_lines.append(line)
        if line == source_row:
            patched_lines.append(stale_row)
    monkeypatch.setattr(module, "render_api_catalog_reference_markdown", lambda: "\n".join(patched_lines))

    gaps = api_reference_markdown_gaps(function)

    assert any("stale-index-catalog" in gap and "stale index_catalog row" in gap for gap in gaps)


def test_api_reference_markdown_contract_flags_missing_catalog_summary_line(monkeypatch) -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_api_catalog_table")
    table = load_api_table(function)
    summary_line = f"- References / Reference 数: {table['summary']['reference_count']}"
    module = importlib.import_module(function.module_name)
    original_renderer = module.render_api_catalog_reference_markdown
    patched_markdown = "\n".join(line for line in original_renderer().splitlines() if line != summary_line)
    monkeypatch.setattr(module, "render_api_catalog_reference_markdown", lambda: patched_markdown)

    gaps = api_reference_markdown_gaps(function)

    assert any("summary" in gap and "reference_count" in gap and "markdown" in gap for gap in gaps)


def test_api_reference_markdown_contract_flags_stale_catalog_summary_line(monkeypatch) -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_api_catalog_table")
    table = load_api_table(function)
    summary_line = f"- References / Reference 数: {table['summary']['reference_count']}"
    stale_line = f"- References / Reference 数: {table['summary']['reference_count'] + 1}"
    module = importlib.import_module(function.module_name)
    original_renderer = module.render_api_catalog_reference_markdown
    patched_lines: list[str] = []
    for line in original_renderer().splitlines():
        patched_lines.append(line)
        if line == summary_line:
            patched_lines.append(stale_line)
    monkeypatch.setattr(module, "render_api_catalog_reference_markdown", lambda: "\n".join(patched_lines))

    gaps = api_reference_markdown_gaps(function)

    assert any(stale_line in gap and "stale summary reference_count" in gap for gap in gaps)


def test_api_reference_markdown_contract_flags_missing_catalog_index_count_summary_line(monkeypatch) -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_api_catalog_table")
    table = load_api_table(function)
    summary_line = f"- Index dimensions / Index 维度数: {table['summary']['index_count']}"
    module = importlib.import_module(function.module_name)
    original_renderer = module.render_api_catalog_reference_markdown
    patched_markdown = "\n".join(line for line in original_renderer().splitlines() if line != summary_line)
    monkeypatch.setattr(module, "render_api_catalog_reference_markdown", lambda: patched_markdown)

    gaps = api_reference_markdown_gaps(function)

    assert any("summary" in gap and "index_count" in gap and "markdown" in gap for gap in gaps)


def test_api_catalog_references_match_generated_manual_pages() -> None:
    assert api_catalog_reference_gaps() == []


def test_api_catalog_reference_contract_flags_non_tests_anchor(monkeypatch) -> None:
    table = surfaces.get_api_catalog_table()
    patched_rows = [dict(row) for row in table["rows"]]
    patched_rows[0]["test_anchor"] = "src/paradev/cli.py::main"
    monkeypatch.setattr(surfaces, "get_api_catalog_table", lambda: {**table, "rows": patched_rows})

    gaps = api_catalog_reference_gaps()

    assert any("api catalog api-catalog" in gap and "test_anchor" in gap and "tests/" in gap for gap in gaps)


def test_user_manual_index_lists_api_catalog_references() -> None:
    assert api_manual_reference_index_gaps() == []


def test_user_manual_index_contract_flags_missing_api_reference_link(monkeypatch) -> None:
    table = surfaces.get_api_catalog_table()
    row = {
        **table["rows"][0],
        "id": "new-api-reference",
        "title": "New API Reference",
        "doc_page": "docs/user-manual/new-api-reference.md",
    }
    patched_table = {**table, "rows": [*table["rows"], row]}
    monkeypatch.setattr(surfaces, "get_api_catalog_table", lambda: patched_table)

    gaps = api_manual_reference_index_gaps()

    assert any("new-api-reference.md" in gap and "docs/user-manual/README.md" in gap for gap in gaps)


def test_user_manual_index_contract_flags_missing_chinese_api_reference_link(monkeypatch) -> None:
    table = surfaces.get_api_catalog_table()
    row = next(row for row in table["rows"] if row["id"] == "api-catalog")
    doc_page = row["doc_page"]
    relative_doc_page = doc_page.removeprefix("docs/user-manual/")
    original_load_txt = api_contracts.load_txt
    markdown = original_load_txt("docs/user-manual/README.md", encoding="utf-8")
    english, chinese = markdown.split("\n## 中文\n", 1)
    patched_chinese = "\n".join(line for line in chinese.splitlines() if f"({relative_doc_page})" not in line)

    def load_manual_with_missing_chinese_link(path: str, *args: object, **kwargs: object) -> str:
        if path == "docs/user-manual/README.md":
            return f"{english}\n## 中文\n{patched_chinese}"
        return original_load_txt(path, *args, **kwargs)

    monkeypatch.setattr(api_contracts, "load_txt", load_manual_with_missing_chinese_link)

    gaps = api_manual_reference_index_gaps()

    assert any(doc_page in gap and "Chinese" in gap for gap in gaps)


def test_user_manual_index_contract_flags_stale_api_reference_link(monkeypatch) -> None:
    original_load_txt = api_contracts.load_txt
    markdown = original_load_txt("docs/user-manual/README.md", encoding="utf-8")
    stale_row = "| [Stale API Reference](stale-api-reference.md) | Stale generated API reference link. |"
    patched_markdown = markdown.replace(
        "| [API Catalog Reference](api-catalog-reference.md) |", f"{stale_row}\n| [API Catalog Reference](api-catalog-reference.md) |", 1
    )

    def load_manual_with_stale_link(path: str, *args: object, **kwargs: object) -> str:
        if path == "docs/user-manual/README.md":
            return patched_markdown
        return original_load_txt(path, *args, **kwargs)

    monkeypatch.setattr(api_contracts, "load_txt", load_manual_with_stale_link)

    gaps = api_manual_reference_index_gaps()

    assert any("stale-api-reference.md" in gap and "API catalog" in gap for gap in gaps)


def test_api_catalog_rows_match_source_helper_metadata() -> None:
    assert api_catalog_payload_metadata_gaps() == []


def test_api_catalog_metadata_contract_flags_self_reference_index_drift(monkeypatch) -> None:
    table = surfaces.get_api_catalog_table()
    patched_rows = [dict(row) for row in table["rows"]]
    api_catalog_row = next(row for row in patched_rows if row["id"] == "api-catalog")
    api_catalog_row["index_names"] = [name for name in api_catalog_row["index_names"] if name != "surface_index"]
    patched_table = {key: value for key, value in table.items() if key != "surface_index"}
    patched_table["rows"] = patched_rows
    monkeypatch.setattr(surfaces, "get_api_catalog_table", lambda: patched_table)

    gaps = api_catalog_payload_metadata_gaps()

    assert any("api-catalog" in gap and "index_names" in gap and "surface_index" in gap for gap in gaps)


def test_api_catalog_metadata_contract_flags_missing_payload_surface(monkeypatch) -> None:
    table = sdk.get_architecture_api_table()
    patched_payload = {
        **table,
        "surface_index": {**table["surface_index"], "desktop": ["get_architecture_spec"]},
    }
    monkeypatch.setattr(sdk, "get_architecture_api_table", lambda: patched_payload)

    gaps = api_catalog_payload_metadata_gaps()

    assert any("architecture-api" in gap and "surfaces" in gap and "desktop" in gap for gap in gaps)


def test_api_catalog_lists_every_generated_api_table_helper() -> None:
    assert api_catalog_api_table_helper_gaps(api_table_functions()) == []


def test_api_catalog_api_table_helper_contract_flags_missing_table(monkeypatch) -> None:
    table = surfaces.get_api_catalog_table()
    patched_rows = []
    for row in table["rows"]:
        patched_row = dict(row)
        if patched_row["table_helper"] == "get_rest_api_table":
            patched_row["table_helper"] = "get_missing_rest_api_table"
        patched_rows.append(patched_row)
    monkeypatch.setattr(surfaces, "get_api_catalog_table", lambda: {**table, "rows": patched_rows})

    gaps = api_catalog_api_table_helper_gaps(api_table_functions())

    assert any("get_rest_api_table" in gap for gap in gaps)


def test_api_catalog_api_table_helper_contract_flags_wrong_owner_module(monkeypatch) -> None:
    function = next(function for function in api_table_functions() if function.function_name == "get_rest_api_table")
    table = surfaces.get_api_catalog_table()
    patched_rows = []
    for row in table["rows"]:
        patched_row = dict(row)
        if patched_row["table_helper"] == function.function_name:
            patched_row["owner_module"] = "paradev.surfaces.api_catalog"
        patched_rows.append(patched_row)
    monkeypatch.setattr(surfaces, "get_api_catalog_table", lambda: {**table, "rows": patched_rows})

    gaps = api_catalog_api_table_helper_gaps(api_table_functions())

    assert any(f"{function.module_name}.{function.function_name}" in gap for gap in gaps)


def test_api_catalog_rows_have_stable_shape() -> None:
    assert api_catalog_row_shape_gaps() == []


def test_api_catalog_rows_flag_unknown_surface(monkeypatch) -> None:
    table = surfaces.get_api_catalog_table()
    patched_rows = [dict(row) for row in table["rows"]]
    patched_rows[0]["surfaces"] = [*patched_rows[0]["surfaces"], "stale-surface"]
    monkeypatch.setattr(surfaces, "get_api_catalog_table", lambda: {**table, "rows": patched_rows})

    gaps = api_catalog_row_shape_gaps()

    assert any("stale-surface" in gap and "surface" in gap for gap in gaps)


def test_api_catalog_rows_flag_source_id_drift(monkeypatch) -> None:
    table = surfaces.get_api_catalog_table()
    patched_rows = [dict(row) for row in table["rows"]]
    patched_rows[1]["id"] = "stale-sdk-api"
    monkeypatch.setattr(surfaces, "get_api_catalog_table", lambda: {**table, "rows": patched_rows})

    gaps = api_catalog_row_shape_gaps()

    assert any("sdk-api" in gap and "missing source id" in gap for gap in gaps)
    assert any("stale-sdk-api" in gap and "unknown source id" in gap for gap in gaps)


def test_api_catalog_rows_flag_source_metadata_drift(monkeypatch) -> None:
    table = surfaces.get_api_catalog_table()
    patched_rows = [dict(row) for row in table["rows"]]
    sdk_row = next(row for row in patched_rows if row["id"] == "sdk-api")
    sdk_row["title"] = "Stale SDK Reference"
    sdk_row["surfaces"] = ["sdk", "docs"]
    monkeypatch.setattr(surfaces, "get_api_catalog_table", lambda: {**table, "rows": patched_rows})

    gaps = api_catalog_row_shape_gaps()

    assert any("sdk-api" in gap and "title" in gap and "Stale SDK Reference" in gap for gap in gaps)
    assert any("sdk-api" in gap and "surfaces" in gap and "cli" in gap for gap in gaps)


def test_api_catalog_rows_flag_source_order_drift(monkeypatch) -> None:
    table = surfaces.get_api_catalog_table()
    patched_rows = [dict(row) for row in table["rows"]]
    patched_rows[1], patched_rows[2] = patched_rows[2], patched_rows[1]
    monkeypatch.setattr(surfaces, "get_api_catalog_table", lambda: {**table, "rows": patched_rows})

    gaps = api_catalog_row_shape_gaps()

    assert any("source order" in gap and "sdk-api" in gap and "package-api" in gap for gap in gaps)


def test_api_catalog_summary_and_reference_groups_are_consistent() -> None:
    assert api_catalog_summary_group_gaps() == []


def test_api_catalog_reference_groups_flag_stale_kind_summary(monkeypatch) -> None:
    table = surfaces.get_api_catalog_table()
    patched_table = {
        **table,
        "reference_groups": [dict(row) for row in table["reference_groups"]],
    }
    patched_table["reference_groups"][0]["kinds"] = ["stale-kind"]
    monkeypatch.setattr(surfaces, "get_api_catalog_table", lambda: patched_table)

    gaps = api_catalog_summary_group_gaps()

    assert any("reference group" in gap and "kinds" in gap for gap in gaps)


def test_api_catalog_reference_groups_flag_missing_reader_fields(monkeypatch) -> None:
    table = surfaces.get_api_catalog_table()
    patched_table = {
        **table,
        "reference_groups": [dict(row) for row in table["reference_groups"]],
    }
    patched_table["reference_groups"][0]["title"] = ""
    patched_table["reference_groups"][0]["usage"] = ""
    monkeypatch.setattr(surfaces, "get_api_catalog_table", lambda: patched_table)

    gaps = api_catalog_summary_group_gaps()

    assert any("reference_groups row 0" in gap and "title" in gap for gap in gaps)
    assert any("reference_groups row 0" in gap and "usage" in gap for gap in gaps)


def test_api_catalog_reference_groups_flag_stale_group_index_key(monkeypatch) -> None:
    table = surfaces.get_api_catalog_table()
    patched_table = {
        **table,
        "group_index": {**table["group_index"], "stale-group": []},
    }
    monkeypatch.setattr(surfaces, "get_api_catalog_table", lambda: patched_table)

    gaps = api_catalog_summary_group_gaps()

    assert any("group_index" in gap and "stale-group" in gap and "reference_groups" in gap for gap in gaps)


def test_api_catalog_reference_groups_flag_non_string_group_index_key(monkeypatch) -> None:
    table = surfaces.get_api_catalog_table()
    patched_table = {
        **table,
        "group_index": {**table["group_index"], 42: []},
    }
    monkeypatch.setattr(surfaces, "get_api_catalog_table", lambda: patched_table)

    gaps = api_catalog_summary_group_gaps()

    assert any("group_index" in gap and "42" in gap and "string" in gap for gap in gaps)


def test_api_catalog_indexes_cover_row_fields() -> None:
    assert api_catalog_index_coverage_gaps() == []


def test_api_catalog_indexes_flag_unknown_reference_ids(monkeypatch) -> None:
    table = surfaces.get_api_catalog_table()
    doc_page, reference_ids = next(iter(table["doc_page_index"].items()))
    patched_table = {
        **table,
        "doc_page_index": {
            **table["doc_page_index"],
            doc_page: [*reference_ids, "stale-reference"],
        },
    }
    monkeypatch.setattr(surfaces, "get_api_catalog_table", lambda: patched_table)

    gaps = api_catalog_index_coverage_gaps()

    assert any("doc_page_index" in gap and "stale-reference" in gap and "unknown" in gap for gap in gaps)


def test_api_catalog_indexes_flag_wrong_index_key(monkeypatch) -> None:
    table = surfaces.get_api_catalog_table()
    patched_table = {
        **table,
        "layer_index": {
            **table["layer_index"],
            "surface": [*table["layer_index"]["surface"], "sdk-api"],
        },
    }
    monkeypatch.setattr(surfaces, "get_api_catalog_table", lambda: patched_table)

    gaps = api_catalog_index_coverage_gaps()

    assert any("layer_index" in gap and "surface" in gap and "sdk-api" in gap and "matching row field" in gap for gap in gaps)


def test_api_catalog_index_catalog_matches_lookup_helpers() -> None:
    assert api_catalog_index_catalog_gaps() == []


def test_api_catalog_index_catalog_flags_stale_helper_arguments(monkeypatch) -> None:
    table = surfaces.get_api_catalog_table()
    patched_table = {
        **table,
        "index_catalog": [dict(row) for row in table["index_catalog"]],
    }
    for row in patched_table["index_catalog"]:
        if row["id"] == "surface":
            row["python_helper"] = "get_api_catalog_reference_ids('layer', layer)"
            break

    monkeypatch.setattr(surfaces, "get_api_catalog_table", lambda: patched_table)

    gaps = api_catalog_index_catalog_gaps()

    assert any("surface" in gap and "python_helper" in gap for gap in gaps)


def test_api_catalog_cli_commands_match_cli_api_table() -> None:
    assert api_catalog_cli_command_gaps() == []


def test_api_catalog_cli_commands_flag_stale_cli_surface_marker(monkeypatch) -> None:
    table = surfaces.get_api_catalog_table()
    patched_rows = []
    for row in table["rows"]:
        patched_row = dict(row)
        if patched_row["id"] == "frontend-api":
            patched_row["surfaces"] = [surface for surface in patched_row["surfaces"] if surface != "cli"]
        patched_rows.append(patched_row)
    monkeypatch.setattr(surfaces, "get_api_catalog_table", lambda: {**table, "rows": patched_rows})

    gaps = api_catalog_cli_command_gaps()

    assert any("frontend-api" in gap and "cli" in gap for gap in gaps)


def test_api_catalog_cli_commands_flag_unmapped_generated_cli_api_command(monkeypatch) -> None:
    table = cli.get_cli_api_table()
    selector_row = next(row for row in table["rows"] if row["command_key"] == "package-api")
    markdown_row = next(row for row in table["rows"] if row["command_key"] == "package-api --markdown")
    patched_table = {
        **table,
        "row_count": table["row_count"] + 2,
        "rows": [
            *table["rows"],
            {
                **selector_row,
                "symbol": "paradev cli new-api",
                "command_key": "new-api",
                "adapter": "get_new_api_selection",
            },
            {
                **markdown_row,
                "symbol": "paradev cli new-api --markdown",
                "command_key": "new-api --markdown",
                "adapter": "render_new_api_reference_markdown",
            },
        ],
    }
    monkeypatch.setattr(cli, "get_cli_api_table", lambda: patched_table)

    gaps = api_catalog_cli_command_gaps()

    assert any("new-api" in gap and "API catalog" in gap for gap in gaps)


def test_api_catalog_selector_surfaces_match_rest_and_mcp_tables() -> None:
    assert api_catalog_selector_surface_gaps() == []


def test_api_catalog_selector_surfaces_flag_unmapped_rest_selector_route(monkeypatch) -> None:
    table = rest.get_rest_api_table()
    route = {
        **table["rows"][0],
        "symbol": "GET /new-api",
        "feature": "new-api",
        "path": "/new-api",
        "inputs": "query:symbol, query:index_name, query:key",
        "returns": "200 New API table, row, or index lookup payload.",
        "raises": "400 Invalid new API selector.",
        "registry_seam": "OpenAPI path /new-api",
        "frontend_operation_ids": [],
    }
    patched_table = {
        **table,
        "row_count": table["row_count"] + 1,
        "feature_index": {**table["feature_index"], "new-api": ["GET /new-api"]},
        "method_index": {**table["method_index"], "GET": [*table["method_index"]["GET"], "GET /new-api"]},
        "rows": [*table["rows"], route],
    }
    monkeypatch.setattr(rest, "get_rest_api_table", lambda: patched_table)

    gaps = api_catalog_selector_surface_gaps()

    assert any("new-api" in gap and "REST API table" in gap and "API catalog" in gap for gap in gaps)


def test_api_catalog_selector_surfaces_flag_stale_mcp_metadata(monkeypatch) -> None:
    table = surfaces.get_api_catalog_table()
    patched_rows = []
    for row in table["rows"]:
        patched_row = dict(row)
        if patched_row["id"] == "frontend-api":
            patched_row["surfaces"] = [surface for surface in patched_row["surfaces"] if surface != "mcp"]
        patched_rows.append(patched_row)
    monkeypatch.setattr(surfaces, "get_api_catalog_table", lambda: {**table, "rows": patched_rows})

    gaps = api_catalog_selector_surface_gaps()

    assert any("frontend-api" in gap and "mcp" in gap for gap in gaps)


def test_api_catalog_surfaces_match_static_surface_contracts() -> None:
    assert api_catalog_surface_contract_gaps() == []


def test_api_catalog_surfaces_flag_stale_surface_contract_reference(monkeypatch) -> None:
    table = surfaces.get_api_catalog_table()
    patched_rows = []
    for row in table["rows"]:
        patched_row = dict(row)
        if patched_row["id"] == "surface-contract-reference":
            patched_row["surfaces"] = [surface for surface in patched_row["surfaces"] if surface != "bundle"]
        patched_rows.append(patched_row)
    monkeypatch.setattr(surfaces, "get_api_catalog_table", lambda: {**table, "rows": patched_rows})

    gaps = api_catalog_surface_contract_gaps()

    assert any("surface-contract-reference" in gap and "bundle" in gap for gap in gaps)
