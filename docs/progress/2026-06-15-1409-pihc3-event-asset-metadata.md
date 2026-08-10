# PIHC3 Event Asset Metadata

Slice: enrich compiled normal event sprite/picture asset modules while keeping the family path-preserving and generic.

Changes:

- Added GFX and DDS metadata extraction to `projects/PIHC3/scripts/migrate_pihc2_event_asset_components.py`.
- Kept `event_asset_component` on the existing shared `assets` copy slot.
- Regenerated 867 modules under `projects/PIHC3/src/modules/event_asset_component/`.
- Updated the event asset migration note, design overview, and legacy inventory.

Metadata now records component id, source slot counts, GFX/DDS source counts, sprite names, texture paths, optional `noOfFrames` values, DDS dimensions, mipmap counts, byte sizes, FourCC values, header sizes, and per-source GFX/DDS summaries.

Representative checks cover:

- `EVENT_ASSET_COMPONENT_EVENT_C33_MAIN_1`: sprite `GFX_EVENT_C33_MAIN_1`, texture path `gfx/event_pictures/EVENT_C33_MAIN_1.dds`, and a 210x176 DXT5 DDS payload.
- `EVENT_ASSET_COMPONENT_EVENT_ARTIFACTS_1`: paired normal event GFX/DDS metadata for `GFX_EVENT_ARTIFACTS_1`.
- `EVENT_ASSET_COMPONENT_BORDER_WAR`: DDS-only support picture with no sprite declaration.

Verification:

- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k event_asset_component` -> 3 passed, 204 deselected.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_event_asset_components.py tests/test_pihc3_migration_contracts.py` -> OK.
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_event_asset_components.py --clean` -> 867 modules regenerated.
- `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json` -> 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, `blocked: false`.
- Build artifact ownership check found all 1,733 reviewed normal event asset outputs owned by `module:event_asset_component/...`.
- Superevent DDS outputs remain owned by `module:superevent/...`.

Remaining work:

- Higher-level event picture authoring workflows remain future work.
- `events/BCE.txt` remains owned by `event_component`.
- Superevent DDS pictures and sprite aggregation remain owned by `superevent`.
