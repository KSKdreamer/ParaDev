# PIHC3 Bookmark Import

Date: 2026-06-14 09:01 Asia/Shanghai

## Summary

- Added `projects/PIHC3/scripts/migrate_pihc2_bookmarks.py` to import compiled PIHC2 bookmarks from `PIHC_dev/common/bookmarks/PIHC.txt`.
- Regenerated 2 `src/modules/bookmark` modules: `PIHC` and `PIHC_DIE_NEBENWELT`.
- Updated the project-local `bookmark` family with a shared `picture` copy slot for `gfx/interface/bookmarks/*.dds`.
- Excluded `common/bookmarks/*.txt` and `gfx/interface/bookmarks/*.dds` from the PIHC_dev copy overlay so generated PIHC3 modules own reviewed bookmark definitions and picture files.
- Updated migration docs and the legacy inventory with the bookmark cutover.

## Verification

- Red check before implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'bookmark'` failed on the missing `picture` slot and missing `projects/PIHC3/scripts/migrate_pihc2_bookmarks.py`.
- Focused green after implementation and localization ownership fix: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'ideology or bookmark'` passed `4 passed, 60 deselected`.
- Formatting/style: `rtk uv run black projects/PIHC3/scripts/migrate_pihc2_bookmarks.py tests/test_pihc3_migration_contracts.py` and `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_bookmarks.py projects/PIHC3/scripts/migrate_pihc2_ideologies.py tests/test_pihc3_migration_contracts.py` completed cleanly.
- Importer run: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_bookmarks.py --clean` imported 2 modules.
- Full PIHC3 emit build: `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json` completed with 11,851 modules, 62 collections, 36,178 artifacts, 3,842 diagnostics, 0 errors, and `blocked: false`.
- Manifest check found 8 bookmark-owned artifacts and 0 bookmark diagnostics.

## Notes

- Bookmark modules intentionally import only their own name/description localization. Country history keys such as `C01_DESC` remain owned by native country modules or copied shared localization to avoid duplicate localization errors.
- The mixed `interface/PIHC_bookmark_countries_hint.gfx` file remains copy-overlay owned because it also declares country-selection UI sprites.
