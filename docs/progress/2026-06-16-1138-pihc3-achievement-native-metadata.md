# 2026-06-16 11:38 PIHC3 achievement native metadata

## Scope

Enrich the native PIHC2 achievement import so PIHC3 can browse source provenance, localization, source icons, and generated trigger metadata through generic settings without changing the achievement compiler family.

## Changes

- Added a focused red contract for `PIHC_1CO_ALL_THE_FIRST_GAME` covering achievement ids, aggregate legacy path, source slot counts, legacy resource evidence, info/localization counts, direct field groups, possible/happened condition counts, source/emitted icon metadata, and `legacy/source.yaml`.
- Extended `projects/PIHC3/scripts/migrate_pihc2_achievements.py` to emit generic metadata from existing `info.json`, `locs.txt`, and source icon files.
- Preserved non-emitted source evidence in `legacy/source.yaml` and copied the original source icon into `legacy/`.
- Regenerated all 49 native achievement modules with `--clean`.
- Updated the PIHC3 achievement migration note, design overview, and legacy inventory with the refreshed native coverage.

## Evidence

- Red contract: `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k achievement_importer_extracts_source_slot_localization_and_icon_metadata_contract` failed first with `KeyError: 'achievement_id'`.
- Green contract: the same focused command passed with `1 passed, 229 deselected`.
- Regeneration: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_achievements.py --clean` migrated 49 achievements.
- Metadata coverage: 49 modules, 34 settings per module, 49 localized modules, 49 source-icon modules, 49 legacy manifests, 147 legacy resource evidence paths, 249 `possible` conditions, and 51 `happened` conditions.
- Focused regression: `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k achievement_importer` passed with `2 passed, 228 deselected`.
- Formatting: `rtk uv run black --check projects/PIHC3/scripts/migrate_pihc2_achievements.py tests/test_pihc3_migration_contracts.py` passed.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_achievements.py tests/test_pihc3_migration_contracts.py` returned `OK: 2 file(s) - no banned imports`.
- Build: `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-achievement-native-metadata-build.json` completed with 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.
- Build ownership: native achievement modules own 196 artifacts, including 49 PDX files, 98 localization YAML files, and 49 PNG icon copies. The build has 0 copy-root-owned paths under `common/achievements` or `gfx/achievements`.

## Follow-Up

Aggregate-pack-native emission, DDS regeneration from source icons, achievement UI/ribbon behavior, and broader multi-language parity remain future achievement slices.
