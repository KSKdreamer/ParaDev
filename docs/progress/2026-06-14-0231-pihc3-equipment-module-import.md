# PIHC3 Equipment Module Import

## Summary

Imported the missing PIHC2 tank/plane equipment designer module layer into PIHC3 native source modules.

## Changes

- Added `projects/PIHC3/system/equipment_module_family.py`.
- Added `projects/PIHC3/scripts/migrate_pihc2_equipment_modules.py`.
- Registered `equipment_module` through `python_modules`.
- Added `equipment_module_category` as a generic simple-source family.
- Imported:
  - 130 `equipment_module` modules under `projects/PIHC3/src/modules/equipment_module`.
  - 49 `equipment_module_category` modules under `projects/PIHC3/src/modules/equipment_module_category`.
- Added copy-root excludes for native tank/plane module aggregate files, module/category DDS icons, copied per-sprite GFX files, and module/category localization.
- Updated equipment migration, copy overlay, and design inventory docs.

## Legacy Evidence

PIHC2 builds the layer in `scripts/C07_add_military.py`:

- `AddModules(module_type="tank", path=resources/equipments/modules/tank)`
- `AddModules(module_type="plane", path=resources/equipments/modules/plane)`

Compiled PIHC_dev parity files:

- `common/units/equipment/modules/00_tank_modules.txt`
- `common/units/equipment/modules/00_plane_modules.txt`
- `gfx/interface/modules/MODULE_*.dds`
- `gfx/interface/modules/GFX_EMI_*.dds`
- `interface/modules/MODULE_*.gfx`
- `interface/modules/GFX_EMI_*.gfx`

## Verification

- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q`
  - `8 passed`
- PIHC3 dry build:
  - modules: 3,032
  - collections: 62
  - artifacts: 25,722
  - diagnostics: 4,183 warnings
  - errors: 0
  - blocked: false
- Aggregate spot checks:
  - `common/units/equipment/modules/00_tank_modules.txt` owned by `project:PIHC3`.
  - `common/units/equipment/modules/00_plane_modules.txt` owned by `project:PIHC3`.
  - `interface/PIHC3_equipment_modules.gfx` contains 260 module sprite declarations.
  - `interface/PIHC3_equipment_module_categories.gfx` contains 49 category sprite declarations.
  - equipment-module copy-shadow filter returned 0 matches.

## Remaining Work

Regular equipment still preserves compiled PDX instead of reconstructing inheritance from PIHC2 JSON. Ship designer modules, designer-window GUI fragments generated from `module_slots`, and deeper balancing validators remain future slices.
