# 2026-06-20 20:18 Focus Source Parent Writeback

## Summary

- Added PIHC3 source-backed focus tree parent writeback coverage for reparenting and clearing visual parents.
- Updated focus parent metadata writes to prefer `settings.source_focuses[].focus_id` before falling back to compiled `settings.focuses[].id`.
- Verified the focus diagram smoke page renders and its zoom controls remain interactive after reload.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramMetadata.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramMetadata.test.ts src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts`
- `rtk npm --prefix apps/desktop run build`
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k focus_tree_importer_extracts_source_localization_and_image_metadata_contract`
- Browser QA: `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html`, default in-app browser viewport, no console errors or warnings, zoom `100% -> 150% -> 100%`.

## Notes

- Vite still reports the pre-existing large chunk warning for the production build.
