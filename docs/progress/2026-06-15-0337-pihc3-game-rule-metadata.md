# PIHC3 Game-Rule Metadata Progress

Date: 2026-06-15 03:37

Linear: TAL-000

## Done

- Added a focused migration contract for compiled game-rule metadata using `PIHC_GAME_RULE_DYNAMIC_PORTRAITS` and `CWC_only_core_claims`.
- Extended `projects/PIHC3/scripts/migrate_pihc2_game_rules.py` to mirror direct compiled rule fields and option blocks into module metadata.
- Regenerated all 27 game-rule modules; generated metadata now covers 84 `default`/`option` blocks, 24 default-option blocks, 21 icon-bearing rules, 185 owned localization rows, and 287 referenced localization keys.
- Updated the game-rule migration note, design summary, and legacy inventory with the new metadata scope.

## Verification

- Red: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k game_rule_importer_extracts_individual_rule_contract` failed with missing `settings["rule_id"]`.
- Green: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k game_rule_importer_extracts_individual_rule_contract` passed: 1 passed, 167 deselected.
- Regeneration: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_game_rules.py --clean`.
- Dry build: `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-game-rule-metadata-dry-build.json` reported 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.

## Risks Or Blockers

- Game-rule metadata intentionally summarizes direct top-level rule fields and option blocks only. Scripted consumers of rule choices remain in their owning scripted-effect, scripted-trigger, decision, focus, or event modules.
- Shared group labels and shared vanilla option labels remain outside individual rule-owned localization to avoid duplicate project loc ownership.

## Next

- Continue enhancing low-data non-map families with source-owned metadata where it improves GUI browsing without splitting compiled support bundles prematurely.
