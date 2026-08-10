# 2026-06-14 20:33 CST - PIHC3 Support Static Model Assets

## Done

- Expanded the `support_component` shared copy slot to own the remaining reviewed non-map shader/model support files:
  - `gfx/FX/buttonstate_nodowneffect.shader`
  - `gfx/models/nambugame_nambu mat_color.dds`
  - `gfx/models/nambugame_nambu mat_norm.dds`
  - `gfx/models/nambugame_nambu mat_spec.dds`
  - `gfx/models/paper_normal.dds`
  - `gfx/models/paper_spec.dds`
  - `gfx/models/paper_texture.dds`
  - `gfx/models/wood_table_texture.dds`
- Regenerated `src/modules/support_component/`, increasing the family from 9 to 17 path-preserving modules.
- Excluded the eight reviewed shader/model support paths from the PIHC_dev copy overlay after native ownership.
- Updated support-component migration docs and copy-overlay baseline labels for the current build.

## Verification

- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_support_components.py --clean`
- Byte-checked representative generated shader/model assets against `/Users/magolor/Documents/Paradox Interactive/Hearts of Iron IV/mod/PIHC_dev`.
- `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-support-static-models-build.json`

The build reports 16,569 modules across 87 families, 36,179 artifacts, 713 diagnostics, 0 errors, and `blocked: false`. The manifest contains 17 `support_component` artifacts; all eight newly reviewed shader/model support paths are owned by `support_component`, with 0 copy-root-owned artifacts for those paths.

## Risk

- This remains compiled-support preservation through generic slots; the shader and DDS files are not editable high-level records.
- Map shader/include files, border meshes/textures, minimap assets, loading screens, and broad interface GUI/GFX assets remain owned by other component families or future skipped-map slices.

## Next

- Continue trimming remaining non-map copy-root assets where a narrow shared component family can own exact compiled outputs without introducing per-type boilerplate.
