# PIHC3 Difficulty Setting Native Metadata

## Scope

- Continued PIHC2 difficulty-setting migration without changing the shared `def.txt` and `main.loc` slots.
- Enhanced `projects/PIHC3/scripts/migrate_pihc2_difficulty_settings.py` so each difficulty-setting module exposes generic PDX and localization provenance in both `meta.yaml` settings and `legacy/source.yaml`.
- Regenerated all ignored native difficulty-setting modules with `--clean`: 9 modules.

## Result

- Each difficulty-setting module now records compiled source paths, source file extension counts, source byte/line facts, generated setting text byte/line facts, generated localization text byte/line facts, compiled PDX/localization output paths, source file stem, and `file_summaries_by_path`.
- `custom_diff_strong_C01` records `common/difficulty_settings/00_difficulty.txt`, 1,687 source bytes, 74 source lines, 166 generated setting bytes, 10 generated setting lines, 142 generated localization bytes, 5 generated localization lines, and output `common/difficulty_settings/custom_diff_strong_C01.txt`.
- The regenerated tree has 9 `legacy/source.yaml` manifests, one unique compiled source file, 9 source path references, 15,183 compiled source bytes, 666 compiled source lines, 1,491 generated setting bytes, 90 generated setting lines, 1,258 generated localization bytes, and 45 generated localization lines.
- Existing difficulty-setting browsing metadata is preserved: 18 owned localization rows, two localization languages per module, field order, scalar field values, modifier keys, multipliers, and country tags.

## Verification

- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k difficulty_setting_importer_extracts_generic_provenance_contract` failed before implementation on missing `compiled_source_paths`, then passed after the importer change.
- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k pihc3_difficulty_setting` passed with 4 selected tests.
- `rtk uv run black --check projects/PIHC3/scripts/migrate_pihc2_difficulty_settings.py tests/test_pihc3_migration_contracts.py` passed.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_difficulty_settings.py tests/test_pihc3_migration_contracts.py` reported `OK: 2 file(s) - no banned imports`.
- `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-difficulty-setting-native-metadata-build.json` passed with 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.
- The build manifest contains 9 `module:difficulty_setting/<id>` PDX artifacts, 18 module-owned difficulty-setting localization artifacts, and 0 copy-root-owned `common/difficulty_settings` artifacts.

## Remaining Work

- Keep per-country roster generation, custom difficulty modifier definitions, and broader balancing review for later parity slices.
- Current shared slots remain sufficient: `def.txt` owns the wrapped difficulty-setting PDX record and `main.loc` owns the selected display localization rows.
