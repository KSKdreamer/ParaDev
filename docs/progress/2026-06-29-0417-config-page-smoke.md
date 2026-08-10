# Config Page Smoke Fixture

Time: 2026-06-29 04:17 CST

Continued the GUI usability/API-alignment loop by adding a rendered Settings smoke fixture for the desktop shell path.

- Added `config-page-smoke.html` / `config-page-smoke.tsx`, mounting the real `AppShell` with PIHC3-shaped project state.
- The smoke starts on the normal Projects rail, clicks into Config, verifies the Configuration side panel, and records stable dataset fields for `paradev.cli.output` and `paradev.build.parallelism`.
- Added `config-page-smoke-state.ts` plus a focused unit test for the dataset writer.
- Documented the fixture and expected browser assertions in `apps/desktop/e2e/README.md`.

Subagent notes:

- One audit confirmed the smallest useful fixture should mount `AppShell` directly and use real `configOptions`.
- A second audit pushed the smoke toward a user-perspective flow: start outside Settings, click the Config rail button, then verify General and Project config controls rather than duplicating every ConfigPage unit assertion.

Validation:

- Browser fixture flow at `http://127.0.0.1:5183/e2e/config-page-smoke.html`: correct URL/title, nonblank shell, no framework overlay, no console warnings/errors, clicked `Config`, verified `Configuration panel`, `paradev.cli.output = json`, clicked `Projects`, verified `paradev.build.parallelism = 4` with `min="1"`, and captured screenshot evidence.
- `PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 rtk bash scripts/run.bash --tauri`: compiled and launched `target/debug/paradev-desktop` with no startup error or late startup logs before shutdown.
- `rtk npm --prefix apps/desktop run test:unit -- e2e/config-page-smoke-state.test.ts`: 1 passed.
- `rtk npm --prefix apps/desktop run test:unit`: 44 files passed, 577 tests passed.
- `rtk npm --prefix apps/desktop run build`: passed; Vite reported the existing large-chunk warning.
- `rtk git diff --check`: passed.
- `rtk bash scripts/flake.bash --ci`: passed.
- `rtk bash scripts/test.bash`: 1158 passed, 1 warning.

PIHC3 status: clean on `v3.1`; no PIHC3 files changed.
