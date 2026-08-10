# PIHC3 Portrait Asset Metadata

Slice: enrich compiled portrait sprite/texture asset modules while keeping the family path-preserving and generic.

Changes:

- Added GFX and DDS metadata extraction to `projects/PIHC3/scripts/migrate_pihc2_portrait_asset_components.py`.
- Kept `portrait_asset_component` on the existing shared `assets` copy slot.
- Preserved the existing random-character source evidence fields.
- Regenerated 258 modules under `projects/PIHC3/src/modules/portrait_asset_component/`.
- Updated the portrait asset migration note, character migration note, design overview, and legacy inventory.

Metadata now records component id, source slot counts, GFX/DDS source counts, sprite names, texture paths, optional `noOfFrames` values, DDS dimensions, mipmap counts, byte sizes, FourCC values, header sizes, and per-source GFX/DDS summaries.

Representative checks cover:

- `PORTRAIT_ASSET_COMPONENT_CHARACTER_ABYSSINIA_KING_MEOWMEOW`: 6 sprite declarations, 6 DXT5 DDS textures, 156x210 main portraits, and 65x67 small portraits.
- `PORTRAIT_ASSET_COMPONENT_RANDOM_CHARACTER_PONY_MILITARY`: 64 sprite declarations, 64 DDS textures, and 64 PIHC2 random-character source evidence files.
- `PORTRAIT_ASSET_COMPONENT_LEADER_UNKNOWN`: DDS-only fallback texture with a 156x225 blank-FourCC 32-bit DDS payload.

Verification:

- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k portrait_asset_component` -> 3 passed, 207 deselected.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_portrait_asset_components.py tests/test_pihc3_migration_contracts.py` -> OK.
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_portrait_asset_components.py --clean` -> 258 modules regenerated.
- `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json` -> 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, `blocked: false`.
- Build artifact ownership check found all 1,917 reviewed portrait sprite/texture outputs owned by `module:portrait_asset_component/...`.
- The seven reviewed `portraits/*.txt` support outputs remain owned by `module:portrait_component/...`.

Remaining work:

- Portrait DDS regeneration from source images remains future work.
- Editable random-character pool reconstruction remains future work.
- Animation strip handling and role-specific portrait authoring remain future work.
