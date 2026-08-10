# C08 Main Source Layout Fields Progress

Date: 2026-06-21 01:57

Linear: TAL-000

## Done

- Added a PIHC3 migration contract that checks the local `C08_MAIN` focus-tree module preserves legacy source layout fields in `settings.source_focuses`.
- Regenerated `projects/PIHC3/src/modules/focus_tree/C08_MAIN` with `projects/PIHC3/scripts/migrate_pihc2_focuses.py --only C08_MAIN` so the GUI source-backed fixture has real `tree`, `parent`, `x`, `y`, `dx`, `dy`, `dw`, `dc`, and `priority` values.
- Kept this scoped to the ignored local PIHC3 fixture; the tracked durable change is the regression test guarding the fixture shape.

## Verification

- Red: `rtk bash scripts/test.bash tests/test_pihc3_migration_contracts.py -k checked_in_focus_tree_metadata_preserves_legacy_layout_fields -q` failed with missing `source_focuses[*].tree`.
- Regenerated: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_focuses.py --only C08_MAIN`.
- Green: `rtk bash scripts/test.bash tests/test_pihc3_migration_contracts.py -k checked_in_focus_tree_metadata_preserves_legacy_layout_fields -q`.
- `rtk bash scripts/test.bash tests/test_pihc3_migration_contracts.py -k 'focus_tree_importer_extracts_source_localization_and_image_metadata_contract or checked_in_focus_tree_metadata_preserves_legacy_layout_fields' -q`.
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/projectDiagram.test.ts src/moduleEditor/diagramMetadata.test.ts`.

## Risks Or Blockers

- `projects/PIHC3/` is ignored by Git in this workspace, so the regenerated `C08_MAIN` metadata is local fixture state, not a tracked diff.
- A full `desktop_state` probe over PIHC3 was stopped because it exceeded the useful verification window for this slice.

## Next

- Move toward source-folder `info.json` draft writes for source-backed focus edits so the GUI can update the PIHC source layer directly instead of only editing module metadata summaries.
