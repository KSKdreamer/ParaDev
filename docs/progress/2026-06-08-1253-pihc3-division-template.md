# PIHC3 Division Template Progress

Date: 2026-06-08 12:53 CST

Linear: TAL-298, TAL-297

## Done

- Added the project-local `division` simple-source family to `projects/PIHC3/paradev.yaml`.
- Added the `pihc3:division/basic` authoring template for one-call SDK or compact GUI creation.
- Kept the compact create form minimal: `title` is the only primary field.
- The template writes `meta.yaml` and `def.pdx` under `src/modules/division/{object_id}/`.
- The default body is a land-unit history shell with one `division_template` and one deployed `units = { division = { ... } }` block.
- Refreshed the starter shape against current local HOI4 unit-history files under `/Users/magolor/Library/Application Support/Steam/steamapps/common/Hearts of Iron IV/history/units/`.
- Added SDK example coverage proving `Project.create_module("division", ...)` resolves the PIHC3 template, writes source files, and builds cleanly.
- Updated the PIHC3 user manual and added `projects/PIHC3/docs/migration/16-divisions.md`.

## Verification

- Red checks: the new division test first failed with `KeyError: 'division'` and the primary-field metadata test failed with `KeyError: 'pihc3:division/basic'`.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py::test_pihc3_division_template_scaffolds_basic_unit_history_shell tests/test_sdk_examples.py::test_pihc3_template_args_mark_only_primary_create_fields -q`: 2 passed.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py -q`: 26 passed.
- SDK template projection: `division ['title']`, with `location` defaulting to advanced string `11805`.
- Desktop-state template projection: `PIHC3 division ['title']`.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_sdk_examples.py`: passed.
- `rtk bash scripts/flake.bash --ci --paths tests/test_sdk_examples.py`: passed.
- PIHC3 build through the SDK: 529 modules, 0 collections, 0 dependencies, 26892 artifacts, 0 diagnostics, 0 errors, not blocked.
- `rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json`: 0 diagnostics.
- `rtk git diff --check`: passed.

## Risks Or Blockers

- This is a starter authoring template, not a PIHC2 division importer.
- Country OOB grouping, name-list wiring, support companies, multi-division files, air wings, naval task forces, starting stockpiles, equipment production, and legacy parity review remain future slices.
- The starter template only creates a minimal land-unit history source file; authors still need later templates, importers, or OOB tooling for a playable country setup.
- `projects/PIHC3/` is ignored by the current `.gitignore`, so the PIHC3 manifest and migration-note changes are local project-state changes rather than normal tracked diff entries.

## Next

- Continue expanding GUI-visible PIHC3 families that still lack starters, such as ideology or special-project shells, or begin mapping PIHC2 division source shapes for import.
