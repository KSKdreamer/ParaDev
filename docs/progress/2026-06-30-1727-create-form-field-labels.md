# Create Form Field Labels Progress

Date: 2026-06-30 17:27

Linear: ongoing usability goal

## Done

- Humanized fallback create-form labels derived from SDK template args, so fields such as `legacy_tag` render as `Legacy tag`.
- Kept raw arg names as stable payload keys for SDK draft creation.
- Updated create-form input placeholders to use the friendly field label when no preview/default value is available.

## Verification

- Red first: `rtk npm --prefix apps/desktop run test:unit -- --run src/moduleEditor/model.test.ts -t "humanizes fallback create-form arg labels"`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/moduleEditor/model.test.ts -t "humanizes fallback create-form arg labels"`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/moduleEditor/model.test.ts src/moduleEditor/ModuleEntityList.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 47840`

## Risks Or Blockers

- SDK-provided `form.fields` labels still win exactly, so project-authored template labels remain authoritative.

## Next

- Continue with project identity cleanup or wire the Developer rail to the existing surface contract table.
