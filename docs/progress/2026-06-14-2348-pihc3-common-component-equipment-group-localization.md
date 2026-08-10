# 2026-06-14 23:48 PIHC3 common component equipment group localization

## Scope

Continued the non-map PIHC2 to PIHC3 migration by expanding `common_component` localization ownership for the compiled MIO equipment-group support file. This keeps equipment groups in the shared path-preserving common-component family instead of adding type-specific authoring code.

## Changes

- Added path-gated localization extraction for `common/equipment_groups/mio_equipment_groups.txt`.
- Equipment-group extraction now owns top-level `mio_cat_eq_*` PDX records only.
- Regenerated 48 common component modules.
- Generated `main.loc` for `COMMON_COMPONENT_EQUIPMENT_GROUPS_MIO_EQUIPMENT_GROUPS`, covering all 16 group IDs across the available languages.
- Updated migration docs and the legacy inventory note.

## Evidence

- Red contract: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k "common_component_importer"` first failed with `KeyError: 'l_english'` for `common/equipment_groups/mio_equipment_groups.txt`.
- Green contract after the path-gated extractor change: `1 passed, 160 deselected in 217.04s`.
- Regeneration: `Imported 48 PIHC2 common component modules into /Users/magolor/Utils/ParaDev-3/projects/PIHC3/src/modules/common_component`.
- Generated metadata: `COMMON_COMPONENT_EQUIPMENT_GROUPS_MIO_EQUIPMENT_GROUPS` now has `loc_key_count: 160`.
- Dry build: `rtk uv run paradev build projects/PIHC3 --json > /tmp/pihc3-common-equipment-group-loc-dry-build.json`.
- Dry-build summary: 16,581 modules, 62 collections, 37,424 artifacts, 713 diagnostics, 0 errors, `blocked: false`.
- Dry-build diagnostics: 546 `copy_root.shadowed_artifact` warnings and 167 metadata warnings.
- Dry-build ownership: 48 `common_component` PDX artifacts and 214 `common_component` localization artifacts from 23 localized common-component modules.

## Follow-Up

- Candidate remaining common-component localization slices include technology tags, technology sharing, and resistance/compliance modifiers.
- Keep future extractors path-gated to clear current-game PDX conventions before considering new editable module families.
