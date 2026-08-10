# LSP PDX Payload Progress

Date: 2026-06-08 21:31 CST

Linear: TAL-299, TAL-295

## Done

- Addressed the 10:44 and 15:45 alignment reviews by continuing the frontend API reconciliation on `master` instead of pulling the large stale branch wholesale.
- Added SDK-owned PDX-backed LSP payload helpers in `paradev.sdk`: diagnostics, document symbols, hover, and formatting.
- Added `paradev lsp diagnostics`, `paradev lsp symbols`, `paradev lsp hover`, and `paradev lsp formatting` CLI projections that read editor-buffer text from `--text` or `--text-file`.
- Updated `src/paradev/surfaces/lsp.py` so the LSP surface contract lists the four SDK-owned method payloads and their implementation functions.
- Promoted the frontend API catalog LSP rows from `planned` to `implemented`; the generated reference now reports 65 total operations, 54 implemented, 10 planned, and 1 frontend-local.
- Updated the bilingual frontend API and Python SDK manual pages with LSP CLI and SDK examples for editor integrations.
- Posted Linear comments: `TAL-299` comment `7eaf3bd8-0413-4777-8595-026dcf745be7`; `TAL-295` comment `5e3b9d2f-06b5-4420-8062-ff97bff5b90b`.

## Verification

- `rtk uv run black src/paradev/sdk/lsp.py src/paradev/sdk/__init__.py src/paradev/sdk/frontend_api.py src/paradev/surfaces/lsp.py src/paradev/cli.py tests/test_lsp.py tests/test_architecture.py tests/test_cli.py`: passed.
- `rtk python -m py_compile src/paradev/sdk/lsp.py src/paradev/sdk/__init__.py src/paradev/sdk/frontend_api.py src/paradev/surfaces/lsp.py src/paradev/cli.py`: passed.
- `rtk bash scripts/test.bash tests/test_lsp.py tests/test_architecture.py::test_frontend_api_catalog_lists_master_line_operations tests/test_architecture.py::test_lsp_surface_contract_lists_sdk_owned_methods tests/test_cli.py::test_lsp_diagnostics_cli_outputs_lsp_payload tests/test_cli.py::test_lsp_formatting_cli_reads_text_file -q`: passed, 7 tests.
- `rtk uv run paradev frontend-api --group lsp --json`: passed and showed all four LSP operations as `implemented`.
- `rtk uv run black --check src/paradev/sdk/lsp.py src/paradev/sdk/__init__.py src/paradev/sdk/frontend_api.py src/paradev/surfaces/lsp.py src/paradev/cli.py tests/test_lsp.py tests/test_architecture.py tests/test_cli.py`: passed.
- `rtk bash scripts/test.bash tests/test_lsp.py tests/test_architecture.py tests/test_cli.py -q`: passed, 35 tests and 1 skipped for missing optional `fastapi.testclient`.
- `rtk uv run paradev lsp diagnostics --text 'value = 0x' --json`: passed and returned a `paradev.lsp.diagnostics.v1` payload with zero-based ranges.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/lsp.py src/paradev/sdk/__init__.py src/paradev/sdk/frontend_api.py src/paradev/surfaces/lsp.py src/paradev/cli.py tests/test_lsp.py tests/test_architecture.py tests/test_cli.py`: passed, 8 files.
- `rtk bash scripts/flake.bash --ci`: passed.
- `rtk git diff --check`: passed.
- `rtk uv build`: passed and included `paradev/sdk/lsp.py` in the wheel.
- `rtk bash scripts/test.bash -q`: passed, 430 tests and 1 skipped for missing optional `fastapi.testclient`.

## Risks Or Blockers

- The new LSP helpers are payload-level SDK functions, not a long-running JSON-RPC server. A later editor/server slice can wrap them without changing the frontend API contract.
- PDX diagnostics currently expose parser syntax failures. Game-semantic diagnostics remain a later compiler/indexing responsibility.
- The optional FastAPI endpoint test still skips in the default environment when `fastapi.testclient` is absent.
- Local `.codex-artifacts/` and `.playwright-mcp/` files remain automation artifacts and should not be staged.

## Next

- Promote module edit/rename/remove and collection edit/remove rows from `planned` to implemented SDK/CLI contracts.
- Add REST/MCP adapters over the same SDK payload helpers after the SDK contracts are stable.
- Keep frontend integrations reading the generated frontend API reference instead of duplicating operation metadata.
