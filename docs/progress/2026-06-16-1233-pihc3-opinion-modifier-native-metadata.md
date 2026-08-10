# 2026-06-16 12:33 PIHC3 opinion-modifier native metadata

## Scope

Enrich the PIHC2 individual opinion-modifier import so PIHC3 native modules expose PIHC2 source provenance, localization summaries, compiled source facts, and shallow field groups through generic settings.

## Changes

- Added a focused red contract for `OPINION_C00_C01_BASE` metadata covering source slot counts, PIHC2 resource evidence paths, compiled source byte/line counts, `info.json` keys, localization counts, direct field groups, numeric value, and `legacy/source.yaml`.
- Extended `projects/PIHC3/scripts/migrate_pihc2_opinions.py` with compact metadata helpers while leaving the `opinion_modifier` family slots and compiler unchanged.
- Regenerated all 428 opinion-modifier modules with `--clean`.
- Updated the opinion-modifier migration note, design overview, and legacy inventory with the refreshed native coverage.

## Evidence

- Red contract: `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k opinion_modifier_importer_extracts_source_localization_and_field_metadata_contract` failed first with `KeyError: 'source_file_count'`.
- Green contract: the same focused command passed with `1 passed, 233 deselected`.
- Regeneration: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_opinions.py --clean` migrated 428 opinion modifiers.
- Metadata coverage: 428 modules, 30 settings per module, 428 legacy manifests, 790 PIHC2 source evidence paths, 790 localization rows, 428 direct scalar summaries, 13 unique values, and a value range from -200 to 200.
- Focused regression: `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k opinion_modifier_importer` passed with `2 passed, 232 deselected`.
- Formatting: `rtk uv run black --check projects/PIHC3/scripts/migrate_pihc2_opinions.py tests/test_pihc3_migration_contracts.py` passed.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_opinions.py tests/test_pihc3_migration_contracts.py` returned `OK: 2 file(s) - no banned imports`.
- Build: `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-opinion-modifier-native-metadata-build.json` completed with 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.
- Build ownership: native opinion-modifier modules own 428 individual opinion PDX artifacts and 790 localization artifacts; the build has 0 copy-root-owned individual `common/opinion_modifiers/OPINION_*` artifacts.

## Follow-Up

Aggregate opinion authoring reconstruction from source focuses, decisions, events, and inventory systems remains future work. The shared aggregate opinion PDX files stay owned by `modifier_component`.
