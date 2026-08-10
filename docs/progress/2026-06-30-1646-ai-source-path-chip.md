# AI Source Path Chip Progress

Date: 2026-06-30 16:46

Linear: ongoing usability goal

## Done

- Added `detail` to selected file AI chat source descriptors so the GUI can show which PIHC3 source file is attached.
- Updated floating AI chat context chips to expose source details in the chip title, accessible toggle label, and compact visible path text.
- Added regression coverage for selected source paths from the App context builder and the floating chat chip markup.

## Verification

- Red first: `rtk npm --prefix apps/desktop run test:unit -- --run src/App.test.ts src/components/FloatingChatShell.test.tsx -t "source path|source context when a diagram-open|dirty source text|intentionally empty selected source"`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/App.test.ts src/components/FloatingChatShell.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 47840`

## Risks Or Blockers

- The chip still truncates long paths visually to preserve the compact floating chat layout; the full path remains available through the title and accessible label.

## Next

- Continue with the remaining GUI audit items: shared source-picker styling or friendly localization language labels.
