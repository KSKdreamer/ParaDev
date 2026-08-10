# PIHC3 Operation Metadata Progress

Date: 2026-06-15 04:05

Linear: TAL-000

## Done

- Added a focused migration contract for compiled operation metadata using `operation_infiltrate_civilian` and `operation_collaboration_government`.
- Extended `projects/PIHC3/scripts/migrate_pihc2_operations.py` to mirror direct compiled operation fields into module metadata.
- Regenerated all 18 operation modules; generated metadata now covers 193 phase references across 54 phase blocks, 5 equipment entries, 5 awarded-token references, 24 risk modifier references, 25 outcome modifier references, and 21 cost modifier references.
- Updated the operations migration note, design summary, and legacy inventory with the new metadata scope.

## Verification

- Red: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k operation_importer_extracts_individual_operation_contract` failed with missing `settings["operation_id"]`.
- Green: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k operation_importer_extracts_individual_operation_contract` passed: 1 passed, 167 deselected.
- Regeneration: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_operations.py --clean`.
- Dry build: `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-operation-metadata-dry-build.json` reported 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.

## Risks Or Blockers

- Operation metadata intentionally summarizes direct top-level fields, list references, and phase ids/base weights only. Deep target selection, scripted outcome semantics, AI strategy balancing, equipment balancing, and map icon art remain future slices.

## Next

- Continue enhancing low-data non-map families with source-owned metadata where it improves GUI browsing without splitting compiled support bundles prematurely.
