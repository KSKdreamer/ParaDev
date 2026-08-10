# C01 Mode Apply Source Progress

Date: 2026-06-21 12:26

Linear: TAL-000

## Done

- Made the full `C01_MAIN` diagram smoke item source-backed with `source_root`, `source_root_relative_path`, and a real `meta.yaml` source slot.
- Extended the source-backed focus smoke bridge to serve migrated PIHC3 focus-tree `meta.yaml` and `legacy/*/info.json` text sources, and to accept diagram source-edit apply payloads.
- Added C01 mode-switch coverage proving `FOCUS_C01_COZY_GLOW_CORONATION` relative-mode edits draft `legacy/C01_COZY_GLOW_CORONATION/info.json`.
- Added bridge coverage for two-edit applies so the smoke dataset records the source `info.json` edit instead of the first `meta.yaml` edit.

## Verification

- `rtk npm --prefix apps/desktop exec vitest run e2e/source-backed-focus-image-bridge.test.ts src/diagramEditor/sourceBackedSmokeModel.test.ts src/moduleEditor/sourceBackedDiagramApplySmokeModel.test.ts`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke: `http://127.0.0.1:5180/e2e/diagram-tab-smoke.html` opened `C01_MAIN` with `83/83` hydrated focus images, switched `FOCUS_C01_COZY_GLOW_CORONATION` to relative mode, reviewed, and applied; the bridge recorded `legacy/C01_COZY_GLOW_CORONATION/info.json` with `relative_position_id`.

## Risks Or Blockers

- The smoke apply still writes both `meta.yaml` and source `info.json` for this mode switch; this is useful for review coverage, but future cleanup may decide source-info-only is preferable for source-backed PIHC focus edits.

## Next

- Continue tightening the focus-tree editor interaction model around relative, pinned, and auto positioning for subtree moves.
