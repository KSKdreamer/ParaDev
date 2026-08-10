# PIHC3 Ideology Template Progress

Date: 2026-06-08 13:04 CST

Linear: TAL-298, TAL-297

## Done

- Added the project-local `ideology` simple-source family to `projects/PIHC3/paradev.yaml`.
- Added the `pihc3:ideology/basic` authoring template for one-call SDK or compact GUI creation.
- Kept the compact create form minimal: `title` and `description` are the only primary fields.
- The template writes `meta.yaml`, `def.pdx`, and `main.loc` under `src/modules/ideology/{object_id}/`.
- The default body follows the local HOI4 `ideologies = { ... }` shape with one ideology group, one subtype, a color, basic rules, and world-tension impact fields.
- Refreshed the starter shape against current local HOI4 ideology files under `/Users/magolor/Library/Application Support/Steam/steamapps/common/Hearts of Iron IV/common/ideologies/`.
- Added SDK example coverage proving `Project.create_module("ideology", ...)` resolves the PIHC3 template, writes source files, and builds cleanly.
- Updated the PIHC3 user manual and added `projects/PIHC3/docs/migration/18-ideologies.md`.

## Verification

- Red checks: the new ideology test first failed with `KeyError: 'ideology'` and the primary-field metadata test failed with `KeyError: 'pihc3:ideology/basic'`.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py::test_pihc3_ideology_template_scaffolds_basic_ideology_group tests/test_sdk_examples.py::test_pihc3_template_args_mark_only_primary_create_fields -q`: 2 passed.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py -q`: 28 passed.
- SDK template projection: `ideology ['title', 'description']`, with `color` defaulting to advanced string `120 150 220`.
- Desktop-state template projection: `PIHC3 ideology ['title', 'description']`.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_sdk_examples.py`: passed.
- `rtk bash scripts/flake.bash --ci --paths tests/test_sdk_examples.py`: passed.
- PIHC3 build through the SDK: 529 modules, 0 collections, 0 dependencies, 26892 artifacts, 0 diagnostics, 0 errors, not blocked.
- `rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json`: 0 diagnostics.
- `rtk git diff --check`: passed.

## Risks Or Blockers

- This is a starter authoring template, not a PIHC2 ideology importer.
- Party names, country ideology setup, icons, modifiers, faction names, AI behavior fields, ideology drift hooks, and legacy parity review remain future slices.
- The starter template only creates one editable ideology group and subtype; authors still need later templates or importers for a complete ideology system.
- `projects/PIHC3/` is ignored by the current `.gitignore`, so the PIHC3 manifest and migration-note changes are local project-state changes rather than normal tracked diff entries.

## Next

- Continue expanding GUI-visible PIHC3 families that still lack starters, such as special-project or intelligence-agency shells, or begin mapping PIHC2 ideology source shapes for import.
