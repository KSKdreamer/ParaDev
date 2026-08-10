# PIHC3 Scripted Effect And Trigger Template Progress

Date: 2026-06-08 12:22 CST

Linear: TAL-298, TAL-297

## Done

- Added project-local `scripted_effect` and `scripted_trigger` simple-source families to `projects/PIHC3/paradev.yaml`.
- Added `pihc3:scripted_effect/basic` and `pihc3:scripted_trigger/basic` authoring templates.
- Kept the compact create form minimal: `title` is the only primary field for both templates.
- The scripted effect template writes `meta.yaml` and an empty `{object_id} = {}` body under `src/modules/scripted_effect/{object_id}/`.
- The scripted trigger template writes `meta.yaml` and a starter `{object_id} = { always = yes }` body under `src/modules/scripted_trigger/{object_id}/`.
- Added SDK example coverage proving `Project.create_module("scripted_effect", ...)` and `Project.create_module("scripted_trigger", ...)` resolve the PIHC3 templates, write source files, and build cleanly.
- Updated the PIHC3 user manual and added `projects/PIHC3/docs/migration/11-scripted-effect-trigger.md`.

## Verification

- Red checks: the new scripted effect and trigger tests first failed with `KeyError: 'scripted_effect'` and `KeyError: 'scripted_trigger'`.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py::test_pihc3_scripted_effect_template_scaffolds_basic_effect tests/test_sdk_examples.py::test_pihc3_scripted_trigger_template_scaffolds_basic_trigger tests/test_sdk_examples.py::test_pihc3_template_args_mark_only_primary_create_fields -q`: 3 passed.
- SDK template projection: `scripted_effect ['title']`, `scripted_trigger ['title']`.
- Desktop-state template projection: `PIHC3 scripted_effect ['title'] scripted_trigger ['title']`.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py -q`: 21 passed.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_sdk_examples.py`: passed.
- `rtk bash scripts/flake.bash --ci --paths tests/test_sdk_examples.py`: passed.
- PIHC3 build through the SDK: 529 modules, 0 collections, 0 dependencies, 26892 artifacts, 0 diagnostics, 0 errors, not blocked.
- `rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json`: 0 diagnostics.
- `rtk git diff --check`: passed.

## Risks Or Blockers

- This is a starter authoring template slice, not a PIHC2 scripted effect or scripted trigger importer.
- There is no parsed helper API, preset recipe library, decision/event wiring helper, or balancing validation in this slice.
- Authors still edit the generated `def.pdx` bodies directly after scaffolding.
- `projects/PIHC3/` is ignored by the current `.gitignore`, so the PIHC3 manifest and migration-note changes are local project-state changes rather than normal tracked diff entries.

## Next

- Continue expanding GUI-visible PIHC3 families that still lack starters, or begin mapping PIHC2 scripted effect/trigger source shapes for import once authored shells are enough.
