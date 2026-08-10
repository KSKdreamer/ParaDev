# API Catalog Selector Helpers Progress

Date: 2026-06-20 04:54 +0800

Linear: N/A

## Done

- Exposed `get_architecture_api_selection`, `get_project_api_selection`, `get_pdx_api_selection`, and `get_lsp_api_selection` through the top-level `paradev.sdk` facade.
- Filled `selector_helper` metadata for selectable API catalog rows so the overall catalog groups references by their shared selector API.
- Regenerated `docs/user-manual/sdk-api-reference.md` and `docs/user-manual/api-catalog-reference.md` from a clean index export to avoid including unrelated `MODULE_BATCH_EDIT_SCHEMA` work.

## Verification

- Red: `rtk uv run pytest -q tests/test_api_catalog_selector_helpers.py tests/test_sdk_api_selector_exports.py` failed on blank catalog selector metadata and missing SDK facade exports.
- Green: `rtk uv run pytest -q tests/test_api_catalog_selector_helpers.py tests/test_sdk_api_selector_exports.py` passed with 2 tests after the selector metadata and SDK exports were added.

## Risks Or Blockers

- The main worktree still contains unrelated `module-batch-edit` changes in SDK, CLI, Project, and generated references; this slice stages only selector-helper and clean generated-reference changes.
- Skipped the full suite to keep CPU free for concurrent PIHC2/PIHC3 migration work.

## Next

- Continue tightening generated reference parity once the module-batch slice lands or clears its dirty files.
