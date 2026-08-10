# PIHC3 Unit Medal Native Metadata

## Scope

- Continued PIHC2 unit-medal migration without changing the shared `def.txt` and `main.loc` slots.
- Enhanced `projects/PIHC3/scripts/migrate_pihc2_unit_medals.py` so each unit-medal module exposes generic PDX and localization provenance in both `meta.yaml` settings and `legacy/source.yaml`.
- Regenerated all ignored native unit-medal modules with `--clean`: 16 unit-medal modules.

## Result

- Each unit-medal module now records compiled source paths, source file extension counts, source byte/line facts, generated medal text byte/line facts, generated localization text byte/line facts, compiled PDX/localization output paths, source file stem, and `file_summaries_by_path`.
- `fascism_order_brave` records `common/unit_medals/00_default.txt`, 5,751 source bytes, 234 source lines, 296 generated medal bytes, 18 generated medal lines, 516 generated localization bytes, 29 generated localization lines, and output `common/unit_medals/fascism_order_brave.txt`.
- The regenerated tree has 16 `legacy/source.yaml` manifests, one unique compiled source file, 16 source path references, 92,016 compiled source bytes, 3,744 compiled source lines, 4,732 generated medal bytes, 279 generated medal lines, 8,425 generated localization bytes, and 464 generated localization lines.
- Existing unit-medal browsing metadata is preserved: 160 owned localization rows, ten localization languages per module, shared `@cost = 30` header metadata, field order, icon/frame/cost fields, availability roots, unit-modifier roots, and one-time-effect roots.

## Verification

- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k unit_medal_importer_extracts_generic_provenance_contract` failed before implementation on missing `compiled_source_paths`, then passed after the importer change.
- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k pihc3_unit_medal` passed with 3 selected tests.
- `rtk uv run black --check projects/PIHC3/scripts/migrate_pihc2_unit_medals.py tests/test_pihc3_migration_contracts.py` passed.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_unit_medals.py tests/test_pihc3_migration_contracts.py` reported `OK: 2 file(s) - no banned imports`.
- `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-unit-medal-native-metadata-build.json` passed with 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.
- The build manifest contains 16 `module:unit_medal/<id>` PDX artifacts, 160 module-owned unit-medal localization artifacts, and 0 copy-root-owned `common/unit_medals` artifacts.

## Remaining Work

- Keep medal icon atlas parity, ideology mapping review, commander XP/effect balance, and higher-level unit-medal authoring for later parity slices.
- Current shared slots remain sufficient: `def.txt` owns the wrapped PDX record and `main.loc` owns the selected localization rows.
