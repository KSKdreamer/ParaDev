# 2026-06-16 09:02 PIHC3 balance-of-power metadata

## Scope

Continued the non-map PIHC2 to PIHC3 migration by enriching native `balance_of_power` module metadata. The module family still uses shared generic slots for `def.txt`, `main.loc`, and side-icon copies; this slice only exposes compiled BOP structure in `meta.yaml` for GUI browsing and parity review.

## Changes

- Added a red metadata contract for generated balance-of-power `meta.yaml` settings.
- Added native BOP importer metadata for BOP ids, source slot counts, `initial_value`, `decision_category`, left/right side ids, side icon sprite keys, side and neutral range counts, ordered range ids, range bounds, shallow `on_activate`/`on_deactivate` root-key counts, localization languages and keys, and compiled icon file/source/byte-size facts.
- Regenerated all 8 native `balance_of_power` modules under `projects/PIHC3/src/modules/balance_of_power/`.
- Updated the BOP migration note, PIHC3 design summary, and legacy inventory.

## Evidence

- Red contract: `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k balance_of_power_importer_extracts_metadata_contract` failed with `KeyError: 'balance_of_power_id'`.
- Green focused contract before regeneration: `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k balance_of_power_importer_extracts_metadata_contract` passed with 1 test and 219 deselected.
- Regeneration: `Migrated balance-of-power modules: 8`.
- Metadata coverage: 8 native balance-of-power modules now have 28 settings keys each.
- Formatting: `rtk uv run black projects/PIHC3/scripts/migrate_pihc2_bops.py tests/test_pihc3_migration_contracts.py` left both files unchanged.
- Green focused group after regeneration: `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k balance_of_power` passed with 4 tests and 216 deselected.
- Black check: `rtk uv run black --check projects/PIHC3/scripts/migrate_pihc2_bops.py tests/test_pihc3_migration_contracts.py` passed.
- Heaven-style scan: `OK: 2 file(s) - no banned imports`.
- Build: `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json`.
- Build summary: 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, `blocked: false`.
- Build ownership: 40 `module:balance_of_power/...` artifacts, including 8 PDX definitions, 16 side-icon DDS copies, and 16 generated localization files. The reviewed native BOP `common/bop/BOP_*` and `gfx/interface/bop/BOP_*.dds` paths have 0 copy-root-owned artifacts.

## Follow-Up

Decision-category workflows, side-specific events and decisions, dynamic side graphics, scripted state changes, and gameplay balancing review remain future BOP slices. This slice improves browsing and audit metadata without changing compiled output ownership.
