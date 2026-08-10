# Frontend API Group Required Summary Index Progress

Date: 2026-06-14 07:44

Linear: not linked

## Done

- Added RED assertions for the generated Group Required Summary Index heading and representative `modules`/`surfaces` rows in the architecture and CLI reference tests.
- Refactored required-input summary aggregation into `_frontend_api_required_summary_cells(...)`, then reused it for workspace-section and operation-group required-input summary tables.
- Added English and Chinese renderer/manual copy for the new group required summary table and regenerated `docs/user-manual/frontend-api-reference.md`.

## Verification

- RED: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown` failed on the missing `Group Required Summary` heading before implementation.
- GREEN: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown` -> `2 passed in 0.80s`.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py` -> `OK: 3 file(s) - no banned imports`.
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py` -> `3 files would be left unchanged`.
- `rtk rg -n 'Group Required Summary|_frontend_api_group_required_summary|_frontend_api_required_summary_cells|\| `modules` \| 13 \| 76 \| 18|\| `surfaces` \| 12 \| 13 \| 7 \| `surface.frontend_api.action`' ...` found the renderer helpers, tests, manual note, and generated English/Chinese reference rows.
- `rtk git diff --check -- src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py docs/user-manual/frontend-api.md docs/user-manual/frontend-api-reference.md` exited cleanly.

## Risks Or Blockers

- Full-suite tests were intentionally waived for this slice to reduce CPU pressure during concurrent PIHC2-to-PIHC3 migration work.
- The touched files still include earlier uncommitted frontend API refactor slices; this note records only the Group Required Summary Index addition.

## Next

- Continue filling the remaining group-level alias summary while preserving the existing SDK/CLI/REST/MCP/LSP behavior.
