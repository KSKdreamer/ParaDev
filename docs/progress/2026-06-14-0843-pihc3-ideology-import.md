# PIHC3 Ideology Import

Date: 2026-06-14 08:43 Asia/Shanghai

## Summary

- Added `projects/PIHC3/scripts/migrate_pihc2_ideologies.py` to import compiled PIHC2 ideology groups from `PIHC_dev/common/ideologies/00_ideologies.txt`.
- Regenerated 9 `src/modules/ideology` modules: `anarchy`, `corporation`, `democratic`, `despotic`, `equatism`, `fascism`, `harmonicism`, `peacism`, and `transcendence`.
- Updated the project-local `ideology` family localization contract to require only group title/description keys; real subtype localization is selected from parsed `types` entries.
- Excluded `common/ideologies/*.txt` from the PIHC_dev copy overlay so generated PIHC3 ideology PDX owns the reviewed definition files.
- Updated migration docs and the legacy inventory with the ideology cutover.

## Verification

- Red check before implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'ideology'` failed on missing `projects/PIHC3/scripts/migrate_pihc2_ideologies.py`.
- Focused green after implementation and validation-contract fix: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'ideology'` passed `2 passed, 60 deselected`.
- Formatting/style: `rtk uv run black projects/PIHC3/scripts/migrate_pihc2_ideologies.py tests/test_pihc3_migration_contracts.py` and `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_ideologies.py tests/test_pihc3_migration_contracts.py` completed cleanly.
- Importer run: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_ideologies.py --clean` imported 9 modules.
- Full PIHC3 emit build: `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json` completed with 11,849 modules, 62 collections, 36,173 artifacts, 3,842 diagnostics, 0 errors, and `blocked: false`.
- Manifest check found 27 ideology-owned artifacts and 0 ideology diagnostics.

## Notes

- This slice preserves compiled PIHC_dev ideology PDX. Reconstructing higher-level ideology authoring records, party-name review, country ideology setup, drift hooks, icon/interface review, AI behavior balancing, and broader localization replacement-file cleanup remain future work.
