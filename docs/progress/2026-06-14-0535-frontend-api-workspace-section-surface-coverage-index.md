# Frontend API Workspace Section Surface Coverage Index Progress

Date: 2026-06-14 05:35

Linear: Not updated; continuing the rolling frontend API maintenance lane.

## Done

- Added a generated Workspace Section Surface Coverage Index to the frontend API reference renderer.
- Derived per-section SDK, CLI, REST, MCP, LSP, frontend-local, unbound, and default-surface counts from SDK-owned workspace action execution metadata.
- Updated the frontend API guide and regenerated `docs/user-manual/frontend-api-reference.md`.
- Added renderer and CLI assertions for representative section coverage rows.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk rg -n -e 'Workspace Section Surface Coverage Index' ...`
- `rtk git diff --check -- src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py docs/user-manual/frontend-api.md docs/user-manual/frontend-api-reference.md docs/progress/2026-06-14-0535-frontend-api-workspace-section-surface-coverage-index.md`

## Risks Or Blockers

- Full suite intentionally not run to preserve CPU for concurrent PIHC3 migration workers.
- Worktree has unrelated desktop and PIHC3 changes; this slice only touched the frontend API renderer, generated docs, tests, and this progress note.

## Next

- Continue adding grouped API audit tables where maintainers still need to scan action-level rows by hand.
