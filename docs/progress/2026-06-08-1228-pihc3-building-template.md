# PIHC3 Building Template Progress

Date: 2026-06-08 12:28 CST

Linear: TAL-298, TAL-297

## Done

- Added the project-local `building` simple-source family to `projects/PIHC3/paradev.yaml`.
- Added the `pihc3:building/basic` authoring template for one-call SDK or compact GUI creation.
- Kept the compact create form minimal: `title` and `description` are the only primary fields.
- The template writes `meta.yaml`, `def.pdx`, and `main.loc` under `src/modules/building/{object_id}/`.
- The default building body is a small `buildings = { ... }` block with `base_cost = 1000`, `value = 1`, and `infrastructure_construction_effect = yes`.
- Added SDK example coverage proving `Project.create_module("building", ...)` resolves the PIHC3 template, writes source files, and builds cleanly.
- Updated the PIHC3 user manual and added `projects/PIHC3/docs/migration/12-buildings.md`.

## Verification

- Red checks: the new building test first failed with `KeyError: 'building'` and the primary-field metadata test failed with `KeyError: 'pihc3:building/basic'`.
- The first green attempt caught YAML boolean coercion where unquoted `yes` rendered as `True`; the manifest now quotes that default.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py::test_pihc3_building_template_scaffolds_basic_building tests/test_sdk_examples.py::test_pihc3_template_args_mark_only_primary_create_fields -q`: 2 passed.
- SDK template projection: `building ['title', 'description']`, with `infrastructure_construction_effect` defaulting to string `yes`.
- Desktop-state template projection: `PIHC3 building ['title', 'description']`.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py -q`: 22 passed.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_sdk_examples.py`: passed.
- `rtk bash scripts/flake.bash --ci --paths tests/test_sdk_examples.py`: passed.
- PIHC3 build through the SDK: 529 modules, 0 collections, 0 dependencies, 26892 artifacts, 0 diagnostics, 0 errors, not blocked.
- `rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json`: 0 diagnostics.
- `rtk git diff --check`: passed.

## Risks Or Blockers

- This is a starter authoring template, not a PIHC2 building importer.
- State placement, building slots, map rendering, icons, and scripted effects remain future slices.
- The starter template only creates a minimal `buildings = { ... }` definition; authors still refine gameplay semantics in `def.pdx` after scaffolding.
- `projects/PIHC3/` is ignored by the current `.gitignore`, so the PIHC3 manifest and migration-note changes are local project-state changes rather than normal tracked diff entries.

## Next

- Continue expanding GUI-visible PIHC3 families that still lack starters, especially `state`, `equipment`, and `division`, or begin mapping PIHC2 building source shapes for import.
