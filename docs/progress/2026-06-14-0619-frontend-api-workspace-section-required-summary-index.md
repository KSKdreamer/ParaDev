# Frontend API Workspace Section Required Summary Index Progress

Date: 2026-06-14 06:19

Linear: Not updated; continuing the rolling frontend API maintenance lane.

## Done

- Added a generated Workspace Section Required Summary Index to the frontend API reference renderer.
- Derived per-section input counts, required input counts, required operation ids, required fields, target buckets, option providers, and aliases from SDK-owned frontend API input metadata.
- Updated the frontend API guide and regenerated `docs/user-manual/frontend-api-reference.md`.
- Added renderer and CLI assertions for authoring, source-editor, build, catalog, and surface-contract required-input rows.

## Verification

- RED: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- GREEN: `rtk bash scripts/test.bash tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- GREEN: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk rg -n -e 'Workspace Section Required Summary Index' -e '_frontend_api_workspace_section_required_summary_index_rows' src/paradev/sdk/frontend_api.py docs/user-manual/frontend-api.md docs/user-manual/frontend-api-reference.md tests/test_architecture.py tests/test_cli.py`
- `rtk rg -n -e '\| `authoring` \| 12 \| 68 \| 21 \|' -e '\| `source-editor` \| 15 \| 71 \| 25 \|' -e '\| `build` \| 14 \| 94 \| 0 \|' -e '\| `catalog` \| 4 \| 14 \| 0 \|' -e '\| `surface-contracts` \| 12 \| 13 \| 7 \|' docs/user-manual/frontend-api-reference.md tests/test_architecture.py tests/test_cli.py`
- `rtk git diff --check -- src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py docs/user-manual/frontend-api.md docs/user-manual/frontend-api-reference.md docs/progress/2026-06-14-0619-frontend-api-workspace-section-required-summary-index.md`

## Risks Or Blockers

- Full suite intentionally not run to preserve CPU for concurrent PIHC3 migration workers.
- Worktree has unrelated desktop and PIHC3 changes; this slice only touched the frontend API renderer, generated docs, tests, and this progress note.

## Next

- Continue expanding grouped generated API audit tables and reduce duplicated renderer helper plumbing where focused tests cover the behavior.
