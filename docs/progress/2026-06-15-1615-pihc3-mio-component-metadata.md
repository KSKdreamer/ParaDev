# 2026-06-15 16:15 PIHC3 MIO component metadata

## Scope

Continued the non-map PIHC2 to PIHC3 migration by enriching the existing `military_industrial_organization_component` importer with generic metadata for current-format MIO support files. The slice keeps the module family minimal: compiled PDX still flows through the shared path-preserving PDX slot, localization still flows through the shared `main.loc` slot, and GUI-facing details are mirrored into `meta.yaml` settings.

## Changes

- Added a red metadata contract for generated MIO component `meta.yaml` settings.
- Added shared importer metadata for component id/domain, source size, line counts, record ids, direct field-key counts, localization languages, and localization keys.
- Mirrored AI bonus-weight metadata: profile ids, 85 weight keys, bounded key samples, and value counts.
- Mirrored organization metadata: allowed tags, equipment/research categories, tree headers, initial trait names, trait tokens, trait icons, trait positions, relative-position counts, mutually exclusive blocks, equipment limits, and bonus fields.
- Mirrored policy metadata: policy ids/icons, allowed/available counts, `has_mio_size` and `same_as_mio` usage, policy equipment-type gates, bonus block counts, and bonus fields.
- Regenerated the 7 `military_industrial_organization_component` modules under `projects/PIHC3/src/modules/military_industrial_organization_component/`.
- Updated the MIO migration note, the PIHC3 design summary, and the legacy inventory.

## Evidence

- Red contract: `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k military_industrial_organization_component_importer_extracts_metadata_contract` failed with `KeyError: 'component_id'`.
- Green focused contract: `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k military_industrial_organization_component` passed with 3 tests and 212 deselected.
- Formatting: `rtk uv run black --check projects/PIHC3/scripts/migrate_pihc2_military_industrial_organization_components.py tests/test_pihc3_migration_contracts.py` passed.
- Heaven-style scan: `OK: 2 file(s) - no banned imports`.
- Regeneration: `Imported 7 PIHC2 MIO component modules into /Users/magolor/Utils/ParaDev-3/projects/PIHC3/src/modules/military_industrial_organization_component`.
- Build: `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json`.
- Build summary: 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, `blocked: false`.
- Build ownership: 7 `military_industrial_organization_component` PDX artifacts, 60 `military_industrial_organization_component` localization artifacts, and 0 copy-owned files under `common/military_industrial_organization/`.

## Follow-Up

MIO organizations, policies, and AI bonus weights remain compiled support preservation. Structured editable MIO trait-tree authoring and Arms Against Tyranny gameplay behavior validation remain future work.
