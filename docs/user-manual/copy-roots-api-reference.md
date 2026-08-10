# Copy Roots API Reference

Generated from `paradev.sdk.copy_roots.get_copy_roots_api_table()`.

Regenerate this file whenever SDK copy-root helpers change:

```bash
rtk uv run paradev copy-roots-api --markdown > docs/user-manual/copy-roots-api-reference.md
```

## Summary / 汇总

- API rows / API 行数: 12
- Copy-root modules / Copy-root 模块数: 1
- Features / Feature 数: 6
- Row kinds / 行类型数: 6

## Module Index / 模块索引

| Module | Symbols | Public Exports |
| --- | --- | --- |
| `sdk.copy_roots` | 12 | `ARTIFACT_TARGET_ROOTS`, `ProjectCopyRootSpecError`, `CopyRootSpec`, `project_copy_roots`, `copy_root_artifacts`, `merge_copy_root_artifacts`, `COPY_ROOTS_API_TABLE_SCHEMA`, `CopyRootsApiRow`, `CopyRootsApiTable`, `get_copy_roots_api_selection`, `get_copy_roots_api_table`, `render_copy_roots_api_reference_markdown` |

## Feature Index / Feature 索引

| Feature | Symbols | Public Exports |
| --- | --- | --- |
| `target-roots` | 1 | `ARTIFACT_TARGET_ROOTS` |
| `errors` | 1 | `ProjectCopyRootSpecError` |
| `models` | 1 | `CopyRootSpec` |
| `manifest` | 1 | `project_copy_roots` |
| `artifacts` | 2 | `copy_root_artifacts`, `merge_copy_root_artifacts` |
| `copy-roots-api` | 6 | `COPY_ROOTS_API_TABLE_SCHEMA`, `CopyRootsApiRow`, `CopyRootsApiTable`, `get_copy_roots_api_selection`, `get_copy_roots_api_table`, `render_copy_roots_api_reference_markdown` |

## Kind Index / 行类型索引

| Kind | Symbols | Public Exports |
| --- | --- | --- |
| `set constant` | 1 | `ARTIFACT_TARGET_ROOTS` |
| `exception` | 1 | `ProjectCopyRootSpecError` |
| `dataclass` | 1 | `CopyRootSpec` |
| `function` | 6 | `project_copy_roots`, `copy_root_artifacts`, `merge_copy_root_artifacts`, `get_copy_roots_api_selection`, `get_copy_roots_api_table`, `render_copy_roots_api_reference_markdown` |
| `schema constant` | 1 | `COPY_ROOTS_API_TABLE_SCHEMA` |
| `TypedDict` | 2 | `CopyRootsApiRow`, `CopyRootsApiTable` |

## API Standard Table / API 标准表

