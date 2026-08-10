# Frontend API Index REST Row Helper Rollout

## Scope

- Continued the behavior-preserving frontend API renderer cleanup stream.
- Routed the index catalog, group/status/mode/surface indexes, REST route index, and REST request planner rows through `_frontend_api_table_row`.
- Routed workspace-section and group REST summary wrappers through the shared owner-operation summary helper.
- Kept detailed input/provider row builders for later slices to avoid a broad mechanical patch in the shared worktree.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk git diff --check -- src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py docs/user-manual/frontend-api.md docs/user-manual/frontend-api-reference.md`

## Notes

- Full-suite tests were intentionally skipped to keep CPU available for parallel PIHC2-to-PIHC3 migration work.
- Generated frontend API markdown behavior remained covered by the focused SDK renderer and CLI markdown tests.
