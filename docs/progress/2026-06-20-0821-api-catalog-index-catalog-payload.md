# API Catalog Index Catalog Payload Progress

Date: 2026-06-20 08:21

Linear: ongoing refactor goal

## Done

- Added `index_catalog` to the aggregate `ApiCatalogTable` payload so full SDK, CLI JSON, REST, and MCP selection consumers can discover supported lookup dimensions from the same table JSON.
- Kept `API_CATALOG_INDEX_CATALOG` as the source of truth and made `get_api_catalog_index_catalog()` return detached copies from the full table payload.
- Routed the generated Markdown index-catalog section through the table payload; rendered API catalog Markdown stayed unchanged.

## Verification

- Red: `rtk uv run --extra dev --extra rest pytest -q tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_architecture.py::test_api_catalog_rest_route_outputs_table_reference_and_index_json tests/test_cli.py::test_api_catalog_cli_outputs_table_json` failed on missing `index_catalog`.
- Green: same targeted command passed in `/tmp/paradev-api-catalog-index-catalog.R8P8o2` (`3 passed`).
- Broader focused check: `rtk uv run --extra dev --extra rest pytest -q tests/test_architecture.py::test_surfaces_api_table_lists_surface_facade tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_architecture.py::test_api_catalog_rest_route_outputs_table_reference_and_index_json tests/test_cli.py::test_api_catalog_cli_outputs_table_json tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown tests/test_cli.py::test_surfaces_api_cli_outputs_table_json tests/test_cli.py::test_surfaces_api_cli_outputs_reference_markdown` passed in the clean checkout (`7 passed`).
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/api_catalog.py` passed.

## Risks Or Blockers

- Main worktree still has unrelated dirty docs, tests, desktop, skill, and PIHC3 migration files. This slice stages clean test blobs from the temporary checkout.
- Full-suite tests remain intentionally deferred to keep CPU free for concurrent PIHC3 migration workers.

## Next

- Continue making full API table payloads self-describing where it reduces separate helper calls for SDK, REST, MCP, CLI, or GUI consumers.
