# PIHC3 Decision Asset Metadata

Slice: enrich compiled decision sprite/icon asset modules while keeping the family path-preserving and generic.

Changes:

- Added GFX and DDS metadata extraction to `projects/PIHC3/scripts/migrate_pihc2_decision_asset_components.py`.
- Kept `decision_asset_component` on the existing shared `assets` copy slot.
- Regenerated 464 modules under `projects/PIHC3/src/modules/decision_asset_component/`.
- Updated the decision asset migration note, design overview, and legacy inventory.

Metadata now records component id, source slot counts, GFX/DDS source counts, sprite names, texture paths, optional `noOfFrames` values, DDS dimensions, mipmap counts, byte sizes, FourCC values, header sizes, and per-source GFX/DDS summaries.

Representative checks cover:

- `DECISION_ASSET_COMPONENT_DECISION_C01_GREAT`: paired sprite `GFX_decision_DECISION_C01_GREAT`, texture path `gfx/interface/decisions/DECISION_C01_GREAT.dds`, and a 52x40 DXT5 DDS payload.
- `DECISION_ASSET_COMPONENT_DECISION_C08_16_A`: DDS-only icon with no sprite declaration.
- `DECISION_ASSET_COMPONENT_DECISION_C08_16_A_1A`: GFX-only sprite declaration preserving its missing compiled DDS reference.

Verification:

- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k decision_asset_component` -> 3 passed, 205 deselected.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_decision_asset_components.py tests/test_pihc3_migration_contracts.py` -> OK.
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_decision_asset_components.py --clean` -> 464 modules regenerated.
- `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json` -> 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, `blocked: false`.
- Build artifact ownership check found all 925 reviewed decision sprite/icon outputs owned by `module:decision_asset_component/...`.

Remaining work:

- Category-specific GUI editing remains future work.
- Scripted GUI parity and deeper per-decision asset generation remain future work.
