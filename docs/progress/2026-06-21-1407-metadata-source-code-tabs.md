# Metadata Source Code Tabs Progress

Date: 2026-06-21 14:07

Linear: TAL-000

## Done

- Changed module source-slot classification so `slot: meta` opens as a code source instead of being treated as localization just because `meta.yaml` has a YAML extension.
- Kept localization YAML behavior for actual localization slots such as `loc`.
- Updated model coverage for PIHC source-backed focus modules, project-local scaffold drafts, and SDK-applied source paths.

## Verification

- Red test first: `rtk npm --prefix apps/desktop exec vitest run src/moduleEditor/model.test.ts` failed because `meta.yaml` still produced `editorKind: "localization"`.
- `rtk npm --prefix apps/desktop exec vitest run src/moduleEditor/model.test.ts src/moduleEditor/ModuleEntityDetails.test.tsx src/moduleEditor/ModuleEditor.test.tsx`
- `rtk npm --prefix apps/desktop exec vitest run src/moduleEditor/model.test.ts src/moduleEditor/ModuleEntityDetails.test.tsx src/moduleEditor/ModuleEditor.test.tsx src/moduleEditor/diagramMetadata.test.ts src/moduleEditor/sourceBackedDiagramApplySmokeModel.test.ts src/moduleEditor/technologyDiagramApplySmokeModel.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/components/Workspace.test.tsx src/components/AppShell.test.tsx`
- `rtk npm --prefix apps/desktop run build`

## Risks Or Blockers

- This is a model/editor classification fix; no fresh browser smoke was run.
- The production build still emits the existing Vite large-chunk warning.
