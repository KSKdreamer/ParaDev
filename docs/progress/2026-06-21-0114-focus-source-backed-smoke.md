# Focus Source Backed Smoke Progress

Date: 2026-06-21 01:14

Linear: TAL-000

## Done

- Added the `diagram-source-backed-smoke.html` Vite fixture that renders `C08_MAIN` from a PIHC3 project-browser payload instead of a hand-authored diagram document.
- The smoke page hydrates real migrated focus images from `src/modules/focus_asset_component/FOCUS_ASSET_COMPONENT_<FOCUS_ID>/preview.png` through a mocked Tauri binary-source bridge.
- Browser verification confirmed six compact HOI4-style focus icon nodes, 11 tree/dependency links, zero legacy/default image URLs, and zero focus icon placeholders.
- Fixed adapter normalization for PIHC3 focus ids with punctuation, such as `FOCUS_C12_PINK_ISN'T_FARM'S_COLOR`, so their canvas icons resolve to the sanitized migrated asset component folders.
- Added a PIHC3 migration contract test that maps all 738 compiled focus ids to existing migrated `preview.png` files, including the two apostrophe-bearing C12 ids.
- Documented the smoke fixture and its expected DOM dataset/image-size checks in `apps/desktop/e2e/README.md`.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/projectDiagram.test.ts -t "normalizes PIHC3 focus asset component ids"`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/projectDiagram.test.ts -t "larger PIHC3 source-backed"`
- `rtk bash scripts/test.bash tests/test_pihc3_migration_contracts.py -k focus_tree_preview_icons_resolve -q`
- `rtk bash scripts/test.bash tests/test_pihc3_migration_contracts.py -k "focus_asset_component or focus_tree_preview_icons_resolve" -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_pihc3_migration_contracts.py`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/projectDiagram.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/diagramImages.test.ts src/diagramEditor/layoutModel.test.ts src/styles/diagram.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/projectDiagram.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- PIHC3 preview coverage contract: `focus_count=738`, `missing_preview_count=0`.
- Browser smoke at `http://127.0.0.1:5180/e2e/diagram-source-backed-smoke.html`
- Browser metrics: `imageCount=6`, `focusNodeCount=6`, `placeholderCount=0`, `previewNodeCount=6`, `legacyNodeCount=0`, `imageReadCount=6`, `imageCacheWriteCount=6`, `maxImageWidth=34`, `maxImageHeight=34`, `bodyOverflowX=0`.

## Risks Or Blockers

- The browser smoke still uses a bounded C08 fixture; broader PIHC3 focus-tree coverage should come from a generated browser payload or SDK-backed e2e harness.

## Next

- Use the source-backed smoke route as the visual regression target for future focus-tree layout work.
