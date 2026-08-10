# Diagram Source Scope Guards Progress

Date: 2026-06-20 17:24

Linear: TAL-000

## Done

- Added a shared diagram relationship source-scope helper for embedded focus items and source-backed module nodes.
- Reused the helper in GUI candidate filtering, layout model edits, and JSON import compatibility.
- Rejected cross-scope child insertion, tree parent changes, dependency/reference edges, and imported tree/relationship edges.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/layoutModel.test.ts src/diagramEditor/diagramJsonImport.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramJsonImport.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/diagramMetadata.test.ts src/moduleEditor/diagramSelection.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke at `http://127.0.0.1:5173/`: app loaded, `科技` tab selected, no framework overlay, no warn/error console logs.

## Risks Or Blockers

- Plain Vite still shows the expected `SDK browser unavailable` placeholder because live SDK data requires the Tauri desktop shell.
- The source-scope helper intentionally keeps payload-less generic diagrams in one fallback scope for existing generic tests and demos.

## Next

- Continue reviewing diagram import and metadata persistence paths for stale edge cases that can surface during PIHC3 focus/technology migration.
