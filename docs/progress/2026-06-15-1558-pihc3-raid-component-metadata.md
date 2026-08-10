# 2026-06-15 15:58 PIHC3 raid component metadata

## Scope

Continued the non-map PIHC2 to PIHC3 migration by enriching the existing `raid_component` importer with generic metadata for current-format raid category and type support files. The slice keeps the module family minimal: compiled PDX still flows through the shared path-preserving PDX slot, localization still flows through the shared `main.loc` slot, and GUI-facing details are mirrored into `meta.yaml` settings.

## Changes

- Added a red metadata contract for generated raid component `meta.yaml` settings.
- Added shared importer metadata for component id/domain, source size, line counts, wrapper keys, localization languages, and localization keys.
- Mirrored category metadata: category ids, field-key counts, intel sources, visibility/availability counts, and free-targeting usage.
- Mirrored raid type metadata: raid type ids, raid category counts, target selectors/icons, custom map icons, launch sounds, arrow/start types, unit requirement counts, equipment and battalion requirements, success factors/levels, and explicit tooltip/target loc keys.
- Regenerated the 4 `raid_component` modules under `projects/PIHC3/src/modules/raid_component/`.
- Updated the raid migration note, the PIHC3 design summary, and the legacy inventory.

## Evidence

- Red contract: `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k raid_component_importer_extracts_metadata_contract` failed with `KeyError: 'component_id'`.
- Green focused contract: `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k raid_component` passed with 3 tests and 211 deselected.
- Formatting: `rtk uv run black --check projects/PIHC3/scripts/migrate_pihc2_raid_components.py tests/test_pihc3_migration_contracts.py` passed.
- Heaven-style scan: `OK: 2 file(s) - no banned imports`.
- Regeneration: `Imported 4 PIHC2 raid component modules into /Users/magolor/Utils/ParaDev-3/projects/PIHC3/src/modules/raid_component`.
- Build: `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json`.
- Build summary: 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, `blocked: false`.
- Build ownership: 4 `raid_component` PDX artifacts, 40 `raid_component` localization artifacts, and 0 copy-owned files under `common/raids/`.

## Follow-Up

Raid type/category records remain compiled support preservation. Structured editable raid authoring and Gotterdammerung gameplay behavior validation remain future work.
