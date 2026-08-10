# PIHC3 Intelligence Agency Metadata Progress

Date: 2026-06-14 23:58

Linear: TAL-000

## Done

- Added intelligence-agency migration contracts for shared family slots and one-folder importer metadata.
- Made `projects/PIHC3/scripts/migrate_pihc2_intel_agencies.py` import-safe from tests.
- Added `import_intelligence_agency(...)` and regenerated all 9 PIHC2 intelligence agency modules with names, default/available trigger blocks, picture sprite ids, localization keys, and compiled GFX/DDS output paths in `meta.yaml`.
- Updated the intelligence-agency migration note, global PIHC3 migration design, and legacy inventory evidence.

## Verification

- Red check before implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'intelligence_agency_importer or intelligence_agency_family or intelligence_agency_component or intelligence_agency_asset_component'` failed on the missing `_entity_migration_common` import path.
- Green check after implementation/regeneration: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'intelligence_agency_importer or intelligence_agency_family or intelligence_agency_component or intelligence_agency_asset_component'` passed with 6 passed and 157 deselected.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_intel_agencies.py tests/test_pihc3_migration_contracts.py` reported `OK: 2 file(s) - no banned imports`.
- `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-intelligence-agency-metadata-build.json` reported 16,581 modules, 62 collections, 37,424 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.

## Risks Or Blockers

- Native agency modules still emit one file per agency while `intelligence_agency_component` preserves the compiled aggregate support file for parity.
- Source-image regeneration, agency upgrades, country/focus creation hooks, and aggregate-to-editable emission remain future slices.

## Next

- Continue enriching sparse non-map families; likely candidates are special projects/rewards, focus trees, events, or opinion modifiers.
