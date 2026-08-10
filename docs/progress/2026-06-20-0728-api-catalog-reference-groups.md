# API Catalog Reference Groups

## Scope

- Added a generated reader group map to `render_api_catalog_reference_markdown()`.
- Kept `get_api_catalog_table()` and selector JSON payloads unchanged.
- Regenerated `docs/user-manual/api-catalog-reference.md` from a clean detached worktree so unrelated local edits did not affect catalog row counts.

## Result

- The API catalog now has an overall grouping section before the detailed indexes:
  - overall catalog
  - facade API tables
  - object and module tables
  - workflow contracts
  - callable surface API tables
  - adapter contracts

## Verification

- `rtk git diff --check`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/api_catalog.py`
- `rtk uv run --extra dev --extra rest pytest -q tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown tests/test_cli.py::test_api_catalog_cli_outputs_table_json`

## Waiver

- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_architecture.py tests/test_cli.py` still reports the pre-existing top-level `json` and `pathlib` imports in both broad test modules. This slice only added assertions inside those tests and did not expand that import surface.
