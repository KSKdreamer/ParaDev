# PIHC3 Achievement Metadata Progress

Date: 2026-06-14 23:47

Linear: TAL-000

## Done

- Added an achievement migration contract covering the shared `achievement` family slots and one-folder importer metadata.
- Made `projects/PIHC3/scripts/migrate_pihc2_achievements.py` import-safe from tests.
- Added `import_achievement(...)` and regenerated all 49 PIHC2 achievement modules with `unique_id`, ordered achievement/body keys, full `possible` and `happened` trigger blocks, localization keys, and compiled normal/grey/not-eligible DDS output paths in `meta.yaml`.
- Updated achievement migration, global PIHC3 migration design, and legacy inventory notes.

## Verification

- Red check before implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'achievement_importer or achievement_family or achievement_component or achievement_asset_component'` failed on the missing `_entity_migration_common` import path.
- Green check after implementation/regeneration: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'achievement_importer or achievement_family or achievement_component or achievement_asset_component'` passed with 6 passed and 155 deselected.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_achievements.py tests/test_pihc3_migration_contracts.py` reported `OK: 2 file(s) - no banned imports`.
- `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-achievement-metadata-build.json` reported 16,581 modules, 62 collections, 37,414 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.

## Risks Or Blockers

- The native achievement modules still emit one file per achievement while `achievement_component` preserves the compiled aggregate PIHC achievement pack for parity.
- Source-image regeneration for grey/not-eligible DDS variants and achievement UI/ribbon behavior remain future slices.

## Next

- Continue reducing sparse families with native metadata; likely candidates are intelligence agencies, special projects/rewards, focus trees, events, or opinion modifiers.
