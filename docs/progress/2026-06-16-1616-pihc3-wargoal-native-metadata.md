# PIHC3 Wargoal Native Metadata

## Scope

- Continued PIHC2 wargoal migration without changing the shared `def.txt` and `main.loc` slots.
- Enhanced `projects/PIHC3/scripts/migrate_pihc2_wargoals.py` so each wargoal module exposes generic PDX and localization provenance in both `meta.yaml` settings and `legacy/source.yaml`.
- Regenerated all ignored native wargoal modules with `--clean`: 13 wargoal modules.

## Result

- Each wargoal module now records compiled source paths, source file extension counts, source byte/line facts, generated wargoal text byte/line facts, generated localization text byte/line facts, compiled PDX/localization output paths, source file stem, and `file_summaries_by_path`.
- `take_claimed_state` records `common/wargoals/00_invasion.txt`, 3,439 source bytes, 173 source lines, 298 generated wargoal bytes, 15 generated wargoal lines, 4,172 generated localization bytes, 149 generated localization lines, and output `common/wargoals/take_claimed_state.txt`.
- The regenerated tree has 13 `legacy/source.yaml` manifests, one unique compiled source file, 13 source path references, 44,707 compiled source bytes, 2,249 compiled source lines, 2,748 generated wargoal bytes, 183 generated wargoal lines, 36,398 generated localization bytes, and 1,409 generated localization lines.
- Existing wargoal browsing metadata is preserved: 474 owned localization rows, module localization language counts of either 2 or 10, field order, scalar cost/threat fields, block root keys, and war-name localization keys.

## Verification

- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k wargoal_importer_extracts_generic_provenance_contract` failed before implementation on missing `compiled_source_paths`, then passed after the importer change.
- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k pihc3_wargoal` passed with 3 selected tests.
- `rtk uv run black --check projects/PIHC3/scripts/migrate_pihc2_wargoals.py tests/test_pihc3_migration_contracts.py` passed.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_wargoals.py tests/test_pihc3_migration_contracts.py` reported `OK: 2 file(s) - no banned imports`.
- `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-wargoal-native-metadata-build.json` passed with 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.
- The build manifest contains 13 `module:wargoal/<id>` PDX artifacts, 106 module-owned wargoal localization artifacts, and 0 copy-root-owned `common/wargoals` artifacts.

## Remaining Work

- Keep scripted consumers, peace-conference balance, AI behavior, and higher-level war-goal authoring for later parity slices.
- Current shared slots remain sufficient: `def.txt` owns the wrapped PDX record and `main.loc` owns the selected localization rows.
