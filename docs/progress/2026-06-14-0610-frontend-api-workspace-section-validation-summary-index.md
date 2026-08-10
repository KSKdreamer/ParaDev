# Frontend API Workspace Section Validation Summary Index Progress

Date: 2026-06-14 06:10

Linear: Not updated; continuing the rolling frontend API maintenance lane.

## Done

- Added a generated Workspace Section Validation Summary Index to the frontend API reference renderer.
- Derived per-section input counts, constraint counts, choice counts, minimum counts, constrained operation ids, choice fields, and minimum fields from SDK-owned frontend API input metadata.
- Updated the frontend API guide and regenerated `docs/user-manual/frontend-api-reference.md`.
- Added renderer and CLI assertions for choice-only, minimum-only, empty, and surface-contract validation rows.

## Verification

- RED: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- GREEN: `rtk bash scripts/test.bash tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- GREEN: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk rg -n -e 'Workspace Section Validation Summary Index' -e '_frontend_api_workspace_section_validation_summary_index_rows' src/paradev/sdk/frontend_api.py docs/user-manual/frontend-api.md docs/user-manual/frontend-api-reference.md tests/test_architecture.py tests/test_cli.py`
- `rtk rg -n -e '\| `project-browser` \| 9 \| 54 \| 6 \| 6 \| 0 \|' -e '\| `authoring` \| 12 \| 68 \| 4 \| 4 \| 0 \|' -e '\| `source-editor` \| 15 \| 71 \| 6 \| 0 \| 6 \|' -e '\| `build` \| 14 \| 94 \| 6 \| 6 \| 0 \|' -e '\| `catalog` \| 4 \| 14 \| 0 \| 0 \| 0 \|' -e '\| `surface-contracts` \| 12 \| 13 \| 1 \| 1 \| 0 \|' docs/user-manual/frontend-api-reference.md tests/test_architecture.py tests/test_cli.py`
- `rtk git diff --check -- src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py docs/user-manual/frontend-api.md docs/user-manual/frontend-api-reference.md docs/progress/2026-06-14-0610-frontend-api-workspace-section-validation-summary-index.md`

## Risks Or Blockers

- Full suite intentionally not run to preserve CPU for concurrent PIHC3 migration workers.
- Worktree has unrelated desktop and PIHC3 changes; this slice only touched the frontend API renderer, generated docs, tests, and this progress note.

## Next

- Continue expanding grouped generated API audit tables while preserving runtime behavior.
