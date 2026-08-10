# LSP Symbols API

Date: 2026-06-08 02:19 CST

Issues: TAL-299, TAL-295

## Summary

- Added SDK payload schema `paradev.lsp.symbols.v1`.
- Added `document_symbols_pdx_lsp_text(...)` for editor-buffer PDX document symbols.
- Returned nested LSP `DocumentSymbol` rows from parsed PDX keys, using AST key spans for zero-based `range` and `selectionRange`.
- Added REST/OpenAPI `POST /lsp/symbols` as a desktop/GUI bridge over the same SDK helper.
- Changed frontend API row `lsp.symbols` from `planned` to implemented.
- Updated the LSP surface contract so `textDocument/documentSymbol` points to `document_symbols_pdx_lsp_text(...)`.
- Updated English and Chinese frontend API, Python SDK, developer manual, and architecture docs.

## Tests

- Red: `rtk bash scripts/test.bash tests/test_sdk_examples.py::test_document_symbols_pdx_lsp_text_sdk_returns_nested_symbols tests/test_sdk_examples.py::test_document_symbols_pdx_lsp_text_sdk_maps_parse_errors_to_lsp_diagnostics tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_lsp_surface_contract_lists_sdk_owned_methods -q`
  - Failed before implementation because `document_symbols_pdx_lsp_text`, REST `/lsp/symbols`, frontend API implementation status, and the LSP method contract did not exist.
- Focused green: same command.
  - `5 passed`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/lsp.py src/paradev/sdk/__init__.py src/paradev/sdk/frontend_api.py src/paradev/surfaces/lsp.py src/paradev/surfaces/rest.py tests/test_sdk_examples.py tests/test_architecture.py`
  - `OK: 7 file(s) - no banned imports`
- `rtk rg -n 'planned `lsp\.symbols`|lsp\.symbols.*planned|Planned .*lsp\.symbols|Planned 的 .*lsp\.symbols' docs src tests`
  - Confirmed no stale all-planned `lsp.symbols` rows; only intended "diagnostics/symbols/formatting implemented, hover planned" wording remains.
- `rtk bash scripts/flake.bash --ci`
  - Passed.
- `rtk bash scripts/test.bash`
  - `438 passed`
- `rtk uv build`
  - Built `dist/paradev-0.1.0.0.dev0.tar.gz` and `dist/paradev-0.1.0.0.dev0-py3-none-any.whl`.
- `rtk git diff --check`
  - Passed.

## Review

- The symbol helper accepts current editor text and does not read or write files.
- Clean PDX returns nested `DocumentSymbol` rows for keyed PDX entries.
- Parse failures return `ok: false`, no symbols, and LSP diagnostics with ParaDev parser codes preserved.
- Ranges currently cover key spans because the PDX AST records scalar token positions but not full block end spans yet.
- REST runtime tests remain out of the default suite because the `rest` extra is optional; the OpenAPI seed and SDK helper are covered in default gates.
- LSP hover, JSON-RPC server process, and VS Code client wiring remain out of scope for this slice.

## Linear

- `TAL-299`: comment `8b4ec136-9e29-4d1d-90f3-9f3b455fed99`.
- `TAL-295`: comment `4010fb16-84f0-4d9e-a84a-e05ae5c289d7`.
