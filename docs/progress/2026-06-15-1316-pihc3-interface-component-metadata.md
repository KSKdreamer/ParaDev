# PIHC3 Interface Component Metadata

Date: 2026-06-15

## Slice

Expanded the PIHC2 interface support importer so `INTERFACE_COMPONENT_PIHC_INTERFACE` is no longer metadata-thin. The importer still preserves the 671 reviewed `interface/**/*.gfx`, `interface/**/*.gui`, `gfx/interface/**/*.dds`, and `gfx/interface/**/*.tga` files through one shared path-preserving `assets` slot, but `meta.yaml` now records the component id, extension counts, source-folder counts, total bytes, text/binary counts, text line totals, GFX sprite-name counts, texture-reference counts, `legacy_lazy_load` counts, GUI name counts, GUI assignment/type counts, and per-file summaries.

## Verification

- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k interface_component`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_interface_components.py tests/test_pihc3_migration_contracts.py`
- `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-interface-component-metadata-build.json`

The build reported 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`. The manifest owns all 671 reviewed interface support artifacts with `module:interface_component/INTERFACE_COMPONENT_PIHC_INTERFACE`, with 0 copy-root-owned artifacts under `interface/` or `gfx/interface/`.
