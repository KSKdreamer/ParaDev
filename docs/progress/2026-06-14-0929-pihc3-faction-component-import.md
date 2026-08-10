# PIHC3 Faction Component Import

Date: 2026-06-14 09:29 Asia/Shanghai

## Summary

- Added `projects/PIHC3/scripts/migrate_pihc2_faction_components.py` to import the compiled PIHC_dev faction-system files outside `common/factions/templates/`.
- Added the project-local `faction_component` family with generic path-preserving PDX and localization slots instead of separate families for goals, manifests, rules, upgrades, member upgrades, and icon pools.
- Regenerated 19 `src/modules/faction_component` modules, one per reviewed compiled file under `common/factions/goals/`, `common/factions/icons/`, `common/factions/member_upgrades/`, `common/factions/rules/`, and `common/factions/upgrades/`.
- Excluded the reviewed faction-system component paths from the PIHC_dev copy overlay so generated PIHC3 modules own those outputs.
- Updated the faction migration note, copy-overlay baseline, main migration design, and legacy inventory with the faction-component cutover.

## Verification

- Red check before implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'faction_component'` failed on the missing `faction_component` family and missing `projects/PIHC3/scripts/migrate_pihc2_faction_components.py`.
- Focused green after implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'faction_component'` passed `2 passed, 64 deselected`.
- Formatting/style: `rtk uv run black projects/PIHC3/scripts/migrate_pihc2_faction_components.py tests/test_pihc3_migration_contracts.py` and `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_faction_components.py tests/test_pihc3_migration_contracts.py` completed cleanly.
- Importer run: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_faction_components.py --clean` imported 19 modules.
- Full PIHC3 emit build: `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json` completed with 11,870 modules, 62 collections, 36,208 artifacts, 3,842 diagnostics, 0 errors, and `blocked: false`.
- Manifest check found 19 faction-component modules, 49 faction-component-owned artifacts, and 0 build errors.

## Notes

- The importer intentionally skips `common/factions/templates/*.txt`; those records remain owned by the existing `faction` family.
- Component localization is limited to top-level record ids and direct `name`/`description` display fields. Nested script placeholders such as `FACTION`, `FACTION_NAME`, and `FACTION_CORE_STATES_NOT_FULLY_CONTROLLED` remain shared/base-game localization and are not imported into module-local `main.loc`.
- Higher-level editable faction goal/rule/upgrade source reconstruction, AI initiative strategy review, country creation effect review, and deeper gameplay validation remain future work.
