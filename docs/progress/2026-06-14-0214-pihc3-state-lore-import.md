# PIHC3 State Lore Import

## Summary

Imported all 79 PIHC2 `resources/state_lores` folders into native PIHC3 `state_lore` modules and added a project-local aggregate family for the two legacy `PIHC_STATE_LORES` outputs.

## Changes

- Added `projects/PIHC3/scripts/migrate_pihc2_state_lores.py`.
- Added `projects/PIHC3/system/state_lore_family.py` and registered it through `python_modules` in `paradev.yaml`.
- Replaced the old declarative `state_lore` simple-source family with an aggregate family that emits:
  - `common/scripted_localisation/PIHC_STATE_LORES.txt`
  - `common/on_actions/PIHC_STATE_LORES.txt`
  - per-state localization files.
- Imported 79 modules under `projects/PIHC3/src/modules/state_lore/STATE_LORE_<id>`.
- Preserved conditional description variants for:
  - `STATE_LORE_217_0`
  - `STATE_LORE_772_0`
- Removed stale compiled-common `projects/PIHC3/src/modules/on_action/PIHC_STATE_LORES`, which collided with the new aggregate owner.
- Added copy-root exclusions for generated state-lore scripted-localisation and localization outputs.

## Notes

The family reconstructs `<state id>.id` references from `settings.state_id` when emitting aggregate PDX. This avoids the generic PDX parser turning numeric dotted ids into `146 . id` after parsing module fragments.

Shared state-lore GUI/scripted-GUI support and shared replacement localization remain copy-overlay owned.

## Verification

- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q`
  - `6 passed`
- PIHC3 dry build:
  - modules: 2,853
  - collections: 62
  - artifacts: 25,899
  - diagnostics: 4,183 warnings
  - errors: 0
  - blocked: false
- Aggregate payload spot checks:
  - `state_lore_text_state_id = 146.id`
  - `global.states_with_lore = 146.id`
  - `STATE_LORE_217_0`
  - `STATE_LORE_772_0`
  - no tokenized-dot output.
