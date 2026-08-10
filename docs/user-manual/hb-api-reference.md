# HeavenBase Facade API Reference

Generated from `paradev.hb.get_hb_api_table()`.

Regenerate this file whenever the public `paradev.hb` facade changes:

```bash
rtk uv run paradev hb-api --markdown > docs/user-manual/hb-api-reference.md
```

## Summary / 汇总

- API rows / API 行数: 27
- HeavenBase modules / HeavenBase 模块数: 2
- Features / Feature 数: 11
- Row kinds / 行类型数: 4

## Module Index / 模块索引

| Module | Symbols | Public Exports |
| --- | --- | --- |
| `catalog` | 21 | `CATALOG_API_TABLE_ROWS`, `CATALOG_API_TABLE_SCHEMA`, `CATALOG_SCHEMA`, `CatalogApiRow`, `CatalogApiTable`, `ENTITY_TYPES`, `QUERY_SCHEMA`, `REFRESH_SCHEMA`, `SMOKE_SCHEMA`, `STATUS_SCHEMA`, `WRITE_SCHEMA`, `catalog_completion_items`, `catalog_preview`, `catalog_query`, `catalog_refresh`, `catalog_smoke`, `catalog_status`, `catalog_write`, `get_catalog_api_selection`, `get_catalog_api_table`, `render_catalog_api_reference_markdown` |
| `api` | 6 | `HB_API_TABLE_SCHEMA`, `HbApiRow`, `HbApiTable`, `get_hb_api_selection`, `get_hb_api_table`, `render_hb_api_reference_markdown` |

## Feature Index / Feature 索引

| Feature | Symbols | Public Exports |
| --- | --- | --- |
| `catalog-api` | 6 | `CATALOG_API_TABLE_ROWS`, `CATALOG_API_TABLE_SCHEMA`, `CatalogApiRow`, `CatalogApiTable`, `get_catalog_api_table`, `render_catalog_api_reference_markdown` |
| `preview` | 2 | `CATALOG_SCHEMA`, `catalog_preview` |
| `entities` | 1 | `ENTITY_TYPES` |
| `hb-api` | 6 | `HB_API_TABLE_SCHEMA`, `HbApiRow`, `HbApiTable`, `get_hb_api_selection`, `get_hb_api_table`, `render_hb_api_reference_markdown` |
| `query` | 2 | `QUERY_SCHEMA`, `catalog_query` |
| `refresh` | 2 | `REFRESH_SCHEMA`, `catalog_refresh` |
| `smoke` | 2 | `SMOKE_SCHEMA`, `catalog_smoke` |
| `status` | 2 | `STATUS_SCHEMA`, `catalog_status` |
| `write` | 2 | `WRITE_SCHEMA`, `catalog_write` |
| `completion` | 1 | `catalog_completion_items` |
| `catalog` | 1 | `get_catalog_api_selection` |

## Kind Index / 行类型索引

| Kind | Symbols | Public Exports |
| --- | --- | --- |
| `tuple constant` | 2 | `CATALOG_API_TABLE_ROWS`, `ENTITY_TYPES` |
| `schema constant` | 8 | `CATALOG_API_TABLE_SCHEMA`, `CATALOG_SCHEMA`, `HB_API_TABLE_SCHEMA`, `QUERY_SCHEMA`, `REFRESH_SCHEMA`, `SMOKE_SCHEMA`, `STATUS_SCHEMA`, `WRITE_SCHEMA` |
| `TypedDict` | 4 | `CatalogApiRow`, `CatalogApiTable`, `HbApiRow`, `HbApiTable` |
| `function` | 13 | `catalog_completion_items`, `catalog_preview`, `catalog_query`, `catalog_refresh`, `catalog_smoke`, `catalog_status`, `catalog_write`, `get_catalog_api_selection`, `get_catalog_api_table`, `get_hb_api_selection`, `get_hb_api_table`, `render_hb_api_reference_markdown`, `render_catalog_api_reference_markdown` |

## API Standard Table / API 标准表

