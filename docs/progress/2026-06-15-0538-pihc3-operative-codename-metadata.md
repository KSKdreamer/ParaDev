# PIHC3 Operative Codename Metadata Progress

Date: 2026-06-15 05:38

Linear: TAL-000

## Done

- Extended the operative-codename importer contract to assert generated `meta.yaml` structure for `GENERIC_ENG_OPERATIVE_CODENAME_HISTORICAL`.
- Updated `projects/PIHC3/scripts/migrate_pihc2_operative_codenames.py` to mirror shallow compiled theme structure into module settings: theme id, field order, scalar fields, localized name key, theme type, fallback pattern, owned localization keys, localization language count, and unique codename names.
- Regenerated the native `operative_codename` module from compiled PIHC_dev `common/units/codenames_operatives/generic_opertive_codenames.txt`.
- Updated the operative-codename migration note, design summary, and legacy inventory evidence.

## Verification

- Red: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k operative_codename_importer_extracts_individual_theme_contract` failed with missing `settings["theme_id"]`.
- Green: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k operative_codename_importer_extracts_individual_theme_contract` passed: 1 passed, 169 deselected.
- Related operative-codename contracts: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k "operative_codename_family_uses_shared_def_and_loc_slots or operative_codename_importer_extracts_individual_theme_contract or operative_codename_uses_dedicated_importer_not_generic_common_batch"` passed: 3 passed, 167 deselected.
- Format: `rtk uv run black projects/PIHC3/scripts/migrate_pihc2_operative_codenames.py tests/test_pihc3_migration_contracts.py` reformatted the test file and left the importer unchanged.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_operative_codenames.py tests/test_pihc3_migration_contracts.py` passed.
- Regeneration: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_operative_codenames.py --clean` wrote 1 operative-codename module.
- Metadata sample: regenerated module covers 17 unique codenames, 2 owned localization keys, and the compiled `name`, `type`, and `fallback_name` scalar fields.
- Dry build: `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-operative-codename-metadata-dry-build.json` reported 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.

## Risks Or Blockers

- This slice summarizes direct operative-codename theme structure only. It does not reconstruct broader codename packs, multilingual codename lists, country coverage, or non-codename name-theme variants.

## Next

- Continue improving thin non-map gameplay families with shallow metadata and focused dry-build checks.
