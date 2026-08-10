# AI Chat Profile Sources Progress

Date: 2026-06-29 17:27

Linear: N/A

## Done

- Made the floating AI chat default its checked context sources from the selected SDK-backed chat profile `sourceKinds`.
- Mapped profile source kinds to the frontend context kinds used by the shell: `project` selects workspace context, `selection` selects source context, and direct kinds such as `diagnostics` stay direct.
- Updated role changes so switching profiles immediately reapplies that profile's default context sources.

## Verification

- Red check before implementation: `rtk npm --prefix apps/desktop run test:unit -- --run src/components/FloatingChatShell.test.tsx` failed because diagnostics was checked for the default chat profile.
- Green focused check: `rtk npm --prefix apps/desktop run test:unit -- --run src/components/FloatingChatShell.test.tsx`.
- Adjacent GUI/API checks: `rtk npm --prefix apps/desktop run test:unit -- --run src/components/FloatingChatShell.test.tsx src/App.test.ts src/services/paradev.test.ts src/configPage/ConfigPage.test.tsx src/aiChatProfileText.test.ts`.
- Production frontend build: `rtk npm --prefix apps/desktop run build`.
- Native GUI smoke: `PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 rtk bash scripts/run.bash --tauri --port 5191` launched `target/debug/paradev-desktop` with no terminal-side startup errors before manual stop.

## Risks Or Blockers

- Config and AI profile persistence failures still only warn in the console; a visible localized save/error state remains a separate GUI usability slice.

## Next

- Add user-visible config/profile save states on the Config page.
- Translate the remaining boot progress accessibility label in the desktop shell.
