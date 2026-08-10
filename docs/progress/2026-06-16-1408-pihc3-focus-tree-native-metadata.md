# PIHC3 Focus Tree Native Metadata

## Scope

- Continued PIHC2 focus migration without splitting compiled focus trees into per-node modules.
- Enhanced `projects/PIHC3/scripts/migrate_pihc2_focuses.py` so every focus-tree module records PIHC2 source inventory, tree/focus `info.json` summaries, localization row counts, source icon summaries, and compiled focus file facts.
- Added `focus_tree.settings_keys` in `projects/PIHC3/paradev.yaml` so generic surfaces can discover the new metadata fields.
- Regenerated all 28 ignored PIHC3 focus-tree modules with `--clean`.

## Result

- The 28 focus-tree modules now expose 38 settings each instead of 12.
- Metadata records 2,024 non-hidden PIHC2 source files, 28 tree-level `info.json` files, 517 source icon summaries, 1,689 localization keys, and 738 compiled focus blocks.
- `C08_PARTII` now exposes source folder counts, per-focus `info.json` field counts, `default.png` dimensions, localization row counts, and compiled `common/national_focus/C08_PARTII.txt` byte/line facts.
- The build output contains 28 focus-tree PDX artifacts, 38 focus-tree localization artifacts, and 1,477 focus-asset artifacts.

## Verification

- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k focus_tree_importer_extracts_source_localization_and_image_metadata_contract` failed before implementation on missing `module_id`, then passed after the importer change.
- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k focus_tree` passed with 2 selected tests.
- `rtk uv run black --check projects/PIHC3/scripts/migrate_pihc2_focuses.py tests/test_pihc3_migration_contracts.py` passed.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_focuses.py tests/test_pihc3_migration_contracts.py` reported `OK: 2 file(s) - no banned imports`.
- `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-focus-tree-native-metadata-build.json` passed with 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.

## Remaining Work

- Keep per-node editable focus reconstruction as a later slice unless GUI workflows require it.
- Review GUI-first layout parity and no-focus guard mutation behavior against PIHC2 before changing gameplay generation.
