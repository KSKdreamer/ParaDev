# PIHC3 Special Project Template Progress

Date: 2026-06-08 13:09 CST

Linear: TAL-298, TAL-297

## Done

- Added the project-local `special_project` simple-source family to `projects/PIHC3/paradev.yaml`.
- Added the `pihc3:special_project/basic` authoring template for one-call SDK or compact GUI creation.
- Kept the compact create form minimal: `title` and `description` are the only primary fields.
- The template writes `meta.yaml`, `def.pdx`, and `main.loc` under `src/modules/special_project/{object_id}/`.
- The default body follows the local HOI4 special-project project shape with specialization, project tag, AI weight, availability, breakthrough cost, prototype time, complexity, project output, and one generic prototype reward.
- Refreshed the starter shape against current local HOI4 special-project files under `/Users/magolor/Library/Application Support/Steam/steamapps/common/Hearts of Iron IV/common/special_projects/`.
- Added SDK example coverage proving `Project.create_module("special_project", ...)` resolves the PIHC3 template, writes source files, and builds cleanly.
- Updated the PIHC3 user manual and added `projects/PIHC3/docs/migration/19-special-projects.md`.

## Verification

- Red checks: the new special project test first failed with `KeyError: 'special_project'` and the primary-field metadata test failed with `KeyError: 'pihc3:special_project/basic'`.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py::test_pihc3_special_project_template_scaffolds_basic_project_shell tests/test_sdk_examples.py::test_pihc3_template_args_mark_only_primary_create_fields -q`: 2 passed.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py -q`: 29 passed.
- SDK template projection: `special_project ['title', 'description']`, with `specialization` defaulting to advanced string `specialization_land`.
- Desktop-state template projection: `PIHC3 special_project ['title', 'description']`.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_sdk_examples.py`: passed.
- `rtk bash scripts/flake.bash --ci --paths tests/test_sdk_examples.py`: passed.
- PIHC3 build through the SDK: 529 modules, 0 collections, 0 dependencies, 26892 artifacts, 0 diagnostics, 0 errors, not blocked.
- `rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json`: 0 diagnostics.
- `rtk git diff --check`: passed.

## Risks Or Blockers

- This is a starter authoring template, not a PIHC2 special project importer.
- Project-tag definitions, prototype reward definitions, specializations, icons, facilities, equipment unlocks, scripted effects, reward option localization, and legacy parity review remain future slices.
- The starter template only creates one editable special-project project record; authors still need later templates or importers for a complete special project chain.
- `projects/PIHC3/` is ignored by the current `.gitignore`, so the PIHC3 manifest and migration-note changes are local project-state changes rather than normal tracked diff entries.

## Next

- Continue expanding GUI-visible PIHC3 families that still lack starters, such as achievement, balance-of-power, or intelligence-agency shells, or begin mapping PIHC2 special project source shapes for import.
