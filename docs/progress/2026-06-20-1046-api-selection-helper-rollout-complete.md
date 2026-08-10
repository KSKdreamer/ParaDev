# 2026-06-20 10:46 API selection helper rollout complete

## Summary

- Extended the shared API selection test helper to cover scalar field mutation, list append mutation, alternate mutation symbols, and surface-specific unknown-symbol probes.
- Migrated the remaining template, project, SDK, REST, MCP, REST facade, CLI, architecture, and surfaces API selection tests to the shared helper.
- Preserved existing selector behavior coverage, including REST/MCP nested `frontend_operation_ids` copy checks.

## Verification

- `rtk bash scripts/flake.bash --all --paths tests/api_selection_contracts.py tests/test_templates_api_selection.py tests/test_project_api_selection.py tests/test_sdk_api_selection.py tests/test_rest_api_selection.py tests/test_mcp_api_selection.py tests/test_rest_facade_api_selection.py tests/test_cli_api_selection.py tests/test_architecture_api_selection.py tests/test_surfaces_api_selection_exports.py`
- `rtk uv run pytest tests/test_templates_api_selection.py tests/test_project_api_selection.py tests/test_sdk_api_selection.py tests/test_rest_api_selection.py tests/test_mcp_api_selection.py tests/test_rest_facade_api_selection.py tests/test_cli_api_selection.py tests/test_architecture_api_selection.py tests/test_surfaces_api_selection_exports.py -q`
- `rtk uv run pytest tests/test_*api_selection.py tests/test_surfaces_api_selection_exports.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_selection_contracts.py tests/test_templates_api_selection.py tests/test_project_api_selection.py tests/test_sdk_api_selection.py tests/test_rest_api_selection.py tests/test_mcp_api_selection.py tests/test_rest_facade_api_selection.py tests/test_cli_api_selection.py tests/test_architecture_api_selection.py tests/test_surfaces_api_selection_exports.py`
- `rtk git diff --check`
