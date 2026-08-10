# Template Index Contract

Date: 2026-06-07 22:51

Issues: TAL-294, TAL-295

## Summary

- Added `index` to `Project.templates()` / `paradev templates --json` payloads.
- The index maps `id`, `family`, `source`, `authoring_ready`, and `diagnostic_code` values to template row numbers.
- Kept the existing template rows as the display source of truth; the index is derived from those rows in the same SDK response.
- Updated English and Chinese user/developer manuals plus architecture/build-flow docs so GUI, REST, MCP, importer, and CLI clients do not duplicate row scans.

## Tests

- Red: `rtk bash scripts/test.bash tests/test_project.py::test_project_templates_list_builtin_authoring_templates tests/test_project.py::test_project_templates_mark_unknown_family_not_authoring_ready tests/test_cli.py::test_templates_cli_lists_available_authoring_templates -q`
  - Failed before implementation because `Project.templates()` did not include `index`.
- Focused green: `rtk bash scripts/test.bash tests/test_project.py::test_project_templates_list_builtin_authoring_templates tests/test_project.py::test_project_templates_mark_unknown_family_not_authoring_ready tests/test_project.py::test_project_templates_mark_project_local_family_authoring_ready tests/test_cli.py::test_templates_cli_lists_available_authoring_templates -q`
  - `4 passed`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py tests/test_project.py tests/test_cli.py`
  - `OK: 3 file(s) - no banned imports`
- `rtk rg -n 'authoring_ready|template\\.unknown_family|template index|diagnostic_code|Project\\.templates|Project\\.scaffold_module' docs/user-manual docs/architecture/interfaces.md docs/workflows/build-flow.md src/paradev/sdk/project.py tests/test_project.py tests/test_cli.py`
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

- This is an additive `paradev.sdk.templates.v1` field. Existing consumers that read only `templates` remain compatible.
- `authoring_ready` index keys are strings, `true` and `false`, because JSON object keys are strings.
- No PIHC3 migration logic or GUI-specific implementation was added.

## Linear

- `TAL-295` updated with comment `5aad3a81-5f7d-47f0-9f9b-4a7ecde282ef`.
- `TAL-294` updated with comment `4f4d8221-8ce1-458e-a159-454ac9910d42`.
