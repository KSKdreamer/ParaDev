# Config Profile Badges I18n Progress

Date: 2026-06-29 18:41

Linear: N/A

## Done

- Replaced visible AI chat profile id badges on the config Models page with translated profile labels.
- Kept internal profile ids for React keys, prompt data attributes, and SDK-backed save/reset calls.
- Added a regression test proving the Chinese config page shows `聊天 · 默认` and `说明 HOI4 代码` instead of `chat · 默认` and `explain`.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- --run src/configPage/ConfigPage.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/configPage/ConfigPage.test.tsx src/components/FloatingChatShell.test.tsx`
- `rtk npm --prefix apps/desktop run build`
- `rtk git diff --check`
- `PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 rtk bash scripts/run.bash --tauri --port 5200`

## Risks Or Blockers

- Backend LLM test detail and persistence error text can still surface raw bridge messages; those need a separate status/error normalization slice.

## Next

- Continue removing raw config keys and backend English from visible config-page helper text.
