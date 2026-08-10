# 2026-06-14 21:10 CST - PIHC3 Technology Source Image Evidence

## Done

- Extended `technology_asset_component` import to preserve PIHC2 `resources/technologies/<TAG>/default.png` files as module-local legacy evidence.
- Copied 277 available source PNGs into matching technology asset modules under `legacy/technologies/<TAG>/default.png`.
- Recorded those source paths in each matching module's `meta.yaml` settings and `legacy/source.yaml`.
- Left emitted game artifacts unchanged: compiled `interface/technologies/*.gfx` and `gfx/interface/technologies/*.dds` files still use the existing shared copy slot.
- Updated technology migration docs and the legacy inventory to describe the non-emitted source image evidence.

## Verification

- Red check first: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k technology_asset_component` failed because technology asset components lacked `legacy_source_paths`.
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k technology_asset_component`
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_technology_asset_components.py --clean`
- Byte-checked `legacy/technologies/FIREARM_I/default.png` against the PIHC2 source image.
- `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-technology-source-images-build.json`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_technology_asset_components.py tests/test_pihc3_migration_contracts.py`
- `rtk git diff --check`

The build reports 16,581 modules across 62 collections, 36,856 artifacts, 713 diagnostics, 0 errors, and `blocked: false`. The manifest still contains 605 `technology_asset_component` artifacts; representative `TECHNOLOGY_FIREARM_I` GFX/DDS outputs are owned by `technology_asset_component`, and 0 `legacy/technologies/.../default.png` files are emitted as artifacts.

## Risk

- This preserves source images for audit and future reconstruction; it does not regenerate DDS icons or sprite declarations from `default.png`.
- Twenty-three PIHC2 technology resource folders do not currently have `default.png`, and five DDS-only support icons remain compiled-output evidence only.

## Next

- Continue source-evidence upgrades for asset families that still only preserve compiled PIHC_dev outputs.
