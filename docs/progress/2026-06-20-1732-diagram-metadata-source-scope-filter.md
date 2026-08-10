# Diagram Metadata Source Scope Filter Progress

Date: 2026-06-20 17:32

Linear: TAL-000

## Done

- Added metadata-level filtering for dependency and reference edge grouping so stale diagram documents cannot persist relationships across source scopes.
- Covered stale non-focus cross-family dependencies and stale foreign focus-tree dependency/reference edges as PIHC3 migration cases.
- Kept the fix local to metadata edge collection; editor actions and JSON import guards continue to enforce the same relationship scope earlier in the flow.

## Verification

- Red check: `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramMetadata.test.ts` failed on the two new stale cross-scope tests before the implementation.
- `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramMetadata.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramJsonImport.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/diagramMetadata.test.ts src/moduleEditor/diagramSelection.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke at `http://127.0.0.1:5173/`: app loaded, `科技` tab selected, no framework overlay, no warn/error console logs.

## Risks Or Blockers

- Plain Vite still shows the expected `SDK browser unavailable` placeholder because live SDK project data is provided by the Tauri shell.
- The production build still emits the existing Vite large chunk warning.

## Next

- Continue tightening PIHC3 diagram save/import boundaries and then move back up to user-facing focus/technology tree editing workflows.
