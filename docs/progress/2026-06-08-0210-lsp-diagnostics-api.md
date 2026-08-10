# LSP Diagnostics API

Date: 2026-06-08 02:10 CST

Issues: TAL-299, TAL-295

## Summary

- Added SDK payload schema `paradev.lsp.diagnostics.v1`.
- Added `diagnose_pdx_lsp_text(...)` for editor-buffer PDX diagnostics.
- Reused the LSP diagnostic mapping from formatting so parse errors return zero-based ranges and numeric severities.
- Added REST/OpenAPI `POST /lsp/diagnostics` as a desktop/GUI bridge over the same SDK helper.
- Changed frontend API row `lsp.diagnostics` from `planned` to implemented.
- Updated the LSP surface contract so `textDocument/publishDiagnostics` points to `diagnose_pdx_lsp_text(...)`.
- Updated English and Chinese frontend API, Python SDK, developer manual, and architecture docs.

## Tests

- Red: `rtk bash scripts/test.bash tests/test_sdk_examples.py::test_diagnose_pdx_lsp_text_sdk_reports_clean_document tests/test_sdk_examples.py::test_diagnose_pdx_lsp_text_sdk_maps_parse_errors_to_lsp_diagnostics tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_lsp_surface_contract_lists_sdk_owned_methods -q`
  - Failed before implementation because `diagnose_pdx_lsp_text`, REST `/lsp/diagnostics`, frontend API implementation status, and the LSP method contract did not exist.
- Focused green: same command.
  - `5 passed`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/lsp.py src/paradev/sdk/__init__.py src/paradev/sdk/frontend_api.py src/paradev/surfaces/lsp.py src/paradev/surfaces/rest.py tests/test_sdk_examples.py tests/test_architecture.py`
  - `OK: 7 file(s) - no banned imports`
- `rtk rg -n 'planned `lsp\.diagnostics`|lsp\.diagnostics.*planned|Planned .*lsp\.diagnostics|Planned 的 .*lsp\.diagnostics' docs src tests`
  - Confirmed no stale all-planned `lsp.diagnostics` rows; only intended "diagnostics/formatting implemented, symbols/hover planned" wording remains.
- `rtk bash scripts/flake.bash --ci`
  - Passed.
- `rtk bash scripts/test.bash`
  - `436 passed`
- `rtk uv build`
  - Built `dist/paradev-0.1.0.0.dev0.tar.gz` and `dist/paradev-0.1.0.0.dev0-py3-none-any.whl`.
- `rtk git diff --check`
  - Passed.

## Review

- The diagnostics helper accepts current editor text and does not read or write files.
- Clean PDX returns `ok: true` and an empty diagnostics list.
- Parse failures return LSP diagnostics with ParaDev parser codes preserved in `code` and `source: paradev.pdx`.
- REST runtime tests remain out of the default suite because the `rest` extra is optional; the OpenAPI seed and SDK helper are covered in default gates.
- LSP symbols, hover, JSON-RPC server process, and VS Code client wiring remain out of scope for this slice.

## Linear

- `TAL-299`: comment `e310cfa1-c1ba-47a9-b278-7e21ee765e20`.
- `TAL-295`: comment `812af9b4-8ac7-4981-9625-314e58d5db74`.
