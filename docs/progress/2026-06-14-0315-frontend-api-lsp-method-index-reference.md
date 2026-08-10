# Frontend API LSP Method Index Reference Progress

Date: 2026-06-14 03:15 +0800

Linear: none

## Done

- Added generated LSP Method Index tables to the frontend API reference renderer.
- The new table maps LSP method strings back to canonical frontend operation ids from `contract["index"]["binding"]["lsp"]`.
- Reused the existing surface-binding row renderer through a thin LSP wrapper.
- Regenerated `docs/user-manual/frontend-api-reference.md`.
- Updated the frontend API guide to mention the LSP method-to-operation table for VS Code and language-server audits.
- Added targeted architecture and CLI assertions for representative LSP method rows.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`

## Risks Or Blockers

- Full Python test suite was intentionally not run to avoid competing with concurrent PIHC3 migration work.
- The worktree still contains unrelated desktop, loader, PIHC3, project-test, and progress-note changes from other workers.

## Next

- Continue consolidating API reference tables around generated indexes instead of duplicated hand-maintained lists.
