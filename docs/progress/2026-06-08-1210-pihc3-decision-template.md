# PIHC3 Decision Template Progress

Date: 2026-06-08 12:10 CST

Linear: TAL-298, TAL-297

## Done

- Added the project-local `pihc3:decision/basic` authoring template to `projects/PIHC3/paradev.yaml`.
- Kept the end-user create form compact: `title` and `description` are the only primary fields; `category_id`, `icon`, `cost`, and `language` are defaulted advanced fields.
- The template writes `meta.yaml`, `def.pdx`, and `main.loc` under `src/modules/decision/{object_id}/`.
- The default decision category is `PIHC3_DECISIONS`, matching the current HoI4 decision compiler requirement that module metadata `collection` matches the PDX category id.
- Added SDK example coverage proving `Project.create_module("decision", ...)` resolves the PIHC3 template, writes source files, and builds to `common/decisions/PIHC3_DECISIONS.txt`.
- Updated the PIHC3 user manual and added `projects/PIHC3/docs/migration/09-decisions.md`.

## Verification

- Red check: `test_pihc3_decision_template_scaffolds_basic_decision` first failed with `KeyError: 'pihc3:decision/basic'`.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py::test_pihc3_decision_template_scaffolds_basic_decision tests/test_sdk_examples.py::test_pihc3_template_args_mark_only_primary_create_fields -q`: 2 passed.
- SDK template projection: `decision ['title', 'description'] PIHC3_DECISIONS`.
- Desktop-state template projection: `PIHC3 decision ['title', 'description']`.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py -q`: 18 passed.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_sdk_examples.py`: passed.
- `rtk bash scripts/flake.bash --ci --paths tests/test_sdk_examples.py`: passed.
- PIHC3 build through the SDK: 529 modules, 0 collections, 0 dependencies, 26892 artifacts, 0 diagnostics, 0 errors, not blocked.
- `rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json`: 0 diagnostics.

## Risks Or Blockers

- This is a starter authoring template, not a PIHC2 decision importer.
- PIHC2 decision category descriptors and category localization remain copy-only until a later migration slice.
- More advanced decision workflows still need dedicated templates or parsed helpers for category variants, scripted trigger/effect wiring, icon assets, and category localization.

## Next

- Continue expanding PIHC3 starter templates where GUI module creation still lacks a project-local template, or start the decision category importer once the legacy decision source shape is mapped.
