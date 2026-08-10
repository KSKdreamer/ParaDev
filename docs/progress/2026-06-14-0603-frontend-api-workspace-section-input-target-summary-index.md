# Frontend API Workspace Section Input Target Summary Index Progress

Date: 2026-06-14 06:03

Linear: Not updated; continuing the rolling frontend API maintenance lane.

## Done

- Added a generated Workspace Section Input Target Summary Index to the frontend API reference renderer.
- Derived per-section input counts, required input counts, target bucket counts, parameter fields, project-context fields, selector fields, projection fields, and frontend-to-SDK aliases from the SDK-owned frontend API contract.
- Updated the frontend API guide and regenerated `docs/user-manual/frontend-api-reference.md`.
- Added renderer and CLI assertions for project-backed, build/catalog, and surface-contract target bucket rows.

## Verification

- RED: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- GREEN: `rtk bash scripts/test.bash tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- GREEN: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk rg -n -e 'Workspace Section Input Target Summary Index' -e '_frontend_api_workspace_section_input_target_summary_index_rows' src/paradev/sdk/frontend_api.py docs/user-manual/frontend-api.md docs/user-manual/frontend-api-reference.md tests/test_architecture.py tests/test_cli.py`
- `rtk rg -n -e '\| `project-browser` \| 9 \| 54 \| 2 \|' -e '\| `authoring` \| 12 \| 68 \| 21 \|' -e '\| `source-editor` \| 15 \| 71 \| 25 \|' -e '\| `build` \| 14 \| 94 \| 0 \|' -e '\| `catalog` \| 4 \| 14 \| 0 \|' -e '\| `surface-contracts` \| 12 \| 13 \| 7 \|' docs/user-manual/frontend-api-reference.md tests/test_architecture.py tests/test_cli.py`
- `rtk git diff --check -- src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py docs/user-manual/frontend-api.md docs/user-manual/frontend-api-reference.md docs/progress/2026-06-14-0603-frontend-api-workspace-section-input-target-summary-index.md`

## Risks Or Blockers

- Full suite intentionally not run to preserve CPU for concurrent PIHC3 migration workers.
- Worktree has unrelated desktop and PIHC3 changes; this slice only touched the frontend API renderer, generated docs, tests, and this progress note.

## Next

- Continue expanding grouped generated API audit tables while preserving runtime behavior.
