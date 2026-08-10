# Frontend API Table Row Helper Rollout

## Scope

- Continued the behavior-preserving frontend API renderer cleanup stream.
- Routed selected summary and action/execution/confirmation table renderers through the shared private `_frontend_api_table_row` helper.
- Covered high-level summary rows, workspace section surface/binding/form summaries, workspace action execution rows, group/workspace-section execution summaries, group confirmation summaries, workspace section confirmation summaries, and confirmation detail rows.
- Left remaining detailed input/provider/index row builders for later slices to avoid a wide mechanical patch in the shared worktree.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk git diff --check -- src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py docs/user-manual/frontend-api.md docs/user-manual/frontend-api-reference.md`

## Notes

- Full-suite tests were intentionally skipped to keep CPU available for parallel PIHC2-to-PIHC3 migration work.
- Generated frontend API markdown behavior remained covered by the focused SDK renderer and CLI markdown tests.
