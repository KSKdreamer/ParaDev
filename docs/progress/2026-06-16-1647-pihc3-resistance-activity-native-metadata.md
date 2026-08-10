# PIHC3 Resistance Activity Native Metadata

## Scope

- Continued PIHC2 resistance-activity migration without changing the shared `def.txt` and `main.loc` slots.
- Enhanced `projects/PIHC3/scripts/migrate_pihc2_resistance_activities.py` so each resistance-activity module exposes generic PDX and localization provenance in both `meta.yaml` settings and `legacy/source.yaml`.
- Regenerated all ignored native resistance-activity modules with `--clean`: 17 modules.

## Result

- Each resistance-activity module now records compiled source paths, source file extension counts, source byte/line facts, generated activity text byte/line facts, generated localization text byte/line facts, compiled PDX/localization output paths, source file stem, and `file_summaries_by_path`.
- `sabotage_oil` records `common/resistance_activity/resistance_activity.txt`, 15,422 source bytes, 641 source lines, 1,051 generated activity bytes, 60 generated activity lines, 1,112 generated localization bytes, 59 generated localization lines, and output `common/resistance_activity/sabotage_oil.txt`.
- The regenerated tree has 17 `legacy/source.yaml` manifests, one unique compiled source file, 17 source path references, 262,174 compiled source bytes, 10,897 compiled source lines, 10,905 generated activity bytes, 641 generated activity lines, 21,909 generated localization bytes, and 1,003 generated localization lines.
- Existing resistance-activity browsing metadata is preserved: 340 owned localization rows, ten localization languages per module, field order, scalar alert keys, block root keys, and repeated root-key counts for activity effects and weights.

## Verification

- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k resistance_activity_importer_extracts_generic_provenance_contract` failed before implementation on missing `compiled_source_paths`, then passed after the importer change.
- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k pihc3_resistance_activity` passed with 3 selected tests.
- `rtk uv run black --check projects/PIHC3/scripts/migrate_pihc2_resistance_activities.py tests/test_pihc3_migration_contracts.py` passed.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_resistance_activities.py tests/test_pihc3_migration_contracts.py` reported `OK: 2 file(s) - no banned imports`.
- `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-resistance-activity-native-metadata-build.json` passed with 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.
- The build manifest contains 17 `module:resistance_activity/<id>` PDX artifacts, 170 module-owned resistance-activity localization artifacts, and 0 copy-root-owned `common/resistance_activity` artifacts.

## Remaining Work

- Keep targeted sabotage variables, building-specific damage effects, occupation-law balancing, and broader resistance workflow authoring for later parity slices.
- Current shared slots remain sufficient: `def.txt` owns the activity PDX record and `main.loc` owns the selected title/alert localization rows.
