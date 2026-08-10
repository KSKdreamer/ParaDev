# 2026-07-01 03:50 - Config project root display

## Slice

Made Config > Projects show the active local project root as the row value instead of showing the internal project id beside the path status and open action. This keeps the visible value aligned with the path the button opens, which is clearer for PIHC3 modders working from local folders.

## Red

- `rtk npm --prefix apps/desktop run test:unit -- --run src/configPage/ConfigPage.test.tsx -t "Projects tab root row"` failed because the Projects root row rendered `<code>minimal_hoi4</code>` while the open action targeted `/tmp/minimal`.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- --run src/configPage/ConfigPage.test.tsx -t "Projects tab root row"`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/configPage/ConfigPage.test.tsx src/i18n/locales.test.ts -t "Projects tab root row|locale dictionaries"`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/configPage/ConfigPage.test.tsx src/i18n/locales.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/App.test.ts -t "config page settings|desktop config|Config"`
- `rtk npm --prefix apps/desktop run build`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 47840`

## Notes

- Desktop unit suite passed with `760 passed`.
- Fast repo gate passed with `1235 passed, 290 warnings`.
- PIHC3 Tauri smoke reached `Running target/debug/paradev-desktop` and showed no startup warnings during the smoke window.
- Read-only subagents found no missing current desktop config bridge key in the Config page. Follow-up candidates: make `paradev.ai.preset` actually drive AI route resolution, and add rendered smoke coverage for Config Models -> floating chat send.
