# Chat Role SelectField Progress

Date: 2026-06-30 16:19

Linear: ongoing usability goal

## Done

- Replaced the floating AI chat role dropdown with the shared compact `SelectField` primitive.
- Removed the bespoke chat-role `<select>` styling so role selection uses the same focus, chevron, and compact-control styling as the rest of the desktop shell.
- Preserved localized profile labels and the existing `data-paradev-chat-role` hook.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- --run src/components/FloatingChatShell.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/components/FloatingChatShell.test.tsx src/components/AppShell.test.tsx src/i18n/locales.test.ts`
- `rtk npm --prefix apps/desktop run build`
- `rtk npm --prefix apps/desktop run test:unit -- --run`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 47840`

## Risks Or Blockers

- The change is UI-only; live role switching behavior remains covered by existing component state tests rather than a native click-through test.

## Next

- Localize the remaining preview-tab tooltip gap or continue moving GUI shell registries toward SDK-owned workspace metadata.
