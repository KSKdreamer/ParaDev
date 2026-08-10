# Frontend API Group Form Summary Index Progress

Date: 2026-06-14 05:14 +0800

Linear: none

## Done

- Added generated Group Form Summary Index tables to the frontend API reference renderer.
- The new table aggregates form footprint by operation group, including operation count, input count, required fields, defaults, aliases, option sources, constraints, and control-kind counts.
- Reused SDK-derived form control metadata so group summaries match the existing operation-level form summary and form-control tables.
- Regenerated `docs/user-manual/frontend-api-reference.md`.
- Updated the frontend API guide to mention the group-level form audit table.
- Added targeted architecture and CLI assertions for projects, modules, build, and LSP group form summary rows.

## Verification

- RED: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- GREEN: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- ``rtk rg -n 'Group Form Summary Index|_frontend_api_group_form_summary_index_rows|\| `projects` \| Projects \| 13 \| 36|\| `modules` \| Modules \| 13 \| 76|\| `build` \| Build \| 14 \| 94|\| `lsp` \| LSP \| 7 \| 30' src/paradev/sdk/frontend_api.py docs/user-manual/frontend-api.md docs/user-manual/frontend-api-reference.md tests/test_architecture.py tests/test_cli.py``
- `rtk git diff --check -- src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py docs/user-manual/frontend-api.md docs/user-manual/frontend-api-reference.md docs/progress/2026-06-14-0514-frontend-api-group-form-summary-index.md`

## Risks Or Blockers

- Full Python test suite was intentionally not run to avoid competing with concurrent PIHC3 migration work.
- The worktree still contains unrelated desktop, loader, PIHC3, project-test, and progress-note changes from other workers.

## Next

- Continue consolidating feature-level, surface-level, and input-level API maintenance tables around generated frontend contract metadata.
