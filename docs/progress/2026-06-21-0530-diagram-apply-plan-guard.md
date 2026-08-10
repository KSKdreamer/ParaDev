# Diagram Apply Plan Guard Progress

Date: 2026-06-21 05:30 +0800

Linear: TAL-000

## Done

- Added a pure diagram apply-plan helper that reconciles changed review rows, generated PIHC3 metadata drafts, and source text edits before any desktop write.
- Hardened the diagram Apply handler to refresh the generated draft rows at apply time and block with the existing unavailable-draft message when any changed row cannot be generated.
- Added a regression for a PIHC3 focus-tree edit where a writable `meta.yaml` draft exists but a changed `legacy/<focus>/info.json` row is unavailable, preventing partial writes.

## Verification

- Red check: `rtk npm --prefix apps/desktop run test:unit -- ModuleEditor.test.tsx -t "blocks diagram apply plans"` failed because `buildDiagramApplyDraftPlan` was undefined.
- Green focused check: `rtk npm --prefix apps/desktop run test:unit -- ModuleEditor.test.tsx -t "blocks diagram apply plans"`.
- Broader GUI apply checks: `rtk npm --prefix apps/desktop run test:unit -- ModuleEditor.test.tsx ProjectDiagramView.test.tsx diagramMetadata.test.ts`.
- Desktop build: `rtk npm --prefix apps/desktop run build`.

## Risks Or Blockers

- The production build still reports Vite's existing large-chunk warning, but TypeScript and bundling completed successfully.

## Next

- Continue tightening PIHC3 source-backed diagram apply behavior and rendered focus-tree ergonomics.
