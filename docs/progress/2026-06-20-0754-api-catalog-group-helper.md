# API Catalog Group Helper Progress

Date: 2026-06-20 07:54

Linear: not updated

## Done

- Added `get_api_catalog_group_reference_ids(group)` as the first-class SDK-facing helper for reader-oriented API catalog groups.
- Updated the API catalog index catalog so the `group` row documents the dedicated helper instead of the generic index lookup.
- Regenerated `docs/user-manual/api-catalog-reference.md` and `docs/user-manual/surfaces-api-reference.md`.
- Kept the slice away from PIHC3 migration paths and staged test updates from a clean checkout.

## Verification

- `rtk git diff --check` passed in `/tmp/paradev-api-catalog-group-helper-verify`.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/api_catalog.py src/paradev/surfaces/__init__.py src/paradev/surfaces/api.py` passed.
- `rtk uv run --extra dev --extra rest pytest -q tests/test_architecture.py::test_surfaces_api_table_lists_surface_facade tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_architecture.py::test_api_catalog_helpers_reject_unknown_keys tests/test_architecture.py::test_api_catalog_rest_route_outputs_table_reference_and_index_json tests/test_cli.py::test_api_catalog_cli_outputs_table_json tests/test_cli.py::test_api_catalog_cli_outputs_index_ids_json tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown tests/test_cli.py::test_surfaces_api_cli_outputs_table_json tests/test_cli.py::test_surfaces_api_cli_outputs_reference_markdown` passed in a clean detached worktree.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_architecture.py tests/test_cli.py` still reports the pre-existing top-level `json` and `pathlib` imports in those broad test files.

## Risks Or Blockers

- Full suite intentionally not run to avoid CPU churn while parallel PIHC3 work is active.
- Main worktree still contains unrelated dirty files from other workers; test updates were prepared in `/tmp/paradev-api-catalog-group-helper`.

## Next

- Continue turning generic selector/index projections into small documented helpers only where they reduce caller guesswork.
