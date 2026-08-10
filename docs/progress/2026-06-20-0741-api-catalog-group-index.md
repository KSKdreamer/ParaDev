# API Catalog Group Index

## Scope

- Added a machine-readable `group_index` to `get_api_catalog_table()`.
- Exposed `group` through the existing `get_api_catalog_reference_ids(index_name, key)` and `get_api_catalog_selection(index_name, key)` selector path.
- Kept the change additive: existing reference, layer, feature, kind, owner module, surface, CLI command, selector helper, and doc page selectors remain unchanged.
- Regenerated the API Catalog and Surfaces API reference pages from a clean detached worktree.

## Result

- SDK, CLI, REST, and MCP-facing API catalog callers can use the existing `index_name/key` contract with `group` values:
  - `overall`
  - `facades`
  - `modules`
  - `workflows`
  - `surfaces`
  - `adapters`

## Verification

- `rtk git diff --check`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/api_catalog.py`
- `rtk uv run --extra dev --extra rest pytest -q tests/test_architecture.py::test_surfaces_api_table_lists_surface_facade tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_architecture.py::test_api_catalog_rest_route_outputs_table_reference_and_index_json tests/test_cli.py::test_api_catalog_cli_outputs_table_json tests/test_cli.py::test_api_catalog_cli_outputs_index_ids_json tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown`

## Waiver

- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_architecture.py tests/test_cli.py` still reports the pre-existing top-level `json` and `pathlib` imports in both broad test modules. This slice added assertions only and did not expand those imports.
