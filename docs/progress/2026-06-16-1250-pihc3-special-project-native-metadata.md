# PIHC3 Special Project Native Metadata Progress

Date: 2026-06-16 12:50

Linear: TAL-000

## Done

- Extended `projects/PIHC3/scripts/migrate_pihc2_special_projects.py` so native `special_project` modules mirror source, localization, field, compiled icon, and source-image metadata in `meta.yaml`.
- Regenerated 25 project modules and 18 reward modules with `--clean`; project modules now include `legacy/source.yaml` plus non-emitted PIHC2 `default.png`, `raw.png`, `info.json`, and `locs.txt` evidence.
- Synced the special-project migration page, PIHC3 design note, and legacy inventory with the new project-side coverage.

## Verification

- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k special_project_importer_extracts_source_localization_and_icon_metadata_contract`
- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k 'special_project_family or special_project_importer or special_project_reward'`
- `rtk uv run black --check projects/PIHC3/scripts/migrate_pihc2_special_projects.py tests/test_pihc3_migration_contracts.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_special_projects.py tests/test_pihc3_migration_contracts.py`
- `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-special-project-native-metadata-build.json`
- Build summary: 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, `blocked: false`.

## Risks Or Blockers

- Source-image regeneration is still evidence-only; native modules emit the compiled DDS icon copied from PIHC_dev.
- Structured project-tag, specialization, and GUI behavior authoring remains future work.

## Next

- Continue enriching the remaining low-density non-map migration families with source/localization/image metadata and focused compile checks.
