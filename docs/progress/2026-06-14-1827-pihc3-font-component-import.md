# PIHC3 Font Component Progress

Date: 2026-06-14 18:27 CST

Linear: none

## Done

- Added the `font_component` simple-source family with one shared path-preserving copy slot.
- Added `migrate_pihc2_font_components.py` for 127 compiled `gfx/fonts` files.
- Imported the compiled font bundle into one aggregate module at `src/modules/font_component/FONT_COMPONENT_PIHC_FONTS/`.
- Excluded reviewed `gfx/fonts/*.fnt`, `gfx/fonts/*.dds`, and `gfx/fonts/*.tga` paths from the PIHC_dev copy overlay.
- Updated migration docs and central legacy inventory.

## Verification

- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k font_component`
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_font_components.py --clean`
- `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-font-component-build.json`
- Build summary: 16,546 modules, 62 collections, 36,216 artifacts, 713 warnings, 0 errors, `blocked: false`.
- Ownership check: all 127 reviewed `gfx/fonts` artifacts are `font_component` owned, with 0 copy-root-owned font artifacts.

## Risks Or Blockers

- The slice preserves compiled font metadata and atlases byte-for-byte; it does not regenerate BMFont atlases or create editable font schemas.

## Next

- Continue with another non-map copy-owned domain such as particles, remaining model/entity support, doctrine/state-category support, or smaller common root files.
