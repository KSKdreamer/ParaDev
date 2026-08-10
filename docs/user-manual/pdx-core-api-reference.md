# PDX Core API Reference

Generated from `paradev.pdx.get_pdx_core_api_table()`.

Regenerate this file whenever the public `paradev.pdx` facade changes:

```bash
rtk uv run paradev pdx-core-api --markdown > docs/user-manual/pdx-core-api-reference.md
```

## Summary / 汇总

- API rows / API 行数: 23
- PDX modules / PDX 模块数: 5
- Features / Feature 数: 6
- Row kinds / 行类型数: 8

## Module Index / 模块索引

| Module | Symbols | Public Exports |
| --- | --- | --- |
| `ast` | 9 | `PDXBlock`, `PDXEntry`, `PDXScalar`, `SCALAR_BOOL`, `SCALAR_COLOR`, `SCALAR_ID`, `SCALAR_NUM`, `SCALAR_STR`, `SCALAR_VAR` |
| `api` | 6 | `PDX_CORE_API_TABLE_SCHEMA`, `PdxCoreApiRow`, `PdxCoreApiTable`, `get_pdx_core_api_selection`, `get_pdx_core_api_table`, `render_pdx_core_api_reference_markdown` |
| `diagnostics` | 2 | `PDXDiagnostic`, `PDXParseError` |
| `parser` | 2 | `PDXParser`, `parse_pdx` |
| `token` | 4 | `PDXTokenizer`, `Token`, `TokenType`, `reconstruct` |

## Feature Index / Feature 索引

| Feature | Symbols | Public Exports |
| --- | --- | --- |
| `ast` | 3 | `PDXBlock`, `PDXEntry`, `PDXScalar` |
| `pdx-core-api` | 6 | `PDX_CORE_API_TABLE_SCHEMA`, `PdxCoreApiRow`, `PdxCoreApiTable`, `get_pdx_core_api_selection`, `get_pdx_core_api_table`, `render_pdx_core_api_reference_markdown` |
| `diagnostics` | 2 | `PDXDiagnostic`, `PDXParseError` |
| `parser` | 2 | `PDXParser`, `parse_pdx` |
| `tokens` | 4 | `PDXTokenizer`, `Token`, `TokenType`, `reconstruct` |
| `scalars` | 6 | `SCALAR_BOOL`, `SCALAR_COLOR`, `SCALAR_ID`, `SCALAR_NUM`, `SCALAR_STR`, `SCALAR_VAR` |

## Kind Index / 行类型索引

| Kind | Symbols | Public Exports |
| --- | --- | --- |
| `dataclass` | 5 | `PDXBlock`, `PDXDiagnostic`, `PDXEntry`, `PDXScalar`, `Token` |
| `schema constant` | 1 | `PDX_CORE_API_TABLE_SCHEMA` |
| `exception` | 1 | `PDXParseError` |
| `class` | 2 | `PDXParser`, `PDXTokenizer` |
| `TypedDict` | 2 | `PdxCoreApiRow`, `PdxCoreApiTable` |
| `scalar constant` | 6 | `SCALAR_BOOL`, `SCALAR_COLOR`, `SCALAR_ID`, `SCALAR_NUM`, `SCALAR_STR`, `SCALAR_VAR` |
| `enum` | 1 | `TokenType` |
| `function` | 5 | `get_pdx_core_api_selection`, `get_pdx_core_api_table`, `parse_pdx`, `reconstruct`, `render_pdx_core_api_reference_markdown` |

## API Standard Table / API 标准表

