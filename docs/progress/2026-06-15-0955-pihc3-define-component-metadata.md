# 2026-06-15 09:55 PIHC3 Define Component Metadata

## Slice

Continued the PIHC2 to PIHC3 migration by enriching `define_component` modules. The family still uses one shared path-preserving copy slot for `common/defines/*.lua`, but generated `meta.yaml` settings now expose GUI-browsable Lua and `NDefines` metadata.

## Changes

- Added a contract test for compiled define metadata covering `pihc_defines.lua` and `nuke_defines.lua`.
- Updated `projects/PIHC3/scripts/migrate_pihc2_define_components.py` to record common component/file identity, Lua line counts, direct `NDefines` assignment counts, namespace counts, define keys, define values, and a compact Lua summary.
- Regenerated the 6 ignored PIHC3 define-component modules with 285 direct assignments across 16 `NDefines` namespaces and 392 total Lua lines.
- Updated the PIHC3 migration notes and the shared legacy inventory.

## Verification

- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k define_component` passed: 3 passed, 184 deselected.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_define_components.py tests/test_pihc3_migration_contracts.py` passed.
- `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json` passed with 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.
- The build manifest contains 6 `define_component`-owned Lua artifacts.
