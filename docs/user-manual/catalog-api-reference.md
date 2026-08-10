# Catalog API Reference

Generated from `paradev.hb.get_catalog_api_table()`.

Regenerate this file whenever the Catalog API table changes:

```bash
rtk uv run paradev catalog-api --markdown > docs/user-manual/catalog-api-reference.md
```

## Summary / 汇总

- API rows / API 行数: 37
- Surfaces / Surface 数: 4
- Features / Feature 数: 9

## Feature Index / Feature 索引

| Feature | APIs | Symbols |
| --- | --- | --- |
| `preview` | 5 | `CATALOG_SCHEMA`, `catalog_preview`, `paradev hb catalog-preview`, `GET /projects/inspect?kind=catalog-preview`, `project_inspect kind=catalog-preview` |
| `smoke` | 3 | `SMOKE_SCHEMA`, `catalog_smoke`, `paradev hb catalog-smoke` |
| `write` | 4 | `WRITE_SCHEMA`, `catalog_write`, `paradev hb catalog-write`, `POST /projects/catalog` |
| `refresh` | 4 | `REFRESH_SCHEMA`, `catalog_refresh`, `paradev hb catalog-refresh`, `PUT /projects/catalog` |
| `query` | 5 | `QUERY_SCHEMA`, `catalog_query`, `paradev hb catalog-query`, `GET /projects/inspect?kind=catalog-query`, `project_inspect kind=catalog-query` |
| `status` | 3 | `STATUS_SCHEMA`, `catalog_status`, `GET /projects/catalog` |
| `api-table` | 11 | `CATALOG_API_TABLE_SCHEMA`, `CATALOG_API_TABLE_ROWS`, `CatalogApiRow`, `CatalogApiTable`, `get_catalog_api_selection`, `get_catalog_api_table`, `render_catalog_api_reference_markdown`, `paradev catalog-api`, `paradev catalog-api --markdown`, `GET /catalog-api`, `catalog_api` |
| `entities` | 1 | `ENTITY_TYPES` |
| `completion` | 1 | `catalog_completion_items` |

## Surface Index / Surface 索引

| Surface | APIs | Symbols |
| --- | --- | --- |
| `sdk` | 21 | `CATALOG_SCHEMA`, `SMOKE_SCHEMA`, `WRITE_SCHEMA`, `REFRESH_SCHEMA`, `QUERY_SCHEMA`, `STATUS_SCHEMA`, `CATALOG_API_TABLE_SCHEMA`, `CATALOG_API_TABLE_ROWS`, `CatalogApiRow`, `CatalogApiTable`, `get_catalog_api_selection`, `ENTITY_TYPES`, `catalog_preview`, `catalog_smoke`, `catalog_write`, `catalog_refresh`, `catalog_query`, `catalog_status`, `catalog_completion_items`, `get_catalog_api_table`, `render_catalog_api_reference_markdown` |
| `cli` | 7 | `paradev catalog-api`, `paradev catalog-api --markdown`, `paradev hb catalog-preview`, `paradev hb catalog-smoke`, `paradev hb catalog-write`, `paradev hb catalog-refresh`, `paradev hb catalog-query` |
| `rest` | 6 | `GET /projects/inspect?kind=catalog-preview`, `GET /projects/inspect?kind=catalog-query`, `GET /projects/catalog`, `POST /projects/catalog`, `PUT /projects/catalog`, `GET /catalog-api` |
| `mcp` | 3 | `project_inspect kind=catalog-preview`, `project_inspect kind=catalog-query`, `catalog_api` |

## API Standard Table / API 标准表

