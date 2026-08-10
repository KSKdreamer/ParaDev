# Catalog API Reference Progress

Date: 2026-06-15 00:30 +0800

Linear: none

## Done

- Added a generated HeavenBase Catalog API table with stable `CatalogApiRow` / `CatalogApiTable` SDK contracts.
- Added `get_catalog_api_table()` and `render_catalog_api_reference_markdown()` to keep catalog SDK, CLI, REST, MCP, and completion seams in one maintained reference.
- Added CLI `paradev catalog-api --json/--markdown` and registered it in the static CLI surface contract.
- Generated `docs/user-manual/catalog-api-reference.md` and linked it from the user manual, Python SDK page, developer manual, and architecture interface contract.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_catalog_api_table_lists_catalog_surfaces tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_cli.py::test_catalog_api_cli_outputs_table_json tests/test_cli.py::test_catalog_api_cli_outputs_reference_markdown tests/test_cli.py::test_catalog_api_cli_rejects_markdown_json_combo tests/test_hb.py::test_hb_catalog_preview_cli_outputs_json tests/test_hb.py::test_hb_catalog_query_reads_written_sqlite_catalog -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/hb/__init__.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/hb/__init__.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk git diff --check`

## Risks Or Blockers

- Full Python suite was intentionally not run to avoid competing with concurrent PIHC3 migration work.
- The root worktree still contains unrelated desktop, PIHC3, loader, localization, logo, and skill changes from other workers.
- Root `node_modules/` remains untracked and must not be staged.

## Next

- Continue adding generated API tables for remaining stable SDK-owned surfaces where they reduce manual adapter lists.
- Keep catalog behavior changes separate from this documentation/reference contract slice.