| Symbol | Kind | Layer | Module | Feature | Import Path | Returns | Value | Registry Seam | Surface | Doc Page | Test Anchor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `ARTIFACT_TARGET_ROOTS` | `set constant` | `sdk` | `sdk.copy_roots` | `target-roots` | `paradev.sdk.copy_roots.ARTIFACT_TARGET_ROOTS` | `set[2]` | build, output | `copy-root target roots` | `sdk` | `docs/user-manual/copy-roots-api-reference.md` | `tests/test_architecture.py::test_copy_roots_api_table_lists_copy_root_contract` |
| `ProjectCopyRootSpecError` | `exception` | `sdk` | `sdk.copy_roots` | `errors` | `paradev.sdk.copy_roots.ProjectCopyRootSpecError` | `ProjectCopyRootSpecError exception` |  | `copy-root validation` | `sdk` | `docs/user-manual/copy-roots-api-reference.md` | `tests/test_architecture.py::test_copy_roots_api_table_lists_copy_root_contract` |
| `CopyRootSpec` | `dataclass` | `sdk` | `sdk.copy_roots` | `models` | `paradev.sdk.copy_roots.CopyRootSpec` | `CopyRootSpec dataclass` |  | `copy-root manifest model` | `sdk` | `docs/user-manual/copy-roots-api-reference.md` | `tests/test_architecture.py::test_copy_roots_api_table_lists_copy_root_contract` |
| `project_copy_roots` | `function` | `sdk` | `sdk.copy_roots` | `manifest` | `paradev.sdk.copy_roots.project_copy_roots` | `tuple[CopyRootSpec, ...]` |  | `project manifest copy_roots parser` | `sdk` | `docs/user-manual/copy-roots-api-reference.md` | `tests/test_architecture.py::test_copy_roots_api_table_lists_copy_root_contract` |
| `copy_root_artifacts` | `function` | `sdk` | `sdk.copy_roots` | `artifacts` | `paradev.sdk.copy_roots.copy_root_artifacts` | `tuple[tuple[Artifact, ...], tuple[Diagnostic, ...]]` |  | `copy-root artifact pipeline` | `sdk` | `docs/user-manual/copy-roots-api-reference.md` | `tests/test_architecture.py::test_copy_roots_api_table_lists_copy_root_contract` |
| `merge_copy_root_artifacts` | `function` | `sdk` | `sdk.copy_roots` | `artifacts` | `paradev.sdk.copy_roots.merge_copy_root_artifacts` | `tuple[tuple[Artifact, ...], tuple[Diagnostic, ...]]` |  | `copy-root artifact pipeline` | `sdk` | `docs/user-manual/copy-roots-api-reference.md` | `tests/test_architecture.py::test_copy_roots_api_table_lists_copy_root_contract` |
| `COPY_ROOTS_API_TABLE_SCHEMA` | `schema constant` | `sdk` | `sdk.copy_roots` | `copy-roots-api` | `paradev.sdk.copy_roots.COPY_ROOTS_API_TABLE_SCHEMA` | `paradev.sdk.copy_roots.api-table.v1` | paradev.sdk.copy_roots.api-table.v1 | `copy roots API table` | `sdk` | `docs/user-manual/copy-roots-api-reference.md` | `tests/test_architecture.py::test_copy_roots_api_table_lists_copy_root_contract` |
| `CopyRootsApiRow` | `TypedDict` | `sdk` | `sdk.copy_roots` | `copy-roots-api` | `paradev.sdk.copy_roots.CopyRootsApiRow` | `TypedDict schema` |  | `copy roots API table` | `sdk` | `docs/user-manual/copy-roots-api-reference.md` | `tests/test_architecture.py::test_copy_roots_api_table_lists_copy_root_contract` |
| `CopyRootsApiTable` | `TypedDict` | `sdk` | `sdk.copy_roots` | `copy-roots-api` | `paradev.sdk.copy_roots.CopyRootsApiTable` | `TypedDict schema` |  | `copy roots API table` | `sdk` | `docs/user-manual/copy-roots-api-reference.md` | `tests/test_architecture.py::test_copy_roots_api_table_lists_copy_root_contract` |
| `get_copy_roots_api_selection` | `function` | `sdk` | `sdk.copy_roots` | `copy-roots-api` | `paradev.sdk.copy_roots.get_copy_roots_api_selection` | `CopyRootsApiTable \| CopyRootsApiRow \| list[str]` |  | `copy roots API table` | `sdk` | `docs/user-manual/copy-roots-api-reference.md` | `tests/test_architecture.py::test_copy_roots_api_table_lists_copy_root_contract` |
| `get_copy_roots_api_table` | `function` | `sdk` | `sdk.copy_roots` | `copy-roots-api` | `paradev.sdk.copy_roots.get_copy_roots_api_table` | `CopyRootsApiTable` |  | `copy roots API table` | `sdk` | `docs/user-manual/copy-roots-api-reference.md` | `tests/test_architecture.py::test_copy_roots_api_table_lists_copy_root_contract` |
| `render_copy_roots_api_reference_markdown` | `function` | `sdk` | `sdk.copy_roots` | `copy-roots-api` | `paradev.sdk.copy_roots.render_copy_roots_api_reference_markdown` | `str` |  | `copy roots API table` | `sdk` | `docs/user-manual/copy-roots-api-reference.md` | `tests/test_architecture.py::test_copy_roots_api_table_lists_copy_root_contract` |
