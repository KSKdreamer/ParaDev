# Project Facade API Reference

Generated from `paradev.project.get_project_facade_api_table()`.

Regenerate this file whenever the public `paradev.project` facade changes:

```bash
rtk uv run paradev project-facade-api --markdown > docs/user-manual/project-facade-api-reference.md
```

## Summary / 汇总

- API rows / API 行数: 8
- Project modules / Project 模块数: 2
- Features / Feature 数: 3
- Row kinds / 行类型数: 5

## Module Index / 模块索引

| Module | Symbols | Public Exports |
| --- | --- | --- |
| `sdk.project` | 2 | `Project`, `ProjectManifestError` |
| `api` | 6 | `PROJECT_FACADE_API_TABLE_SCHEMA`, `ProjectFacadeApiRow`, `ProjectFacadeApiTable`, `get_project_facade_api_selection`, `get_project_facade_api_table`, `render_project_facade_api_reference_markdown` |

## Feature Index / Feature 索引

| Feature | Symbols | Public Exports |
| --- | --- | --- |
| `projects` | 1 | `Project` |
| `errors` | 1 | `ProjectManifestError` |
| `project-facade-api` | 6 | `PROJECT_FACADE_API_TABLE_SCHEMA`, `ProjectFacadeApiRow`, `ProjectFacadeApiTable`, `get_project_facade_api_selection`, `get_project_facade_api_table`, `render_project_facade_api_reference_markdown` |

## Kind Index / 行类型索引

| Kind | Symbols | Public Exports |
| --- | --- | --- |
| `dataclass` | 1 | `Project` |
| `exception` | 1 | `ProjectManifestError` |
| `schema constant` | 1 | `PROJECT_FACADE_API_TABLE_SCHEMA` |
| `TypedDict` | 2 | `ProjectFacadeApiRow`, `ProjectFacadeApiTable` |
| `function` | 3 | `get_project_facade_api_selection`, `get_project_facade_api_table`, `render_project_facade_api_reference_markdown` |

## API Standard Table / API 标准表

| Symbol | Kind | Layer | Module | Feature | Import Path | Returns | Value | Registry Seam | Surface | Doc Page | Test Anchor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `Project` | `dataclass` | `project` | `sdk.project` | `projects` | `paradev.project.Project` | `Project class` |  | `project family/template registry` | `sdk` | `docs/user-manual/project-api-reference.md` | `tests/test_architecture.py::test_project_facade_api_table_lists_project_package_facade` |
| `ProjectManifestError` | `exception` | `project` | `sdk.project` | `errors` | `paradev.project.ProjectManifestError` | `ProjectManifestError class` |  | `project manifest validation` | `sdk` | `docs/user-manual/project-api-reference.md` | `tests/test_architecture.py::test_project_facade_api_table_lists_project_package_facade` |
| `PROJECT_FACADE_API_TABLE_SCHEMA` | `schema constant` | `project` | `api` | `project-facade-api` | `paradev.project.PROJECT_FACADE_API_TABLE_SCHEMA` | `paradev.project.facade-api-table.v1` | `paradev.project.facade-api-table.v1` | `project facade API table` | `sdk` | `docs/user-manual/project-facade-api-reference.md` | `tests/test_architecture.py::test_project_facade_api_table_lists_project_package_facade` |
| `ProjectFacadeApiRow` | `TypedDict` | `project` | `api` | `project-facade-api` | `paradev.project.ProjectFacadeApiRow` | `TypedDict schema` |  | `project facade API table` | `sdk` | `docs/user-manual/project-facade-api-reference.md` | `tests/test_architecture.py::test_project_facade_api_table_lists_project_package_facade` |
| `ProjectFacadeApiTable` | `TypedDict` | `project` | `api` | `project-facade-api` | `paradev.project.ProjectFacadeApiTable` | `TypedDict schema` |  | `project facade API table` | `sdk` | `docs/user-manual/project-facade-api-reference.md` | `tests/test_architecture.py::test_project_facade_api_table_lists_project_package_facade` |
| `get_project_facade_api_selection` | `function` | `project` | `api` | `project-facade-api` | `paradev.project.get_project_facade_api_selection` | `ProjectFacadeApiTable \| ProjectFacadeApiRow \| list[str]` |  | `project facade API table` | `sdk` | `docs/user-manual/project-facade-api-reference.md` | `tests/test_architecture.py::test_project_facade_api_table_lists_project_package_facade` |
| `get_project_facade_api_table` | `function` | `project` | `api` | `project-facade-api` | `paradev.project.get_project_facade_api_table` | `ProjectFacadeApiTable` |  | `project facade API table` | `sdk` | `docs/user-manual/project-facade-api-reference.md` | `tests/test_architecture.py::test_project_facade_api_table_lists_project_package_facade` |
| `render_project_facade_api_reference_markdown` | `function` | `project` | `api` | `project-facade-api` | `paradev.project.render_project_facade_api_reference_markdown` | `str` |  | `project facade API table` | `sdk` | `docs/user-manual/project-facade-api-reference.md` | `tests/test_architecture.py::test_project_facade_api_table_lists_project_package_facade` |
