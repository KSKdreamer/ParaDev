# PDX And LSP Frontend API Inputs

Date: 2026-06-08 04:04 CST

Issues: TAL-299, TAL-295

Linear comments:

- TAL-299: `2a5d6c16-199b-415e-ae34-0f599e84811b`
- TAL-295: `0a686162-aee5-4faa-b885-2e6256720477`

## Summary

- Added canonical `inputs` metadata to PDX frontend API rows for parse, tokens, dump, and format actions.
- Added canonical `inputs` metadata to LSP frontend API rows for diagnostics, symbols, hover, and formatting actions.
- Kept the frontend mental model explicit: PDX rows operate on saved files through required `path` inputs, while LSP rows operate on unsaved editor text with optional document identity and required hover positions.
- Updated the English and Chinese frontend API manual, SDK manual, developer manual, and architecture interface contract.

## Verification

- Red test: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations -q` failed on missing `pdx.parse["inputs"]`.
- Focused green: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations -q` passed.
- Lookup coverage: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_frontend_api_lookup_helpers_return_canonical_rows -q` passed.
- SDK probe: `rtk uv run python - <<'PY' ... get_frontend_api_operation(...) ... PY` confirmed PDX and LSP inputs through the public SDK.
- Docs/source check: `rtk rg -n 'PDX rows use saved-file inputs|PDX 行使用已保存文件输入|pdx_format_inputs|lsp_hover_inputs|PDX and LSP frontend rows|input_names\("pdx|input_names\("lsp|_input\("text"' src/paradev/sdk/frontend_api.py tests/test_architecture.py docs/user-manual docs/architecture/interfaces.md`
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py`
- Formatting: `rtk bash scripts/flake.bash --ci`
- Full tests: `rtk bash scripts/test.bash` (`443 passed`)
- Package build: `rtk uv build`

## Review

- This is contract metadata only; it does not change parser, formatter, LSP helper, REST, MCP, or CLI behavior.
- PDX file operations and LSP editor-buffer operations now have separate frontend action signatures, reducing the chance that GUI or importer agents copy REST schemas by hand.
- Build, catalog, and surface rows remain the next API-input maintenance areas.
