# Frontend API REST Operation Helper Refactor

## Scope

- Continued the behavior-preserving frontend API renderer cleanup stream.
- Added private REST operation traversal helpers for contract-wide and grouped-operation row builders.
- Routed REST route, request planner, REST summary, static query, dynamic query, and routed input tables through the shared helper.
- Left non-REST surface binding summaries unchanged for later focused cleanup.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`

## Notes

- Full-suite tests were intentionally skipped to keep CPU available for parallel PIHC2-to-PIHC3 migration work.
- No PIHC migration files were edited in this slice.
