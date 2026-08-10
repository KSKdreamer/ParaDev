# Package API Reference

Generated from `paradev.get_package_api_table()`.

Regenerate this file whenever the root `paradev` facade changes:

```bash
rtk uv run paradev package-api --markdown > docs/user-manual/package-api-reference.md
```

## Summary / 汇总

- API rows / API 行数: 15
- Package modules / Package 模块数: 5
- Features / Feature 数: 6
- Row kinds / 行类型数: 7

## Module Index / 模块索引

| Module | Symbols | Public Exports |
| --- | --- | --- |
| `sdk.architecture` | 3 | `ArchitectureSpec`, `SurfaceSpec`, `get_architecture_spec` |
| `config` | 1 | `CM_PARADEV` |
| `package_api` | 6 | `PACKAGE_API_TABLE_SCHEMA`, `PackageApiRow`, `PackageApiTable`, `get_package_api_selection`, `get_package_api_table`, `render_package_api_reference_markdown` |
| `sdk.project` | 4 | `ParaDevProject`, `Project`, `ProjectManifestError`, `open_project` |
| `version` | 1 | `__version__` |

## Feature Index / Feature 索引

| Feature | Symbols | Public Exports |
| --- | --- | --- |
| `architecture` | 3 | `ArchitectureSpec`, `SurfaceSpec`, `get_architecture_spec` |
| `config` | 1 | `CM_PARADEV` |
| `package-api` | 6 | `PACKAGE_API_TABLE_SCHEMA`, `PackageApiRow`, `PackageApiTable`, `get_package_api_selection`, `get_package_api_table`, `render_package_api_reference_markdown` |
| `projects` | 3 | `ParaDevProject`, `Project`, `open_project` |
| `errors` | 1 | `ProjectManifestError` |
| `version` | 1 | `__version__` |

## Kind Index / 行类型索引

| Kind | Symbols | Public Exports |
| --- | --- | --- |
| `dataclass` | 4 | `ArchitectureSpec`, `ParaDevProject`, `Project`, `SurfaceSpec` |
| `ConfigManager` | 1 | `CM_PARADEV` |
| `schema constant` | 1 | `PACKAGE_API_TABLE_SCHEMA` |
| `TypedDict` | 2 | `PackageApiRow`, `PackageApiTable` |
| `exception` | 1 | `ProjectManifestError` |
| `version constant` | 1 | `__version__` |
| `function` | 5 | `get_architecture_spec`, `get_package_api_selection`, `get_package_api_table`, `open_project`, `render_package_api_reference_markdown` |

## API Standard Table / API 标准表

| Symbol | Kind | Layer | Module | Feature | Import Path | Returns | Value | Registry Seam | Surface | Doc Page | Test Anchor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `ArchitectureSpec` | `dataclass` | `package` | `sdk.architecture` | `architecture` | `paradev.ArchitectureSpec` | `ArchitectureSpec class` |  | `surface architecture registry` | `sdk` | `docs/user-manual/architecture-api-reference.md` | `tests/test_architecture.py::test_package_api_table_lists_root_facade` |
| `CM_PARADEV` | `ConfigManager` | `package` | `config` | `config` | `paradev.CM_PARADEV` | `ConfigManager` |  | `HeavenBase ConfigManager` | `sdk` | `docs/user-manual/troubleshooting.md` | `tests/test_architecture.py::test_package_api_table_lists_root_facade` |
| `PACKAGE_API_TABLE_SCHEMA` | `schema constant` | `package` | `package_api` | `package-api` | `paradev.PACKAGE_API_TABLE_SCHEMA` | `paradev.package.api-table.v1` | `paradev.package.api-table.v1` | `none` | `sdk` | `docs/user-manual/package-api-reference.md` | `tests/test_architecture.py::test_package_api_table_lists_root_facade` |
| `ParaDevProject` | `dataclass` | `package` | `sdk.project` | `projects` | `paradev.ParaDevProject` | `Project class` |  | `project family/template registry` | `sdk` | `docs/user-manual/project-api-reference.md` | `tests/test_architecture.py::test_package_api_table_lists_root_facade` |
| `PackageApiRow` | `TypedDict` | `package` | `package_api` | `package-api` | `paradev.PackageApiRow` | `TypedDict schema` |  | `none` | `sdk` | `docs/user-manual/package-api-reference.md` | `tests/test_architecture.py::test_package_api_table_lists_root_facade` |
| `PackageApiTable` | `TypedDict` | `package` | `package_api` | `package-api` | `paradev.PackageApiTable` | `TypedDict schema` |  | `none` | `sdk` | `docs/user-manual/package-api-reference.md` | `tests/test_architecture.py::test_package_api_table_lists_root_facade` |
| `Project` | `dataclass` | `package` | `sdk.project` | `projects` | `paradev.Project` | `Project class` |  | `project family/template registry` | `sdk` | `docs/user-manual/project-api-reference.md` | `tests/test_architecture.py::test_package_api_table_lists_root_facade` |
| `ProjectManifestError` | `exception` | `package` | `sdk.project` | `errors` | `paradev.ProjectManifestError` | `ProjectManifestError class` |  | `none` | `sdk` | `docs/user-manual/project-api-reference.md` | `tests/test_architecture.py::test_package_api_table_lists_root_facade` |
| `SurfaceSpec` | `dataclass` | `package` | `sdk.architecture` | `architecture` | `paradev.SurfaceSpec` | `SurfaceSpec class` |  | `surface architecture registry` | `sdk` | `docs/user-manual/architecture-api-reference.md` | `tests/test_architecture.py::test_package_api_table_lists_root_facade` |
| `__version__` | `version constant` | `package` | `version` | `version` | `paradev.__version__` | `str` | `0.1.0.000dev` | `none` | `sdk` | `docs/user-manual/getting-started.md` | `tests/test_architecture.py::test_package_api_table_lists_root_facade` |
| `get_architecture_spec` | `function` | `package` | `sdk.architecture` | `architecture` | `paradev.get_architecture_spec` | `ArchitectureSpec` |  | `surface architecture registry` | `sdk` | `docs/user-manual/architecture-api-reference.md` | `tests/test_architecture.py::test_package_api_table_lists_root_facade` |
| `get_package_api_selection` | `function` | `package` | `package_api` | `package-api` | `paradev.get_package_api_selection` | `PackageApiTable \| PackageApiRow \| list[str]` |  | `none` | `sdk` | `docs/user-manual/package-api-reference.md` | `tests/test_architecture.py::test_package_api_table_lists_root_facade` |
| `get_package_api_table` | `function` | `package` | `package_api` | `package-api` | `paradev.get_package_api_table` | `PackageApiTable` |  | `none` | `sdk` | `docs/user-manual/package-api-reference.md` | `tests/test_architecture.py::test_package_api_table_lists_root_facade` |
| `open_project` | `function` | `package` | `sdk.project` | `projects` | `paradev.open_project` | `Project` |  | `none` | `sdk` | `docs/user-manual/project-api-reference.md` | `tests/test_architecture.py::test_package_api_table_lists_root_facade` |
| `render_package_api_reference_markdown` | `function` | `package` | `package_api` | `package-api` | `paradev.render_package_api_reference_markdown` | `str` |  | `none` | `sdk` | `docs/user-manual/package-api-reference.md` | `tests/test_architecture.py::test_package_api_table_lists_root_facade` |
