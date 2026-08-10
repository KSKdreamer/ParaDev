# PIHC3 Event Metadata Progress

Date: 2026-06-15 03:11

Linear: TAL-000

## Done

- Added a focused migration contract for normal event namespace metadata using `C08_MAIN`.
- Extended `projects/PIHC3/scripts/migrate_pihc2_events.py` to mirror top-level compiled `country_event` and `news_event` records into module metadata.
- Regenerated all 41 event namespace modules; `C08_MAIN` now reports 84 top-level events, 69 country events, 15 news events, picture keys, loc keys, and bounded per-event summaries.
- Updated the event migration note, design summary, and legacy inventory with the new event metadata scope.

## Verification

- Red: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'event_importer_extracts_namespace_metadata'` failed with missing `settings["event_count"]`.
- Green: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'event_importer_extracts_namespace_metadata'` passed: 1 passed, 166 deselected.
- Regeneration: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_events.py --clean`.
- Dry build: `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-event-metadata-dry-build.json` reported 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.

## Risks Or Blockers

- Event metadata intentionally summarizes top-level namespace records only. Nested event calls inside effects remain in `def.txt`.

## Next

- Continue enhancing low-data non-map families with source-owned metadata where it improves GUI browsing without splitting compiled support bundles prematurely.
