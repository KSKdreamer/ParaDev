# SDK Create Module Alias Progress

Date: 2026-06-08 11:08 CST

Linear: TAL-298, TAL-297

## Done

- Added `Project.create_module(...)` as the user-facing SDK verb for creating a new source module from a family shorthand or full template id.
- Made `Project.create_module(...)` write by default, so the SDK create verb matches the end-user expectation that a create call creates files.
- Kept `Project.scaffold_module(...)` as the lower-level dry-run/scaffold planning name.
- Added coverage that:
  - `project.scaffold_module("idea", ...)` remains a dry-run by default;
  - starter projects can call `project.create_module("idea", ...)` without `write=True` and get written files;
  - PIHC3 can call `project.create_module("idea", ...)` without `write=True` and resolve/write the project-local template.
- Updated user-facing docs to teach `create_module` first:
  - `docs/user-manual/sdk-python.md`
  - `docs/user-manual/modules-and-collections.md`
  - `docs/user-manual/pihc3.md`
  - `docs/workflows/build-flow.md`

## Verification

- Red check: targeted tests failed first because `Project` had no `create_module` attribute.
- Red check: after the alias existed, no-`write=True` create calls failed because files were not written by default.
- `rtk bash scripts/test.bash tests/test_project.py::test_project_scaffold_module_dry_runs_by_default tests/test_project.py::test_project_create_module_is_intuitive_sdk_alias tests/test_project.py::test_project_scaffold_module_writes_builtin_idea_template tests/test_project.py::test_project_scaffold_module_accepts_builtin_family_shorthand tests/test_sdk_examples.py::test_project_add_two_ideas_with_sdk_templates_example tests/test_sdk_examples.py::test_pihc3_create_module_uses_family_shorthand tests/test_sdk_examples.py::test_pihc3_idea_template_scaffolds_from_family_shorthand -q`: 7 passed.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py tests/test_project.py tests/test_sdk_examples.py`: passed.
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/project.py tests/test_project.py tests/test_sdk_examples.py`: passed.
- `rtk uv run paradev build projects/PIHC3 --emit-manifests --json`: 529 modules, 26892 artifacts, 0 diagnostics, not blocked.
- `rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json`: 0 diagnostics.

## Risks Or Blockers

- The CLI command remains `paradev scaffold`; this slice only changes the Python SDK mental model.
- `Project.create_module(...)` still returns the existing scaffold plan payload, so docs need to keep explaining blocked plans and diagnostics.

## Next

- Consider a future CLI alias only if users need a friendlier command than `scaffold`.
- Continue toward REST/OpenAPI apply for source-slot edits, removals, and assets.
