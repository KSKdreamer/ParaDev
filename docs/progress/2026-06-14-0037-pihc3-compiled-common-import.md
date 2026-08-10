# 2026-06-14 00:37 +0800 - PIHC3 Compiled Common Import

## Summary

Imported compiled PIHC_dev common files into native PIHC3 modules for families that can use the existing generic `simple_source` compiler path without localization reconstruction.

## Changes

- Added `projects/PIHC3/scripts/migrate_pihc2_common_sources.py`.
- Imported 323 modules:
  - `difficulty_setting`: 1
  - `on_action`: 93
  - `scripted_effect`: 129
  - `scripted_gui`: 13
  - `scripted_trigger`: 87
- Preserved each compiled PIHC_dev `.txt` file as module `def.txt`.
- Recorded source provenance in each module `meta.yaml`.
- Excluded the imported `.txt` paths from the PIHC_dev copy overlay so native artifacts own those outputs.
- Updated family migration notes and the PIHC3 migration design audit.

## Verification

- `rtk git diff --check -- docs/progress/2026-06-14-0037-pihc3-compiled-common-import.md`
- `rtk git diff --check -- paradev.yaml scripts/migrate_pihc2_common_sources.py docs/migration/00-design.md docs/migration/11-scripted-effect-trigger.md docs/migration/26-on-actions.md docs/migration/31-scripted-guis.md docs/migration/36-difficulty-settings.md` from `projects/PIHC3`
- `rtk rg -n "[[:blank:]]$" <changed paths>`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_common_sources.py`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
  - 554 passed in 177.57s
- `Project.load(Path("projects/PIHC3")).build(emit_artifacts=True, emit_manifests=True)`
  - dry_run: false
  - modules: 2,807
  - collections: 62
  - artifacts: 25,957
  - diagnostics: 4,183
  - errors: 0
  - blocked: false
- `rtk uv run paradev summary projects/PIHC3 --json`
  - modules: 2,807
  - collections: 62
  - artifacts: 25,957
  - diagnostics: 4,183
  - errors: 0
  - blocked: false
- Native ownership spot checks:
  - `common/scripted_effects/PIHC_INVENTORY.txt`
  - `common/scripted_triggers/PIHC_INVENTORY_ITEM_5LG_ARTIFACT_STAFF_OF_SACANAS.txt`
  - `common/on_actions/PIHC_ALL_DOCTRINE.txt`
  - `common/scripted_guis/PIHC_inventory.txt`
  - `common/difficulty_settings/00_difficulty.txt`