| Symbol | Kind | Layer | Module | Feature | Import Path | Returns | Value | Registry Seam | Surface | Doc Page | Test Anchor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `CATALOG_API_TABLE_ROWS` | `tuple constant` | `hb` | `catalog` | `catalog-api` | `paradev.hb.CATALOG_API_TABLE_ROWS` | `tuple[37]` | `37 rows` | `catalog API reference table` | `sdk` | `docs/user-manual/catalog-api-reference.md` | `tests/test_architecture.py::test_hb_api_table_lists_public_hb_facade` |
| `CATALOG_API_TABLE_SCHEMA` | `schema constant` | `hb` | `catalog` | `catalog-api` | `paradev.hb.CATALOG_API_TABLE_SCHEMA` | `paradev.hb.catalog-api-table.v1` | `paradev.hb.catalog-api-table.v1` | `catalog API reference table` | `sdk` | `docs/user-manual/catalog-api-reference.md` | `tests/test_architecture.py::test_hb_api_table_lists_public_hb_facade` |
| `CATALOG_SCHEMA` | `schema constant` | `hb` | `catalog` | `preview` | `paradev.hb.CATALOG_SCHEMA` | `paradev.hb.catalog-preview.v1` | `paradev.hb.catalog-preview.v1` | `HeavenBase catalog integration` | `sdk` | `docs/user-manual/catalog-api-reference.md` | `tests/test_architecture.py::test_hb_api_table_lists_public_hb_facade` |
| `CatalogApiRow` | `TypedDict` | `hb` | `catalog` | `catalog-api` | `paradev.hb.CatalogApiRow` | `TypedDict schema` |  | `catalog API reference table` | `sdk` | `docs/user-manual/catalog-api-reference.md` | `tests/test_architecture.py::test_hb_api_table_lists_public_hb_facade` |
| `CatalogApiTable` | `TypedDict` | `hb` | `catalog` | `catalog-api` | `paradev.hb.CatalogApiTable` | `TypedDict schema` |  | `catalog API reference table` | `sdk` | `docs/user-manual/catalog-api-reference.md` | `tests/test_architecture.py::test_hb_api_table_lists_public_hb_facade` |
| `ENTITY_TYPES` | `tuple constant` | `hb` | `catalog` | `entities` | `paradev.hb.ENTITY_TYPES` | `tuple[16]` | `16 entity types` | `HOI4 HeavenBase extension registry` | `sdk` | `docs/user-manual/catalog-api-reference.md` | `tests/test_architecture.py::test_hb_api_table_lists_public_hb_facade` |
| `HB_API_TABLE_SCHEMA` | `schema constant` | `hb` | `api` | `hb-api` | `paradev.hb.HB_API_TABLE_SCHEMA` | `paradev.hb.api-table.v1` | `paradev.hb.api-table.v1` | `HeavenBase facade API table` | `sdk` | `docs/user-manual/hb-api-reference.md` | `tests/test_architecture.py::test_hb_api_table_lists_public_hb_facade` |
| `HbApiRow` | `TypedDict` | `hb` | `api` | `hb-api` | `paradev.hb.HbApiRow` | `TypedDict schema` |  | `HeavenBase facade API table` | `sdk` | `docs/user-manual/hb-api-reference.md` | `tests/test_architecture.py::test_hb_api_table_lists_public_hb_facade` |
| `HbApiTable` | `TypedDict` | `hb` | `api` | `hb-api` | `paradev.hb.HbApiTable` | `TypedDict schema` |  | `HeavenBase facade API table` | `sdk` | `docs/user-manual/hb-api-reference.md` | `tests/test_architecture.py::test_hb_api_table_lists_public_hb_facade` |
| `QUERY_SCHEMA` | `schema constant` | `hb` | `catalog` | `query` | `paradev.hb.QUERY_SCHEMA` | `paradev.hb.catalog-query.v1` | `paradev.hb.catalog-query.v1` | `HeavenBase catalog integration` | `sdk` | `docs/user-manual/catalog-api-reference.md` | `tests/test_architecture.py::test_hb_api_table_lists_public_hb_facade` |
| `REFRESH_SCHEMA` | `schema constant` | `hb` | `catalog` | `refresh` | `paradev.hb.REFRESH_SCHEMA` | `paradev.hb.catalog-refresh.v1` | `paradev.hb.catalog-refresh.v1` | `HeavenBase SQLite backend` | `sdk` | `docs/user-manual/catalog-api-reference.md` | `tests/test_architecture.py::test_hb_api_table_lists_public_hb_facade` |
| `SMOKE_SCHEMA` | `schema constant` | `hb` | `catalog` | `smoke` | `paradev.hb.SMOKE_SCHEMA` | `paradev.hb.catalog-smoke.v1` | `paradev.hb.catalog-smoke.v1` | `HeavenBase catalog integration` | `sdk` | `docs/user-manual/catalog-api-reference.md` | `tests/test_architecture.py::test_hb_api_table_lists_public_hb_facade` |
| `STATUS_SCHEMA` | `schema constant` | `hb` | `catalog` | `status` | `paradev.hb.STATUS_SCHEMA` | `paradev.hb.catalog-status.v1` | `paradev.hb.catalog-status.v1` | `HeavenBase catalog integration` | `sdk` | `docs/user-manual/catalog-api-reference.md` | `tests/test_architecture.py::test_hb_api_table_lists_public_hb_facade` |
| `WRITE_SCHEMA` | `schema constant` | `hb` | `catalog` | `write` | `paradev.hb.WRITE_SCHEMA` | `paradev.hb.catalog-write.v1` | `paradev.hb.catalog-write.v1` | `HeavenBase SQLite backend` | `sdk` | `docs/user-manual/catalog-api-reference.md` | `tests/test_architecture.py::test_hb_api_table_lists_public_hb_facade` |
| `catalog_completion_items` | `function` | `hb` | `catalog` | `completion` | `paradev.hb.catalog_completion_items` | `list[dict[str, object]]` |  | `LSP catalog completion` | `sdk` | `docs/user-manual/catalog-api-reference.md` | `tests/test_architecture.py::test_hb_api_table_lists_public_hb_facade` |
| `catalog_preview` | `function` | `hb` | `catalog` | `preview` | `paradev.hb.catalog_preview` | `dict[str, object]` |  | `HeavenBase catalog integration` | `sdk` | `docs/user-manual/catalog-api-reference.md` | `tests/test_architecture.py::test_hb_api_table_lists_public_hb_facade` |
| `catalog_query` | `function` | `hb` | `catalog` | `query` | `paradev.hb.catalog_query` | `dict[str, object]` |  | `HeavenBase catalog integration` | `sdk` | `docs/user-manual/catalog-api-reference.md` | `tests/test_architecture.py::test_hb_api_table_lists_public_hb_facade` |
| `catalog_refresh` | `function` | `hb` | `catalog` | `refresh` | `paradev.hb.catalog_refresh` | `dict[str, object]` |  | `HeavenBase SQLite backend` | `sdk` | `docs/user-manual/catalog-api-reference.md` | `tests/test_architecture.py::test_hb_api_table_lists_public_hb_facade` |
| `catalog_smoke` | `function` | `hb` | `catalog` | `smoke` | `paradev.hb.catalog_smoke` | `dict[str, object]` |  | `HeavenBase catalog integration` | `sdk` | `docs/user-manual/catalog-api-reference.md` | `tests/test_architecture.py::test_hb_api_table_lists_public_hb_facade` |
| `catalog_status` | `function` | `hb` | `catalog` | `status` | `paradev.hb.catalog_status` | `dict[str, object]` |  | `HeavenBase catalog integration` | `sdk` | `docs/user-manual/catalog-api-reference.md` | `tests/test_architecture.py::test_hb_api_table_lists_public_hb_facade` |
| `catalog_write` | `function` | `hb` | `catalog` | `write` | `paradev.hb.catalog_write` | `dict[str, object]` |  | `HeavenBase SQLite backend` | `sdk` | `docs/user-manual/catalog-api-reference.md` | `tests/test_architecture.py::test_hb_api_table_lists_public_hb_facade` |
| `get_catalog_api_selection` | `function` | `hb` | `catalog` | `catalog` | `paradev.hb.get_catalog_api_selection` | `CatalogApiTable \| CatalogApiRow \| list[str]` |  | `none` | `sdk` | `docs/user-manual/catalog-api-reference.md` | `tests/test_architecture.py::test_hb_api_table_lists_public_hb_facade` |
| `get_catalog_api_table` | `function` | `hb` | `catalog` | `catalog-api` | `paradev.hb.get_catalog_api_table` | `CatalogApiTable` |  | `catalog API reference table` | `sdk` | `docs/user-manual/catalog-api-reference.md` | `tests/test_architecture.py::test_hb_api_table_lists_public_hb_facade` |
| `get_hb_api_selection` | `function` | `hb` | `api` | `hb-api` | `paradev.hb.get_hb_api_selection` | `HbApiTable \| HbApiRow \| list[str]` |  | `HeavenBase facade API table` | `sdk` | `docs/user-manual/hb-api-reference.md` | `tests/test_architecture.py::test_hb_api_table_lists_public_hb_facade` |
| `get_hb_api_table` | `function` | `hb` | `api` | `hb-api` | `paradev.hb.get_hb_api_table` | `HbApiTable` |  | `HeavenBase facade API table` | `sdk` | `docs/user-manual/hb-api-reference.md` | `tests/test_architecture.py::test_hb_api_table_lists_public_hb_facade` |
| `render_hb_api_reference_markdown` | `function` | `hb` | `api` | `hb-api` | `paradev.hb.render_hb_api_reference_markdown` | `str` |  | `HeavenBase facade API table` | `sdk` | `docs/user-manual/hb-api-reference.md` | `tests/test_architecture.py::test_hb_api_table_lists_public_hb_facade` |
| `render_catalog_api_reference_markdown` | `function` | `hb` | `catalog` | `catalog-api` | `paradev.hb.render_catalog_api_reference_markdown` | `str` |  | `catalog API reference table` | `sdk` | `docs/user-manual/catalog-api-reference.md` | `tests/test_architecture.py::test_hb_api_table_lists_public_hb_facade` |
