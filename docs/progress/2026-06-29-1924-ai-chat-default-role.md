# AI Chat Default Role Progress

Date: 2026-06-29 19:24

Linear: none

## Done

- Wired the SDK-owned AI chat `defaultRole` from `AppShell` into the floating chat shell.
- Updated the floating chat role initialization so a non-first SDK default role is selected when the panel opens.
- Kept manual role choice stable across profile refreshes, while still following an actual SDK default-role change.
- Added a regression proving the Build/debug role can be the initial selected task and that its project plus diagnostics context sources are selected by default.
- Asked a read-only explorer subagent to inspect AI profile API/CLI/GUI alignment; it identified source-kind toggles and direct CLI profile commands as follow-up slices.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- --run src/components/FloatingChatShell.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/components/FloatingChatShell.test.tsx src/components/AppShell.test.tsx src/components/Workspace.test.tsx src/configPage/ConfigPage.test.tsx src/services/paradev.test.ts`
- `rtk npm --prefix apps/desktop run build`
- `rtk git diff --check`
- `rtk env PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 bash scripts/run.bash --tauri --port 5206`

## Notes

- The Vite production build still reports the existing large-chunk warning.
- `projects/PIHC3` stayed clean after the native Tauri smoke run.
- Unrelated local work on PIHC3 building-icon contracts was present and intentionally left unstaged.
