# Frontend API Operation ID Index Row Progress

Date: 2026-06-14 11:08

Linear: N/A

## Done

- Extracted shared operation-id index row rendering for status, mode, surface, binding-surface, and payload API tables.
- Preserved each table's existing key ordering and operation-id list rendering.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_sdk_cli_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown tests/test_cli.py::test_frontend_api_cli_outputs_sdk_cli_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py`

## Risks Or Blockers

- Shared worktree still contains unrelated desktop, PIHC3 migration, logo, and docs changes from other workers; this slice stages only the SDK renderer and this note.

## Next

- Continue consolidating frontend API table helpers without changing documented API contract output.
