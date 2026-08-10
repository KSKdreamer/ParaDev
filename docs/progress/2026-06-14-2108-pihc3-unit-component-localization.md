# PIHC3 Unit Component Localization

## Slice

Improved the path-preserving unit/equipment support migration so generic `unit_component` modules carry display data without splitting low-level records into new family-specific code.

## Changes

- Added a generic `loc` slot to the `unit_component` family in `projects/PIHC3/paradev.yaml`.
- Added `HOI4_GAME_ROOT` and `--game-root` to `projects/PIHC3/scripts/migrate_pihc2_unit_components.py`.
- Parsed top-level ids from compiled `sub_units`, `equipments`, and `sub_unit_modifiers` wrappers.
- Loaded localization in this order:
  1. current local HOI4 install;
  2. compiled PIHC_dev mod.
- Regenerated all 25 unit/equipment support modules.
- Updated equipment, unit-component, copy-overlay, architecture, and legacy inventory docs.

## Evidence

- Before the change, `unit_component` had only a PDX source slot and no importer helper for localization.
- After the change:
  - 25 unit-component modules are present;
  - all 25 have `main.loc`;
  - generated support localization contains 2,258 localized rows;
  - `convoy_1` uses PIHC_dev override rows such as English `Small Wooden Boat` and Simplified Chinese `小木帆船`;
  - vanilla sub-unit modifier keys such as `modifier_army_sub_unit_infantry_attack_factor` are imported from current-game localization.

## Verification

- Red test:
  - `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k "unit_component_family or unit_component_importer"`
  - Failed with missing `unit_component` loc slot and missing `compiled_unit_component_locs`.
- Focused tests after implementation:
  - `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k "unit_component_family or unit_component_importer"`
  - `2 passed, 147 deselected`.
- Regeneration:
  - `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_unit_components.py --clean`
  - Imported 25 PIHC2 unit component modules.
- Style:
  - `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_unit_components.py tests/test_pihc3_migration_contracts.py`
  - `OK: 2 file(s) - no banned imports`.
  - `rtk uv run black --check projects/PIHC3/scripts/migrate_pihc2_unit_components.py`
  - `1 file would be left unchanged`.
- Dry build:
  - `rtk uv run paradev build projects/PIHC3 --json > /tmp/pihc3-unit-component-localization-dry-build.json`
  - Summary: 16,581 modules, 62 collections, 37,082 planned artifacts, 713 diagnostics, 0 errors, `blocked: false`.
  - Unit-component ownership: 25 PDX artifacts and 226 localization artifacts.
  - Active copy-root artifacts: 1,403, with 0 copy-root artifacts for reviewed unit/equipment support paths.

## Next

Continue improving GUI-visible data in remaining support families while keeping map-adjacent copy-root leftovers for the later map migration slice.
