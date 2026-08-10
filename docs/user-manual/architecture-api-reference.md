# Architecture API Reference

Generated from `paradev.sdk.get_architecture_api_table()`.

Regenerate this file whenever the architecture graph API table changes:

```bash
rtk uv run paradev architecture --api-table-markdown > docs/user-manual/architecture-api-reference.md
```

## Summary / 汇总

- API rows / API 行数: 17
- Surfaces / Surface 数: 4

## Surface Index / Surface 索引

| Surface | APIs | Symbols |
| --- | --- | --- |
| `sdk` | 10 | `SurfaceSpec`, `SurfaceSpec.to_dict`, `ArchitectureSpec`, `ArchitectureSpec.surface`, `ArchitectureSpec.path_chains`, `ArchitectureSpec.to_dict`, `get_architecture_spec`, `get_architecture_api_selection`, `get_architecture_api_table`, `render_architecture_api_reference_markdown` |
| `cli` | 3 | `paradev architecture`, `paradev architecture --api-table`, `paradev architecture --api-table-markdown` |
| `rest` | 1 | `GET /architecture` |
| `mcp` | 3 | `list_surfaces`, `describe_architecture`, `architecture_api` |

## API Standard Table / API 标准表

| Symbol | Kind | Layer | Surface | Inputs | Returns | Raises | Registry Seam | Doc Page | Test Anchor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `SurfaceSpec` | `dataclass` | `sdk` | `sdk` | `identifier, title, runtime, path, role, status, depends_on` | `immutable surface descriptor` |  | `none` | `docs/architecture/interfaces.md` | `tests/test_architecture.py::test_architecture_api_table_lists_public_graph_surface` |
| `SurfaceSpec.to_dict` | `method` | `sdk` | `sdk` | `self` | `JSON-safe surface row` |  | `none` | `docs/architecture/interfaces.md` | `tests/test_architecture.py::test_architecture_api_table_lists_public_graph_surface` |
| `ArchitectureSpec` | `dataclass` | `sdk` | `sdk` | `product, primary_runtime, surfaces, paths` | `immutable architecture graph` |  | `none` | `docs/architecture/interfaces.md` | `tests/test_architecture.py::test_architecture_api_table_lists_public_graph_surface` |
| `ArchitectureSpec.surface` | `method` | `sdk` | `sdk` | `identifier: str` | `SurfaceSpec` | `KeyError on unknown surface id` | `none` | `docs/architecture/interfaces.md` | `tests/test_architecture.py::test_architecture_surfaces_cover_requested_paths` |
| `ArchitectureSpec.path_chains` | `method` | `sdk` | `sdk` | `self` | `list[list[str]]` |  | `none` | `docs/architecture/interfaces.md` | `tests/test_architecture.py::test_architecture_surfaces_cover_requested_paths` |
| `ArchitectureSpec.to_dict` | `method` | `sdk` | `sdk` | `self` | `JSON-safe architecture graph` |  | `none` | `docs/architecture/interfaces.md` | `tests/test_architecture.py::test_architecture_surfaces_cover_requested_paths` |
| `get_architecture_spec` | `function` | `sdk` | `sdk` | `none` | `ArchitectureSpec` |  | `none` | `docs/architecture/interfaces.md` | `tests/test_architecture.py::test_architecture_surfaces_cover_requested_paths` |
| `get_architecture_api_selection` | `function` | `sdk` | `sdk` | `symbol=None, index_name=None, key=None` | `ArchitectureApiTable \| ArchitectureApiRow \| list[str]` | `ValueError or KeyError on unsupported selectors` | `none` | `docs/user-manual/architecture-api-reference.md` | `tests/test_architecture_api_selection.py::test_architecture_api_selection_returns_table_row_and_index_projection` |
| `get_architecture_api_table` | `function` | `sdk` | `sdk` | `none` | `ArchitectureApiTable` |  | `none` | `docs/user-manual/architecture-api-reference.md` | `tests/test_architecture.py::test_architecture_api_table_lists_public_graph_surface` |
| `render_architecture_api_reference_markdown` | `function` | `sdk` | `sdk` | `none` | `Markdown architecture API reference` |  | `none` | `docs/user-manual/architecture-api-reference.md` | `tests/test_architecture.py::test_architecture_api_table_lists_public_graph_surface` |
| `paradev architecture` | `command` | `cli` | `cli` | `--json` | `ArchitectureSpec.to_dict()` | `typer.BadParameter on invalid selector combinations` | `none` | `docs/user-manual/architecture-api-reference.md` | `tests/test_cli.py::test_architecture_cli_outputs_api_table_json` |
| `paradev architecture --api-table` | `command projection` | `cli` | `cli` | `--json` | `ArchitectureApiTable` | `typer.BadParameter on invalid selector combinations` | `none` | `docs/user-manual/architecture-api-reference.md` | `tests/test_cli.py::test_architecture_cli_outputs_api_table_json` |
| `paradev architecture --api-table-markdown` | `command projection` | `cli` | `cli` | `none` | `Markdown architecture API reference` | `typer.BadParameter when combined with selectors or --json` | `none` | `docs/user-manual/architecture-api-reference.md` | `tests/test_cli.py::test_architecture_cli_outputs_api_table_markdown` |
| `GET /architecture` | `REST route` | `rest` | `rest` | `none` | `ArchitectureSpec.to_dict()` |  | `OpenAPI path /architecture` | `docs/architecture/interfaces.md` | `tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server` |
| `list_surfaces` | `MCP tool` | `mcp` | `mcp` | `none` | `ArchitectureSpec.to_dict()` |  | `MCP tool registry` | `docs/architecture/interfaces.md` | `tests/test_architecture.py::test_architecture_api_table_lists_public_graph_surface` |
| `describe_architecture` | `MCP tool` | `mcp` | `mcp` | `none` | `ArchitectureSpec.to_dict()` |  | `MCP tool registry` | `docs/architecture/interfaces.md` | `tests/test_architecture.py::test_architecture_api_table_lists_public_graph_surface` |
| `architecture_api` | `MCP tool` | `mcp` | `mcp` | `symbol=None, index_name=None, key=None` | `ArchitectureApiTable \| ArchitectureApiRow \| list[str]` | `ValueError or KeyError on unsupported selectors` | `MCP tool registry` | `docs/user-manual/architecture-api-reference.md` | `tests/test_mcp_architecture_api_selectors.py::test_mcp_contract_exposes_architecture_api_selector_tool` |
