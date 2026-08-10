# SDK Template Form Metadata Progress

Date: 2026-06-29 18:26

Linear: TAL-000

## Done

- Preserved SDK `Project.templates()` form-field metadata in the desktop module create-field model.
- Updated the create dialog to show SDK-provided field labels and descriptions instead of raw template argument names.
- Added a regression test proving labels, descriptions, field type, and default values survive the desktop handoff.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- --run src/moduleEditor/model.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/moduleEditor/ModuleEntityList.test.tsx src/moduleEditor/model.test.ts`
- `rtk npm --prefix apps/desktop run build`
- `rtk git diff --check`
- `PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 rtk bash scripts/run.bash --tauri --port 5198`

## Risks Or Blockers

- The create dialog still renders every SDK field as a text input; `choice`, `number`, and multiline `text` widgets should be improved in a later slice.

## Next

- Address the config/chat audit findings from the parallel explorer, especially raw config keys and fallback source labels.
