# Localization API Reference

Generated from `paradev.localization.get_localization_api_table()`.

Regenerate this file whenever the public `paradev.localization` facade changes:

```bash
rtk uv run paradev localization-api --markdown > docs/user-manual/localization-api-reference.md
```

## Summary / 汇总

- API rows / API 行数: 8
- Localization modules / Localization 模块数: 2
- Features / Feature 数: 2
- Row kinds / 行类型数: 4

## Module Index / 模块索引

| Module | Symbols | Public Exports |
| --- | --- | --- |
| `localization` | 2 | `HOI4_LANGUAGE_ALIASES`, `canonical_language` |
| `api` | 6 | `LOCALIZATION_API_TABLE_SCHEMA`, `LocalizationApiRow`, `LocalizationApiTable`, `get_localization_api_selection`, `get_localization_api_table`, `render_localization_api_reference_markdown` |

## Feature Index / Feature 索引

| Feature | Symbols | Public Exports |
| --- | --- | --- |
| `languages` | 2 | `HOI4_LANGUAGE_ALIASES`, `canonical_language` |
| `localization-api` | 6 | `LOCALIZATION_API_TABLE_SCHEMA`, `LocalizationApiRow`, `LocalizationApiTable`, `get_localization_api_selection`, `get_localization_api_table`, `render_localization_api_reference_markdown` |

## Kind Index / 行类型索引

| Kind | Symbols | Public Exports |
| --- | --- | --- |
| `dict constant` | 1 | `HOI4_LANGUAGE_ALIASES` |
| `function` | 4 | `canonical_language`, `get_localization_api_selection`, `get_localization_api_table`, `render_localization_api_reference_markdown` |
| `schema constant` | 1 | `LOCALIZATION_API_TABLE_SCHEMA` |
| `TypedDict` | 2 | `LocalizationApiRow`, `LocalizationApiTable` |

## API Standard Table / API 标准表

| Symbol | Kind | Layer | Module | Feature | Import Path | Returns | Value | Registry Seam | Surface | Doc Page | Test Anchor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `HOI4_LANGUAGE_ALIASES` | `dict constant` | `localization` | `localization` | `languages` | `paradev.localization.HOI4_LANGUAGE_ALIASES` | `dict[24]` |  | `HOI4 language alias normalization` | `sdk` | `docs/user-manual/localization-api-reference.md` | `tests/test_architecture.py::test_localization_api_table_lists_public_localization_facade` |
| `canonical_language` | `function` | `localization` | `localization` | `languages` | `paradev.localization.canonical_language` | `str` |  | `HOI4 language alias normalization` | `sdk` | `docs/user-manual/localization-api-reference.md` | `tests/test_architecture.py::test_localization_api_table_lists_public_localization_facade` |
| `LOCALIZATION_API_TABLE_SCHEMA` | `schema constant` | `localization` | `api` | `localization-api` | `paradev.localization.LOCALIZATION_API_TABLE_SCHEMA` | `paradev.localization.api-table.v1` | `paradev.localization.api-table.v1` | `localization facade API table` | `sdk` | `docs/user-manual/localization-api-reference.md` | `tests/test_architecture.py::test_localization_api_table_lists_public_localization_facade` |
| `LocalizationApiRow` | `TypedDict` | `localization` | `api` | `localization-api` | `paradev.localization.LocalizationApiRow` | `TypedDict schema` |  | `localization facade API table` | `sdk` | `docs/user-manual/localization-api-reference.md` | `tests/test_architecture.py::test_localization_api_table_lists_public_localization_facade` |
| `LocalizationApiTable` | `TypedDict` | `localization` | `api` | `localization-api` | `paradev.localization.LocalizationApiTable` | `TypedDict schema` |  | `localization facade API table` | `sdk` | `docs/user-manual/localization-api-reference.md` | `tests/test_architecture.py::test_localization_api_table_lists_public_localization_facade` |
| `get_localization_api_selection` | `function` | `localization` | `api` | `localization-api` | `paradev.localization.get_localization_api_selection` | `LocalizationApiTable \| LocalizationApiRow \| list[str]` |  | `localization facade API table` | `sdk` | `docs/user-manual/localization-api-reference.md` | `tests/test_architecture.py::test_localization_api_table_lists_public_localization_facade` |
| `get_localization_api_table` | `function` | `localization` | `api` | `localization-api` | `paradev.localization.get_localization_api_table` | `LocalizationApiTable` |  | `localization facade API table` | `sdk` | `docs/user-manual/localization-api-reference.md` | `tests/test_architecture.py::test_localization_api_table_lists_public_localization_facade` |
| `render_localization_api_reference_markdown` | `function` | `localization` | `api` | `localization-api` | `paradev.localization.render_localization_api_reference_markdown` | `str` |  | `localization facade API table` | `sdk` | `docs/user-manual/localization-api-reference.md` | `tests/test_architecture.py::test_localization_api_table_lists_public_localization_facade` |
