# Surface Contract Reference Progress

Date: 2026-06-14 23:00

Linear: TAL-299

## Done

- Added `render_surface_contract_reference_markdown()` for the static surface contract catalog.
- Exposed the generated table through `paradev architecture --surface-contracts-markdown`, plus JSON selectors for the summary and one exact surface contract.
- Added `docs/user-manual/surface-contract-reference.md` and linked it from the user manual.
- Updated architecture and developer docs so adapter-reference tables stay SDK-owned.

## Verification

- `rtk uv run python -m py_compile src/paradev/surfaces/__init__.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/__init__.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/surfaces/__init__.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_surface_contract_catalog_lists_static_boundaries tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_cli.py::test_architecture_cli_outputs_surface_contract_summary_json tests/test_cli.py::test_architecture_cli_outputs_one_surface_contract_json tests/test_cli.py::test_architecture_cli_outputs_surface_contract_reference_markdown tests/test_cli.py::test_architecture_cli_rejects_surface_contract_markdown_json_combo -q`
- `rtk bash -lc 'uv run paradev architecture --surface-contracts-markdown | diff -u docs/user-manual/surface-contract-reference.md -'`

## Risks Or Blockers

- Full-suite tests intentionally deferred to reduce CPU contention with concurrent PIHC3 migration workers.

## Next

- Continue moving adapter and API-reference tables onto generated SDK-owned contracts.
