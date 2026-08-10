# PIHC3 Division Metadata

Date: 2026-06-15 08:07

## Slice

- Continued PIHC2-to-PIHC3 migration on the non-map `division` family.
- Kept the existing generic path-preserving PDX slots for `history/units/*.txt` and `common/units/names_divisions/*.txt`.
- Enhanced `projects/PIHC3/scripts/migrate_pihc2_divisions.py` so generated modules expose structured OOB metadata in `meta.yaml`:
  - source JSON template filenames and names;
  - compiled history/name file ownership;
  - top-level history entry counts;
  - division-template names/counts, regiment/support types, priorities, and name-group links;
  - deployed division counts, template usage, location ids, start factors, and name-order ranges;
  - division-name group ids, countries, division types, and fallback names.
- Regenerated 73 division modules under `projects/PIHC3/src/modules/division`.

## Verification

- Red first: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k test_pihc3_division_importer_extracts_oob_metadata_contract` failed on missing `settings["module_id"]`.
- Green after importer update: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k test_pihc3_division_importer_extracts_oob_metadata_contract` passed.
- Focused division group: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k division` passed with 3 tests.
- Heaven-style scan passed for `projects/PIHC3/scripts/migrate_pihc2_divisions.py` and `tests/test_pihc3_migration_contracts.py`.
- PIHC3 dry build passed with 16,581 modules, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.
- `rtk git diff --check` and a trailing-whitespace scan over the touched/generated division paths were clean.

## Next

- Future parity still needs editable OOB/template reconstruction and broader country setup tooling; this slice only makes compiled division modules more inspectable.
