# Frontend API Workspace Action Owner Helper Refactor

## Scope

- Continued the behavior-preserving frontend API renderer cleanup stream.
- Added a private workspace-section action owner helper that normalizes section rows, matched operation rows, and workspace action rows once.
- Routed section REST, surface coverage, execution, action execution, confirmation summary, and confirmation detail renderers through the shared helper.
- Routed remaining group REST, binding, and form summary renderers through the existing group operation owner helper.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk git diff --check -- src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py docs/user-manual/frontend-api.md docs/user-manual/frontend-api-reference.md`

## Notes

- Full-suite tests were intentionally skipped to keep CPU available for parallel PIHC2-to-PIHC3 migration work.
- Generated frontend API markdown behavior was unchanged according to the focused renderer and CLI reference tests.
