# PIHC3 History Component Import

Date: 2026-06-14 12:16 Asia/Shanghai

## Summary

- Added `projects/PIHC3/scripts/migrate_pihc2_history_components.py` to import compiled PIHC_dev general-history support files.
- Added the project-local `history_component` family with a generic path-preserving PDX slot.
- Regenerated 30 `src/modules/history_component` modules from `history/general/*.txt`.
- Excluded `history/general/*.txt` from the PIHC_dev copy overlay.
- Updated the history-component migration note, copy-overlay baseline, main migration design, and legacy inventory.

## Verification

- Red check before implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k history_component` failed on the missing `history_component` family and missing `projects/PIHC3/scripts/migrate_pihc2_history_components.py`.
- Focused green after implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k history_component` passed `2 passed, 80 deselected`.
- Formatting/style: `rtk uv run black projects/PIHC3/scripts/migrate_pihc2_history_components.py tests/test_pihc3_migration_contracts.py` and `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_history_components.py tests/test_pihc3_migration_contracts.py` completed cleanly.
- Importer run: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_history_components.py --clean` imported 30 modules.
- Full PIHC3 emit build: `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json` completed with 12,112 modules, 62 collections, 36,214 artifacts, 3,842 diagnostics, 0 errors, and `blocked: false`.
- Manifest check found 30 history-component modules, 30 history-component-owned PDX artifacts, and 0 build errors.

## Notes

- The importer preserves compiled PIHC_dev support files as game-relative PDX sources with one normalized trailing newline instead of splitting records into editable objects.
- Country history remains owned by `country_component`; unit/OOB history remains owned by `division`; state history remains skipped as map-adjacent work.
- Higher-level editable general-history authoring remains future work only where it proves useful.
