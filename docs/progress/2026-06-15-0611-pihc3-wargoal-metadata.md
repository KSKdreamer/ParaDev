# PIHC3 Wargoal Metadata Progress

Date: 2026-06-15 06:11

Linear: TAL-000

## Done

- Extended the wargoal importer contract to assert generated `meta.yaml` structure for `take_claimed_state`.
- Updated `projects/PIHC3/scripts/migrate_pihc2_wargoals.py` to mirror shallow compiled wargoal structure into module settings: wargoal id, field order, scalar costs and threat values, block field/root keys, war-name localization key, owned localization keys, and localization language count.
- Regenerated the 13 native `wargoal` modules from compiled PIHC_dev `common/wargoals/00_invasion.txt`.
- Updated the wargoal migration design summary and legacy inventory evidence.

## Verification

- Red: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k wargoal_importer_extracts_individual_wargoal_contract` failed with missing `settings["wargoal_id"]`.
- Green: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k wargoal_importer_extracts_individual_wargoal_contract` passed: 1 passed, 169 deselected.
- Related wargoal contracts: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k "wargoal_family_uses_shared_def_and_loc_slots or wargoal_importer_extracts_individual_wargoal_contract"` passed: 2 passed, 168 deselected.
- Format: `rtk uv run black projects/PIHC3/scripts/migrate_pihc2_wargoals.py tests/test_pihc3_migration_contracts.py` reformatted the test file and left the importer unchanged.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_wargoals.py tests/test_pihc3_migration_contracts.py` passed.
- Regeneration: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_wargoals.py --clean` wrote 13 wargoal modules.
- Metadata sample: regenerated `take_claimed_state` and `crusade_wargoal` modules include field order, scalar cost/threat fields, block root keys, localization keys, and localization language counts.
- Dry build: `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-wargoal-metadata-dry-build.json` reported 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.
- Hygiene: `rtk git diff --check` passed; explicit trailing-whitespace scan over touched Python, docs, and sample regenerated wargoal metadata returned no findings.

## Risks Or Blockers

- This slice summarizes direct wargoal records only. It does not reconstruct scripted consumers, peace-conference balance, AI behavior, or higher-level authoring.

## Next

- Continue improving thin non-map gameplay families with shallow metadata and focused dry-build checks.
