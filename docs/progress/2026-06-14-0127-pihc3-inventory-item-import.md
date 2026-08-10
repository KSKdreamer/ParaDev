# 2026-06-14 01:27 +0800 - PIHC3 Inventory Item Import

## Summary

Imported PIHC2 inventory items as native PIHC3 modules while keeping the compiler path on shared source slots.

## Changes

- Added `projects/PIHC3/scripts/migrate_pihc2_inventory_items.py`.
- Imported 80 `resources/inventory_items/<order>-<TAG>` folders into `src/modules/inventory_item`.
- Preserved compiled per-item scripted effects as `effects.txt` and compiled scripted triggers as `triggers.txt`.
- Consolidated compiled localization into `main.loc`, copied compiled large/small DDS icons into `icons/`, and recorded source evidence under `legacy/`.
- Expanded the `inventory_item` family to use shared `scripted_effects`, `scripted_triggers`, `loc`, and `icon` slots, with generic sprite GFX generation at `interface/PIHC3_inventory_items.gfx`.
- Updated the compiled common-source importer to skip `PIHC_INVENTORY_ITEM_*.txt` so per-item helpers are no longer duplicated as standalone `scripted_effect` or `scripted_trigger` modules.

## Verification

- Red test first:
  - `rtk uv run pytest tests/test_pihc3_migration_contracts.py::test_pihc3_inventory_item_family_uses_shared_slots_for_effects_triggers_and_icons -q`
  - Failed before the manifest change because `scripted_effects` was not a source slot.
- Green focused test:
  - `rtk uv run pytest tests/test_pihc3_migration_contracts.py::test_pihc3_inventory_item_family_uses_shared_slots_for_effects_triggers_and_icons -q`
  - 1 passed
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_inventory_items.py --clean`
  - Imported 80 modules
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_common_sources.py --clean --family scripted_effect --family scripted_trigger`
  - Migrated 49 non-inventory scripted effects
  - Migrated 7 non-inventory scripted triggers
- `rtk git diff --check -- <changed files>`
- `rtk rg -n "[[:blank:]]$" <changed files>`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_inventory_items.py projects/PIHC3/scripts/migrate_pihc2_common_sources.py tests/test_pihc3_migration_contracts.py`
  - OK: 3 files, no banned imports
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
  - 555 passed in 175.02s
- `rtk uv run paradev summary projects/PIHC3 --json`
  - modules: 2,761
  - collections: 62
  - artifacts: 25,914
  - diagnostics: 4,183
  - errors: 0
  - blocked: false
- `Project.load(Path("projects/PIHC3")).build(emit_artifacts=True, emit_manifests=True)`
  - dry_run: false
  - modules: 2,761
  - collections: 62
  - artifacts: 25,914
  - diagnostics: 4,183
  - errors: 0
  - blocked: false
- Native ownership spot checks confirmed one native owner for the Staff of Sacanas effect, trigger, English and Simplified Chinese localization files, both DDS icons, and `interface/PIHC3_inventory_items.gfx`.

## Risks Or Blockers

- `PIHC_INVENTORY` scan/debug aggregation remains a generic scripted-effect module.
- Scripted GUI fragments, operation buttons, scripted-localisation selectors, and full UI parity remain future inventory slices.

## Next

- Continue with superevents or state lore, which are the next non-map systems still copy/generated-only.
