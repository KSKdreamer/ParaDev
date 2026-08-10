# 2026-06-30 20:25 - Config path status errors

## Slice

Made Config page project-path status failures visible instead of leaving rows stuck on `Checking` when the desktop SDK path-status call rejects. The app now keeps a separate localized error map, passes it through `AppShell` and `Workspace`, renders a `Failed` status chip with the bridge error detail, and disables the matching open-path action.

## Red

- `rtk npm --prefix apps/desktop run test:unit -- --run src/configPage/ConfigPage.test.tsx src/App.test.ts -t "path status"` failed with the Config page still rendering `Checking` and `App.tsx` still filtering rejected path-status calls to `null`.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- --run src/configPage/ConfigPage.test.tsx src/App.test.ts -t "path status"`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/configPage/ConfigPage.test.tsx src/components/AppShell.test.tsx src/components/Workspace.test.tsx src/i18n/locales.test.ts src/App.test.ts`
- `rtk npm --prefix apps/desktop run build`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 47840`

## Notes

- Full desktop unit suite passed with `759 passed`.
- Fast repo gate passed with `1235 passed, 2 warnings`.
- PIHC3 Tauri smoke reached `Running target/debug/paradev-desktop` and was stopped manually. The app still logs the existing AI profile load warning for the PIHC3 project root; that remains a separate usability follow-up.
- PIHC3 currently has unrelated state-temperature edits in its working tree; this slice left them unstaged.
