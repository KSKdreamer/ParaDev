# PIHC3 Focus-Tree Import Progress

Date: 2026-06-08 19:24

Linear: TAL-297, TAL-298

## Done

- Replaced stale `projects/PIHC3/scripts/migrate_pihc2_focuses.py` with the current-layout focus-tree importer.
- Imported 28 PIHC2 `resources/focuses/<TREE>` folders into `projects/PIHC3/src/modules/focus_tree`.
- Preserved compiled PIHC_dev `common/national_focus/<TREE>.txt` files as `def.pdx`, consolidated English/Simplified Chinese focus localization as `main.loc`, and recorded source evidence in `legacy/source.yaml`.
- Added a project-local `focus_tree` family so imported trees emit `common/national_focus/<TREE>.txt` without colliding with event namespace localization.
- Kept focus icon binaries out of native modules; the importer lists icon source paths while the copy overlay continues to own generated icon and sprite assets.
- Updated PIHC3 user, migration, copy-overlay, Linear sync, and legacy evidence docs.

## Verification

- `rtk uv run pytest tests/test_sdk_examples.py::test_pihc3_focus_importer_writes_current_module_layout -q`
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_focuses.py --clean`
- `rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json`
- `rtk uv run paradev summary projects/PIHC3 --json` reported 1,148 modules, 25,351 artifacts, 0 diagnostics, 0 errors, and `blocked: false`.

## Risks Or Blockers

- Focus icon DDS generation and sprite declarations remain copy-overlay owned.
- Imported full-tree modules are not yet split into editable per-focus source nodes.
- GUI-first focus layout editing, exact no-focus guard policy, and parity review remain later slices.

## Next

- Add a focus-tree parity reviewer against `PIHC_dev/common/national_focus`.
- Pick the next high-value domain, likely decisions, equipment, countries, achievements, or idea categories.
