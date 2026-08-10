# REST Facade API Reference

Generated from `paradev.api.get_rest_facade_api_table()`.

Regenerate this file whenever the public `paradev.api` facade changes:

```bash
rtk uv run paradev rest-facade-api --markdown > docs/user-manual/rest-facade-api-reference.md
```

## Summary / 汇总

- API rows / API 行数: 13
- REST modules / REST 模块数: 2
- Features / Feature 数: 7
- Row kinds / 行类型数: 3

## Module Index / 模块索引

| Module | Symbols | Public Exports |
| --- | --- | --- |
| `rest` | 7 | `apply_project_draft`, `build_app`, `create_module_batch`, `create_module_draft`, `get_openapi_seed`, `read_project_source`, `read_project_source_form` |
| `api` | 6 | `REST_FACADE_API_TABLE_SCHEMA`, `RestFacadeApiRow`, `RestFacadeApiTable`, `get_rest_facade_api_selection`, `get_rest_facade_api_table`, `render_rest_facade_api_reference_markdown` |

## Feature Index / Feature 索引

| Feature | Symbols | Public Exports |
| --- | --- | --- |
| `project-drafts` | 1 | `apply_project_draft` |
| `server` | 1 | `build_app` |
| `module-batches` | 1 | `create_module_batch` |
| `module-drafts` | 1 | `create_module_draft` |
| `openapi` | 1 | `get_openapi_seed` |
| `project-sources` | 2 | `read_project_source`, `read_project_source_form` |
| `rest-facade-api` | 6 | `REST_FACADE_API_TABLE_SCHEMA`, `RestFacadeApiRow`, `RestFacadeApiTable`, `get_rest_facade_api_selection`, `get_rest_facade_api_table`, `render_rest_facade_api_reference_markdown` |

## Kind Index / 行类型索引

| Kind | Symbols | Public Exports |
| --- | --- | --- |
| `function` | 10 | `apply_project_draft`, `build_app`, `create_module_batch`, `create_module_draft`, `get_openapi_seed`, `read_project_source`, `read_project_source_form`, `get_rest_facade_api_selection`, `get_rest_facade_api_table`, `render_rest_facade_api_reference_markdown` |
| `schema constant` | 1 | `REST_FACADE_API_TABLE_SCHEMA` |
| `TypedDict` | 2 | `RestFacadeApiRow`, `RestFacadeApiTable` |

## API Standard Table / API 标准表

| Symbol | Kind | Layer | Module | Feature | Import Path | Returns | Value | Registry Seam | Surface | Doc Page | Test Anchor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `apply_project_draft` | `function` | `rest` | `rest` | `project-drafts` | `paradev.api.apply_project_draft` | `dict[str, object]` |  | `REST project draft bridge` | `rest` | `docs/user-manual/rest-facade-api-reference.md` | `tests/test_architecture.py::test_rest_facade_api_table_lists_public_api_facade` |
| `build_app` | `function` | `rest` | `rest` | `server` | `paradev.api.build_app` | `FastAPI app` |  | `FastAPI app factory` | `rest` | `docs/user-manual/rest-facade-api-reference.md` | `tests/test_architecture.py::test_rest_facade_api_table_lists_public_api_facade` |
| `create_module_batch` | `function` | `rest` | `rest` | `module-batches` | `paradev.api.create_module_batch` | `dict[str, object]` |  | `REST module batch bridge` | `rest` | `docs/user-manual/rest-facade-api-reference.md` | `tests/test_architecture.py::test_rest_facade_api_table_lists_public_api_facade` |
| `create_module_draft` | `function` | `rest` | `rest` | `module-drafts` | `paradev.api.create_module_draft` | `dict[str, object]` |  | `REST module draft bridge` | `rest` | `docs/user-manual/rest-facade-api-reference.md` | `tests/test_architecture.py::test_rest_facade_api_table_lists_public_api_facade` |
| `get_openapi_seed` | `function` | `rest` | `rest` | `openapi` | `paradev.api.get_openapi_seed` | `dict[str, object]` |  | `OpenAPI seed contract` | `rest` | `docs/user-manual/rest-facade-api-reference.md` | `tests/test_architecture.py::test_rest_facade_api_table_lists_public_api_facade` |
| `read_project_source` | `function` | `rest` | `rest` | `project-sources` | `paradev.api.read_project_source` | `dict[str, object]` |  | `REST project source bridge` | `rest` | `docs/user-manual/rest-facade-api-reference.md` | `tests/test_architecture.py::test_rest_facade_api_table_lists_public_api_facade` |
| `read_project_source_form` | `function` | `rest` | `rest` | `project-sources` | `paradev.api.read_project_source_form` | `dict[str, object] \| None` |  | `REST project source bridge` | `rest` | `docs/user-manual/rest-facade-api-reference.md` | `tests/test_architecture.py::test_rest_facade_api_table_lists_public_api_facade` |
| `REST_FACADE_API_TABLE_SCHEMA` | `schema constant` | `rest` | `api` | `rest-facade-api` | `paradev.api.REST_FACADE_API_TABLE_SCHEMA` | `paradev.rest.facade-api-table.v1` | `paradev.rest.facade-api-table.v1` | `REST facade API table` | `rest` | `docs/user-manual/rest-facade-api-reference.md` | `tests/test_architecture.py::test_rest_facade_api_table_lists_public_api_facade` |
| `RestFacadeApiRow` | `TypedDict` | `rest` | `api` | `rest-facade-api` | `paradev.api.RestFacadeApiRow` | `TypedDict schema` |  | `REST facade API table` | `rest` | `docs/user-manual/rest-facade-api-reference.md` | `tests/test_architecture.py::test_rest_facade_api_table_lists_public_api_facade` |
| `RestFacadeApiTable` | `TypedDict` | `rest` | `api` | `rest-facade-api` | `paradev.api.RestFacadeApiTable` | `TypedDict schema` |  | `REST facade API table` | `rest` | `docs/user-manual/rest-facade-api-reference.md` | `tests/test_architecture.py::test_rest_facade_api_table_lists_public_api_facade` |
| `get_rest_facade_api_selection` | `function` | `rest` | `api` | `rest-facade-api` | `paradev.api.get_rest_facade_api_selection` | `RestFacadeApiTable \| RestFacadeApiRow \| list[str]` |  | `REST facade API table` | `rest` | `docs/user-manual/rest-facade-api-reference.md` | `tests/test_architecture.py::test_rest_facade_api_table_lists_public_api_facade` |
| `get_rest_facade_api_table` | `function` | `rest` | `api` | `rest-facade-api` | `paradev.api.get_rest_facade_api_table` | `RestFacadeApiTable` |  | `REST facade API table` | `rest` | `docs/user-manual/rest-facade-api-reference.md` | `tests/test_architecture.py::test_rest_facade_api_table_lists_public_api_facade` |
| `render_rest_facade_api_reference_markdown` | `function` | `rest` | `api` | `rest-facade-api` | `paradev.api.render_rest_facade_api_reference_markdown` | `str` |  | `REST facade API table` | `rest` | `docs/user-manual/rest-facade-api-reference.md` | `tests/test_architecture.py::test_rest_facade_api_table_lists_public_api_facade` |
