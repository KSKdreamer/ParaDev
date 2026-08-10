# PIHC3 Game Rule Native Metadata

## Scope

- Continued PIHC2 game-rule migration without changing the shared `def.txt` and `main.loc` slots.
- Enhanced `projects/PIHC3/scripts/migrate_pihc2_game_rules.py` so each rule module exposes generic PDX and localization provenance in both `meta.yaml` settings and `legacy/source.yaml`.
- Regenerated all ignored native game-rule modules with `--clean`: 27 rule modules.

## Result

- Each game-rule module now records compiled source paths, source file extension counts, source byte/line facts, generated rule text byte/line facts, generated localization text byte/line facts, compiled PDX/localization output paths, source file stem, and `file_summaries_by_path`.
- `allow_wargoals` records `common/game_rules/00_game_rules.txt`, 12,615 source bytes, 472 source lines, 607 generated rule bytes, 27 generated rule lines, 4,955 generated localization bytes, 83 generated localization lines, and output `common/game_rules/allow_wargoals.txt`.
- The regenerated tree has 27 `legacy/source.yaml` manifests, 3 unique compiled source files, 27 source path references, 277,765 compiled source bytes, 10,368 compiled source lines, 13,818 generated rule bytes, 602 generated rule lines, 112,795 generated localization bytes, and 1,803 generated localization lines.
- Existing rule browsing metadata is preserved: 84 `default`/`option` blocks, 24 default-option blocks, 21 icon-bearing rules, 185 unique owned loc keys, 1,402 owned loc rows across languages, and 287 referenced loc keys.

## Verification

- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k game_rule_importer_extracts_generic_provenance_contract` failed before implementation on missing `compiled_source_paths`, then passed after the importer change.
- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k game_rule` passed with 4 selected tests.
- `rtk uv run black --check projects/PIHC3/scripts/migrate_pihc2_game_rules.py tests/test_pihc3_migration_contracts.py` passed.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_game_rules.py tests/test_pihc3_migration_contracts.py` reported `OK: 2 file(s) - no banned imports`.
- `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-game-rule-native-metadata-build.json` passed with 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.
- The build manifest contains 27 `module:game_rule/<id>` PDX artifacts, 214 module-owned game-rule localization artifacts across 10 language folders, and 0 copy-root-owned `common/game_rules` artifacts.

## Remaining Work

- Keep scripted consumer review and icon asset generation for later game-rule parity slices only if GUI authoring expands beyond the compiled definitions.
- Shared group labels and shared vanilla option labels remain intentionally outside individual rule-owned localization.
