# 2026-06-15 02:25 Build API Reference

## Done

- Added `paradev.build.get_build_api_table()` and `render_build_api_reference_markdown()` for the public build facade.
- Added CLI `paradev build-api` with JSON output and `--markdown` reference generation.
- Regenerated the new Build API reference and the CLI API reference so `build-api` is included in command audits.
- Linked the build facade reference from the user manual, build guide, SDK guide, architecture boundary, and developer manual.

## Verification

- `rtk uv run python -m py_compile src/paradev/build/api.py src/paradev/build/__init__.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_build_api_table_lists_public_build_facade tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_cli_api_table_lists_command_contract tests/test_cli.py::test_build_api_cli_outputs_table_json tests/test_cli.py::test_build_api_cli_outputs_reference_markdown tests/test_cli.py::test_build_api_cli_rejects_markdown_json_combo tests/test_cli.py::test_cli_api_cli_outputs_table_json tests/test_cli.py::test_cli_api_cli_outputs_reference_markdown -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/build/api.py src/paradev/build/__init__.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/build/api.py src/paradev/build/__init__.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py`

## Notes

- Full-suite tests were skipped to keep CPU free for the parallel PIHC3 migration work.
- `gh pr status` reported no open PRs, so there were no review opinions to address in this pass.
