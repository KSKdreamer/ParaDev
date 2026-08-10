# Diagram Apply Preview Title Progress

Date: 2026-06-20 18:07

Linear: TAL-000

## Done

- Added a title tooltip to the mixed diagram Apply preview so PIHC3 users can inspect which metadata drafts will write and which will be skipped.
- Kept the compact action-bar preview as `Will write {writable} · Skip {skipped}` while the title lists concrete rows, for example `Write focus_tree:C08_PARTIV src/modules/focus_tree/C08_PARTIV/meta.yaml; Skip focus_tree:C09_CANTERLOT Canterlot`.
- Localized the title row prefixes in English and Chinese.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx` failed before implementation because the preview had no `title`.
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor src/moduleEditor/diagramMetadata.test.ts src/moduleEditor/diagramSelection.test.ts src/moduleEditor/ModuleEditor.test.tsx src/moduleEditor/model.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke at `http://127.0.0.1:5173/`: app loaded with title `ParaDev`, the `科技` module click selected the Technology tab, no framework overlay appeared, and console warn/error logs were empty.

## Risks Or Blockers

- Plain Vite still shows `SDK browser unavailable`; SDK-backed project browser data needs the Tauri shell.
- The build still reports the existing Vite large-chunk warning.

## Next

- Consider promoting the preview title into a richer confirmation/review surface before applying metadata writes.
