# PIHC3 Special Project Component Import

Date: 2026-06-14 15:48 Asia/Shanghai

## Summary

- Added `projects/PIHC3/scripts/migrate_pihc2_special_project_components.py` to import compiled PIHC_dev special-project support PDX and GUI files.
- Added the project-local `special_project_component` family with shared path-preserving `pdx` and `assets` slots.
- Generated one `src/modules/special_project_component` module preserving `common/special_projects/project_tags/tags.txt`, `common/special_projects/specialization/specializations.txt`, and six `interface/special_projects/*.gui` files.
- Excluded reviewed special-project support PDX and GUI paths from the PIHC_dev copy overlay.
- Updated the special-project migration note, new special-project-component note, copy-overlay baseline, main migration design, and legacy inventory.

## Verification

- Red check before implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k special_project_component` failed on the missing `special_project_component` family and missing `projects/PIHC3/scripts/migrate_pihc2_special_project_components.py`.
- Focused green after implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k special_project_component` passed `2 passed, 110 deselected`.
- Formatting/style: `rtk uv run black projects/PIHC3/scripts/migrate_pihc2_special_project_components.py tests/test_pihc3_migration_contracts.py` left both files unchanged; `rtk uv run python /Users/magolor/.agents/skills/heaven-style-0.1.1.1/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_special_project_components.py tests/test_pihc3_migration_contracts.py` completed cleanly.
- Importer run: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_special_project_components.py --clean` imported 1 module.
- Build ownership checks confirmed all 8 reviewed special-project support paths are owned by `special_project_component`, with 0 copy-root-owned reviewed support paths remaining.
- Full PIHC3 emit build: `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json` completed with 16,443 modules, 62 collections, 36,212 artifacts, 1,857 diagnostics, 0 errors, and `blocked: false`.

## Notes

- GUI files are copied byte-for-byte; PDX support files use the normal text slot and retain legacy source provenance.
- Project PDX, reward PDX, project icon DDS, project sprite GFX, and shared special-project sprite/image assets remain with existing native families.
- Full migration contracts were intentionally not run in this slice to reduce CPU load while other ParaDev workers are refactoring. Focused tests plus a full PIHC3 compile check covered the changed family.
