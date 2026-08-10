# PIHC3 Common Batch Trim Progress

Date: 2026-06-14 06:11 CST

Linear: N/A

## Done

- Added a migration contract that keeps already-split common families out of `projects/PIHC3/scripts/migrate_pihc2_common_sources.py`.
- Removed `building`, `operation`, `resistance_activity`, `resource`, `unit_medal`, and `wargoal` from the generic common-source batch.
- Left the generic common-source batch focused on the remaining file-level/common families: autonomous states, continuous focuses, difficulty settings, on-actions, operative codenames, scripted effects, scripted GUIs, and scripted triggers.
- Updated `projects/PIHC3/docs/migration/00-design.md` to record 170 file-level modules across 8 generic common families.

## Verification

- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k "existing_split_common or building_importer or resource_importer or wargoal_importer or resistance_activity_importer or unit_medal_importer or operation_importer"` -> 8 passed.
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q` -> 40 passed.
- PIHC3 emitting build -> 3,332 modules, 62 collections, 27,696 artifacts, 0 errors, `blocked: false`.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_common_sources.py tests/test_pihc3_migration_contracts.py` -> OK.
- `rtk bash scripts/flake.bash --ci` -> passed.

## Risks Or Blockers

- This is a tooling-contract cleanup, not a new content import. PIHC3 build totals should remain unchanged.
- Continuous focuses remain aggregate-shaped and should use a dedicated aggregate design rather than the current file-level common importer.

## Next

- Continue splitting the remaining generic common families where root records are independently editable, starting with low-risk non-map PDX-only families.
