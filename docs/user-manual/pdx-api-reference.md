# PDX API Reference

Generated from `paradev.sdk.get_pdx_api_table()`.

Regenerate this file whenever the PDX API table changes:

```bash
rtk uv run paradev pdx-api --markdown > docs/user-manual/pdx-api-reference.md
```

## Summary / 汇总

- API rows / API 行数: 22
- Surfaces / Surface 数: 4
- Features / Feature 数: 3

## Feature Index / Feature 索引

| Feature | APIs | Symbols |
| --- | --- | --- |
| `parse` | 5 | `PDX_PARSE_SCHEMA`, `parse_pdx_file`, `paradev parse`, `GET /pdx/parse`, `pdx_parse` |
| `format` | 6 | `PDX_FORMAT_SCHEMA`, `format_pdx_text`, `format_pdx_file`, `paradev format`, `POST /pdx/format`, `pdx_format` |
| `api-table` | 11 | `PDX_API_TABLE_SCHEMA`, `PDX_API_TABLE_ROWS`, `PdxApiRow`, `PdxApiTable`, `get_pdx_api_selection`, `get_pdx_api_table`, `render_pdx_api_reference_markdown`, `paradev pdx-api`, `paradev pdx-api --markdown`, `GET /pdx-api`, `pdx_api` |

## Surface Index / Surface 索引

| Surface | APIs | Symbols |
| --- | --- | --- |
| `sdk` | 12 | `PDX_PARSE_SCHEMA`, `PDX_FORMAT_SCHEMA`, `PDX_API_TABLE_SCHEMA`, `PDX_API_TABLE_ROWS`, `PdxApiRow`, `PdxApiTable`, `get_pdx_api_selection`, `parse_pdx_file`, `format_pdx_text`, `format_pdx_file`, `get_pdx_api_table`, `render_pdx_api_reference_markdown` |
| `cli` | 4 | `paradev pdx-api`, `paradev pdx-api --markdown`, `paradev parse`, `paradev format` |
| `rest` | 3 | `GET /pdx/parse`, `POST /pdx/format`, `GET /pdx-api` |
| `mcp` | 3 | `pdx_parse`, `pdx_format`, `pdx_api` |

## API Standard Table / API 标准表

