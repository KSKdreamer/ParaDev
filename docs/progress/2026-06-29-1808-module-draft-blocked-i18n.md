# Module Draft Blocked I18n Progress

Date: 2026-06-29 18:08

Linear: ongoing usability loop

## Done

- Localized the module editor fallback shown when an SDK scaffold/create/apply plan is blocked without a diagnostic message.
- Kept SDK-provided diagnostic messages unchanged so backend context remains visible to the modder.
- Added a regression test for Chinese and English fallback text.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- --run src/moduleEditor/ModuleEditor.test.tsx src/i18n/locales.test.ts`
- `rtk npm --prefix apps/desktop run build`
- `rtk git diff --check`
- `PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 rtk bash scripts/run.bash --tauri --port 5196`

## Risks Or Blockers

- Other backend error strings are intentionally passed through verbatim; only shell-owned fallback copy is translated here.

## Next

- Continue scanning module editor and diagram controls for remaining shell-owned English labels that leak in Chinese mode.
