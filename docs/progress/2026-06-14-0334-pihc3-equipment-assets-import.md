# PIHC3 Equipment Assets Import Progress

Date: 2026-06-14 03:34

Linear: TAL-299

## Done

- Reworked the PIHC3 `equipment` family to use typed `def`, `loc`, and path-preserving `assets` source slots.
- Replaced the previous icon-only equipment migration with 167 compiled equipment modules: 34 `ARCHETYPE_*` modules and 133 `EQUIPMENT_*` modules.
- Preserved compiled equipment UI assets under their real HOI4 paths, including:
  `gfx/interface/equipments/*.dds`, `interface/equipments/*.gfx`, and `interface/equipmentdesigner/*.gui`.
- Switched equipment localization to compiled PIHC_dev localization rows while retaining readable legacy folder notes.
- Added copy-root excludes for generated equipment PDX, localization, equipment sprites, designer GUI files, and interface DDS files.

## Verification

- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k equipment` passed: 4 passed.
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q` passed: 16 passed.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_equipments.py tests/test_pihc3_migration_contracts.py` passed.
- `rtk bash scripts/flake.bash --ci` passed.
- `Project.load("projects/PIHC3").build(emit_artifacts=True, emit_manifests=True)` completed with `dry_run False`, 3,169 modules, 62 collections, 25,865 artifacts, 3,842 warnings, 0 errors, and `blocked False`.
- `rtk bash scripts/test.bash` passed: 571 passed.

## Risks Or Blockers

- The build still reports the existing warning baseline, but no blocking diagnostics or errors.

## Next

- Continue non-map migration with another GUI-empty family, likely equipment-adjacent generated sources such as common equipment support files or technology/resource surfaces.
