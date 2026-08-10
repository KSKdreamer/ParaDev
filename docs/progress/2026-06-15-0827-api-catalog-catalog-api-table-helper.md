# API Catalog Catalog API Table Helper Progress

Date: 2026-06-15 08:27 CST

Linear: none

## Done

- Migrated the overall API catalog reference renderer to the shared API-table Markdown helpers.
- Migrated the HeavenBase catalog API reference renderer to the shared API-table Markdown helpers.
- Preserved generated API schemas, row ordering, manual reference output, CLI JSON output, and CLI Markdown output.

## Verification

- `rtk uv run black src/paradev/surfaces/api_catalog.py src/paradev/hb/__init__.py`
- `rtk uv run python -m py_compile src/paradev/surfaces/api_catalog.py src/paradev/hb/__init__.py`
- `rtk uv run pytest tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_architecture.py::test_catalog_api_table_lists_catalog_surfaces tests/test_cli.py::test_api_catalog_cli_outputs_table_json tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown tests/test_cli.py::test_catalog_api_cli_outputs_table_json tests/test_cli.py::test_catalog_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/api_catalog.py src/paradev/hb/__init__.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/surfaces/api_catalog.py src/paradev/hb/__init__.py`
- `rtk git diff --check -- src/paradev/surfaces/api_catalog.py src/paradev/hb/__init__.py`

## Risks Or Blockers

- Full-suite tests were intentionally not run to avoid competing with concurrent PIHC3 migration work.
- The worktree still contains unrelated Heaven-style skill, desktop app, PIHC3, logo, loader, and `node_modules/` changes from other workers.

## Next

- Continue migrating remaining generated-reference renderers with local Markdown helper copies.
- Keep avoiding build loader, HoI4 package internals, desktop app files, and PIHC3 progress files while those slices remain active elsewhere.
