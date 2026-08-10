# 2026-06-14 20:19 CST - PIHC3 Support Static Assets

## Done

- Expanded `support_component` with an optional shared copy slot while keeping the existing shared PDX slot.
- Imported five additional compiled PIHC_dev support assets:
  - `dlc/dlc034_no_step_back/gfx/train_gfx_database/NSB_generic.txt`
  - `dlc/dlc036_by_blood_alone/gfx/entities/BBA_units_vehicles.asset`
  - `gfx/army_icons/army_icons.txt`
  - `gfx/train_gfx_database/NSB_generic.txt`
  - `thumbnail.png`
- Regenerated `src/modules/support_component/`, increasing the family from 4 to 9 path-preserving modules.
- Excluded the five reviewed static support paths from the copy overlay after native ownership.
- Updated support migration docs, copy-overlay posture, the design rollup, and the legacy inventory.

## Verification

- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k support_component`
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_support_components.py --clean`
- `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-support-static-assets-build.json`

The build reports 16,561 modules across 87 families, 36,216 artifacts, 713 diagnostics, 0 errors, and `blocked: false`. The manifest contains 9 `support_component` artifacts; all five newly reviewed static support paths are owned by `support_component`, with 0 copy-root-owned artifacts for those paths.

## Risk

- This is compiled-support preservation. It does not provide editable train graphics database, army icon table, BBA entity asset, or thumbnail generation.
- Shaders, broad model bundles, and map-related static assets remain copy-root owned or future slices.

## Next

- Continue trimming non-map copy-root assets, especially the remaining shader/model support files and helper-script/documentation cleanup once conflicts with other workers are clear.
