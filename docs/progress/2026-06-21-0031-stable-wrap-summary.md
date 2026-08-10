# Stable Wrap Summary

Date: 2026-06-21 00:31

## Done

- Rechecked the public API catalog/manual surface before the final checkpoint. The generated catalog remains the maintained index across SDK, CLI, REST, MCP, LSP, desktop, and docs references.
- Confirmed the user manual already has bilingual generated-reference coverage guards for every API catalog `doc_page` and stale generated-reference links.
- Included the current focus-tree smoke fixture change as an evolving desktop/editor checkpoint: the smoke page now uses real PIHC3 focus preview assets, and Vite local dev can serve repository-root files needed by that fixture. The asset path details are recorded in [2026-06-21 Focus Preview Icons](2026-06-21-0032-focus-preview-icons.md).
- Kept the wrap-up away from PIHC3 migration content beyond reading fixture assets, so migration workers can keep moving independently.

## Verification

- Passed `rtk npm --prefix apps/desktop run build`.
- Passed `rtk npm --prefix apps/desktop run test:model` with 6 files and 160 tests.
- Passed `rtk uv run pytest tests/test_api_table_contracts.py::test_user_manual_index_lists_api_catalog_references tests/test_api_table_contracts.py::test_api_catalog_references_match_generated_manual_pages tests/test_api_catalog_selector_helpers.py -q`.
- Confirmed the nine PIHC3 preview PNG files imported by `apps/desktop/e2e/diagram-apply-review-smoke.tsx` exist.

## Risks Or Blockers

- The focus-tree editor is still evolving. This checkpoint treats the smoke fixture as current validation coverage, not a final editor contract.
- `apps/desktop/vite.config.ts` now allows local Vite dev access to the repository root so the smoke fixture can import PIHC3 preview assets. The server remains bound to `127.0.0.1`.

## Next

- Continue stabilizing focus-tree editor behavior with model/unit tests before broadening GUI guarantees.
- Keep new public SDK, CLI, REST, MCP, and GUI-facing APIs registered in the API catalog and linked from the manual index.
