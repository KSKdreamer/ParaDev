# 2026-06-15 09:16 PIHC3 Loading Screen Metadata

## Slice

Continued the PIHC2 to PIHC3 migration by enriching `loading_screen_component` modules. The family still uses one shared path-preserving copy slot for `gfx/loadingscreens/*.dds`, but generated `meta.yaml` settings now expose GUI-browsable DDS facts.

## Changes

- Added a contract test for compiled `load_1.dds` and `load_ncns_chi.dds` metadata.
- Updated `projects/PIHC3/scripts/migrate_pihc2_loading_screen_components.py` to parse DDS headers and derive aspect ratios.
- Regenerated the 43 ignored PIHC3 loading-screen modules with component ids, asset keys, dimensions, aspect ratios, mipmap counts, byte sizes, FourCC values, RGB bit counts, header sizes, and per-file summaries.
- Updated the PIHC3 migration notes and the shared legacy inventory.

## Verification

- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k loading_screen_component` passed: 3 passed, 181 deselected.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_loading_screen_components.py tests/test_pihc3_migration_contracts.py` passed.
- `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json` passed with 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.
- The build manifest contains 43 `loading_screen_component`-owned DDS artifacts.
