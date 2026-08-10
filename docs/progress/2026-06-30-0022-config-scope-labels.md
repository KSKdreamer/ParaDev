# Config Scope Labels Progress

Date: 2026-06-30 00:22

Linear: continuous usability goal

## Done

- Made module-default rows distinguish shared config values from desktop-only preview preferences.
- Moved the thumbnail cache config key into the config-page model instead of inferring it from the row id in React.
- Reworded config helper text around user impact: shared build/CLI behavior versus app-preview-only behavior.
- Added a TypeScript guard that keeps desktop-only module defaults out of the `writeConfigValue` bridge.
- Ran two read-only subagent audits for config-page usability and API/CLI/GUI config alignment.

## Verification

- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk env PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 bash scripts/run.bash --tauri`

## Risks Or Blockers

- Config pages still need richer per-field persistence state and path-picker affordances for non-programmer modders.

## Next

- Add project path browse/reveal/validate actions and per-field reset/save feedback.
