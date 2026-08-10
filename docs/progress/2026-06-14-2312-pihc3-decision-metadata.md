# PIHC3 Decision Metadata Extraction

Status: completed slice

## Scope

- Updated `projects/PIHC3/scripts/migrate_pihc2_decisions.py` so native decision category collections and decision modules expose compiled PDX data in `meta.yaml` settings.
- Regenerated all 62 `src/collections/decision/DECISION_CATEGORY_<TAG>` collections and all imported `src/modules/decision/DECISION_<TAG>` modules.
- Kept the built-in HOI4 `decision` family on shared `def`, `loc`, and `icon` slots; no family-specific compiler code was added.

## Details

- Category metadata now records `category_keys`, icon, picture, priority, allowed/visible blocks, and `visible_when_empty` where present.
- Decision metadata now records `decision_keys`, compiled category id, fixed random seed, priority, cost, timers, visible/available/custom-cost triggers, modifiers, effects, AI weights, and icon where present.
- The importer now parses compiled PIHC_dev decision/category PDX for metadata while preserving the compiled source text in `def.txt`.
- Direct import loading now adds the script directory to `sys.path`, so the importer contract can be exercised by focused tests.

## Verification

- Red: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'decision_importer or decision_family or decision_component or decision_asset_component'` first failed on missing script-local helper import.
- Green: the same focused suite passed with 6 tests and 149 deselected after metadata extraction was implemented.
- Regeneration: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_decisions.py --clean` imported 62 decision category collections and rewrote the decision modules.
- Build: `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-decision-metadata-build.json` exited 0 and reported 16,581 modules, 62 collections, 37,390 artifacts, 713 diagnostics, 0 errors, `blocked: false`.

## Remaining

- Decision category creation still needs a first-class template or SDK helper.
- Category-specific GUI/scripted-GUI parity and per-decision asset generation remain future slices.
