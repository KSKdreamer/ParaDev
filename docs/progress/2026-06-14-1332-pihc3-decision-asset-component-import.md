# PIHC3 Decision Asset Component Import

Date: 2026-06-14 13:32 Asia/Shanghai

## Summary

- Added `projects/PIHC3/scripts/migrate_pihc2_decision_asset_components.py` to import compiled PIHC_dev decision sprite/icon assets.
- Added the project-local `decision_asset_component` family with a generic path-preserving copy slot.
- Regenerated 464 `src/modules/decision_asset_component` modules from 463 `interface/decisions/*.gfx` files and 462 `gfx/interface/decisions/*.dds` files.
- Excluded those reviewed decision sprite/icon paths from the PIHC_dev copy overlay.
- Updated the decision-asset-component migration note, decision migration note, copy-overlay baseline, main migration design, and legacy inventory.

## Verification

- Red check before implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k decision_asset_component` failed on the missing `decision_asset_component` family and missing `projects/PIHC3/scripts/migrate_pihc2_decision_asset_components.py`.
- Focused green after implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k decision_asset_component` passed `2 passed, 88 deselected`.
- Formatting/style: `rtk uv run black projects/PIHC3/scripts/migrate_pihc2_decision_asset_components.py tests/test_pihc3_migration_contracts.py` completed cleanly; `rtk uv run python /Users/magolor/.agents/skills/heaven-style-0.1.1.1/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_decision_asset_components.py tests/test_pihc3_migration_contracts.py` completed cleanly.
- Importer run: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_decision_asset_components.py --clean` imported 464 modules.
- Byte checks confirmed generated `DECISION_C01_GREAT` DDS/GFX assets and the unmatched `DECISION_C08_16-A`/`DECISION_C08_16-A.1A` assets match the PIHC_dev source bytes exactly.
- Full PIHC3 emit build: `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json` completed with 12,634 modules, 62 collections, 36,214 artifacts, 3,842 diagnostics, 0 errors, and `blocked: false`.

## Notes

- The importer groups assets by file stem and preserves odd legacy mismatches instead of inventing synthetic pairings.
- Category GUI files, scripted GUI fragments, and broader interface assets remain copy-overlay owned or future asset-support work.
