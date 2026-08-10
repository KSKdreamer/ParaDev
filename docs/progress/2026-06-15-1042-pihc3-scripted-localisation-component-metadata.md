# 2026-06-15 10:42 PIHC3 Scripted Localisation Component Metadata

## Slice

Enriched the `scripted_localisation_component` modules while keeping the existing shared path-preserving PDX slot. The slice does not split compiled `defined_text` records into editable source records.

## Changes

- Added a migration contract test for aggregate scripted-localisation metadata and representative trade, inventory, and superevent selector summaries.
- Updated `projects/PIHC3/scripts/migrate_pihc2_scripted_localisation_components.py` to record component id, source slot, byte size, line counts, top-level key counts, defined-text names/counts, text-entry counts, trigger counts, localization-key counts, and key samples.
- Regenerated the ignored `projects/PIHC3/src/modules/scripted_localisation_component/` modules with metadata for 29 reviewed support files.
- Updated the scripted-localisation migration note, PIHC3 migration design overview, and central legacy inventory.

## Verification

- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k scripted_localisation_component` passed with `3 passed, 188 deselected`.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_scripted_localisation_components.py tests/test_pihc3_migration_contracts.py` passed with no banned imports.
- `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-scripted-localisation-metadata-build.json` passed with 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.
- The build manifest contains 29 `module:scripted_localisation_component/...` artifacts, 0 copy-root-owned reviewed scripted-localisation text artifacts, and the skipped `PIHC_STATE_LORES.txt` remains project-owned.
