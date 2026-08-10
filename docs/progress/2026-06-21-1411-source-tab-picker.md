# Source Tab Picker Progress

Date: 2026-06-21 14:11

Linear: TAL-000

## Done

- Added a compact source-file selector for module editor entities with more than ten editable source tabs.
- Kept the existing button tabs for smaller modules, so common `Info / def / loc / Image` workflows stay quick.
- Covered source-backed focus-tree modules with many generated `focus:<id>:info` slots, selecting the requested `legacy/<focus>/info.json` source without rendering dozens of tab buttons.
- Added localized source-file labels for English and Chinese.

## Verification

- Red test first: `rtk npm --prefix apps/desktop exec vitest run src/moduleEditor/ModuleEntityDetails.test.tsx` failed because the large source-backed focus entity still rendered every source as a button.
- `rtk npm --prefix apps/desktop exec vitest run src/moduleEditor/ModuleEntityDetails.test.tsx`
- `rtk npm --prefix apps/desktop exec vitest run src/moduleEditor/ModuleEntityDetails.test.tsx src/moduleEditor/ModuleEditor.test.tsx src/moduleEditor/model.test.ts src/components/Workspace.test.tsx src/components/AppShell.test.tsx src/styles/diagram.test.ts src/App.test.ts`
- `rtk npm --prefix apps/desktop run build`

## Risks Or Blockers

- No fresh browser gesture smoke was run for this UI-only slice.
- The production build still emits the existing Vite large-chunk warning.
