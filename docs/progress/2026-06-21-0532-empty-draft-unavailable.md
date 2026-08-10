# Empty Draft Unavailable Progress

Date: 2026-06-21 05:32 +0800

Linear: TAL-000

## Done

- Changed diagram draft-row annotation so path-backed PIHC3 metadata rows are marked unavailable when draft generation returns no text.
- Added a regression for the apply plan produced from a dirty focus-tree row with no generated drafts; it now reports `draft-unavailable` instead of `no-changes`.
- Kept no-row handling unchanged, so empty dirty-row sets still remain empty.

## Verification

- Red check: `rtk npm --prefix apps/desktop run test:unit -- ModuleEditor.test.tsx -t "marks path-backed diagram apply rows unavailable"` failed because the plan returned `no-changes`.
- Green focused check: `rtk npm --prefix apps/desktop run test:unit -- ModuleEditor.test.tsx -t "marks path-backed diagram apply rows unavailable"`.
- Broader GUI apply checks: `rtk npm --prefix apps/desktop run test:unit -- ModuleEditor.test.tsx ProjectDiagramView.test.tsx diagramMetadata.test.ts`.
- Desktop build: `rtk npm --prefix apps/desktop run build`.

## Risks Or Blockers

- The production build still reports Vite's existing large-chunk warning, but TypeScript and bundling completed successfully.

## Next

- Continue tightening source-backed PIHC3 diagram review and apply behavior.
