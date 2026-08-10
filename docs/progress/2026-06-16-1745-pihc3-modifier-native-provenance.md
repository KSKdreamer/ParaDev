# PIHC3 Modifier Native Provenance

## Scope

- Continued PIHC2 modifier migration without adding type-specific slots beyond the existing native `def.txt`, `main.loc`, and shared path-preserving asset copy slots.
- Enhanced `projects/PIHC3/scripts/migrate_pihc2_modifiers.py` so every native modifier module exposes generic PDX, localization, and compiled modifier-asset provenance in both `meta.yaml` settings and `legacy/source.yaml`.
- Regenerated all ignored native modifier modules with `--clean`: 107 modules.

## Result

- Each native modifier module now records compiled source paths, source file extension counts, source byte/line facts, generated modifier text byte/line facts, generated localization text byte/line facts, compiled PDX/localization output paths, source file stem, `file_summaries_by_path`, compiled asset paths, asset extension counts, total compiled asset bytes, and per-asset byte-size summaries.
- `MODIFIER_EVERFREE_FOREST` records `common/modifiers/MODIFIER_EVERFREE_FOREST.txt`, 225 source bytes, 9 source lines, 205 generated modifier bytes, 9 generated modifier lines, 117 generated localization bytes, 5 generated localization lines, 2 compiled modifier assets, 2,226 compiled asset bytes, and output `common/modifiers/MODIFIER_EVERFREE_FOREST.txt`.
- The regenerated tree has 107 `legacy/source.yaml` manifests, 16 unique compiled source files, 107 source path references, 779,228 compiled source bytes, 29,800 compiled source lines, 13,870 generated modifier bytes, 568 generated modifier lines, 28,449 generated localization bytes, and 1,430 generated localization lines.
- The regenerated tree also has 14 copied compiled modifier asset files totaling 15,656 bytes: 7 DDS files and 7 GFX files.
- Existing modifier browsing metadata is preserved: 559 localization keys, 495 emitted localization rows, 33 BOP rows owned by balance-of-power modules, 55 modules with module-local localization, 21 PIHC2 resource evidence paths, and 7 modules with compiled modifier assets.

## Verification

- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k modifier_importer_extracts_generic_provenance_contract` failed before implementation on missing `compiled_source_paths`, then passed after the importer change.
- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k 'modifier_importer or modifier_family'` passed with 6 selected tests.
- `rtk uv run black --check projects/PIHC3/scripts/migrate_pihc2_modifiers.py tests/test_pihc3_migration_contracts.py` passed.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_modifiers.py tests/test_pihc3_migration_contracts.py` reported `OK: 2 file(s) - no banned imports`.
- `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-modifier-native-provenance-build.json` passed with 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.
- The build manifest contains 107 `module:modifier/<id>` PDX artifacts, 485 module-owned modifier localization artifacts, 14 module-owned modifier asset artifacts, 0 copy-root-owned modifier artifacts, and 0 emitted `legacy/` artifacts.

## Remaining Work

- Keep dynamic and aggregate opinion modifier source reconstruction from decisions, focuses, and events for later parity slices.
- Current shared slots remain sufficient: `def.txt` owns the single modifier PDX record, `main.loc` owns selected localization rows, and `assets` owns compiled DDS/GFX files.
