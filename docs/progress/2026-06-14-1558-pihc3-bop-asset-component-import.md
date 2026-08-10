# PIHC3 Balance Of Power Asset Component Import

Date: 2026-06-14 15:58 Asia/Shanghai

## Summary

- Added `projects/PIHC3/scripts/migrate_pihc2_balance_of_power_asset_components.py` to import compiled PIHC_dev BOP sprite declarations.
- Added the project-local `balance_of_power_asset_component` family with a generic path-preserving copy slot.
- Generated 8 `src/modules/balance_of_power_asset_component` modules from `interface/bop/BOP_*.gfx`.
- Excluded reviewed BOP GFX declarations from the PIHC_dev copy overlay, while leaving paired DDS side icons with native `balance_of_power` modules.
- Updated the BOP migration note, new BOP asset-component note, copy-overlay baseline, main migration design, and legacy inventory.

## Verification

- Red check before implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k balance_of_power_asset_component` failed on the missing `balance_of_power_asset_component` family and missing `projects/PIHC3/scripts/migrate_pihc2_balance_of_power_asset_components.py`.
- Focused green after implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k balance_of_power_asset_component` passed `2 passed, 112 deselected`.
- Formatting/style: `rtk uv run black projects/PIHC3/scripts/migrate_pihc2_balance_of_power_asset_components.py tests/test_pihc3_migration_contracts.py` completed; `rtk uv run python /Users/magolor/.agents/skills/heaven-style-0.1.1.1/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_balance_of_power_asset_components.py tests/test_pihc3_migration_contracts.py` completed cleanly.
- Importer run: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_balance_of_power_asset_components.py --clean` imported 8 modules.
- Build ownership checks confirmed all 8 reviewed BOP GFX paths are owned by `balance_of_power_asset_component`, with 0 copy-root-owned reviewed BOP GFX paths remaining.
- The same build manifest confirms representative BOP DDS side icons remain owned by native `balance_of_power` modules.
- Full PIHC3 emit build: `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json` completed with 16,451 modules, 62 collections, 36,212 artifacts, 1,857 diagnostics, 0 errors, and `blocked: false`.

## Notes

- The importer preserves compiled BOP GFX bytes exactly and does not regenerate sprite declarations.
- Full migration contracts were intentionally not run in this slice to reduce CPU load while other ParaDev workers are refactoring. Focused tests plus a full PIHC3 compile check covered the changed family.
