# AI Chat Source Kind Localization Progress

Date: 2026-06-30 15:14

Linear: TAL-000

## Done

- Confirmed the current config page already exposes the important `CM_PARADEV` desktop config keys through bridge-backed controls.
- Localized known SDK-provided AI chat source kind rows when runtime rows omit a `labelKey`, including `project-index` and `scripted-gui`.
- Applied the same source-kind label resolver to floating chat context chips and config-page AI chat profile source toggles.
- Added focused source-kind label tests that preserve custom SDK labels while avoiding raw internal IDs in localized UI.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/aiChatSourceKindText.test.ts src/configPage/ConfigPage.test.tsx src/components/FloatingChatShell.test.tsx src/i18n/locales.test.ts`
- `rtk npm --prefix apps/desktop run build`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 1431`

## Risks Or Blockers

- The config page still lacks event-level interaction tests proving each visible config control flows through `onSettingsChange` to the desktop config-value write bridge.

## Next

- Add a small config interaction persistence test slice for all generated desktop config keys.
