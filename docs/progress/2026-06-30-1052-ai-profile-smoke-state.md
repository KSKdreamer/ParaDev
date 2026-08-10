# AI Profile Smoke State Progress

Date: 2026-06-30 10:52 CST
Linear: active usability goal

## Done

- Added stable rendered-state attributes for Config > Models AI chat profile source toggles:
  - `data-paradev-ai-profile-source-kinds` on the source list.
  - `data-paradev-ai-profile-source-selected` on each profile/source checkbox.
- Extended `config-page-smoke.html` to use generated SDK AI chat profiles and source kinds instead of an empty local profile list.
- Extended the config smoke dataset with source-kind order, `Explain HoI4 code` selected sources, template toggle state, toggle count, and local save payload fields.
- Updated the config smoke README with the Models source-toggle flow.

## Verification

- Red first: `rtk npm --prefix apps/desktop run test:unit -- src/configPage/ConfigPage.test.tsx -t "AI chat profile context sources"` failed on the missing source-kind dataset attribute.
- Red first: `rtk npm --prefix apps/desktop run test:unit -- e2e/config-page-smoke-state.test.ts` failed on the missing AI profile smoke dataset fields.
- Focused config-page unit test: `rtk npm --prefix apps/desktop run test:unit -- src/configPage/ConfigPage.test.tsx` passed, 40 tests.
- Focused smoke-state unit test: `rtk npm --prefix apps/desktop run test:unit -- e2e/config-page-smoke-state.test.ts` passed.
- Desktop unit suite: `rtk npm --prefix apps/desktop run test:unit` passed, 710 tests.
- Desktop production build: `rtk npm --prefix apps/desktop run build` passed with the existing Vite large-chunk warning.
- Rendered browser smoke: `config-page-smoke.html` loaded from `http://127.0.0.1:5180/e2e/config-page-smoke.html`; Models rendered four generated AI profiles, exposed `project,selection,diagnostics,templates`, toggled `Explain HoI4 code` Templates on, enabled Save, and recorded `explain` plus `project,selection,templates` in the local smoke dataset with no console warnings or errors.
- Flake gate: `rtk bash scripts/flake.bash --ci` passed.
- Fast repo gate: `rtk bash scripts/test.bash` passed, 1228 tests with 1 warning.
- Native PIHC3 smoke: `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 5205` built and launched the Tauri dev app, then was manually stopped after stable startup with no runtime errors.

## Risks Or Blockers

- The rendered source-toggle interaction currently runs through the Vite smoke fixture, while the native Tauri check remains startup-level.
- The smoke fixture records local save payloads only; it intentionally does not mutate `CM_PARADEV`.

## Next

- Add a native-window interaction smoke for the Models AI profile panel once the Tauri inspection path is stable enough to query the same `data-paradev-*` state.
- Continue checking config-page coverage for remaining `CM_PARADEV` keys that should be user-editable.
