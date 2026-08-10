# Source Picker SelectField Progress

Date: 2026-06-30 16:54

Linear: ongoing usability goal

## Done

- Replaced the module editor's large source-list picker raw `<select>` with the shared compact `SelectField`.
- Removed the bespoke picker select styling while keeping the PIHC3 long-path layout contract for the selector and source path.
- Added/updated tests so the large source picker uses the shared control and keeps the selected path visible.

## Verification

- Red first: `rtk npm --prefix apps/desktop run test:unit -- --run src/moduleEditor/ModuleEntityDetails.test.tsx -t "large source-backed"`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/moduleEditor/ModuleEntityDetails.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 47840`

## Risks Or Blockers

- This changes only the wrapper/control styling for the existing source slot selector; active slot state and source path selection behavior remain unchanged.

## Next

- Continue with friendly localization language labels in the module details localization panel.
