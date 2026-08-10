# 2026-06-15 16:38 PIHC3 common component metadata

## Scope

Continued the non-map PIHC2 to PIHC3 migration by enriching the broad `common_component` importer with generic metadata for the 48 miscellaneous compiled support files. The slice keeps the module family minimal: compiled PDX still flows through one shared path-preserving PDX slot, localization still flows through the shared `main.loc` slot, and GUI-facing structure is mirrored into `meta.yaml` settings.

## Changes

- Added a red metadata contract for generated common component `meta.yaml` settings.
- Added shared importer metadata for component id/domain, source size, line counts, root key counts, wrapper keys, inferred wrapper record, record ids, bounded first/last record samples, direct field-key counts, scalar/block/bare field counts, localization languages, and localization keys.
- Covered representative source shapes in the contract: `common/alerts.txt`, `common/state_category/city.txt`, `common/technology_tags/00_technology.txt`, and empty `common/triggered_modifiers.txt`.
- Regenerated the 48 `common_component` modules under `projects/PIHC3/src/modules/common_component/`.
- Updated the common-component migration note, the PIHC3 design summary, and the legacy inventory.

## Evidence

- Red contract: `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k common_component_importer_extracts_metadata_contract` failed with `KeyError: 'component_id'`.
- Green focused contract before formatting: `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k common_component` passed with 3 tests and 213 deselected.
- Green post-format metadata contract: `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k common_component_importer_extracts_metadata_contract` passed with 1 test and 215 deselected.
- Formatting: `rtk uv run black --check projects/PIHC3/scripts/migrate_pihc2_common_components.py tests/test_pihc3_migration_contracts.py` passed.
- Heaven-style scan: `OK: 2 file(s) - no banned imports`.
- Regeneration: `Imported 48 PIHC2 common component modules into /Users/magolor/Utils/ParaDev-3/projects/PIHC3/src/modules/common_component`.
- Build: `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json`.
- Build summary: 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, `blocked: false`.
- Build ownership: 48 `common_component` PDX artifacts, 270 `common_component` localization artifacts, 0 copy-owned artifacts for reviewed common paths, and 2 terrain copy artifacts left intentionally copy-owned for the skipped map-adjacent terrain slice.

## Follow-Up

Common support files remain compiled support preservation. Structured editable authoring for individual abilities, alerts, tags, state categories, weather rules, equipment upgrades, and name pools remains future work where GUI workflows justify it.
