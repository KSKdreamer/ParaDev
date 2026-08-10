# Frontend API Required Option Source Fields

Date: 2026-06-14 18:27 Asia/Shanghai

## Summary

- Added required option-source accessors for runtime `operation_id` and `values_path`.
- Routed option resolution through the accessors while preserving required-key failure behavior.
- Kept generated frontend API Markdown and TypeScript output unchanged.

## Verification

- Runtime probe for required `operation_id` and `values_path` access, including missing-key `KeyError` behavior.
- Renderer digest check for `render_frontend_api_reference_markdown`, `render_frontend_api_sdk_cli_markdown`, and `render_frontend_api_typescript`.
- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --all --paths src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_sdk_cli_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_typescript_renderer_matches_desktop_contract_file tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown tests/test_cli.py::test_frontend_api_cli_outputs_sdk_cli_reference_markdown tests/test_cli.py::test_frontend_api_cli_outputs_typescript_contract`

## Notes

- This is a behavior-preserving maintainability slice scoped to frontend API option-provider resolution.
- Full-suite tests are intentionally skipped to reduce CPU contention while PIHC3 migration work continues in parallel.
