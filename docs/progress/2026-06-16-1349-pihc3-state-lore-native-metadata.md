# PIHC3 State Lore Native Metadata

## Scope

- Continued the PIHC2 state-lore migration without adding map-editing behavior or splitting the aggregate family.
- Enhanced `projects/PIHC3/scripts/migrate_pihc2_state_lores.py` so each `state_lore` module records source files, localization rows, generated scripted-localisation facts, on-startup state references, and aggregate output paths.
- Updated `projects/PIHC3/system/state_lore_family.py` so generic surfaces can discover the richer settings keys.
- Regenerated all 79 ignored PIHC3 state-lore modules with `--clean`.

## Result

- The 79 modules now expose 36 settings each instead of 5.
- The source inventory records 81 legacy source files: 79 `locs.txt` files plus 2 conditional `info.json` files.
- Metadata records 81 state-lore localization keys across both `l_english` and `l_simp_chinese`.
- `STATE_LORE_217` and `STATE_LORE_772` now expose their `has_global_flag` conditional trigger metadata and conditional localization keys.
- The build output owns 158 state-lore localization artifacts and the two aggregate PDX outputs; shared replacement `STATE_LORE` localization remains owned by `localization_component`.

## Verification

- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k state_lore_importer_extracts_source_localization_and_pdx_metadata_contract` failed before implementation on missing `module_id`, then passed after the importer change.
- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k state_lore` passed with 4 selected tests.
- `rtk uv run black --check projects/PIHC3/scripts/migrate_pihc2_state_lores.py projects/PIHC3/system/state_lore_family.py tests/test_pihc3_migration_contracts.py` passed.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_state_lores.py projects/PIHC3/system/state_lore_family.py tests/test_pihc3_migration_contracts.py` reported `OK: 3 file(s) - no banned imports`.
- `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-state-lore-native-metadata-build.json` passed with 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.

## Remaining Work

- Review state-lore UI behavior against the copied scripted GUI/interface support if GUI parity becomes a target.
- Keep map-state geometry and strategic-region data out of this migration path until the skipped map-related slices resume.
