# 2026-06-14 22:12 PIHC3 raid component localization

## Scope

Continued the non-map PIHC2 to PIHC3 migration by extending `raid_component` from PDX-only preservation to shared PDX plus localization slots. The slice keeps module-specific code minimal by using the generic optional `main.loc` slot and importer-side key extraction for compiled raid category and type files.

## Changes

- Added a shared optional loc slot to `raid_component`.
- Added `compiled_raid_component_locs`.
- Loaded current-game localization first and overlaid PIHC_dev localization rows.
- Derived category localization from `categories = { <id> = ... }` records.
- Derived type localization from `types = { <id> = ... }` records and explicit `localization_key` / `target_loc_key` fields.
- Preferred raid category/type display keys for generated module titles so GUI names stay concise.
- Regenerated 4 raid component modules.
- Wrote `main.loc` for all 4 raid modules.
- Updated migration docs and the legacy inventory note.

## Evidence

- Red contract: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k "raid_component_family or raid_component_importer"` failed with missing `loc` family slot and missing `compiled_raid_component_locs`.
- Title red check: the generated air-raid module title initially used the facility-damage tooltip instead of `Facility Strike`.
- Green contract: `2 passed, 147 deselected in 50.79s`.
- Formatting: `rtk uv run black --check projects/PIHC3/scripts/migrate_pihc2_raid_components.py` passed.
- Formatting: `rtk uv run black --check --line-ranges 2165-2265 tests/test_pihc3_migration_contracts.py` passed.
- Heaven-style scan: `OK: 2 file(s) - no banned imports`.
- Regeneration: `Imported 4 PIHC2 raid component modules into /Users/magolor/Utils/ParaDev-3/projects/PIHC3/src/modules/raid_component`.
- Generated coverage: 4 modules with `main.loc`; 120 localized rows for raid categories, 60 for air raids, 60 for paratrooper raids, and 20 for nuclear raids.
- Dry build: `rtk uv run paradev build projects/PIHC3 --json > /tmp/pihc3-raid-localization-dry-build.json`.
- Dry-build summary: 16,581 modules, 62 collections, 37,210 artifacts, 713 diagnostics, 0 errors, `blocked: false`.
- Dry-build ownership: 4 `raid_component` PDX artifacts, 40 `raid_component` localization artifacts, and 0 copy-owned files under `common/raids/`.

## Follow-Up

- Raid types and categories remain compiled support preservation. Split them into editable records only when GUI authoring needs raid-specific workflows.
