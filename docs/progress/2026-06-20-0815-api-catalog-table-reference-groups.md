# API Catalog Table Reference Groups Progress

Date: 2026-06-20 08:15

Linear: ongoing refactor goal

## Done

- Added `reference_groups` to the aggregate `ApiCatalogTable` payload so full SDK, CLI JSON, REST, and MCP selection consumers can read group titles, kinds, counts, ids, and usage without a separate helper call.
- Kept the existing group specs as the single source of truth and made `get_api_catalog_reference_groups()` return detached copies from the full table payload.
- Left generated Markdown unchanged; the existing API catalog reference equality assertion still covers the rendered page.

## Verification

- Red: `rtk uv run --extra dev --extra rest pytest -q tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_architecture.py::test_api_catalog_rest_route_outputs_table_reference_and_index_json tests/test_cli.py::test_api_catalog_cli_outputs_table_json` failed on missing `reference_groups`.
- Green: same targeted test command passed in `/tmp/paradev-api-catalog-table.QePMhB` (`3 passed`).
- Broader focused check: `rtk uv run --extra dev --extra rest pytest -q tests/test_architecture.py::test_surfaces_api_table_lists_surface_facade tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_architecture.py::test_api_catalog_rest_route_outputs_table_reference_and_index_json tests/test_cli.py::test_api_catalog_cli_outputs_table_json tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown tests/test_cli.py::test_surfaces_api_cli_outputs_table_json tests/test_cli.py::test_surfaces_api_cli_outputs_reference_markdown` passed in the clean checkout (`7 passed`).
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/api_catalog.py` passed.

## Risks Or Blockers

- Main worktree still has unrelated dirty docs, tests, desktop, skill, and PIHC3 migration files. This slice stages clean test blobs from the temporary checkout to avoid absorbing that work.
- Full-suite tests remain intentionally deferred to keep CPU free for concurrent PIHC3 migration workers.

## Next

- Continue lifting generated API catalog metadata into stable full-table payloads only when it reduces hand-filtering for SDK, REST, MCP, CLI, or GUI consumers.
