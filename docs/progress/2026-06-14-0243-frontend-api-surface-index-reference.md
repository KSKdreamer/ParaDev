# Frontend API Surface Index Reference Progress

Date: 2026-06-14 02:43 +0800

Linear: none

## Done

- Added generated Surface Index tables to the frontend API reference renderer.
- The new table maps each callable surface (`sdk`, `cli`, `rest`, `mcp`, `lsp`, and `unbound`) to the canonical frontend operation ids from `contract["index"]["surface"]`.
- Regenerated `docs/user-manual/frontend-api-reference.md`.
- Updated the frontend API guide to mention that the generated reference renders surface operation-id lists.
- Added targeted architecture and CLI assertions for representative REST, LSP, and unbound rows.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`

## Risks Or Blockers

- Full Python test suite was intentionally not run to avoid competing with concurrent PIHC3 migration work.
- The worktree still contains unrelated desktop, loader, PIHC3, and progress-note changes from other workers.

## Next

- Continue extending generated API tables where maintainers still need grouped views across SDK, CLI, REST, MCP, LSP, payload, and workspace boundaries.
- Consider adding compact per-surface feature summaries once the operation-id tables have stabilized.
