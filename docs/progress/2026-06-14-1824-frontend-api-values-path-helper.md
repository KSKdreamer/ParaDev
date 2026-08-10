# Frontend API Values Path Helper

Date: 2026-06-14 18:24 Asia/Shanghai

## Summary

- Added helpers for frontend API option-provider values-path segment extraction and display labels.
- Routed `_frontend_api_values_path` through the helpers to avoid repeated sequence normalization and path formatting.
- Kept generated frontend API Markdown and TypeScript output unchanged.

## Verification

- Runtime probe for successful values-path traversal, missing path errors, non-list path errors, and non-sequence path labels.
- Renderer digest check for `render_frontend_api_reference_markdown`, `render_frontend_api_sdk_cli_markdown`, and `render_frontend_api_typescript`.
- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --all --paths src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_sdk_cli_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_typescript_renderer_matches_desktop_contract_file tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown tests/test_cli.py::test_frontend_api_cli_outputs_sdk_cli_reference_markdown tests/test_cli.py::test_frontend_api_cli_outputs_typescript_contract`

## Notes

- This is a behavior-preserving maintainability slice scoped to frontend API option-provider payload traversal.
- Full-suite tests are intentionally skipped to reduce CPU contention while PIHC3 migration work continues in parallel.
