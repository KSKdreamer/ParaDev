# LLM Route Result Code Progress

Date: 2026-06-29 19:04

Linear: N/A

## Done

- Added a structured `resultCode` field to the SDK desktop LLM route-test payload.
- Preserved raw `detail` / `testDetail` as diagnostic evidence while letting React render localized summaries from `resultCode`.
- Updated Python, TypeScript bridge, REST forwarding, and config-page regressions for `ok`, `empty_response`, and `exception` outcomes.

## Verification

- `rtk bash scripts/test.bash tests/test_desktop_api_selection.py -q`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/services/paradev.test.ts src/configPage/ConfigPage.test.tsx src/i18n/locales.test.ts`
- `rtk git diff --check`
- `rtk npm --prefix apps/desktop run build`
- `PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 rtk bash scripts/run.bash --tauri --port 5203`

## Risks Or Blockers

- `/desktop/llm/test` remains a runtime bridge route rather than a generated frontend API surface; no generated docs/types were required for this additive payload field.

## Next

- Continue moving config-page status and error surfaces from raw bridge prose toward structured status codes and localized summaries.
