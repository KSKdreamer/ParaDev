# Frontend API Group Action Owner Helper Refactor

## Scope

- Continued the behavior-preserving frontend API renderer cleanup stream.
- Added a private group action owner helper that centralizes the operation-group, operation-row, and workspace-action tuple used by group execution/confirmation summaries.
- Routed the group execution and group confirmation summary renderers through the shared helper while preserving the existing workspace action collector validation behavior.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk git diff --check -- src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py docs/user-manual/frontend-api.md docs/user-manual/frontend-api-reference.md`

## Notes

- Full-suite tests were intentionally skipped to keep CPU available for parallel PIHC2-to-PIHC3 migration work.
- Generated frontend API reference behavior stayed covered by the focused renderer and CLI markdown tests.
