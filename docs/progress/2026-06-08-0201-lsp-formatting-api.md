# LSP Formatting API

Date: 2026-06-08 02:01 CST

Issues: TAL-299, TAL-295

## Summary

- Added SDK payload schema `paradev.lsp.formatting.v1`.
- Added `format_pdx_lsp_text(...)` for editor buffers and LSP `textDocument/formatting` responses.
- Mapped PDX parse errors into LSP diagnostics with zero-based ranges and numeric severities.
- Added REST/OpenAPI `POST /lsp/formatting` as a desktop/GUI bridge over the same SDK helper.
- Added method-level LSP surface contracts that mark formatting implemented while diagnostics, symbols, and hover remain planned.
- Changed frontend API row `lsp.formatting` from `planned` to implemented.
- Updated English and Chinese frontend API, Python SDK, developer manual, and architecture docs.

## Tests

- Red: `rtk bash scripts/test.bash tests/test_sdk_examples.py::test_format_pdx_lsp_text_sdk_returns_full_document_edit tests/test_sdk_examples.py::test_format_pdx_lsp_text_sdk_returns_no_edits_when_unchanged tests/test_sdk_examples.py::test_format_pdx_lsp_text_sdk_maps_parse_errors_to_lsp_diagnostics tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_lsp_surface_contract_lists_sdk_owned_methods -q`
  - Failed before implementation because `format_pdx_lsp_text`, REST `/lsp/formatting`, frontend API implementation status, and method-level LSP surface contracts did not exist.
- Focused green: same command.
  - `6 passed`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/lsp.py src/paradev/sdk/__init__.py src/paradev/sdk/frontend_api.py src/paradev/surfaces/lsp.py src/paradev/surfaces/rest.py tests/test_sdk_examples.py tests/test_architecture.py`
  - `OK: 7 file(s) - no banned imports`
- `rtk rg -n 'planned `lsp\.formatting`|Planned `lsp\.diagnostics`, `lsp\.symbols`, `lsp\.hover`, and `lsp\.formatting`|Planned 的 `lsp\.diagnostics`、`lsp\.symbols`、`lsp\.hover` 和 `lsp\.formatting`|lsp\.formatting.*planned' docs src tests`
  - Confirmed no stale all-planned `lsp.formatting` rows; only intended "formatting implemented, other LSP rows planned" wording remains.
- `rtk bash scripts/flake.bash --ci`
  - Passed.
- `rtk bash scripts/test.bash`
  - `434 passed`
- `rtk uv build`
  - Built `dist/paradev-0.1.0.0.dev0.tar.gz` and `dist/paradev-0.1.0.0.dev0-py3-none-any.whl`.
- `rtk git diff --check`
  - Passed.

## Review

- The LSP helper accepts current editor text and does not write files.
- Formatting behavior delegates to `format_pdx_text(...)`, so LSP, REST, and GUI callers share the same formatter and parse diagnostics.
- Successful formatting returns a full-document `TextEdit`; unchanged text returns an empty edit list.
- REST runtime tests are not part of the default suite because the `rest` extra is optional; the OpenAPI seed and SDK helper are covered in the default gates.
- LSP diagnostics, symbols, hover, JSON-RPC server process, and VS Code client wiring remain out of scope for this slice.

## Linear

- `TAL-299`: comment `646d77e5-6301-4afb-ae69-4c98fa729b26`.
- `TAL-295`: comment `402390b7-f0ea-46db-9841-2215dcbc9afd`.
