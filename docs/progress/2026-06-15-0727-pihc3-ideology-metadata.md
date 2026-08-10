# PIHC3 Ideology Metadata Progress

Date: 2026-06-15 07:27

Linear: TAL-000

## Done

- Extended the ideology importer contract to assert generated `meta.yaml` structure for `ideology/harmonicism`.
- Updated `projects/PIHC3/scripts/migrate_pihc2_ideologies.py` to mirror compiled ideology metadata for generic GUI browsing: ideology id, field order, subtype ids, non-random subtype ids, RGB color, scalar tension/AI fields, rule maps, modifier maps, faction modifier maps, AI flags, owned localization keys, and localization language count.
- Regenerated the 9 native `ideology` modules from compiled PIHC_dev `common/ideologies/00_ideologies.txt`.
- Updated the ideology migration design summary and legacy inventory evidence.

## Verification

- Red: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k ideology_importer_extracts_group_metadata_contract` failed with missing `settings["ideology_id"]`.
- Green: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k ideology_importer_extracts_group_metadata_contract` passed: 1 passed, 173 deselected.
- Related ideology contracts: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k "ideology_family_uses_shared_def_and_loc_slots or ideology_importer_extracts_individual_ideology_contract or ideology_importer_extracts_group_metadata_contract"` passed: 3 passed, 171 deselected.
- Format: `rtk uv run black projects/PIHC3/scripts/migrate_pihc2_ideologies.py tests/test_pihc3_migration_contracts.py` reformatted the importer and left the test file unchanged.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_ideologies.py tests/test_pihc3_migration_contracts.py` passed.
- Regeneration: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_ideologies.py --clean` wrote 9 ideology modules.
- Metadata sample: regenerated `harmonicism` exposes 20 subtypes, 8 non-random subtypes, color `[255, 150, 203]`, 8 rule flags, 15 ideology modifiers, one faction modifier, and two-language localization coverage.
- Dry build: `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-ideology-metadata-dry-build.json` reported 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.
- Hygiene: `rtk git diff --check` passed; explicit trailing-whitespace scan over touched Python, docs, progress note, and regenerated ideology metadata returned no findings.

## Risks Or Blockers

- This slice summarizes compiled ideology groups only. It does not reconstruct higher-level ideology authoring, party-name review, country ideology setup, drift hooks, icon/interface review, AI balancing, or replacement-localization cleanup.

## Next

- Continue improving thin non-map gameplay families with shallow metadata and focused dry-build checks.
