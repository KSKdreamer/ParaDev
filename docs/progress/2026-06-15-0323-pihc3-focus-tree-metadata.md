# PIHC3 Focus-Tree Metadata Progress

Date: 2026-06-15 03:23

Linear: TAL-000

## Done

- Added a focused migration contract for compiled focus-tree metadata using `C08_PARTII`.
- Extended `projects/PIHC3/scripts/migrate_pihc2_focuses.py` to mirror direct compiled `focus_tree` and `focus = { ... }` records into module metadata.
- Regenerated all 28 focus-tree modules; generated metadata now covers 28 compiled tree wrappers, 738 direct focus blocks, 738 icon keys, and 1,625 localization keys.
- Updated the focus migration note, design summary, copy-overlay note, and legacy inventory with the new metadata scope.

## Verification

- Red: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k focus_tree_importer_extracts_compiled_tree_metadata` failed with missing `settings["focus_tree_count"]`.
- Green: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k focus_tree_importer_extracts_compiled_tree_metadata` passed: 1 passed, 167 deselected.
- Regeneration: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_focuses.py --clean`.
- Dry build: `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-focus-tree-metadata-dry-build.json` reported 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.

## Risks Or Blockers

- Focus-tree metadata intentionally summarizes direct compiled tree and focus records only. Nested rewards, triggers, and scripted effects remain in `def.txt`.
- Imported `focus_tree` modules remain compiled-tree parity modules; editable per-node reconstruction and GUI-first layout review are still future slices.

## Next

- Continue enhancing low-data non-map families with source-owned metadata where it improves GUI browsing without splitting compiled support bundles prematurely.
