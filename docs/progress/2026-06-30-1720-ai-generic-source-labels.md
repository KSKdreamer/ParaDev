# AI Generic Source Labels Progress

Date: 2026-06-30 17:20

Linear: ongoing usability goal

## Done

- Localized floating-chat context labels when the SDK sends a generic source-kind label such as `Project index`.
- Preserved specific source labels such as `Focus trees` so selected project content remains recognizable.
- Covered the behavior in the shared AI source-kind label helper used by floating chat and config profile source rows.

## Verification

- Red first: `rtk npm --prefix apps/desktop run test:unit -- --run src/aiChatSourceKindText.test.ts -t "localizes generic SDK context labels"`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/aiChatSourceKindText.test.ts -t "localizes generic SDK context labels"`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/aiChatSourceKindText.test.ts src/aiChatProfileText.test.ts src/components/FloatingChatShell.test.tsx src/i18n/locales.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 47840`

## Risks Or Blockers

- Custom SDK source kinds without a translation key still use their SDK-provided label by design.

## Next

- Use the latest explorer findings to remove remaining raw labels in create-module forms and project identity rows.
