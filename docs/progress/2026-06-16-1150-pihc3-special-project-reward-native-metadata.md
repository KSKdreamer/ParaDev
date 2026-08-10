# 2026-06-16 11:50 PIHC3 special-project reward native metadata

## Scope

Enrich the PIHC2 special-project prototype reward import so PIHC3 can browse reward provenance, localization, source files, compiled field groups, option tokens, thresholds, and option effect summaries through generic settings.

## Changes

- Added a focused red contract for `GENERIC_ELEC` reward metadata covering reward ids, compiled output path, source slot counts, legacy source evidence, `info.json` keys, localization counts, direct field groups, option token keys, threshold fields, effect blocks, and `legacy/source.yaml`.
- Extended `projects/PIHC3/scripts/migrate_pihc2_special_projects.py` with reward-only metadata helpers while leaving the project importer and reward family compiler unchanged.
- Regenerated all 25 special-project modules and 18 special-project reward modules with `--clean`.
- Updated the PIHC3 special-project migration note, design overview, and legacy inventory with the refreshed reward coverage.

## Evidence

- Red contract: `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k special_project_reward_importer_extracts_source_localization_and_field_metadata_contract` failed first with `KeyError: 'reward_id'`.
- Green contract: the same focused command passed with `1 passed, 230 deselected`.
- Regeneration: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_special_projects.py --clean` migrated 25 special projects and 18 rewards.
- Metadata coverage: 18 reward modules, 31-32 settings per module, 18 localized modules, 18 legacy manifests, 36 legacy source evidence paths, 20 option blocks, 18 threshold summaries, and 18 effect-summary modules.
- Focused regression: `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k 'special_project_importer or special_project_reward'` passed with `3 passed, 228 deselected`.
- Formatting: `rtk uv run black --check projects/PIHC3/scripts/migrate_pihc2_special_projects.py tests/test_pihc3_migration_contracts.py` passed.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_special_projects.py tests/test_pihc3_migration_contracts.py` returned `OK: 2 file(s) - no banned imports`.
- Build: `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-special-project-reward-native-metadata-build.json` completed with 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.
- Build ownership: native reward modules own 54 artifacts, including 18 reward PDX files and 36 localization YAML files. The build has 0 copy-root-owned reward PDX artifacts.

## Follow-Up

Structured project-tag/specialization authoring, special-project GUI behavior validation, source-image regeneration, and deeper gameplay parity remain future special-project slices.
