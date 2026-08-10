# PIHC3 Doctrine Metadata Progress

Date: 2026-06-15 07:36

Linear: TAL-000

## Done

- Added a focused doctrine migration contract covering one compiled land grand doctrine, one compiled air subdoctrine, and one source-only reward-collapsed doctrine node.
- Added `import_doctrines(...)` so the doctrine importer can generate into test destinations.
- Mirrored PIHC2 source and compiled doctrine structure into native `meta.yaml` settings, including category, XP type, tree position, XOR alternatives, path edges, source categories, scalar/block/list summaries, compiled folder/track ids, XP/icon/localization keys, track ids, milestone counts, rewards, and `compiled_block_found`.
- Regenerated all 94 native doctrine modules and preserved PIHC2 `info.json`, `locs.txt`, and `default.png` under each module's non-emitted `legacy/` folder.

## Verification

- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k doctrine` passed 3 tests.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_doctrines.py tests/test_pihc3_migration_contracts.py` passed.
- `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-doctrine-metadata-dry-build.json` reported 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.
- `rtk git diff --check` passed. A trailing-whitespace scan over touched tracked files and generated doctrine PDX/meta/loc/source YAML outputs had no matches; copied PIHC2 `legacy/info.json` files preserve source whitespace as evidence.

## Risks Or Blockers

- The legacy 1.17+ doctrine generator only emits 51 of the 94 PIHC2 source folders as top-level compiled doctrine records. The remaining 43 are marked `compiled_block_found: false` and still need structured reward/milestone reconstruction in a future doctrine authoring slice.

## Next

- Continue improving thin non-map families with shared metadata and focused dry-build checks.
