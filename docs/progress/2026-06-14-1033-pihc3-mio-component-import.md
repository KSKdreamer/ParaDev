# PIHC3 MIO Component Import

Date: 2026-06-14 10:33 Asia/Shanghai

## Summary

- Added `projects/PIHC3/scripts/migrate_pihc2_military_industrial_organization_components.py` to import compiled PIHC_dev military-industrial-organization support files.
- Added the project-local `military_industrial_organization_component` family with a generic path-preserving PDX slot.
- Regenerated 7 `src/modules/military_industrial_organization_component` modules:
  - 1 `common/military_industrial_organization/ai_bonus_weights/*.txt` file;
  - 3 `common/military_industrial_organization/organizations/*.txt` files;
  - 3 `common/military_industrial_organization/policies/*.txt` files.
- Excluded those reviewed MIO support paths from the PIHC_dev copy overlay and added the MIO subtrees to `replace_path`.
- Updated the MIO migration note, copy-overlay baseline, main migration design, and legacy inventory.

## Verification

- Red check before implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'military_industrial_organization_component'` failed on the missing family and missing importer script.
- Focused green after implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'military_industrial_organization_component'` passed `2 passed, 70 deselected`.
- Formatting/style: `rtk uv run black tests/test_pihc3_migration_contracts.py projects/PIHC3/scripts/migrate_pihc2_military_industrial_organization_components.py` and `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_pihc3_migration_contracts.py projects/PIHC3/scripts/migrate_pihc2_military_industrial_organization_components.py` completed cleanly.
- Importer run: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_military_industrial_organization_components.py --clean` imported 7 modules.
- Full PIHC3 emit build: `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json` completed with 12,033 modules, 62 collections, 36,214 artifacts, 3,842 diagnostics, 0 errors, and `blocked: false`.
- Manifest check found 7 MIO-component modules, 7 MIO-component-owned artifacts, and 0 build errors.

## Notes

- The importer preserves compiled PIHC_dev files exactly as game-relative PDX sources rather than splitting organizations, policies, or traits into editable subrecords.
- The sampled MIO files did not have PIHC_dev-owned localization rows; the C01 custom organization uses a quoted literal display name.
- Higher-level editable MIO trait trees, policy authoring, and gameplay validation remain future work.
