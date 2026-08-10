# 2026-06-15 02:12 Project API Reference

## Done

- Added `paradev.sdk.get_project_api_table()` and `render_project_api_reference_markdown()` for the public `Project` object surface.
- Added CLI `paradev project-api` with JSON output and `--markdown` reference generation.
- Regenerated SDK, CLI, and Project API reference docs, and linked the Project API reference from the user, architecture, and developer manuals.
- Added tests that pin `Project` fields/methods to CLI commands, frontend operation ids, and inspection kinds.

## Verification

- `rtk uv run python -m py_compile src/paradev/sdk/project_api.py src/paradev/sdk/api.py src/paradev/sdk/__init__.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_project_api_table_lists_project_object_surface tests/test_architecture.py::test_sdk_api_table_lists_facade_exports tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_cli_api_table_lists_command_contract tests/test_cli.py::test_project_api_cli_outputs_table_json tests/test_cli.py::test_project_api_cli_outputs_reference_markdown tests/test_cli.py::test_project_api_cli_rejects_markdown_json_combo tests/test_cli.py::test_sdk_api_cli_outputs_table_json tests/test_cli.py::test_sdk_api_cli_outputs_reference_markdown tests/test_cli.py::test_cli_api_cli_outputs_table_json tests/test_cli.py::test_cli_api_cli_outputs_reference_markdown -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/project_api.py src/paradev/sdk/api.py src/paradev/sdk/__init__.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/project_api.py src/paradev/sdk/api.py src/paradev/sdk/__init__.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py`

## Notes

- Full-suite tests were skipped to keep CPU free for the parallel PIHC3 migration work.
- `gh pr status` reported no open PRs, so there were no review opinions to address in this pass.
