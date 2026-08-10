# 2026-06-29 21:33 AI Chat Side Dock

## Summary

- Made the global AI chat window controlled by app state instead of local component-only state.
- Added persisted chat UI settings under `paradev.desktop.app-settings.v1` for open/closed state and dock mode.
- Added a side-docked chat mode that reserves a right-side shell column so the chat panel no longer covers workspace, config, or build controls.
- Added a header dock toggle with English and Chinese labels while preserving the compact floating launcher.
- Ran parallel read-only explorers for GUI usability, SDK/CLI/GUI alignment, and PIHC3 minimization. Follow-up candidates are SDK-owned module drafts and PIHC3 metadata diet.

## Verification

- Red checks first failed on missing `normalizeChatSettings`, missing side-dock class, and missing dock toggle.
- `rtk npm --prefix apps/desktop run test:unit -- --run src/components/FloatingChatShell.test.tsx src/components/AppShell.test.tsx src/App.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/i18n/locales.test.ts src/components/FloatingChatShell.test.tsx src/components/AppShell.test.tsx src/App.test.ts src/configPage/ConfigPage.test.tsx src/services/paradev.test.ts`
- `rtk npm --prefix apps/desktop run build`
- `rtk npm --prefix apps/desktop run test:unit -- --run`
- `rtk env PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 bash scripts/run.bash --tauri --port 5198`
- `rtk git diff --check`
- `rtk bash scripts/flake.bash --ci`

## Notes

- The Vite production build still reports the existing large-chunk warning.
- The Tauri smoke reached Vite ready, Rust compile completion, and `target/debug/paradev-desktop` launch, then the dev session was stopped manually.
