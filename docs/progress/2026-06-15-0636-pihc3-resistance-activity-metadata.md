# PIHC3 Resistance Activity Metadata Progress

Date: 2026-06-15 06:36

Linear: TAL-000

## Done

- Extended the resistance-activity importer contract to assert generated `meta.yaml` structure for `sabotage_oil`.
- Updated `projects/PIHC3/scripts/migrate_pihc2_resistance_activities.py` to mirror shallow compiled activity structure into module settings: activity id, field order, scalar fields, block field/root keys, repeated root-key counts, alert key, owned localization keys, and localization language count.
- Regenerated the 17 native `resistance_activity` modules from compiled PIHC_dev `common/resistance_activity/resistance_activity.txt`.
- Updated the resistance-activity migration design summary and legacy inventory evidence.

## Verification

- Red: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k resistance_activity_importer_extracts_individual_activity_contract` failed with missing `settings["activity_id"]`.
- Green: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k resistance_activity_importer_extracts_individual_activity_contract` passed: 1 passed, 169 deselected.
- Related resistance-activity contracts: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k "resistance_activity_family_uses_shared_def_and_loc_slots or resistance_activity_importer_extracts_individual_activity_contract"` passed: 2 passed, 168 deselected.
- Format: `rtk uv run black projects/PIHC3/scripts/migrate_pihc2_resistance_activities.py tests/test_pihc3_migration_contracts.py` reformatted the test file and left the importer unchanged.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_resistance_activities.py tests/test_pihc3_migration_contracts.py` passed.
- Regeneration: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_resistance_activities.py --clean` wrote 17 resistance-activity modules.
- Metadata sample: regenerated `sabotage_oil` and `sabotage_arms_factory` modules include activity id, field order, alert key, block root keys, repeated root-key counts, and 10-language localization coverage.
- Dry build: `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-resistance-activity-metadata-dry-build.json` reported 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.
- Hygiene: `rtk git diff --check` passed; explicit trailing-whitespace scan over touched Python, docs, and sample regenerated resistance-activity metadata returned no findings.

## Risks Or Blockers

- This slice summarizes direct resistance-activity records only. It does not reconstruct targeted sabotage variables, occupation-law weight modifiers, dynamic resource sabotage duration, or broader balancing semantics.

## Next

- Continue improving thin non-map gameplay families with shallow metadata and focused dry-build checks.
