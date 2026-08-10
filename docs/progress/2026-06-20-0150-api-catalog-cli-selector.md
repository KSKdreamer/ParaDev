# API Catalog CLI Selector Progress

Date: 2026-06-20 01:50 +0800

Linear: none

## Done

- Consolidated CLI `api-catalog`, `api-catalog --reference`, and `api-catalog --index --key` static contract rows onto `get_api_catalog_selection(...)`, matching the runtime selector path.
- Regenerated the CLI API reference; CLI API row count stays 143 while the distinct adapter count drops from 132 to 130.
- Updated the architecture guide to list SDK, CLI, REST, and MCP API catalog selector paths together.
- Strengthened CLI API tests to lock the adapter index and rendered table snippets for the selector-backed projections.

## Verification

- Red check before source edit: `rtk uv run pytest -q tests/test_cli.py::test_cli_api_cli_outputs_table_json tests/test_cli.py::test_cli_api_cli_outputs_reference_markdown tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_cli_api_table_lists_command_contract`
- Focused check after doc regeneration: `rtk uv run pytest -q tests/test_cli.py::test_cli_api_cli_outputs_table_json tests/test_cli.py::test_cli_api_cli_outputs_reference_markdown tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_cli_api_table_lists_command_contract` passed, 4 tests.
- Affected modules: `rtk uv run pytest -q tests/test_architecture.py tests/test_cli.py` passed, 222 tests.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py` passed.
- Path-scoped lint: `rtk bash scripts/flake.bash --ci --paths src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py` passed.

## Risks Or Blockers

- Full suite intentionally not run in this slice to avoid unnecessary CPU load while other workers continue PIHC2 to PIHC3 migration work.
- The repository still contains unrelated dirty PIHC3, desktop, and skill-guide changes; this slice leaves them untouched.

## Next

- Continue checking generated API table parity where CLI projections already share runtime selector helpers but still advertise split static adapters.
