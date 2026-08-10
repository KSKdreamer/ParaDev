# Surface Contract CLI Selector Progress

Date: 2026-06-20 01:42 +0800

Linear: none

## Done

- Routed CLI `architecture --surface-contracts` and `architecture --surface-contract <id>` through the shared SDK-owned `get_surface_contract_selection(...)` helper.
- Updated the static CLI contract so both surface-contract projections map to one selector adapter instead of separate summary and contract helpers.
- Regenerated `docs/user-manual/cli-api-reference.md`; the CLI API table still has 143 rows, and the adapter index now groups both surface-contract projections under `get_surface_contract_selection`.
- Updated architecture guidance to list SDK, CLI, REST, and MCP surface-contract selector paths together.

## Verification

- Red check before implementation: `rtk uv run pytest -q tests/test_cli.py::test_architecture_cli_outputs_one_surface_contract_json tests/test_cli.py::test_cli_api_cli_outputs_table_json tests/test_cli.py::test_cli_api_cli_outputs_reference_markdown tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_cli_api_table_lists_command_contract`
- Green focused check: same command, `5 passed`.
- `rtk uv run pytest -q tests/test_architecture.py tests/test_cli.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py`

## Risks Or Blockers

- Full suite intentionally not run to keep CPU usage down while PIHC3 migration work is active.
- Existing unrelated dirty worktree files remain untouched.

## Next

- Continue checking API-surface selector parity and generated reference tables before adding new surface-specific commands.
