# Template Authoring Readiness

Date: 2026-06-07 22:43

Issues: TAL-294, TAL-295

## Summary

- Added `authoring_ready` to `Project.templates()` rows so CLI, SDK, GUI, MCP, REST, and importer callers can tell whether a starter template targets a registered build family before offering scaffold writes.
- Added `diagnostic_codes: ["template.unknown_family"]` for templates whose `family` is not registered by the HoI4 profile, project-local `families`, or project Python registry modules.
- Changed `Project.scaffold_module(...)` to reject unknown-family templates with a template-specific error before rendering files.
- Updated bilingual user and developer manual sections plus the architecture/build-flow contract docs for the new field.

## Tests

- Red: `rtk bash scripts/test.bash tests/test_project.py::test_project_templates_list_builtin_authoring_templates tests/test_project.py::test_project_templates_mark_unknown_family_not_authoring_ready tests/test_project.py::test_project_templates_mark_project_local_family_authoring_ready tests/test_project.py::test_project_scaffold_module_rejects_template_with_unknown_family tests/test_cli.py::test_templates_cli_lists_available_authoring_templates -q`
  - Failed before implementation because template rows lacked `authoring_ready` and scaffold reported the generic unknown-family preflight error.
- Focused green: `rtk bash scripts/test.bash tests/test_project.py::test_project_templates_list_builtin_authoring_templates tests/test_project.py::test_project_templates_mark_unknown_family_not_authoring_ready tests/test_project.py::test_project_templates_mark_project_local_family_authoring_ready tests/test_project.py::test_project_scaffold_module_rejects_template_with_unknown_family tests/test_project.py::test_project_scaffold_module_supports_project_local_template_args tests/test_cli.py::test_templates_cli_lists_available_authoring_templates tests/test_cli.py::test_scaffold_cli_plans_and_writes_authoring_template -q`
  - `7 passed`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py tests/test_project.py tests/test_cli.py`
  - `OK: 3 file(s) - no banned imports`
- `rtk rg -n "authoring_ready|template\\.unknown_family|Project\\.templates|Project\\.scaffold_module" docs/user-manual docs/architecture/interfaces.md docs/workflows/build-flow.md src/paradev/sdk/project.py tests/test_project.py tests/test_cli.py`
  - Confirmed SDK, tests, and manual/architecture coverage.
- `rtk git diff --check`
  - Passed.
- `rtk bash scripts/flake.bash --ci`
  - Passed.
- `rtk bash scripts/test.bash`
  - `394 passed`
- `rtk uv build`
  - Built `dist/paradev-0.1.0.0.dev0.tar.gz` and `dist/paradev-0.1.0.0.dev0-py3-none-any.whl`.

## Review

- Kept readiness in `Project.templates()` instead of `ModuleTemplate.to_view()` because readiness depends on the loaded project registry, including project-local families and Python registry modules.
- Reused the same build registry for scaffold preflight and post-write authoring-plan refresh to avoid divergent SDK behavior.
- Did not add PIHC3-specific import or migration logic.

## Linear

- `TAL-295` read attempt through the Codex app Linear connector returned `UNAUTHORIZED; Session expired. Please re-authenticate.` at the start of this slice.
- `TAL-295` was updated through the alternate Linear tool with comment `d95a9ffc-95e5-4159-a96f-e67eb0e5457f`.
- `TAL-294` was updated through the alternate Linear tool with comment `bb2f3b6a-2451-45fd-9cb8-df393d76ad0d`.
