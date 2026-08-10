# 2026-06-15 08:37 PIHC3 Intelligence Agency Asset Metadata

## Slice

Continued the PIHC2 to PIHC3 migration by enriching `intelligence_agency_asset_component` modules. The family still uses one shared path-preserving copy slot for `interface/intelligence_agencies/*.gfx` and `gfx/interface/intelligence_agencies/*.dds`, but generated `meta.yaml` settings now expose GUI-browsable sprite and DDS facts.

## Changes

- Added a contract test for the compiled `INTEL_AGENCY_BOC` asset module metadata.
- Updated `projects/PIHC3/scripts/migrate_pihc2_intelligence_agency_asset_components.py` to parse GFX sprite declarations and DDS headers.
- Regenerated the 9 ignored PIHC3 intelligence agency asset modules with component ids, source counts, sprite names, texture paths, `noOfFrames`, image dimensions, mipmaps, byte sizes, FourCC values, header sizes, and per-source summaries.
- Updated the PIHC3 migration notes and the shared legacy inventory.

## Verification

- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k intelligence_agency_asset_component` passed: 3 passed, 177 deselected.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_intelligence_agency_asset_components.py tests/test_pihc3_migration_contracts.py` passed.
- `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json` passed with 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.
- The build manifest contains 18 `intelligence_agency_asset_component`-owned GFX/DDS artifacts.
