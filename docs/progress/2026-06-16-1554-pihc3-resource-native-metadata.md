# PIHC3 Resource Native Metadata

## Scope

- Continued PIHC2 strategic-resource migration without changing the shared `def.txt` and `main.loc` slots.
- Enhanced `projects/PIHC3/scripts/migrate_pihc2_resources.py` so each resource module exposes generic PDX and localization provenance in both `meta.yaml` settings and `legacy/source.yaml`.
- Regenerated all ignored native resource modules with `--clean`: 9 resource modules.

## Result

- Each resource module now records compiled source paths, source file extension counts, source byte/line facts, generated resource text byte/line facts, generated localization text byte/line facts, compiled PDX/localization output paths, source file stem, and `file_summaries_by_path`.
- `crystals` records `common/resources/00_resources.txt`, 802 source bytes, 47 source lines, 80 generated resource bytes, 7 generated resource lines, 526 generated localization bytes, 17 generated localization lines, and output `common/resources/crystals.txt`.
- The regenerated tree has 9 `legacy/source.yaml` manifests, one unique compiled source file, 9 source path references, 7,218 compiled source bytes, 423 compiled source lines, 715 generated resource bytes, 63 generated resource lines, 4,481 generated localization bytes, and 153 generated localization lines.
- Existing resource browsing metadata is preserved: 54 owned localization rows, two localization languages per module, and icon frames 1 through 9.

## Verification

- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k resource_importer_extracts_generic_provenance_contract` failed before implementation on missing `compiled_source_paths`, then passed after the importer change.
- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k resource` passed with 3 selected tests.
- `rtk uv run black --check projects/PIHC3/scripts/migrate_pihc2_resources.py tests/test_pihc3_migration_contracts.py` passed.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_resources.py tests/test_pihc3_migration_contracts.py` reported `OK: 2 file(s) - no banned imports`.
- `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-resource-native-metadata-build.json` passed with 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.
- The build manifest contains 9 `module:resource/<id>` PDX artifacts, 18 module-owned resource localization artifacts across English and Simplified Chinese, and 0 copy-root-owned `common/resources` artifacts.

## Remaining Work

- Keep state resource placement, map review, market/AI balancing, and resource-strip art for later resource parity slices.
- Shared resource strip graphics and topbar/interface files remain owned by component asset families rather than per-resource modules.
