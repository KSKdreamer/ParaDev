# PIHC3 Technology Component Import

Date: 2026-06-14 19:00 CST

## Done

- Added the `technology_component` `simple_source` family with a shared path-preserving PDX source slot.
- Added `projects/PIHC3/scripts/migrate_pihc2_technology_components.py` to import the two remaining compiled technology support PDX files into one aggregate module.
- Imported `TECHNOLOGY_COMPONENT_PIHC_TECHNOLOGY_SUPPORT` under `projects/PIHC3/src/modules/technology_component/`.
- Excluded the reviewed technology support PDX files from the copy root while leaving editable `TECHNOLOGY_*` records owned by `technology`.
- Updated migration design, copy-overlay, technology-component, and legacy inventory documentation.

## Verification

- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k technology_component`
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_technology_components.py --clean`
- `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-technology-component-build.json`

Build summary:

- 16,549 modules across 82 families.
- 36,216 artifacts.
- 713 diagnostics, 0 errors, `blocked: false`.
- 2 `technology_component` artifacts.
- 0 copy-root-owned `common/technologies` artifacts.

## Risk

- This slice preserves compiled support PDX files only; it does not reconstruct editable vanilla technology-tree source or root technology GUI.
- Root technology GUI fragments remain owned by `interface_component`; native GUI-first authoring is still future work.

## Next

- Continue with the next non-map copy-root buckets, likely root common/support PDX groups or remaining decision/BCE-specific support, while avoiding state/map modules for now.
