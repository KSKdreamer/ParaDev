# 2026-06-16 11:24 PIHC3 event native metadata

## Scope

Enrich the native PIHC2 normal-event namespace import so PIHC3 can browse event provenance, source folders, localization density, source images, and compiled field groups through generic module settings.

## Changes

- Added a focused red contract for `C08_MAIN` event metadata covering namespace ids, compiled source status, source slot counts, legacy resource evidence, folder tag facts, `info.json` key counts, localization counts, field groups, option counts, and trigger/effect summaries.
- Extended `projects/PIHC3/scripts/migrate_pihc2_events.py` with generic metadata helpers for event source evidence, localization summaries, info-key counts, and compiled PDX field groups.
- Regenerated all 41 native event namespace modules with `--clean`.
- Updated the PIHC3 event migration note, design overview, and legacy inventory with the refreshed native event coverage.

## Evidence

- Red contract: `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k event_importer_extracts_source_slot_localization_and_field_metadata_contract` failed first with `KeyError: 'namespace_id'`.
- Green contract: the same focused command passed with `1 passed, 228 deselected`.
- Regeneration: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_events.py --clean` imported 41 PIHC2 event namespace modules.
- Metadata coverage: 41 modules, 41 settings per module, 866 top-level events, 1,288 options, 5,997 localization rows, 2,396 legacy resource evidence paths, 659 source images, 8 trigger-summary modules, and 23 effect-summary modules.
- Focused regression: `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k event_importer` passed with `4 passed, 225 deselected`.
- Formatting: `rtk uv run black --check projects/PIHC3/scripts/migrate_pihc2_events.py tests/test_pihc3_migration_contracts.py` passed.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_events.py tests/test_pihc3_migration_contracts.py` returned `OK: 2 file(s) - no banned imports`.
- Build: `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-event-native-metadata-build.json` completed with 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.
- Build ownership: native event modules own 124 artifacts, including 41 `events/<namespace>.txt` files and 83 localization YAML files. The build has 0 copy-root-owned `events/` artifacts.

## Follow-Up

Date-triggered on-action side effects, editable BCE border-conflict reconstruction, and higher-level namespace/event authoring workflows remain future event slices.