| Symbol | Kind | Layer | Feature | Surface | Inputs | Returns | Raises | Registry Seam | Payload Schema | Doc Page | Test Anchor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `CATALOG_SCHEMA` | `constant` | `sdk` | `preview` | `sdk` | `none` | `paradev.hb.catalog-preview.v1` |  | `none` | `paradev.hb.catalog-preview.v1` | `docs/user-manual/catalog-api-reference.md` | `tests/test_architecture.py::test_catalog_api_table_lists_catalog_surfaces` |
| `SMOKE_SCHEMA` | `constant` | `sdk` | `smoke` | `sdk` | `none` | `paradev.hb.catalog-smoke.v1` |  | `none` | `paradev.hb.catalog-smoke.v1` | `docs/user-manual/catalog-api-reference.md` | `tests/test_architecture.py::test_catalog_api_table_lists_catalog_surfaces` |
| `WRITE_SCHEMA` | `constant` | `sdk` | `write` | `sdk` | `none` | `paradev.hb.catalog-write.v1` |  | `none` | `paradev.hb.catalog-write.v1` | `docs/user-manual/catalog-api-reference.md` | `tests/test_architecture.py::test_catalog_api_table_lists_catalog_surfaces` |
| `REFRESH_SCHEMA` | `constant` | `sdk` | `refresh` | `sdk` | `none` | `paradev.hb.catalog-refresh.v1` |  | `none` | `paradev.hb.catalog-refresh.v1` | `docs/user-manual/catalog-api-reference.md` | `tests/test_architecture.py::test_catalog_api_table_lists_catalog_surfaces` |
| `QUERY_SCHEMA` | `constant` | `sdk` | `query` | `sdk` | `none` | `paradev.hb.catalog-query.v1` |  | `none` | `paradev.hb.catalog-query.v1` | `docs/user-manual/catalog-api-reference.md` | `tests/test_architecture.py::test_catalog_api_table_lists_catalog_surfaces` |
| `STATUS_SCHEMA` | `constant` | `sdk` | `status` | `sdk` | `none` | `paradev.hb.catalog-status.v1` |  | `none` | `paradev.hb.catalog-status.v1` | `docs/user-manual/catalog-api-reference.md` | `tests/test_hb.py::test_hb_catalog_status_missing_is_side_effect_free` |
| `CATALOG_API_TABLE_SCHEMA` | `constant` | `sdk` | `api-table` | `sdk` | `none` | `paradev.hb.catalog-api-table.v1` |  | `none` | `paradev.hb.catalog-api-table.v1` | `docs/user-manual/catalog-api-reference.md` | `tests/test_architecture.py::test_catalog_api_table_lists_catalog_surfaces` |
| `CATALOG_API_TABLE_ROWS` | `constant` | `sdk` | `api-table` | `sdk` | `none` | `tuple[CatalogApiRow, ...]` |  | `none` | `paradev.hb.catalog-api-table.v1` | `docs/user-manual/catalog-api-reference.md` | `tests/test_architecture.py::test_catalog_api_table_lists_catalog_surfaces` |
| `CatalogApiRow` | `TypedDict` | `sdk` | `api-table` | `sdk` | `symbol, kind, layer, feature, inputs, returns, raises, registry_seam, surface, payload_schema, doc_page, test_anchor` | `Catalog API table row schema` |  | `none` | `paradev.hb.catalog-api-table.v1` | `docs/user-manual/catalog-api-reference.md` | `tests/test_architecture.py::test_catalog_api_table_lists_catalog_surfaces` |
| `CatalogApiTable` | `TypedDict` | `sdk` | `api-table` | `sdk` | `schema, row_count, surface_index, feature_index, rows` | `Catalog API table schema` |  | `none` | `paradev.hb.catalog-api-table.v1` | `docs/user-manual/catalog-api-reference.md` | `tests/test_architecture.py::test_catalog_api_table_lists_catalog_surfaces` |
| `get_catalog_api_selection` | `function` | `sdk` | `api-table` | `sdk` | `symbol=None, index_name=None, key=None` | `CatalogApiTable \| CatalogApiRow \| list[str]` | `ValueError or KeyError on unsupported selectors` | `none` | `paradev.hb.catalog-api-table.v1` | `docs/user-manual/catalog-api-reference.md` | `tests/test_catalog_api_selection.py::test_catalog_api_selection_returns_table_row_and_index_projection` |
| `ENTITY_TYPES` | `constant` | `sdk` | `entities` | `sdk` | `none` | `tuple[str, ...]` |  | `HOI4 HeavenBase extension registry` | `paradev.hb.catalog-preview.v1` | `docs/user-manual/catalog-api-reference.md` | `tests/test_architecture.py::test_catalog_api_table_lists_catalog_surfaces` |
| `catalog_preview` | `function` | `sdk` | `preview` | `sdk` | `project, profile=None, registry=None, result=None` | `catalog preview payload` |  | `Project build registry` | `paradev.hb.catalog-preview.v1` | `docs/user-manual/catalog-api-reference.md` | `tests/test_hb.py::test_hb_catalog_preview_projects_build_rows_without_writing` |
| `catalog_smoke` | `function` | `sdk` | `smoke` | `sdk` | `project, profile=None, registry=None, preview=None` | `catalog smoke payload` |  | `HeavenBase in-memory workspace` | `paradev.hb.catalog-smoke.v1` | `docs/user-manual/catalog-api-reference.md` | `tests/test_hb.py::test_hb_catalog_smoke_registers_preview_rows_without_writing` |
| `catalog_write` | `function` | `sdk` | `write` | `sdk` | `project, profile=None, registry=None, preview=None, database=None` | `catalog write payload` | `FileExistsError on existing database path` | `HeavenBase SQLite backend` | `paradev.hb.catalog-write.v1` | `docs/user-manual/catalog-api-reference.md` | `tests/test_hb.py::test_hb_catalog_write_creates_sqlite_database_without_build_output` |
| `catalog_refresh` | `function` | `sdk` | `refresh` | `sdk` | `project, profile=None, registry=None, preview=None, database=None` | `catalog refresh payload` | `OSError on database replacement failure` | `HeavenBase SQLite backend` | `paradev.hb.catalog-refresh.v1` | `docs/user-manual/catalog-api-reference.md` | `tests/test_hb.py::test_hb_catalog_refresh_replaces_existing_database_files` |
| `catalog_query` | `function` | `sdk` | `query` | `sdk` | `project, database=None, entity=None, target_id=None, name=None, tag=None, limit=None, offset=0, include_data=True` | `catalog query payload` | `FileNotFoundError on missing database; RuntimeError on stale database; ValueError on invalid paging arguments` | `HeavenBase SQLite catalog` | `paradev.hb.catalog-query.v1` | `docs/user-manual/catalog-api-reference.md` | `tests/test_hb.py::test_hb_catalog_query_reads_written_sqlite_catalog` |
| `catalog_status` | `function` | `sdk` | `status` | `sdk` | `project, database=None` | `catalog status payload` |  | `HeavenBase SQLite catalog` | `paradev.hb.catalog-status.v1` | `docs/user-manual/catalog-api-reference.md` | `tests/test_hb.py::test_hb_catalog_status_missing_is_side_effect_free` |
| `catalog_completion_items` | `function` | `sdk` | `completion` | `sdk` | `project, database=None, prefix=None, limit=100` | `LSP CompletionItem rows` | `FileNotFoundError on missing database; RuntimeError on stale database; ValueError on non-positive limit` | `HeavenBase SQLite catalog` | `LSP CompletionItem[]` | `docs/user-manual/catalog-api-reference.md` | `tests/test_lsp.py::test_catalog_completion_reuses_cached_database_rows` |
| `get_catalog_api_table` | `function` | `sdk` | `api-table` | `sdk` | `none` | `CatalogApiTable` |  | `none` | `paradev.hb.catalog-api-table.v1` | `docs/user-manual/catalog-api-reference.md` | `tests/test_architecture.py::test_catalog_api_table_lists_catalog_surfaces` |
| `render_catalog_api_reference_markdown` | `function` | `sdk` | `api-table` | `sdk` | `none` | `Markdown catalog API reference` |  | `none` | `paradev.hb.catalog-api-table.v1` | `docs/user-manual/catalog-api-reference.md` | `tests/test_architecture.py::test_catalog_api_table_lists_catalog_surfaces` |
| `paradev catalog-api` | `command` | `cli` | `api-table` | `cli` | `--json` | `CatalogApiTable` | `typer.BadParameter when combined selectors are invalid` | `Typer command registry` | `paradev.hb.catalog-api-table.v1` | `docs/user-manual/catalog-api-reference.md` | `tests/test_cli.py::test_catalog_api_cli_outputs_table_json` |
| `paradev catalog-api --markdown` | `command projection` | `cli` | `api-table` | `cli` | `none` | `Markdown catalog API reference` | `typer.BadParameter when combined with --json` | `Typer command registry` | `paradev.hb.catalog-api-table.v1` | `docs/user-manual/catalog-api-reference.md` | `tests/test_cli.py::test_catalog_api_cli_outputs_reference_markdown` |
| `paradev hb catalog-preview` | `command` | `cli` | `preview` | `cli` | `path, --profile, --json` | `catalog preview payload` | `typer.BadParameter on project load failure` | `Typer command registry` | `paradev.hb.catalog-preview.v1` | `docs/user-manual/catalog-api-reference.md` | `tests/test_hb.py::test_hb_catalog_preview_cli_outputs_json` |
| `paradev hb catalog-smoke` | `command` | `cli` | `smoke` | `cli` | `path, --profile, --json` | `catalog smoke payload` | `typer.BadParameter on project load failure` | `Typer command registry` | `paradev.hb.catalog-smoke.v1` | `docs/user-manual/catalog-api-reference.md` | `tests/test_hb.py::test_hb_catalog_smoke_cli_outputs_json` |
| `paradev hb catalog-write` | `command` | `cli` | `write` | `cli` | `path, --profile, --database, --json` | `catalog write payload` | `typer.BadParameter on project load or existing database failure` | `Typer command registry` | `paradev.hb.catalog-write.v1` | `docs/user-manual/catalog-api-reference.md` | `tests/test_hb.py::test_hb_catalog_write_cli_outputs_json` |
| `paradev hb catalog-refresh` | `command` | `cli` | `refresh` | `cli` | `path, --profile, --database, --json` | `catalog refresh payload` | `typer.BadParameter on project load or replacement failure` | `Typer command registry` | `paradev.hb.catalog-refresh.v1` | `docs/user-manual/catalog-api-reference.md` | `tests/test_hb.py::test_hb_catalog_refresh_cli_outputs_json` |
| `paradev hb catalog-query` | `command` | `cli` | `query` | `cli` | `path, --database, --entity, --target-id, --name, --tag, --limit=100, --offset=0, --data=false, --json` | `catalog query payload` | `typer.BadParameter on project load, missing or stale database, or invalid paging` | `Typer command registry` | `paradev.hb.catalog-query.v1` | `docs/user-manual/catalog-api-reference.md` | `tests/test_hb.py::test_hb_catalog_query_cli_outputs_json` |
| `GET /projects/inspect?kind=catalog-preview` | `REST route` | `rest` | `preview` | `rest` | `path, kind=catalog-preview, profile=None` | `catalog preview payload` |  | `OpenAPI path /projects/inspect` | `paradev.hb.catalog-preview.v1` | `docs/architecture/interfaces.md` | `tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server` |
| `GET /projects/inspect?kind=catalog-query` | `REST route` | `rest` | `query` | `rest` | `path, kind=catalog-query, database=None, entity=None, target_id=None, name=None, tag=None, limit=100, offset=0, include_data=false` | `catalog query payload` | `HTTP 400 on missing or stale database or invalid bounded paging` | `OpenAPI path /projects/inspect` | `paradev.hb.catalog-query.v1` | `docs/architecture/interfaces.md` | `tests/test_architecture.py::test_catalog_api_table_lists_catalog_surfaces` |
| `GET /projects/catalog` | `REST route` | `rest` | `status` | `rest` | `path` | `catalog status payload` |  | `OpenAPI path /projects/catalog` | `paradev.hb.catalog-status.v1` | `docs/architecture/interfaces.md` | `tests/test_native_web_bridge.py::test_native_web_bridge_catalog_status_uses_the_read_only_project_resource` |
| `POST /projects/catalog` | `REST route` | `rest` | `write` | `rest` | `path, profile=None, database=None` | `catalog write payload` |  | `OpenAPI path /projects/catalog` | `paradev.hb.catalog-write.v1` | `docs/architecture/interfaces.md` | `tests/test_hb.py::test_hb_catalog_write_and_refresh_rest_routes_output_json` |
| `PUT /projects/catalog` | `REST route` | `rest` | `refresh` | `rest` | `path, profile=None, database=None` | `catalog refresh payload` |  | `OpenAPI path /projects/catalog` | `paradev.hb.catalog-refresh.v1` | `docs/architecture/interfaces.md` | `tests/test_hb.py::test_hb_catalog_write_and_refresh_rest_routes_output_json` |
| `GET /catalog-api` | `REST route` | `rest` | `api-table` | `rest` | `symbol=None, index_name=None, key=None` | `CatalogApiTable \| CatalogApiRow \| list[str]` | `ValueError or KeyError on unsupported selectors` | `OpenAPI path /catalog-api` | `paradev.hb.catalog-api-table.v1` | `docs/user-manual/catalog-api-reference.md` | `tests/test_catalog_api_surface_selectors.py::test_catalog_api_table_lists_rest_and_mcp_selector_surfaces` |
| `project_inspect kind=catalog-preview` | `MCP tool projection` | `mcp` | `preview` | `mcp` | `path, kind=catalog-preview, profile=None` | `catalog preview payload` |  | `MCP project_inspect dispatcher` | `paradev.hb.catalog-preview.v1` | `docs/architecture/interfaces.md` | `tests/test_architecture.py::test_catalog_api_table_lists_catalog_surfaces` |
| `project_inspect kind=catalog-query` | `MCP tool projection` | `mcp` | `query` | `mcp` | `path, kind=catalog-query, database=None, entity=None, target_id=None, name=None, tag=None, limit=100, offset=0, include_data=false` | `catalog query payload` | `FileNotFoundError or RuntimeError on missing or stale database; ValueError on invalid bounded paging` | `MCP project_inspect dispatcher` | `paradev.hb.catalog-query.v1` | `docs/architecture/interfaces.md` | `tests/test_architecture.py::test_catalog_api_table_lists_catalog_surfaces` |
| `catalog_api` | `MCP tool` | `mcp` | `api-table` | `mcp` | `symbol=None, index_name=None, key=None` | `CatalogApiTable \| CatalogApiRow \| list[str]` | `ValueError or KeyError on unsupported selectors` | `MCP tool registry` | `paradev.hb.catalog-api-table.v1` | `docs/user-manual/catalog-api-reference.md` | `tests/test_catalog_api_surface_selectors.py::test_catalog_api_table_lists_rest_and_mcp_selector_surfaces` |
