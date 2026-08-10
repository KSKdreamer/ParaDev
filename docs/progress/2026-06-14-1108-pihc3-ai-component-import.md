# PIHC3 AI Component Import

Date: 2026-06-14 11:08 Asia/Shanghai

## Summary

- Added `projects/PIHC3/scripts/migrate_pihc2_ai_components.py` to import compiled PIHC_dev AI support files.
- Added the project-local `ai_component` family with a generic path-preserving PDX slot.
- Regenerated 31 `src/modules/ai_component` modules:
  - 1 `common/ai_faction_theaters/*.txt` file;
  - 1 `common/ai_focuses/*.txt` file;
  - 3 `common/ai_navy/**/*.txt` files;
  - 13 `common/ai_strategy/*.txt` files;
  - 12 `common/ai_strategy_plans/*.txt` files;
  - 1 `common/ai_templates/*.txt` file.
- Excluded those reviewed AI support paths from the PIHC_dev copy overlay.
- Updated the AI migration note, copy-overlay baseline, main migration design, and legacy inventory.

## Verification

- Red check before implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'ai_component'` failed on the missing `ai_component` family and missing `projects/PIHC3/scripts/migrate_pihc2_ai_components.py`.
- Focused green after implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'ai_component'` passed `2 passed, 74 deselected`.
- Formatting/style: `rtk uv run black tests/test_pihc3_migration_contracts.py projects/PIHC3/scripts/migrate_pihc2_ai_components.py` and `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_pihc3_migration_contracts.py projects/PIHC3/scripts/migrate_pihc2_ai_components.py` completed cleanly.
- Importer run: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_ai_components.py --clean` imported 31 modules.
- Full PIHC3 emit build: `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json` completed with 12,068 modules, 62 collections, 36,214 artifacts, 3,842 diagnostics, 0 errors, and `blocked: false`.
- Manifest check found 31 AI-component modules, 31 AI-component-owned artifacts, and 0 build errors.

## Notes

- The importer preserves compiled PIHC_dev AI support files exactly as game-relative PDX sources instead of splitting strategy or template records into editable objects.
- Documentation-only AI files are intentionally skipped.
- Higher-level editable AI strategy/template authoring and gameplay validation remain future work.
