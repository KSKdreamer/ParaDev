# Frontend API Owner Summary Row Helper

## Scope

- Continued the behavior-preserving frontend API renderer cleanup stream.
- Added a private table-row helper and a private owner-operation summary helper for the repeated group/workspace-section summary-table pattern.
- Routed mode/status, payload coverage, control, option-source, input-target, validation, default, required, and alias summary wrappers through the shared helper.
- Left specialized REST, binding, form, execution, and confirmation summary tables untouched because their row shape includes owner-specific extra fields or action rows.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk git diff --check -- src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py docs/user-manual/frontend-api.md docs/user-manual/frontend-api-reference.md`

## Notes

- Full-suite tests were intentionally skipped to keep CPU available for parallel PIHC2-to-PIHC3 migration work.
- Generated frontend API markdown behavior remained covered by the focused SDK renderer and CLI markdown tests.
