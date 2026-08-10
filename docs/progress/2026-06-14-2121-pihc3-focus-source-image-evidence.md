# 2026-06-14 21:21 CST - PIHC3 Focus Source Image Evidence

## Done

- Extended `focus_asset_component` import to preserve PIHC2 `resources/focuses/<TREE>/<TAG>/default.png` files as module-local legacy evidence.
- Copied 500 available source PNGs into matching focus asset modules under `legacy/focuses/<TREE>/<TAG>/default.png`.
- Recorded those source paths in each matching module's `meta.yaml` settings and `legacy/source.yaml`.
- Left emitted game artifacts unchanged: compiled `interface/focuses/*.gfx` and `gfx/interface/goals/*.dds` files still use the existing shared copy slot.
- Updated focus migration docs and the legacy inventory to describe the non-emitted source image evidence.

## Verification

- Red check first: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k focus_asset_component` failed because focus asset components lacked `legacy_source_paths`.
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k focus_asset_component`
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_focus_asset_components.py --clean`
- Byte-checked `legacy/focuses/C01_MAIN/C01_CANTERLOT_PACT/default.png` against the PIHC2 source image.
- `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-focus-source-images-build.json`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_focus_asset_components.py tests/test_pihc3_migration_contracts.py`
- `rtk git diff --check`

The build reports 16,581 modules across 62 collections, 37,082 artifacts, 713 diagnostics, 0 errors, and `blocked: false`. The manifest still contains 1,477 `focus_asset_component` artifacts; representative `FOCUS_C01_CANTERLOT_PACT` GFX/DDS outputs are owned by `focus_asset_component`, and 0 `legacy/focuses/.../default.png` files are emitted as artifacts.

## Risk

- This preserves source images for audit and future reconstruction; it does not regenerate DDS icons or sprite declarations from `default.png`.
- Focus folders without `default.png` and the DDS-only `goal_unknown` support icon remain compiled-output evidence only.
- The artifact count reflects the current dirty workspace build, including parallel work outside this slice.

## Next

- Continue source-evidence upgrades for asset families that still only preserve compiled PIHC_dev outputs, or move to remaining GUI-visible data gaps such as deeper equipment/modifier authoring.
