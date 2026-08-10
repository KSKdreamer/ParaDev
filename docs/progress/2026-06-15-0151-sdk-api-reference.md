# SDK API Reference Progress

## Done

- Added `paradev.sdk.get_sdk_api_table()` and `paradev.sdk.render_sdk_api_reference_markdown()` as the generated audit surface for public `paradev.sdk` facade exports.
- Exposed CLI `paradev sdk-api` with JSON and Markdown output, and added it to the generated CLI command contract.
- Generated `docs/user-manual/sdk-api-reference.md` and regenerated `docs/user-manual/cli-api-reference.md`.
- Updated the SDK manual, user-manual index, developer manual, and architecture interface notes to route facade audits through the generated SDK table.

## Verification

- `rtk uv run python -m py_compile src/paradev/sdk/api.py src/paradev/sdk/__init__.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_sdk_api_table_lists_facade_exports tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_cli_api_table_lists_command_contract tests/test_cli.py::test_sdk_api_cli_outputs_table_json tests/test_cli.py::test_sdk_api_cli_outputs_reference_markdown tests/test_cli.py::test_sdk_api_cli_rejects_markdown_json_combo tests/test_cli.py::test_cli_api_cli_outputs_table_json tests/test_cli.py::test_cli_api_cli_outputs_reference_markdown -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/api.py src/paradev/sdk/__init__.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/api.py src/paradev/sdk/__init__.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py`

## Risks

- Full-suite tests were not run to preserve CPU for the parallel PIHC3 work.
- The table intentionally reflects the public `paradev.sdk.__all__` facade; deeper non-exported SDK internals remain out of scope for this reference.

## Next

- Continue reducing hand-maintained API lists by routing feature/module audits through generated SDK-owned tables.
