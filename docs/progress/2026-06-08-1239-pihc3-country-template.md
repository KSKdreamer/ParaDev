# PIHC3 Country Template Progress

Date: 2026-06-08 12:39 CST

Linear: TAL-298, TAL-297

## Done

- Added the project-local `country` simple-source family to `projects/PIHC3/paradev.yaml`.
- Added the `pihc3:country/basic` authoring template for one-call SDK or compact GUI creation.
- Kept the compact create form minimal: `title` and `description` are the only primary fields.
- The template writes `meta.yaml`, `def.pdx`, and `main.loc` under `src/modules/country/{object_id}/`.
- The default country body is a common-country definition shell with `graphical_culture`, `graphical_culture_2d`, `color = rgb { ... }`, and `color_ui = rgb { ... }`.
- Refreshed the starter shape against current local HOI4 country files under `/Users/magolor/Library/Application Support/Steam/steamapps/common/Hearts of Iron IV/common/countries/`.
- Added SDK example coverage proving `Project.create_module("country", ...)` resolves the PIHC3 template, writes source files, and builds cleanly.
- Updated the PIHC3 user manual and added `projects/PIHC3/docs/migration/14-countries.md`.

## Verification

- Red checks: the new country test first failed with `KeyError: 'country'` and the primary-field metadata test failed with `KeyError: 'pihc3:country/basic'`.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py::test_pihc3_country_template_scaffolds_basic_country_shell tests/test_sdk_examples.py::test_pihc3_template_args_mark_only_primary_create_fields -q`: 2 passed.
- SDK template projection: `country ['title', 'description']`, with `color` defaulting to string `100 160 220`.
- Desktop-state template projection: `PIHC3 country ['title', 'description']`.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py -q`: 24 passed.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_sdk_examples.py`: passed.
- `rtk bash scripts/flake.bash --ci --paths tests/test_sdk_examples.py`: passed.
- PIHC3 build through the SDK: 529 modules, 0 collections, 0 dependencies, 26892 artifacts, 0 diagnostics, 0 errors, not blocked.
- `rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json`: 0 diagnostics.
- `rtk git diff --check`: passed.

## Risks Or Blockers

- This is a starter authoring template, not a PIHC2 country importer.
- Country tag registration, history files, flags, portraits, map ownership, AI setup, and OOB wiring remain future slices.
- The starter template only creates a minimal common-country definition; authors still need later templates or importers for a playable country.
- `projects/PIHC3/` is ignored by the current `.gitignore`, so the PIHC3 manifest and migration-note changes are local project-state changes rather than normal tracked diff entries.

## Next

- Continue expanding GUI-visible PIHC3 families that still lack starters, especially `state` and `division`, or begin mapping PIHC2 country source shapes for import.