| Symbol | Kind | Layer | Feature | Surface | Inputs | Returns | Raises | Registry Seam | Payload Schema | Doc Page | Test Anchor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `PDX_PARSE_SCHEMA` | `constant` | `sdk` | `parse` | `sdk` | `none` | `paradev.pdx.parse.v1` |  | `none` | `paradev.pdx.parse.v1` | `docs/user-manual/pdx-api-reference.md` | `tests/test_architecture.py::test_pdx_api_table_lists_parse_format_surfaces` |
| `PDX_FORMAT_SCHEMA` | `constant` | `sdk` | `format` | `sdk` | `none` | `paradev.pdx.format.v1` |  | `none` | `paradev.pdx.format.v1` | `docs/user-manual/pdx-api-reference.md` | `tests/test_architecture.py::test_pdx_api_table_lists_parse_format_surfaces` |
| `PDX_API_TABLE_SCHEMA` | `constant` | `sdk` | `api-table` | `sdk` | `none` | `paradev.sdk.pdx-api-table.v1` |  | `none` | `paradev.sdk.pdx-api-table.v1` | `docs/user-manual/pdx-api-reference.md` | `tests/test_architecture.py::test_pdx_api_table_lists_parse_format_surfaces` |
| `PDX_API_TABLE_ROWS` | `constant` | `sdk` | `api-table` | `sdk` | `none` | `tuple[PdxApiRow, ...]` |  | `none` | `paradev.sdk.pdx-api-table.v1` | `docs/user-manual/pdx-api-reference.md` | `tests/test_architecture.py::test_pdx_api_table_lists_parse_format_surfaces` |
| `PdxApiRow` | `TypedDict` | `sdk` | `api-table` | `sdk` | `symbol, kind, layer, feature, inputs, returns, raises, registry_seam, surface, payload_schema, doc_page, test_anchor` | `PDX API table row schema` |  | `none` | `paradev.sdk.pdx-api-table.v1` | `docs/user-manual/pdx-api-reference.md` | `tests/test_architecture.py::test_pdx_api_table_lists_parse_format_surfaces` |
| `PdxApiTable` | `TypedDict` | `sdk` | `api-table` | `sdk` | `schema, row_count, surface_index, feature_index, rows` | `PDX API table schema` |  | `none` | `paradev.sdk.pdx-api-table.v1` | `docs/user-manual/pdx-api-reference.md` | `tests/test_architecture.py::test_pdx_api_table_lists_parse_format_surfaces` |
| `get_pdx_api_selection` | `function` | `sdk` | `api-table` | `sdk` | `symbol=None, index_name=None, key=None` | `PdxApiTable \| PdxApiRow \| list[str]` | `ValueError or KeyError on unsupported selectors` | `none` | `paradev.sdk.pdx-api-table.v1` | `docs/user-manual/pdx-api-reference.md` | `tests/test_pdx_api_selection.py::test_pdx_api_selection_returns_table_row_and_index_projection` |
| `parse_pdx_file` | `function` | `sdk` | `parse` | `sdk` | `path, include_dump=False, include_tokens=False` | `PDX parse payload` |  | `none` | `paradev.pdx.parse.v1` | `docs/user-manual/pdx-api-reference.md` | `tests/test_cli.py::test_parse_outputs_pdx_projection_json` |
| `format_pdx_text` | `function` | `sdk` | `format` | `sdk` | `text, path=None, indent="\t", comments=True` | `PDX format payload` | `ValueError on non-string text or indent` | `none` | `paradev.pdx.format.v1` | `docs/user-manual/pdx-api-reference.md` | `tests/test_architecture.py::test_pdx_api_table_lists_parse_format_surfaces` |
| `format_pdx_file` | `function` | `sdk` | `format` | `sdk` | `path, indent="\t", comments=True, write=False` | `PDX format payload` | `ValueError on non-string indent` | `none` | `paradev.pdx.format.v1` | `docs/user-manual/pdx-api-reference.md` | `tests/test_cli.py::test_format_cli_previews_and_writes_pdx_file` |
| `get_pdx_api_table` | `function` | `sdk` | `api-table` | `sdk` | `none` | `PdxApiTable` |  | `none` | `paradev.sdk.pdx-api-table.v1` | `docs/user-manual/pdx-api-reference.md` | `tests/test_architecture.py::test_pdx_api_table_lists_parse_format_surfaces` |
| `render_pdx_api_reference_markdown` | `function` | `sdk` | `api-table` | `sdk` | `none` | `Markdown PDX API reference` |  | `none` | `paradev.sdk.pdx-api-table.v1` | `docs/user-manual/pdx-api-reference.md` | `tests/test_architecture.py::test_pdx_api_table_lists_parse_format_surfaces` |
| `paradev pdx-api` | `command` | `cli` | `api-table` | `cli` | `--json` | `PdxApiTable` | `typer.BadParameter when combined selectors are invalid` | `Typer command registry` | `paradev.sdk.pdx-api-table.v1` | `docs/user-manual/pdx-api-reference.md` | `tests/test_cli.py::test_pdx_api_cli_outputs_table_json` |
| `paradev pdx-api --markdown` | `command projection` | `cli` | `api-table` | `cli` | `none` | `Markdown PDX API reference` | `typer.BadParameter when combined with --json` | `Typer command registry` | `paradev.sdk.pdx-api-table.v1` | `docs/user-manual/pdx-api-reference.md` | `tests/test_cli.py::test_pdx_api_cli_outputs_reference_markdown` |
| `paradev parse` | `command` | `cli` | `parse` | `cli` | `path, --dump, --tokens, --json` | `PDX parse payload` | `exit 1 when diagnostics are returned` | `Typer command registry` | `paradev.pdx.parse.v1` | `docs/user-manual/pdx-api-reference.md` | `tests/test_cli.py::test_parse_outputs_pdx_projection_json` |
| `paradev format` | `command` | `cli` | `format` | `cli` | `path, --indent, --comments/--no-comments, --write, --json` | `formatted text or PDX format payload` | `exit 1 when diagnostics are returned` | `Typer command registry` | `paradev.pdx.format.v1` | `docs/user-manual/pdx-api-reference.md` | `tests/test_cli.py::test_format_cli_previews_and_writes_pdx_file` |
| `GET /pdx/parse` | `REST route` | `rest` | `parse` | `rest` | `path, include_dump=False, include_tokens=False` | `PDX parse payload` |  | `OpenAPI path /pdx/parse` | `paradev.pdx.parse.v1` | `docs/architecture/interfaces.md` | `tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server` |
| `POST /pdx/format` | `REST route` | `rest` | `format` | `rest` | `path, indent="\t", comments=True, write=False` | `PDX format payload` |  | `OpenAPI path /pdx/format` | `paradev.pdx.format.v1` | `docs/architecture/interfaces.md` | `tests/test_architecture.py::test_pdx_api_table_lists_parse_format_surfaces` |
| `GET /pdx-api` | `REST route` | `rest` | `api-table` | `rest` | `symbol=None, index_name=None, key=None` | `PdxApiTable \| PdxApiRow \| list[str]` | `ValueError or KeyError on unsupported selectors` | `OpenAPI path /pdx-api` | `paradev.sdk.pdx-api-table.v1` | `docs/user-manual/pdx-api-reference.md` | `tests/test_pdx_api_surface_selectors.py::test_pdx_api_table_lists_rest_and_mcp_selector_surfaces` |
| `pdx_parse` | `MCP tool` | `mcp` | `parse` | `mcp` | `path, include_dump=False, include_tokens=False` | `PDX parse payload` |  | `MCP tool registry` | `paradev.pdx.parse.v1` | `docs/architecture/interfaces.md` | `tests/test_architecture.py::test_pdx_api_table_lists_parse_format_surfaces` |
| `pdx_format` | `MCP tool` | `mcp` | `format` | `mcp` | `path, indent="\t", comments=True, write=False` | `PDX format payload` |  | `MCP tool registry` | `paradev.pdx.format.v1` | `docs/architecture/interfaces.md` | `tests/test_architecture.py::test_pdx_api_table_lists_parse_format_surfaces` |
| `pdx_api` | `MCP tool` | `mcp` | `api-table` | `mcp` | `symbol=None, index_name=None, key=None` | `PdxApiTable \| PdxApiRow \| list[str]` | `ValueError or KeyError on unsupported selectors` | `MCP tool registry` | `paradev.sdk.pdx-api-table.v1` | `docs/user-manual/pdx-api-reference.md` | `tests/test_pdx_api_surface_selectors.py::test_pdx_api_table_lists_rest_and_mcp_selector_surfaces` |
