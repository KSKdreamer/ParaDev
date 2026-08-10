# 2026-06-14 23:21 PIHC3 common component equipment upgrade localization

## Scope

Continued the non-map PIHC2 to PIHC3 migration by expanding `common_component` localization ownership for the compiled equipment-upgrade support files. This keeps the module family generic: tank, plane, and naval upgrade files still use the shared path-preserving PDX slot plus optional `main.loc`.

## Changes

- Added path-gated localization extraction for `common/units/equipment/upgrades/*.txt`.
- Equipment-upgrade extraction now owns upgrade record IDs under the `upgrades = { ... }` wrapper plus matching `_desc` keys where localization exists.
- Regenerated 48 common component modules.
- Generated `main.loc` for naval, tank, and plane upgrade support modules.
- Updated migration docs and the legacy inventory note.

## Evidence

- Red contract: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k "common_component_importer"` first failed with `KeyError: 'l_english'` for `common/units/equipment/upgrades/pihc_naval_upgrades.txt`.
- Green contract after the path-gated extractor change: `1 passed, 154 deselected in 180.99s`.
- Regeneration: `Imported 48 PIHC2 common component modules into /Users/magolor/Utils/ParaDev-3/projects/PIHC3/src/modules/common_component`.
- Generated metadata: naval upgrades now have `loc_key_count: 260`, tank upgrades now have `loc_key_count: 4`, and plane upgrades now have `loc_key_count: 2`.
- Dry build: `rtk uv run paradev build projects/PIHC3 --json > /tmp/pihc3-common-equipment-upgrade-loc-dry-build.json`.
- Dry-build summary: 16,581 modules, 62 collections, 37,404 artifacts, 713 diagnostics, 0 errors, `blocked: false`.
- Dry-build diagnostics: 546 `copy_root.shadowed_artifact` warnings and 167 metadata warnings.
- Dry-build ownership: 48 `common_component` PDX artifacts and 194 `common_component` localization artifacts from 21 localized common-component modules.

## Follow-Up

- Candidate remaining common-component localization slices include combat tactics, equipment groups, technology tags, technology sharing, and resistance/compliance modifiers.
- Keep future extractors path-gated to clear current-game PDX conventions before considering new editable module families.
