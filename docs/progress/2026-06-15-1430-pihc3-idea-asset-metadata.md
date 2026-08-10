# PIHC3 Idea Asset Metadata

Slice: enrich compiled idea sprite/icon asset modules while keeping the family path-preserving and generic.

Changes:

- Added GFX and DDS metadata extraction to `projects/PIHC3/scripts/migrate_pihc2_idea_asset_components.py`.
- Kept `idea_asset_component` on the existing shared `assets` copy slot.
- Regenerated 440 modules under `projects/PIHC3/src/modules/idea_asset_component/`.
- Updated the idea asset migration note, idea migration note, design overview, and legacy inventory.

Metadata now records component id, source slot counts, GFX/DDS source counts, sprite names, texture paths, optional `noOfFrames` values, DDS dimensions, mipmap counts, byte sizes, FourCC values, header sizes, and per-source GFX/DDS summaries.

Representative checks cover:

- `IDEA_ASSET_COMPONENT_IDEA_C01_ANGRY_BEST_PONY`: paired sprite `GFX_idea_C01_ANGRY_BEST_PONY`, texture path `gfx/interface/ideas/IDEA_C01_ANGRY_BEST_PONY.dds`, and a 74x74 blank-FourCC 32-bit DDS payload.
- `IDEA_ASSET_COMPONENT_IDEA_WAR_ECONOMY`: DDS-only support icon with a 74x74 DXT5 DDS payload.

Verification:

- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k idea_asset_component` -> 3 passed, 206 deselected.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_idea_asset_components.py tests/test_pihc3_migration_contracts.py` -> OK.
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_idea_asset_components.py --clean` -> 440 modules regenerated.
- `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json` -> 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, `blocked: false`.
- Build artifact ownership check found all 863 reviewed idea sprite/icon outputs owned by `module:idea_asset_component/...`.
- The remaining 33 `gfx/interface/ideas` outputs are expected idea-category icons owned by `module:idea_category/...`.

Remaining work:

- Source-image regeneration for idea icons remains future work.
- Nested idea-category law aggregation remains owned by the separate idea-category migration path.
