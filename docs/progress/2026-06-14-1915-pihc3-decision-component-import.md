# PIHC3 Decision Component Import

Date: 2026-06-14 19:15 CST

## Done

- Added the `decision_component` `simple_source` family with a shared path-preserving PDX source slot.
- Added `projects/PIHC3/scripts/migrate_pihc2_decision_components.py` to import the two remaining compiled decision support PDX files into one aggregate module.
- Imported `DECISION_COMPONENT_PIHC_DECISION_SUPPORT` under `projects/PIHC3/src/modules/decision_component/`.
- Excluded the reviewed decision support PDX files from the copy root while leaving `DECISION_*` records and `DECISION_CATEGORY_*` collections owned by `decision`.
- Updated migration design, copy-overlay, decision, decision-component, and legacy inventory documentation.

## Verification

- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k decision_component`
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_decision_components.py --clean`
- `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-decision-component-build.json`

Build summary:

- 16,550 modules across 83 families.
- 36,216 artifacts.
- 713 diagnostics, 0 errors, `blocked: false`.
- 2 `decision_component` artifacts.
- 0 copy-root-owned target decision-support PDX artifacts.

## Risk

- This slice preserves compiled support PDX files only; it does not reconstruct editable debug decision records or category-specific GUI behavior.
- PIHC_dev decision documentation markdown remains copy-owned because it is not game PDX source.

## Next

- Continue with the next non-map copy-root bucket, likely BCE events or small remaining root common support files, while avoiding state/map modules for now.
