# Config Localization Progress

Date: 2026-06-29 02:34 CST

Linear: n/a

## Done

- Moved config model preset labels/details and module default labels/details from raw TypeScript strings to i18n keys.
- Added confirmed English and Chinese copy for those config rows so the default Chinese GUI no longer mixes English in the Models and Module defaults pages.
- Kept the persisted settings shape stable by storing row ids, translation keys, units, and values rather than locale-specific display strings.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- ConfigPage`
- `rtk npm --prefix apps/desktop run test:unit -- src/configPage src/i18n src/App.test.ts`
- `rtk npm --prefix apps/desktop run build`

## Risks Or Blockers

- Vite still reports existing large chunk warnings for desktop bundles.
- Broader GUI translation gaps remain outside the config rows touched here.

## Next

- Add SDK-owned desktop config/dependency/LLM frontend API rows.
- Add a plan-only GUI build path before using the Tauri Build page against real PIHC3.
- Continue filling visible Chinese shell/workspace translation gaps.
