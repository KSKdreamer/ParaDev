# Workspace Preview Tooltip Progress

Date: 2026-06-30 16:28

Linear: ongoing usability goal

## Done

- Replaced the workspace tab preview tooltip's hard-coded English suffix with a localized `workspace.tabs.previewTitle` string.
- Added English and Chinese locale entries for preview tab titles.
- Added a Workspace regression test that renders a Chinese preview tab and rejects the English `(preview)` fallback.

## Verification

- Red first: `rtk npm --prefix apps/desktop run test:unit -- --run src/components/Workspace.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/components/Workspace.test.tsx src/i18n/locales.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 47840`

## Risks Or Blockers

- This is a focused translation cleanup; no SDK, CLI, or Tauri bridge behavior changed.

## Next

- Continue eliminating hard-coded GUI strings and align workspace shell labels with SDK-owned metadata where practical.
