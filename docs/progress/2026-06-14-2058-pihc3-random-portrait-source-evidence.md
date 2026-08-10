# 2026-06-14 20:58 CST - PIHC3 Random Portrait Source Evidence

## Done

- Extended the existing `portrait_asset_component` importer to preserve PIHC2 `resources/characters_random` source files as module-local legacy evidence.
- Copied 132 available `.txt`/`.png` source files into matching random portrait asset modules under `legacy/characters_random/`:
  - `pony_military`: 64 files
  - `pony_political`: 30 files
  - `pony_scientist`: 38 files
- Recorded those source paths in each matching module's `meta.yaml` settings and `legacy/source.yaml`.
- Left emitted game artifacts unchanged: compiled `interface/portraits/*.gfx` and `gfx/leaders/*.dds` files still use the existing shared copy slot.
- Updated character and portrait migration docs to stop describing random-character portrait outputs as copy-overlay owned and to clarify that source files are now preserved as evidence.

## Verification

- Red check first: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k portrait_asset_component` failed because random portrait components lacked `legacy_source_paths`.
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k portrait_asset_component`
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_portrait_asset_components.py --clean`
- Byte-checked `legacy/characters_random/pony_military/001.txt` against PIHC2 source.
- `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-portrait-random-source-build.json`

The build reports 16,581 modules across 87 families, 36,856 artifacts, 713 diagnostics, 0 errors, and `blocked: false`. The manifest still contains 258 `portrait_asset_component` modules and 1,917 portrait asset artifacts; representative random portrait GFX/DDS outputs are owned by `portrait_asset_component` with 0 copy-root ownership.

## Risk

- This is source evidence preservation, not editable random portrait pool reconstruction.
- The compiled `RANDOM_CHARACTER_KIRIN` bundle has no matching files in the local PIHC2 `resources/characters_random/kirin` folder, so it remains compiled-output evidence only.
- The artifact count changed since the previous build because parallel work added building/modifier localization outputs; no `legacy/characters_random` files are emitted as artifacts.

## Next

- Continue source-evidence upgrades where PIHC2 has raw source data that current PIHC3 modules only preserve as compiled game outputs.
