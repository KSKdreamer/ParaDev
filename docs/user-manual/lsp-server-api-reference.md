# LSP Server API Reference

Generated from `paradev.lsp.get_lsp_server_api_table()`.

Regenerate this file whenever the public `paradev.lsp` facade changes:

```bash
rtk uv run paradev lsp-server-api --markdown > docs/user-manual/lsp-server-api-reference.md
```

## Summary / 汇总

- API rows / API 行数: 11
- LSP modules / LSP 模块数: 2
- Features / Feature 数: 5
- Row kinds / 行类型数: 5

## Module Index / 模块索引

| Module | Symbols | Public Exports |
| --- | --- | --- |
| `server` | 5 | `PdxDocument`, `PdxLanguageServer`, `read_lsp_message`, `serve_pdx_lsp_stdio`, `write_lsp_message` |
| `api` | 6 | `LSP_SERVER_API_TABLE_SCHEMA`, `LspServerApiRow`, `LspServerApiTable`, `get_lsp_server_api_selection`, `get_lsp_server_api_table`, `render_lsp_server_api_reference_markdown` |

## Feature Index / Feature 索引

| Feature | Symbols | Public Exports |
| --- | --- | --- |
| `documents` | 1 | `PdxDocument` |
| `server` | 1 | `PdxLanguageServer` |
| `framing` | 2 | `read_lsp_message`, `write_lsp_message` |
| `stdio` | 1 | `serve_pdx_lsp_stdio` |
| `lsp-server-api` | 6 | `LSP_SERVER_API_TABLE_SCHEMA`, `LspServerApiRow`, `LspServerApiTable`, `get_lsp_server_api_selection`, `get_lsp_server_api_table`, `render_lsp_server_api_reference_markdown` |

## Kind Index / 行类型索引

| Kind | Symbols | Public Exports |
| --- | --- | --- |
| `dataclass` | 1 | `PdxDocument` |
| `class` | 1 | `PdxLanguageServer` |
| `function` | 6 | `read_lsp_message`, `serve_pdx_lsp_stdio`, `write_lsp_message`, `get_lsp_server_api_selection`, `get_lsp_server_api_table`, `render_lsp_server_api_reference_markdown` |
| `schema constant` | 1 | `LSP_SERVER_API_TABLE_SCHEMA` |
| `TypedDict` | 2 | `LspServerApiRow`, `LspServerApiTable` |

## API Standard Table / API 标准表

| Symbol | Kind | Layer | Module | Feature | Import Path | Returns | Value | Registry Seam | Surface | Doc Page | Test Anchor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `PdxDocument` | `dataclass` | `lsp` | `server` | `documents` | `paradev.lsp.PdxDocument` | `class` |  | `LSP document cache` | `lsp` | `docs/user-manual/lsp-server-api-reference.md` | `tests/test_architecture.py::test_lsp_server_api_table_lists_public_lsp_facade` |
| `PdxLanguageServer` | `class` | `lsp` | `server` | `server` | `paradev.lsp.PdxLanguageServer` | `class` |  | `LSP JSON-RPC dispatcher` | `lsp` | `docs/user-manual/lsp-server-api-reference.md` | `tests/test_architecture.py::test_lsp_server_api_table_lists_public_lsp_facade` |
| `read_lsp_message` | `function` | `lsp` | `server` | `framing` | `paradev.lsp.read_lsp_message` | `dict[str, object] \| None` |  | `LSP stdio framing` | `lsp` | `docs/user-manual/lsp-server-api-reference.md` | `tests/test_architecture.py::test_lsp_server_api_table_lists_public_lsp_facade` |
| `serve_pdx_lsp_stdio` | `function` | `lsp` | `server` | `stdio` | `paradev.lsp.serve_pdx_lsp_stdio` | `None` |  | `LSP stdio server` | `lsp` | `docs/user-manual/lsp-server-api-reference.md` | `tests/test_architecture.py::test_lsp_server_api_table_lists_public_lsp_facade` |
| `write_lsp_message` | `function` | `lsp` | `server` | `framing` | `paradev.lsp.write_lsp_message` | `None` |  | `LSP stdio framing` | `lsp` | `docs/user-manual/lsp-server-api-reference.md` | `tests/test_architecture.py::test_lsp_server_api_table_lists_public_lsp_facade` |
| `LSP_SERVER_API_TABLE_SCHEMA` | `schema constant` | `lsp` | `api` | `lsp-server-api` | `paradev.lsp.LSP_SERVER_API_TABLE_SCHEMA` | `paradev.lsp.server-api-table.v1` | `paradev.lsp.server-api-table.v1` | `LSP server facade API table` | `lsp` | `docs/user-manual/lsp-server-api-reference.md` | `tests/test_architecture.py::test_lsp_server_api_table_lists_public_lsp_facade` |
| `LspServerApiRow` | `TypedDict` | `lsp` | `api` | `lsp-server-api` | `paradev.lsp.LspServerApiRow` | `TypedDict schema` |  | `LSP server facade API table` | `lsp` | `docs/user-manual/lsp-server-api-reference.md` | `tests/test_architecture.py::test_lsp_server_api_table_lists_public_lsp_facade` |
| `LspServerApiTable` | `TypedDict` | `lsp` | `api` | `lsp-server-api` | `paradev.lsp.LspServerApiTable` | `TypedDict schema` |  | `LSP server facade API table` | `lsp` | `docs/user-manual/lsp-server-api-reference.md` | `tests/test_architecture.py::test_lsp_server_api_table_lists_public_lsp_facade` |
| `get_lsp_server_api_selection` | `function` | `lsp` | `api` | `lsp-server-api` | `paradev.lsp.get_lsp_server_api_selection` | `LspServerApiTable \| LspServerApiRow \| list[str]` |  | `LSP server facade API table` | `lsp` | `docs/user-manual/lsp-server-api-reference.md` | `tests/test_architecture.py::test_lsp_server_api_table_lists_public_lsp_facade` |
| `get_lsp_server_api_table` | `function` | `lsp` | `api` | `lsp-server-api` | `paradev.lsp.get_lsp_server_api_table` | `LspServerApiTable` |  | `LSP server facade API table` | `lsp` | `docs/user-manual/lsp-server-api-reference.md` | `tests/test_architecture.py::test_lsp_server_api_table_lists_public_lsp_facade` |
| `render_lsp_server_api_reference_markdown` | `function` | `lsp` | `api` | `lsp-server-api` | `paradev.lsp.render_lsp_server_api_reference_markdown` | `str` |  | `LSP server facade API table` | `lsp` | `docs/user-manual/lsp-server-api-reference.md` | `tests/test_architecture.py::test_lsp_server_api_table_lists_public_lsp_facade` |
