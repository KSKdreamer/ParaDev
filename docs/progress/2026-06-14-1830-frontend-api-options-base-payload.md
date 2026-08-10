# Frontend API Options Base Payload

Date: 2026-06-14 18:30 Asia/Shanghai

## Summary

- Added `_frontend_api_options_base_payload` for option-provider response scaffolding.
- Routed `resolve_frontend_api_options` through the helper while preserving the payload keys and values.
- Kept generated frontend API Markdown and TypeScript output unchanged.

## Verification

- Runtime probe for base payload key order, availability, missing requirements, provider metadata, and empty options.
- Renderer digest check for `render_frontend_api_reference_markdown`, `render_frontend_api_sdk_cli_markdown`, and `render_frontend_api_typescript`.
- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --all --paths src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_sdk_cli_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_typescript_renderer_matches_desktop_contract_file tests/test_architecture.py::test_frontend_api_option_resolver_executes_sdk_owned_provider_rows tests/test_architecture.py::test_frontend_api_option_resolver_rest_route_output_json tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown tests/test_cli.py::test_frontend_api_cli_outputs_sdk_cli_reference_markdown tests/test_cli.py::test_frontend_api_cli_outputs_typescript_contract tests/test_cli.py::test_frontend_api_cli_resolves_option_source_rows`

## Notes

- This is a behavior-preserving maintainability slice scoped to frontend API option-provider response construction.
- Full-suite tests are intentionally skipped to reduce CPU contention while PIHC3 migration work continues in parallel.
