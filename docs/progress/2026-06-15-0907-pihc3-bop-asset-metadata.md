# 2026-06-15 09:07 PIHC3 BOP Asset Metadata

## Slice

Continued the PIHC2 to PIHC3 migration by enriching `balance_of_power_asset_component` modules. The family still uses one shared path-preserving copy slot for `interface/bop/BOP_*.gfx`; paired DDS side icons remain owned by native `balance_of_power` modules.

## Changes

- Added a contract test for the compiled `BOP_C01_COZY_GLOW_EXHAUSTION` sprite declaration metadata.
- Updated `projects/PIHC3/scripts/migrate_pihc2_balance_of_power_asset_components.py` to parse GFX sprite declarations and referenced DDS headers.
- Regenerated the 8 ignored PIHC3 BOP asset modules with component ids, asset keys, sprite names, texture paths, external texture ownership, referenced image dimensions, mipmaps, byte sizes, FourCC values, header sizes, and per-source summaries.
- Updated the PIHC3 migration notes and the shared legacy inventory.

## Verification

- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k balance_of_power_asset_component` passed: 3 passed, 180 deselected.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_balance_of_power_asset_components.py tests/test_pihc3_migration_contracts.py` passed.
- `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json` passed with 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.
- The build manifest contains 8 `balance_of_power_asset_component`-owned GFX artifacts, and representative BOP side DDS files remain owned by native `balance_of_power` modules.
