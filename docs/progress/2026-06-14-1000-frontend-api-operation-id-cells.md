# 2026-06-14 10:00 - Frontend API Operation ID Cells

## Scope

- Added `_frontend_api_operation_id_cells(...)` for shared operation-id count/list markdown cells.
- Routed group, status, mode, surface, REST route, binding, payload, and workspace-section index tables through the helper.
- Preserved generated API table text and index ordering.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
  - 2 passed in 1.12s.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
  - OK: 1 file(s) - no banned imports.
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py`
  - All done; 1 file would be left unchanged.
- `rtk git diff --check -- src/paradev/sdk/frontend_api.py docs/progress/2026-06-14-1000-frontend-api-operation-id-cells.md`
  - Passed with no whitespace errors.

## Risks Or Blockers

- Full-suite test intentionally skipped to reduce CPU during parallel PIHC3 migration work.
- Shared worktree still contains unrelated desktop, SDK, and PIHC3 files; stage exact paths only.

## Next

- Continue consolidating frontend API renderer row helpers around repeated generated table patterns.
