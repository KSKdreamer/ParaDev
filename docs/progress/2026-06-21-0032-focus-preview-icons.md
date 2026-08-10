# 2026-06-21 00:32 - Focus Preview Icons

## Context

The focus editor now renders HOI4-style square focus nodes, but the image path was still weak: PIHC3 focus asset components preserve compiled DDS icons, and browsers cannot display DDS files in SVG `<image>` nodes. The e2e smoke page also returned synthetic PNG bytes, so it could pass without proving actual PIHC icons were visible.

## Changes

- Added `preview.png` generation to the PIHC3 focus asset component importer.
- Implemented dependency-free DDS preview decoding for the PIHC focus icon formats in the migration script:
  - ARGB8888, used by 738 compiled focus icons.
  - DXT5, used by the `goal_unknown` fallback icon.
- Re-ran the importer, generating 739 `preview.png` files under `projects/PIHC3/src/modules/focus_asset_component/`.
- Added `preview_image_path` and `preview_image_source` metadata to focus asset component `meta.yaml` files.
- Updated focus diagram image fallback to point at `src/modules/focus_asset_component/<component>/preview.png` instead of a browser-undecodable DDS path.
- Updated the diagram image loader to resolve project-relative image paths against `projectRoot` before calling the Tauri binary source bridge.
- Reduced rendered focus icon size from 46px to 40px inside a 3x3 / 24px-grid focus tile, keeping the icon below a 2x2 grid-cell footprint.
- Replaced the fabricated C08 smoke nodes with real C08_PARTIV focus ids and real imported PIHC3 preview PNG assets.

## Verification

- Red checks:
  - `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/projectDiagram.test.ts src/diagramEditor/diagramImages.test.ts src/diagramEditor/ProjectDiagramView.test.tsx` failed on DDS paths, relative loader paths, and 46px focus icon geometry.
  - `rtk uv run pytest tests/test_pihc3_migration_contracts.py -k focus_asset_component -q` failed because generated focus asset modules had no `preview.png` metadata or files.
- Focused green:
  - `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/projectDiagram.test.ts src/diagramEditor/diagramImages.test.ts src/diagramEditor/ProjectDiagramView.test.tsx`
  - `rtk uv run pytest tests/test_pihc3_migration_contracts.py -k focus_asset_component -q`
- Migration:
  - `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_focus_asset_components.py`
  - Generated 739 preview PNGs.
  - `file` confirmed `FOCUS_C08_SECOND_SUMMIT/preview.png` is a 128 x 128 RGBA PNG and `FOCUS_ASSET_COMPONENT_GOAL_UNKNOWN/preview.png` is a 104 x 104 RGBA PNG.
- Broader checks:
  - `rtk npm --prefix apps/desktop run test:unit`
  - `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_focus_asset_components.py tests/test_pihc3_migration_contracts.py`
  - `rtk npm --prefix apps/desktop run build`
- Browser QA at `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html`:
  - Rendered 9 focus image elements from PIHC3 `preview.png` assets.
  - Every focus image rendered at 40 x 40, below the 48 x 48 size of 2 x 2 grid cells.
  - Placeholder count was 0.
  - Console warning/error count was 0.
  - Normal-window horizontal overflow was 0.

## Next

- Wire the normal module-backed focus tab to the same preview path for large PIHC trees and add an app-level smoke check against a real project browser payload.
- Continue visual polish on HOI4 route-line styling and denser viewport fitting for large national focus trees.
