# Frontend API LSP Method Input Index Progress

Date: 2026-06-14 05:06 +0800

Linear: none

## Done

- Added generated LSP Method Input Index tables to the frontend API reference renderer.
- The new table lists LSP-bound operation inputs with method string, operation id, field, type, required/default state, normalizer target bucket, and adapter-side alias.
- Reused the shared binding-input helper through the LSP surface and `method` binding key.
- Regenerated `docs/user-manual/frontend-api-reference.md`.
- Updated the frontend API guide to mention the LSP input audit table.
- Added targeted architecture and CLI assertions for hover, completion, formatting, and semantic-token LSP input rows.

## Verification

- RED: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- GREEN: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- ``rtk rg -n 'LSP Method Input Index|_frontend_api_lsp_method_input_index_rows|\| `textDocument/hover` \| `lsp\.hover` \| `line`|\| `textDocument/completion` \| `lsp\.completion` \| `limit`|\| `textDocument/formatting` \| `lsp\.formatting` \| `comments`|\| `textDocument/semanticTokens/full` \| `lsp\.semantic_tokens` \| `text`' src/paradev/sdk/frontend_api.py docs/user-manual/frontend-api.md docs/user-manual/frontend-api-reference.md tests/test_architecture.py tests/test_cli.py``
- `rtk git diff --check -- src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py docs/user-manual/frontend-api.md docs/user-manual/frontend-api-reference.md docs/progress/2026-06-14-0506-frontend-api-lsp-method-input-index.md`

## Risks Or Blockers

- Full Python test suite was intentionally not run to avoid competing with concurrent PIHC3 migration work.
- The worktree still contains unrelated desktop, loader, PIHC3, project-test, and progress-note changes from other workers.

## Next

- Continue consolidating REST, SDK, CLI, MCP, LSP, and frontend-facing API maintenance tables around generated contract metadata.
