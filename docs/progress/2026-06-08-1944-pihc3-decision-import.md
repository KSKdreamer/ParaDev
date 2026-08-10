# PIHC3 Decision Import Progress

Date: 2026-06-08 19:44 CST

Linear: TAL-297, TAL-298, TAL-295

## Done

- Replaced the stale PIHC3 decision importer with a current-layout importer for `src/collections/decision` and `src/modules/decision`.
- Imported 62 PIHC2 decision category collections and 458 decision modules from PIHC2/PIHC_dev.
- Added copy-root excludes for generated decision PDX and localization outputs to avoid duplicate legacy definitions.
- Updated the PIHC3 migration design, decisions migration note, user manual, and Linear sync notes.

## Verification

- `rtk uv run python -m pytest tests/test_sdk_examples.py::test_pihc3_decision_importer_writes_current_module_and_collection_layout -q`
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_decisions.py --clean`
- `rtk uv run paradev summary projects/PIHC3 --json`
- Final PIHC3 summary: 1,606 modules, 62 collections, 25,355 artifacts, 0 diagnostics, 0 errors, `blocked: false`.

## Risks Or Blockers

- Decision icon DDS generation, category/decision sprite declarations, scripted GUI parity, category authoring helpers, and editable per-decision source reconstruction are unfinished.
- Broader PIHC2 parity still needs achievements, inventory items, superevents, state lore, entities, countries, states, map data, equipment, doctrines, factions, scripted GUI, and other remaining families.

## Next

- Pick the next high-value imported family from the unfinished list and keep the SDK/GUI creation path template-backed and compact.
