# Config Key Smoke Hardening Progress

Date: 2026-06-30 11:06 CST
Linear: active usability goal

## Done

- Fixed `config-page-smoke.html` so it detects SDK-backed config controls through `data-paradev-config-key` instead of scanning visible body text.
- Fixed smoke dataset value reads for `paradev.cli.output` and `paradev.build.parallelism` so they come from the same machine-readable config-key controls.
- Added smoke-state helpers and tests for config-key presence and value reads.
- Added a table-driven ConfigPage rendered test that maps every generated desktop config-value bridge key to the tab where it must render.

## Verification

- Red first: `rtk npm --prefix apps/desktop run test:unit -- e2e/config-page-smoke-state.test.ts` failed when `configPageSmokeHasConfigKey` was missing.
- Red first: `rtk npm --prefix apps/desktop run test:unit -- e2e/config-page-smoke-state.test.ts` failed when `configPageSmokeConfigValue` was missing.
- Focused smoke-state unit test: `rtk npm --prefix apps/desktop run test:unit -- e2e/config-page-smoke-state.test.ts` passed, 3 tests.
- Focused config-page unit test: `rtk npm --prefix apps/desktop run test:unit -- src/configPage/ConfigPage.test.tsx` passed, 41 tests.
- Desktop unit suite: `rtk npm --prefix apps/desktop run test:unit` passed, 713 tests.
- Desktop production build: `rtk npm --prefix apps/desktop run build` passed with the existing Vite large-chunk warning.
- Rendered browser smoke: `config-page-smoke.html` loaded from `http://127.0.0.1:5180/e2e/config-page-smoke.html`; General reported `data-paradev-config-page-smoke-has-cli-output-key="1"` and `data-paradev-config-page-smoke-cli-output-value="json"` from one `paradev.cli.output` control, Projects reported `data-paradev-config-page-smoke-has-build-parallelism-key="1"` and `data-paradev-config-page-smoke-build-parallelism-value="4"` from one `paradev.build.parallelism` control, and browser console warnings/errors were empty.
- Flake gate: `rtk bash scripts/flake.bash --ci` passed.
- Fast repo gate: `rtk bash scripts/test.bash` passed, 1228 tests with 1 warning.
- Native PIHC3 smoke: `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 5206` built and launched the Tauri dev app, then was manually stopped after stable startup with no runtime errors.

## Risks Or Blockers

- This hardens the existing Vite-rendered smoke fixture; it still does not prove bridge-backed `CM_PARADEV` persistence in a rendered app.
- The native Tauri smoke remains startup-level for this slice.

## Next

- Add a bridge-backed `--native-web` rendered PIHC3 smoke with an isolated `PARADEV_ROOT` that toggles an AI profile source, saves through the real desktop bridge, reloads, verifies persisted `paradev.ai.chat.profiles`, and resets afterward.
