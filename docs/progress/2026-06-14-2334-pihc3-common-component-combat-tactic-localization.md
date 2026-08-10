# 2026-06-14 23:34 PIHC3 common component combat tactic localization

## Scope

Continued the non-map PIHC2 to PIHC3 migration by expanding `common_component` localization ownership for the compiled combat-tactics support file. This keeps combat tactics in the shared path-preserving common-component family instead of introducing tactic-specific module code.

## Changes

- Added path-gated localization extraction for `common/combat_tactics.txt`.
- Combat-tactic extraction now owns top-level `tactic_*` PDX records only.
- Regenerated 48 common component modules.
- Generated `main.loc` for `COMMON_COMPONENT_COMBAT_TACTICS`, including PIHC custom tactics and current-game tactic rows.
- Updated migration docs and the legacy inventory note.

## Evidence

- Red contract: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k "common_component_importer"` first failed with `KeyError: 'l_english'` for `common/combat_tactics.txt`.
- Green contract after the path-gated extractor change: `1 passed, 156 deselected in 199.99s`.
- Regeneration: `Imported 48 PIHC2 common component modules into /Users/magolor/Utils/ParaDev-3/projects/PIHC3/src/modules/common_component`.
- Generated metadata: `COMMON_COMPONENT_COMBAT_TACTICS` now has `loc_key_count: 454`.
- Dry build: `rtk uv run paradev build projects/PIHC3 --json > /tmp/pihc3-common-combat-tactic-loc-dry-build.json`.
- Dry-build summary: 16,581 modules, 62 collections, 37,414 artifacts, 713 diagnostics, 0 errors, `blocked: false`.
- Dry-build diagnostics: 546 `copy_root.shadowed_artifact` warnings and 167 metadata warnings.
- Dry-build ownership: 48 `common_component` PDX artifacts and 204 `common_component` localization artifacts from 22 localized common-component modules.

## Follow-Up

- Candidate remaining common-component localization slices include equipment groups, technology tags, technology sharing, and resistance/compliance modifiers.
- Keep future extractors path-gated to clear current-game PDX conventions before considering new editable module families.
