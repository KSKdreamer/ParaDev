# PIHC3 Portrait Component Import

Date: 2026-06-14 19:34 CST

## Done

- Added the `portrait_component` `simple_source` family with a shared path-preserving PDX source slot.
- Added `projects/PIHC3/scripts/migrate_pihc2_portrait_components.py` to import the seven remaining compiled portrait support PDX files into one aggregate module.
- Imported `PORTRAIT_COMPONENT_PIHC_PORTRAIT_SUPPORT` under `projects/PIHC3/src/modules/portrait_component/`.
- Excluded `portraits/*.txt` from the copy root while leaving character records owned by `character` and portrait sprite/texture files owned by `portrait_asset_component`.
- Updated migration design, copy-overlay, portrait asset/component, and legacy inventory documentation.

## Verification

- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k portrait_component`
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_portrait_components.py --clean`
- `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-portrait-component-build.json`

Build summary:

- 16,552 modules across 85 families.
- 36,216 artifacts.
- 713 diagnostics, 0 errors, `blocked: false`.
- 7 `portrait_component` artifacts.
- 0 copy-root-owned `portraits/` artifacts.

## Risk

- This slice preserves compiled support PDX files only; it does not reconstruct editable random-character portrait pools.
- Empty vanilla portrait support files are preserved as zero-byte PDX artifacts because they are present in the compiled PIHC_dev output.

## Next

- Continue with the next non-map copy-root bucket, likely intelligence agency support, weather/generation support, BCE event handling, or remaining small asset support files.
