# 2026-06-20 19:17 - Focus Legacy Offset Writeback

## Summary

- Preserved the difference between PIHC legacy focus offsets and explicit `relative_position_id` offsets in diagram nodes.
- Kept the extra relative-position marker minimal: only legacy `parent` + `dx/dy` nodes carry `relativePositionKind: legacy_offset`.
- Updated diagram metadata drafts so moving a legacy focus writes `dx` and `dy` back to metadata instead of converting the node to `x/y` plus `relative_position_id`.
- Kept ordinary UI-created relative nodes on the existing compact default path so existing layout operations do not gain extra metadata fields.

## Validation

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/projectDiagram.test.ts src/diagramEditor/diagramJson.test.ts src/moduleEditor/diagramMetadata.test.ts`
- `rtk npm --prefix apps/desktop run test:model`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`

The Vite build still reports the existing large-chunk warning.