| Symbol | Kind | Layer | Module | Feature | Import Path | Returns | Value | Registry Seam | Surface | Doc Page | Test Anchor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `PDXBlock` | `dataclass` | `pdx` | `ast` | `ast` | `paradev.pdx.PDXBlock` | `PDXBlock class` |  | `PDX AST contract` | `sdk` | `docs/user-manual/pdx-core-api-reference.md` | `tests/test_architecture.py::test_pdx_core_api_table_lists_public_pdx_facade` |
| `PDX_CORE_API_TABLE_SCHEMA` | `schema constant` | `pdx` | `api` | `pdx-core-api` | `paradev.pdx.PDX_CORE_API_TABLE_SCHEMA` | `paradev.pdx.core-api-table.v1` | `paradev.pdx.core-api-table.v1` | `PDX core facade API table` | `sdk` | `docs/user-manual/pdx-core-api-reference.md` | `tests/test_architecture.py::test_pdx_core_api_table_lists_public_pdx_facade` |
| `PDXDiagnostic` | `dataclass` | `pdx` | `diagnostics` | `diagnostics` | `paradev.pdx.PDXDiagnostic` | `PDXDiagnostic class` |  | `PDX diagnostic contract` | `sdk` | `docs/user-manual/pdx-core-api-reference.md` | `tests/test_architecture.py::test_pdx_core_api_table_lists_public_pdx_facade` |
| `PDXEntry` | `dataclass` | `pdx` | `ast` | `ast` | `paradev.pdx.PDXEntry` | `PDXEntry class` |  | `PDX AST contract` | `sdk` | `docs/user-manual/pdx-core-api-reference.md` | `tests/test_architecture.py::test_pdx_core_api_table_lists_public_pdx_facade` |
| `PDXParseError` | `exception` | `pdx` | `diagnostics` | `diagnostics` | `paradev.pdx.PDXParseError` | `PDXParseError class` |  | `PDX diagnostic contract` | `sdk` | `docs/user-manual/pdx-core-api-reference.md` | `tests/test_architecture.py::test_pdx_core_api_table_lists_public_pdx_facade` |
| `PDXParser` | `class` | `pdx` | `parser` | `parser` | `paradev.pdx.PDXParser` | `PDXParser class` |  | `PDX parser contract` | `sdk` | `docs/user-manual/pdx-core-api-reference.md` | `tests/test_architecture.py::test_pdx_core_api_table_lists_public_pdx_facade` |
| `PDXScalar` | `dataclass` | `pdx` | `ast` | `ast` | `paradev.pdx.PDXScalar` | `PDXScalar class` |  | `PDX AST contract` | `sdk` | `docs/user-manual/pdx-core-api-reference.md` | `tests/test_architecture.py::test_pdx_core_api_table_lists_public_pdx_facade` |
| `PDXTokenizer` | `class` | `pdx` | `token` | `tokens` | `paradev.pdx.PDXTokenizer` | `PDXTokenizer class` |  | `PDX token stream contract` | `sdk` | `docs/user-manual/pdx-core-api-reference.md` | `tests/test_architecture.py::test_pdx_core_api_table_lists_public_pdx_facade` |
| `PdxCoreApiRow` | `TypedDict` | `pdx` | `api` | `pdx-core-api` | `paradev.pdx.PdxCoreApiRow` | `TypedDict schema` |  | `PDX core facade API table` | `sdk` | `docs/user-manual/pdx-core-api-reference.md` | `tests/test_architecture.py::test_pdx_core_api_table_lists_public_pdx_facade` |
| `PdxCoreApiTable` | `TypedDict` | `pdx` | `api` | `pdx-core-api` | `paradev.pdx.PdxCoreApiTable` | `TypedDict schema` |  | `PDX core facade API table` | `sdk` | `docs/user-manual/pdx-core-api-reference.md` | `tests/test_architecture.py::test_pdx_core_api_table_lists_public_pdx_facade` |
| `SCALAR_BOOL` | `scalar constant` | `pdx` | `ast` | `scalars` | `paradev.pdx.SCALAR_BOOL` | `str` | `bool` | `PDX AST contract` | `sdk` | `docs/user-manual/pdx-core-api-reference.md` | `tests/test_architecture.py::test_pdx_core_api_table_lists_public_pdx_facade` |
| `SCALAR_COLOR` | `scalar constant` | `pdx` | `ast` | `scalars` | `paradev.pdx.SCALAR_COLOR` | `str` | `color` | `PDX AST contract` | `sdk` | `docs/user-manual/pdx-core-api-reference.md` | `tests/test_architecture.py::test_pdx_core_api_table_lists_public_pdx_facade` |
| `SCALAR_ID` | `scalar constant` | `pdx` | `ast` | `scalars` | `paradev.pdx.SCALAR_ID` | `str` | `id` | `PDX AST contract` | `sdk` | `docs/user-manual/pdx-core-api-reference.md` | `tests/test_architecture.py::test_pdx_core_api_table_lists_public_pdx_facade` |
| `SCALAR_NUM` | `scalar constant` | `pdx` | `ast` | `scalars` | `paradev.pdx.SCALAR_NUM` | `str` | `num` | `PDX AST contract` | `sdk` | `docs/user-manual/pdx-core-api-reference.md` | `tests/test_architecture.py::test_pdx_core_api_table_lists_public_pdx_facade` |
| `SCALAR_STR` | `scalar constant` | `pdx` | `ast` | `scalars` | `paradev.pdx.SCALAR_STR` | `str` | `str` | `PDX AST contract` | `sdk` | `docs/user-manual/pdx-core-api-reference.md` | `tests/test_architecture.py::test_pdx_core_api_table_lists_public_pdx_facade` |
| `SCALAR_VAR` | `scalar constant` | `pdx` | `ast` | `scalars` | `paradev.pdx.SCALAR_VAR` | `str` | `var` | `PDX AST contract` | `sdk` | `docs/user-manual/pdx-core-api-reference.md` | `tests/test_architecture.py::test_pdx_core_api_table_lists_public_pdx_facade` |
| `Token` | `dataclass` | `pdx` | `token` | `tokens` | `paradev.pdx.Token` | `Token class` |  | `PDX token stream contract` | `sdk` | `docs/user-manual/pdx-core-api-reference.md` | `tests/test_architecture.py::test_pdx_core_api_table_lists_public_pdx_facade` |
| `TokenType` | `enum` | `pdx` | `token` | `tokens` | `paradev.pdx.TokenType` | `TokenType class` |  | `PDX token stream contract` | `sdk` | `docs/user-manual/pdx-core-api-reference.md` | `tests/test_architecture.py::test_pdx_core_api_table_lists_public_pdx_facade` |
| `get_pdx_core_api_selection` | `function` | `pdx` | `api` | `pdx-core-api` | `paradev.pdx.get_pdx_core_api_selection` | `PdxCoreApiTable \| PdxCoreApiRow \| list[str]` |  | `PDX core facade API table` | `sdk` | `docs/user-manual/pdx-core-api-reference.md` | `tests/test_architecture.py::test_pdx_core_api_table_lists_public_pdx_facade` |
| `get_pdx_core_api_table` | `function` | `pdx` | `api` | `pdx-core-api` | `paradev.pdx.get_pdx_core_api_table` | `PdxCoreApiTable` |  | `PDX core facade API table` | `sdk` | `docs/user-manual/pdx-core-api-reference.md` | `tests/test_architecture.py::test_pdx_core_api_table_lists_public_pdx_facade` |
| `parse_pdx` | `function` | `pdx` | `parser` | `parser` | `paradev.pdx.parse_pdx` | `PDXBlock` |  | `PDX parser contract` | `sdk` | `docs/user-manual/pdx-core-api-reference.md` | `tests/test_architecture.py::test_pdx_core_api_table_lists_public_pdx_facade` |
| `reconstruct` | `function` | `pdx` | `token` | `tokens` | `paradev.pdx.reconstruct` | `str` |  | `PDX token stream contract` | `sdk` | `docs/user-manual/pdx-core-api-reference.md` | `tests/test_architecture.py::test_pdx_core_api_table_lists_public_pdx_facade` |
| `render_pdx_core_api_reference_markdown` | `function` | `pdx` | `api` | `pdx-core-api` | `paradev.pdx.render_pdx_core_api_reference_markdown` | `str` |  | `PDX core facade API table` | `sdk` | `docs/user-manual/pdx-core-api-reference.md` | `tests/test_architecture.py::test_pdx_core_api_table_lists_public_pdx_facade` |
