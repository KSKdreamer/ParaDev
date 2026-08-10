# 2026-06-14 20:19 CST - PIHC3 Support Component Static Assets

## Done

- Continued the shared `support_component` path instead of creating a narrower family.
- Verified the family has shared path-preserving `pdx` and `assets` slots.
- Regenerated 9 support modules, adding support ownership for:
  - `dlc/dlc034_no_step_back/gfx/train_gfx_database/NSB_generic.txt`
  - `dlc/dlc036_by_blood_alone/gfx/entities/BBA_units_vehicles.asset`
  - `gfx/army_icons/army_icons.txt`
  - `gfx/train_gfx_database/NSB_generic.txt`
  - `thumbnail.png`
- Updated the support-component note, design rollup, copy-overlay posture, and legacy inventory.

## Verification

- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k support_component`
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_support_components.py --clean`
- `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-support-component-assets-build.json`

The build reports 16,561 modules across 87 families, 36,216 artifacts, 713 diagnostics, 0 errors, and `blocked: false`. The manifest contains 9 `support_component` modules and 0 copy-root-owned artifacts for the five newly reviewed static support paths.

## Risk

- This slice preserves compiled static support bytes first. It does not reconstruct editable train graphics, army icon definitions, BBA unit entity data, or thumbnail authoring.
- Broad map-adjacent static graphics remain intentionally outside this slice.

## Next

- Continue trimming remaining non-map copy-root buckets: documentation/metadata leftovers, entity/particle support files that are not map-owned, and other reviewed static assets.
