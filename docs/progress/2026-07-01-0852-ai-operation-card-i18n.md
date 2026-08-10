# 2026-07-01 08:52 - AI operation card i18n

## Summary

Localized the managed AI chat operation-card titles and summaries for the
floating chat panel and Config > Models profile operation strip. Known SDK
operations now resolve by operation id (`module.draft`, `build.plan`, and
`build.start`) through the maintained locale dictionaries, while unknown future
operation cards still fall back to the SDK payload text.

This removes visible English strings such as `Build Plan`, `Build Start`, and
`Module Draft` from the Chinese AI role/profile workflow without changing the
underlying SDK operation ids, REST labels, or safety copy.

## Verification

- Red checks first:
  - `rtk npm --prefix apps/desktop run test:unit -- --run src/components/FloatingChatShell.test.tsx -t "managed SDK operation cards"`
  - `rtk npm --prefix apps/desktop run test:unit -- --run src/configPage/ConfigPage.test.tsx -t "operation tooltips"`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/components/FloatingChatShell.test.tsx -t "managed SDK operation cards|compact profile operation cards"`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/configPage/ConfigPage.test.tsx -t "operation tooltips"`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/i18n/locales.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/components/FloatingChatShell.test.tsx src/configPage/ConfigPage.test.tsx src/i18n/locales.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build` passed with the pre-existing Vite large-chunk warning.
- `rtk env PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 bash scripts/run.bash --tauri --port 47851` reached Vite ready, finished Cargo build, launched `target/debug/paradev-desktop`, and showed no late startup output before manual stop.
