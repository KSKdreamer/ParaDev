# 2026-06-15 08:57 PIHC3 Special Project Asset Metadata

## Slice

Continued the PIHC2 to PIHC3 migration by enriching `special_project_asset_component` modules. The family still uses one shared path-preserving copy slot for project sprite GFX declarations, the shared `PIHC_special_projects.gfx`, and root-level shared DDS files, while project icon DDS files remain owned by native `special_project` modules.

## Changes

- Added a contract test for the compiled `PIHC_SPECIAL_PROJECTS` shared asset bundle and a project-only GFX module.
- Updated `projects/PIHC3/scripts/migrate_pihc2_special_project_asset_components.py` to parse GFX sprite declarations and DDS headers.
- Regenerated the 26 ignored PIHC3 special-project asset modules with component ids, source counts, sprite names, texture paths, external project-icon references, included/unreferenced DDS paths, `noOfFrames`, dimensions, mipmaps, byte sizes, FourCC values, header sizes, and per-source summaries.
- Updated the PIHC3 migration notes and the shared legacy inventory.

## Verification

- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k special_project_asset_component` passed: 3 passed, 179 deselected.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_special_project_asset_components.py tests/test_pihc3_migration_contracts.py` passed.
- `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json` passed with 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.
- The build manifest contains 43 `special_project_asset_component`-owned GFX/DDS artifacts.
