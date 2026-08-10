# PIHC3 State Template Progress

Date: 2026-06-08 12:46 CST

Linear: TAL-298, TAL-297

## Done

- Added the project-local `state` simple-source family to `projects/PIHC3/paradev.yaml`.
- Added the `pihc3:state/basic` authoring template for one-call SDK or compact GUI creation.
- Kept the compact create form minimal: `title` and `description` are the only primary fields.
- The template writes `meta.yaml`, `def.pdx`, and `main.loc` under `src/modules/state/{object_id}/`.
- The default state body is a history-state shell with `id`, `name`, `manpower`, `state_category`, `history`, `owner`, `add_core_of`, `buildings`, and an empty `provinces` block.
- Refreshed the starter shape against current local HOI4 state files under `/Users/magolor/Library/Application Support/Steam/steamapps/common/Hearts of Iron IV/history/states/`.
- Added SDK example coverage proving `Project.create_module("state", ...)` resolves the PIHC3 template, writes source files, and builds cleanly.
- Updated the PIHC3 user manual and added `projects/PIHC3/docs/migration/15-states.md`.

## Verification

- Red checks: the new state test first failed with `KeyError: 'state'` and the primary-field metadata test failed with `KeyError: 'pihc3:state/basic'`.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py::test_pihc3_state_template_scaffolds_basic_state_shell tests/test_sdk_examples.py::test_pihc3_template_args_mark_only_primary_create_fields -q`: 2 passed.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py -q`: 25 passed.
- SDK template projection: `state ['title', 'description']`, with `state_id` defaulting to advanced string `999`.
- Desktop-state template projection: `PIHC3 state ['title', 'description']`.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_sdk_examples.py`: passed.
- `rtk bash scripts/flake.bash --ci --paths tests/test_sdk_examples.py`: passed.
- PIHC3 build through the SDK: 529 modules, 0 collections, 0 dependencies, 26892 artifacts, 0 diagnostics, 0 errors, not blocked.
- `rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json`: 0 diagnostics.
- `rtk git diff --check`: passed.

## Risks Or Blockers

- This is a starter authoring template, not a PIHC2 state importer.
- Province lists, map ownership, strategic regions, resources, victory points, supply, terrain, and state/category parity review remain future slices.
- The starter template only creates a minimal history-state source file and localization; authors still need later templates, importers, or map tooling for a playable state.
- `projects/PIHC3/` is ignored by the current `.gitignore`, so the PIHC3 manifest and migration-note changes are local project-state changes rather than normal tracked diff entries.

## Next

- Continue expanding GUI-visible PIHC3 families that still lack starters, especially division/unit-history shells, or begin mapping PIHC2 state source shapes for import.
