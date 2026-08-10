# PIHC3 Event Import Progress

Date: 2026-06-08 18:51

Linear: TAL-297, TAL-298

## Done

- Replaced stale `projects/PIHC3/scripts/migrate_pihc2_events.py` with the current-layout event namespace importer.
- Imported 41 normal PIHC2 event namespaces from `resources/events` into `projects/PIHC3/src/modules/event`.
- Preserved compiled PIHC_dev namespace PDX as `def.pdx`, consolidated English/Simplified Chinese localization as `main.loc`, and recorded source evidence in `legacy/source.yaml`.
- Excluded the reviewed normal event namespace PDX/localization files from the PIHC_dev copy overlay while leaving `BCE`, `SUPER`, and `SUPER_NEWS` copy-only.
- Updated PIHC3 user and migration docs with the new event status.

## Verification

- `rtk uv run pytest tests/test_sdk_examples.py::test_pihc3_event_importer_writes_current_module_layout -q`
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_events.py --clean`
- `Project.load("projects/PIHC3").build(emit_manifests=True)` reported 870 modules, 25,313 artifacts, 0 diagnostics, 0 errors, and `blocked: False`.

## Risks Or Blockers

- Event picture DDS files and sprite/interface declarations remain copy-overlay owned.
- Date-triggered event on-action side effects still need review.
- `BCE`, `SUPER`, and `SUPER_NEWS` are not part of the normal event namespace import and need later targeted slices.

## Next

- Add an event parity reviewer against `PIHC_dev/events`.
- Pick the next high-value domain, likely decisions, focuses, characters, or achievements, based on importer complexity and copy-overlay impact.
