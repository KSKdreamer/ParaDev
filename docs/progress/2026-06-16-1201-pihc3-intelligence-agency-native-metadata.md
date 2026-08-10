# 2026-06-16 12:01 PIHC3 intelligence-agency native metadata

## Scope

Enrich the PIHC2 intelligence-agency import so PIHC3 native agency modules expose source provenance, localization counts, body field summaries, and source icon metadata through generic settings.

## Changes

- Added a focused red contract for `CECIA` agency metadata covering agency ids, legacy aggregate output path, source slot counts, legacy resource evidence, `info.json` keys, localization counts, direct field groups, default/availability condition counts, source/emitted icon metadata, source PNG dimensions, and `legacy/source.yaml`.
- Extended `projects/PIHC3/scripts/migrate_pihc2_intel_agencies.py` with compact metadata helpers while leaving the shared family slots and compiler unchanged.
- Regenerated all 9 intelligence-agency modules with `--clean`.
- Updated the PIHC3 intelligence-agency migration note, design overview, and legacy inventory with the refreshed native coverage.

## Evidence

- Red contract: `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k intelligence_agency_importer_extracts_source_localization_and_icon_metadata_contract` failed first with `KeyError: 'agency_id'`.
- Green contract: the same focused command passed with `1 passed, 231 deselected`.
- Regeneration: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_intel_agencies.py --clean` migrated 9 intelligence agencies.
- Metadata coverage: 9 modules, 30-35 settings per module, 9 legacy manifests, 25 legacy source evidence paths, 54 localization rows, and 7 source-icon metadata records.
- Focused regression: `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k 'intelligence_agency_importer or intelligence_agency_family or intelligence_agency_component or intelligence_agency_asset_component'` passed with `9 passed, 223 deselected`.
- Build: `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-intelligence-agency-native-metadata-build.json` completed with 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.
- Build ownership: native intelligence-agency modules own 9 PDX artifacts and 7 source-icon copy artifacts; the support component owns the aggregate agency PDX artifact; asset components own 18 compiled GFX/DDS copy artifacts.

## Follow-Up

Aggregate-to-editable emission, source-image regeneration, agency upgrade workflows, country/focus agency creation hooks, and alternate-name authoring remain future intelligence-agency slices.
