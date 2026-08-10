# 2026-06-14 21:35 PIHC3 peace-conference component localization

## Scope

Continued the non-map PIHC2 to PIHC3 migration by extending `peace_conference_component` from PDX-only preservation to shared PDX plus localization slots. The slice keeps module-specific code minimal: the family uses the same optional `main.loc` slot pattern as other path-preserving support components, and the importer only extracts localization keys from compiled action-category `name = ...` fields.

## Changes

- Added the `peace_conference_component` contract for the shared loc slot and loc output template.
- Added localization extraction to `projects/PIHC3/scripts/migrate_pihc2_peace_conference_components.py`.
- Merged current-game localization first and PIHC_dev localization second so PIHC custom action-category labels override vanilla rows.
- Regenerated 2 modules under `projects/PIHC3/src/modules/peace_conference_component/`.
- Wrote `main.loc` only for `PEACE_CONFERENCE_COMPONENT_PEACE_CONFERENCE_CATEGORIES_00_PEACE_ACTION_CATEGORIES`; `PEACE_CONFERENCE_COMPONENT_PEACE_CONFERENCE_AI_PEACE_00_MISC` remains PDX-only because it has no display keys.
- Updated migration docs and the legacy inventory note.

## Evidence

- Red contract: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k "peace_conference_component_family or peace_conference_component_importer"` failed while the importer did not expose `compiled_peace_conference_component_locs`.
- Green contract: `2 passed, 147 deselected in 34.73s`.
- Formatting: `rtk uv run black --check projects/PIHC3/scripts/migrate_pihc2_peace_conference_components.py` passed.
- Formatting: `rtk uv run black --check --line-ranges 2410-2495 tests/test_pihc3_migration_contracts.py` passed.
- Heaven-style scan: `OK: 2 file(s) - no banned imports`.
- Regeneration: `Imported 2 PIHC2 peace-conference component modules into /Users/magolor/Utils/ParaDev-3/projects/PIHC3/src/modules/peace_conference_component`.
- Dry build: `rtk uv run paradev build projects/PIHC3 --json > /tmp/pihc3-peace-conference-localization-dry-build.json`.
- Dry-build summary: 16,581 modules, 62 collections, 37,110 artifacts, 713 diagnostics, 0 errors, `blocked: false`.
- Dry-build ownership: 2 `peace_conference_component` PDX artifacts, 10 `peace_conference_component` localization artifacts, and 0 copy-owned files under `common/peace_conference/`.

## Follow-Up

- Peace AI desires and action categories are still preserved as compiled support files. Split them into editable authoring records only if GUI authoring becomes useful.
