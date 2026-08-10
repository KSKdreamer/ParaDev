# PIHC3 Achievement Component Import

Date: 2026-06-14 19:25 CST

## Done

- Added the `achievement_component` `simple_source` family with a shared path-preserving PDX source slot.
- Added `projects/PIHC3/scripts/migrate_pihc2_achievement_components.py` to import the two remaining compiled achievement support PDX files into one aggregate module.
- Imported `ACHIEVEMENT_COMPONENT_PIHC_ACHIEVEMENT_SUPPORT` under `projects/PIHC3/src/modules/achievement_component/`.
- Excluded the reviewed achievement support PDX files from the copy root while leaving editable per-achievement records owned by `achievement`.
- Updated migration design, copy-overlay, achievement, achievement-component, and legacy inventory documentation.

## Verification

- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k achievement_component`
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_achievement_components.py --clean`
- `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-achievement-component-build.json`

Build summary:

- 16,551 modules across 84 families.
- 36,216 artifacts.
- 713 diagnostics, 0 errors, `blocked: false`.
- 2 `achievement_component` artifacts.
- 0 copy-root-owned `common/achievements` artifacts.

## Risk

- This slice preserves compiled support PDX files only; it does not reconstruct aggregate-pack emission from editable per-achievement modules.
- PIHC3 currently keeps both editable per-achievement modules and the compiled aggregate support pack for parity with the pre-existing build posture.

## Next

- Continue with the next non-map copy-root bucket, likely portrait definition support, intelligence agency support, or BCE event handling, while avoiding map/state modules for now.
