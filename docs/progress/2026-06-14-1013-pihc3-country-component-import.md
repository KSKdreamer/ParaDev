# PIHC3 Country Component Import

Date: 2026-06-14 10:13 Asia/Shanghai

## Summary

- Added `projects/PIHC3/scripts/migrate_pihc2_country_components.py` to import compiled PIHC_dev country support files not owned by native `country` modules.
- Added the project-local `country_component` family with generic path-preserving PDX and localization slots.
- Regenerated 147 `src/modules/country_component` modules:
  - 2 `common/country_tags/*.txt` files;
  - 1 `common/country_tag_aliases/*.txt` file;
  - 77 unowned `common/countries/*.txt` dynamic/cosmetic/color support files;
  - 67 `history/countries/*.txt` setup files.
- Excluded those reviewed country support paths from the PIHC_dev copy overlay so generated PIHC3 modules own the outputs.
- Updated the country migration note, copy-overlay baseline, main migration design, and legacy inventory.

## Verification

- Red check before implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'country_component'` failed on the missing `country_component` family and missing `projects/PIHC3/scripts/migrate_pihc2_country_components.py`.
- Focused green after implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'country_component'` passed `2 passed, 68 deselected`.
- Formatting/style: `rtk uv run black projects/PIHC3/scripts/migrate_pihc2_country_components.py tests/test_pihc3_migration_contracts.py` and `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_country_components.py tests/test_pihc3_migration_contracts.py` completed cleanly.
- Importer run: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_country_components.py --clean` imported 147 modules.
- Full PIHC3 emit build: `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json` completed with 12,026 modules, 62 collections, 36,214 artifacts, 3,842 diagnostics, 0 errors, and `blocked: false`.
- Manifest check found 147 country-component modules, 147 country-component-owned artifacts, and 0 build errors.

## Notes

- The importer uses PIHC2 `resources/countries/<TAG>/info.json` folders to identify the 67 `common/countries/<TAG>.txt` files already owned by native `country` modules, and imports only the remaining `common/countries/*.txt` support files.
- Country history is preserved path-by-path under `country_component` for now because the generic `country` family has one PDX output template; putting both `def.txt` and `history/countries/<TAG>.txt` in one simple-source country module would collide without a custom family.
- Higher-level editable country setup reconstruction, portraits, map ownership, AI setup, and OOB wiring remain future work.
