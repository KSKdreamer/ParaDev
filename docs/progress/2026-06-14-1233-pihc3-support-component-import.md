# PIHC3 Support Component Import

Date: 2026-06-14 12:33 Asia/Shanghai

## Summary

- Added `projects/PIHC3/scripts/migrate_pihc2_support_components.py` to import compiled PIHC_dev miscellaneous support files.
- Added the project-local `support_component` family with a generic path-preserving PDX slot.
- Regenerated 4 `src/modules/support_component` modules:
  - 1 `country_metadata/*.txt` file;
  - 1 `tutorial/*.txt` file;
  - 2 `gfx/interface/equipmentdesigner/graphic_db/*.txt` files.
- Excluded those reviewed support paths from the PIHC_dev copy overlay.
- Updated the support-component migration note, copy-overlay baseline, main migration design, and legacy inventory.

## Verification

- Red check before implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k support_component` failed on the missing `support_component` family and missing `projects/PIHC3/scripts/migrate_pihc2_support_components.py`.
- Focused green after implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k support_component` passed `2 passed, 82 deselected`.
- Formatting/style: `rtk uv run black projects/PIHC3/scripts/migrate_pihc2_support_components.py tests/test_pihc3_migration_contracts.py` and `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_support_components.py tests/test_pihc3_migration_contracts.py` completed cleanly.
- Importer run: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_support_components.py --clean` imported 4 modules.
- Full PIHC3 emit build: `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json` completed with 12,116 modules, 62 collections, 36,214 artifacts, 3,842 diagnostics, 0 errors, and `blocked: false`.
- Manifest check found 4 support-component modules, 4 support-component-owned PDX artifacts, and 0 build errors.

## Notes

- The importer preserves compiled PIHC_dev support files as game-relative PDX sources with one normalized trailing newline instead of splitting records into editable objects.
- Loading-screen DDS assets and broad interface GUI/GFX files remain copy-overlay owned or future asset-support work.
- Higher-level editable support authoring remains future work only where it proves useful.
