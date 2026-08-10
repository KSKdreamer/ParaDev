# PIHC3 Modifier Component Import

Date: 2026-06-14 09:55 Asia/Shanghai

## Summary

- Added `projects/PIHC3/scripts/migrate_pihc2_modifier_components.py` to import compiled dynamic modifier and peace cost-modifier support files from PIHC_dev.
- Added the project-local `modifier_component` family with generic path-preserving PDX and localization slots.
- Regenerated 9 `src/modules/modifier_component` modules: 7 files under `common/dynamic_modifiers/` and 2 files under `common/peace_conference/cost_modifiers/`.
- Excluded `common/dynamic_modifiers/*.txt` and `common/peace_conference/cost_modifiers/*.txt` from the PIHC_dev copy overlay so generated PIHC3 modules own those reviewed outputs.
- Replaced the stale modifier migration note and updated the copy-overlay baseline, main migration design, and legacy inventory.

## Verification

- Red check before implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'modifier_component'` failed on the missing `modifier_component` family and missing `projects/PIHC3/scripts/migrate_pihc2_modifier_components.py`.
- Duplicate-localization regression check: the focused contract failed until PIHC custom dynamic modifier localization from `PIHC_*_dynamic_modifiers.txt` was treated as owned by the decision/focus modules that already declare those keys.
- Focused green after implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'modifier_component'` passed `2 passed, 66 deselected`.
- Formatting/style: `rtk uv run black projects/PIHC3/scripts/migrate_pihc2_modifier_components.py tests/test_pihc3_migration_contracts.py` and `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_modifier_components.py tests/test_pihc3_migration_contracts.py` completed cleanly.
- Importer run: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_modifier_components.py --clean` imported 9 modules.
- Full PIHC3 emit build: `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json` completed with 11,879 modules, 62 collections, 36,214 artifacts, 3,842 diagnostics, 0 errors, and `blocked: false`.
- Manifest check found 9 modifier-component modules, 15 modifier-component-owned artifacts, and 0 build errors.

## Notes

- The new component family intentionally does not split dynamic modifiers and peace cost modifiers into separate family-specific implementations.
- Vanilla dynamic modifier localization and faction peace tooltip rows are imported into component `main.loc`.
- PIHC custom dynamic modifier display rows such as `C18_URBAN_DYNAMIC_MODIFIER` remain owned by native decision-category or focus-tree modules to avoid duplicate project localization keys.
