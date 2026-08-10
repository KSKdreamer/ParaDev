# PIHC3 Building Import Progress

Date: 2026-06-14 03:00

Linear: TAL-299

## Done

- Replaced the old two-file aggregate building import with 38 individual PIHC3 `building` modules.
- Added `projects/PIHC3/scripts/migrate_pihc2_buildings.py` to split compiled `common/buildings/*.txt` `buildings = { ... }` entries into one module per building.
- Preserved real legacy building localization from `localisation/replace/BUILDINGS_l_english.yml` and `BUILDINGS_l_simp_chinese.yml` for custom buildings without fabricating fallback loc rows for vanilla buildings.
- Confirmed the GUI-facing module count now includes individual buildings such as `bitumen_infrastructure`, `farm_complex`, `research_complex`, and `pihc_bgfx_fog`.

## Verification

- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q` passed: 12 passed.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_entities.py projects/PIHC3/scripts/migrate_pihc2_buildings.py tests/test_pihc3_migration_contracts.py` passed.
- `rtk bash scripts/flake.bash --ci` passed.
- `Project.load("projects/PIHC3").build(emit_artifacts=True, emit_manifests=True)` completed with `dry_run False`, 3,069 modules, 62 collections, 25,790 artifacts, 4,183 warnings, 0 errors, and `blocked False`.
- Verified emitted building files under `projects/PIHC3/build/mod`, including `common/buildings/bitumen_infrastructure.txt`, `common/buildings/pihc_bgfx_fog.txt`, and English/Chinese `bitumen_infrastructure` localization.
- `rtk bash scripts/test.bash` passed: 567 passed.

## Risks Or Blockers

- The build still reports the existing warning baseline, but no blocking diagnostics or errors.

## Next

- Continue with another GUI-empty non-map family, likely modifiers or equipment archetypes/types.
