# 2026-06-29 21:16 PIHC3 Building Icon Strip

## Summary

- Added an SDK build postprocessor for HOI4 building modules that generates `gfx/interface/buildings/building_icon_strip.dds` from per-building `icon` sources.
- Rewrites emitted building definitions with deterministic `icon_frame` values and updates `GFX_buildings_strip.noOfFrames` in emitted interface GFX files.
- Extended PIHC3 migration contracts so building modules own their icon copy slot and importer metadata instead of relying on a legacy shared strip source.
- Verified the true PIHC3 project build emits a 71-frame strip while preserving sentinel `icon_frame = 9999` for system fog buildings.

## Verification

- `rtk bash scripts/test.bash tests/test_hoi4_building_icons.py tests/test_pihc3_migration_contracts.py -q -k "building_icon or building_importer or building_family"`
- `rtk uv run python - <<'PY' ... Project.load('projects/PIHC3').build(family='building') ... PY`
- `rtk uv run python - <<'PY' ... Project.load('projects/PIHC3').build(family='building', emit_artifacts=True, emit_manifests=True, full_rebuild=False) ... PY`
- `rtk bash scripts/test.bash tests/test_project_build.py -q -k "building_family_emit_generates_icon_strip"`
- `rtk bash scripts/test.bash tests/test_project_build.py tests/test_hoi4_building_icons.py tests/test_pihc3_migration_contracts.py -q -k "building_family_emit_generates_icon_strip or building_icon or building_importer or building_family"`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py src/paradev/games/hoi4/building_icons.py tests/test_project_build.py tests/test_hoi4_building_icons.py tests/test_pihc3_migration_contracts.py`
- `rtk git diff --check -- src/paradev/sdk/project.py src/paradev/games/hoi4/building_icons.py tests/test_project_build.py tests/test_hoi4_building_icons.py tests/test_pihc3_migration_contracts.py docs/superpowers/plans/2026-06-29-pihc3-building-icons.md docs/superpowers/specs/2026-06-29-pihc3-building-icons-design.md`

## Notes

- The PIHC3 nested repository has pre-existing staged interface/progressbar work, so this slice leaves PIHC3 staging untouched.
