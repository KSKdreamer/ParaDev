# Chat Source Kind I18n Progress

Date: 2026-06-29 18:35

Linear: TAL-000

## Done

- Fixed floating AI chat source labels so unlabeled built-in source kinds resolve through the translator instead of showing raw identifiers like `workspace`.
- Added chat-specific source-kind labels for project, selection, templates, and diagnostics sources.
- Added a regression render test for Chinese visible text and aria labels.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- --run src/components/FloatingChatShell.test.tsx src/i18n/locales.test.ts`
- `rtk npm --prefix apps/desktop run build`
- `rtk git diff --check`
- `PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 rtk bash scripts/run.bash --tauri --port 5199`

## Risks Or Blockers

- This slice fixes the chat source fallback only. The config page still has raw config-key and backend-detail wording from the same audit queue.

## Next

- Continue with the config page findings: raw `paradev.ai.key_env`, profile id display, and backend route-test detail normalization.
