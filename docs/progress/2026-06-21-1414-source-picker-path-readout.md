# Source Picker Path Readout Progress

Date: 2026-06-21 14:14

Linear: TAL-000

## Done

- Added a compact selected-source path readout next to the large source-file picker.
- The readout uses the source `relative_path` when available and truncates with a tooltip, so source-backed PIHC focus files remain identifiable without opening the dropdown.
- Kept small modules on the existing button-tab UI.

## Verification

- Red test first: `rtk npm --prefix apps/desktop exec vitest run src/moduleEditor/ModuleEntityDetails.test.tsx` failed because the large source picker did not render the active source path.
- `rtk npm --prefix apps/desktop exec vitest run src/moduleEditor/ModuleEntityDetails.test.tsx`
- `rtk npm --prefix apps/desktop exec vitest run src/moduleEditor/ModuleEntityDetails.test.tsx src/moduleEditor/ModuleEditor.test.tsx src/moduleEditor/model.test.ts src/components/Workspace.test.tsx src/components/AppShell.test.tsx src/styles/diagram.test.ts src/App.test.ts`
- `rtk npm --prefix apps/desktop run build`

## Risks Or Blockers

- No fresh browser smoke was run for this UI-only slice.
- The production build still emits the existing Vite large-chunk warning.
