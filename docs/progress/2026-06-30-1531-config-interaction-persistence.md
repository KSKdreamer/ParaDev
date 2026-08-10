# Config Interaction Persistence Progress

Date: 2026-06-30 15:31

Linear: TAL-000

## Done

- Extended the PIHC3-shaped config smoke page so rendered config control changes record the exact SDK config-value write plan from `desktopConfigWritesForSettingsChange`.
- Added smoke-state coverage for the recorded `last-config-write` dataset fields.
- Changed LLM route-test running copy to use the configured provider/model route instead of hard-coding DeepSeek v4 Flash.
- Updated the config smoke instructions to cover CLI output, build parallelism, and LLM model field interaction checks.

## Verification

- Red first: `rtk npm --prefix apps/desktop run test:unit -- e2e/config-page-smoke-state.test.ts src/configPage/ConfigPage.test.tsx` failed on missing `lastConfigWrite*` dataset fields and route-specific running copy.
- Focused green: `rtk npm --prefix apps/desktop run test:unit -- e2e/config-page-smoke-state.test.ts src/configPage/ConfigPage.test.tsx`
- Focused locale/config check: `rtk npm --prefix apps/desktop run test:unit -- e2e/config-page-smoke-state.test.ts src/configPage/ConfigPage.test.tsx src/i18n/locales.test.ts`
- `rtk npm --prefix apps/desktop run build`
- `rtk npm --prefix apps/desktop run test:unit`
- Rendered browser smoke: `http://127.0.0.1:5180/e2e/config-page-smoke.html`
  - changed CLI output to YAML and saw `last-config-write-key="paradev.cli.output"`, value `yaml`;
  - changed build parallelism to `6` and saw key `paradev.build.parallelism`, value `6`;
  - changed AI model to `deepseek-reasoner` and saw key `paradev.ai.model`, value `deepseek-reasoner`;
  - console warnings/errors were empty.
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 1432`

## Risks Or Blockers

- The rendered config interaction smoke is still a browser fixture rather than a CI Playwright test because the desktop package does not currently include a browser test runner.
- Backend empty-response detail still contains a DeepSeek v4 Flash literal, though the UI masks that raw backend detail for localized empty-response summaries.

## Next

- Make the backend LLM test detail generic or route-derived, then update service expectations.
