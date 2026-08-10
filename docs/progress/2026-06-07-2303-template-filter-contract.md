# Template Filter Contract

Date: 2026-06-07 23:03

Issues: TAL-294, TAL-295

## Summary

- Added exact filters to `Project.templates(...)`: `template_id`, `family`, `source`, `authoring_ready`, and `diagnostic_code`.
- Wired the same filters through `paradev templates` and the REST/OpenAPI `/projects/templates` contract.
- Rebuilt `templates.index` from the filtered rows so returned row numbers are always local to the response.
- Updated English and Chinese manuals plus architecture/build-flow docs for SDK, CLI, REST, GUI, MCP, and importer consumers.

## Tests

- Red: `rtk bash scripts/test.bash tests/test_project.py::test_project_templates_filters_rebuild_rows_and_index tests/test_project.py::test_project_templates_filter_by_template_id tests/test_cli.py::test_templates_cli_filters_authoring_templates tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server -q`
  - Failed before implementation because `Project.templates(...)`, `paradev templates`, and OpenAPI did not expose template filters.
- Focused green: `rtk bash scripts/test.bash tests/test_project.py::test_project_templates_filters_rebuild_rows_and_index tests/test_project.py::test_project_templates_filter_by_template_id tests/test_project.py::test_project_templates_list_builtin_authoring_templates tests/test_cli.py::test_templates_cli_filters_authoring_templates tests/test_cli.py::test_templates_cli_lists_available_authoring_templates tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server -q`
  - `6 passed`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py src/paradev/cli.py src/paradev/surfaces/rest.py tests/test_project.py tests/test_cli.py tests/test_architecture.py`
  - `OK: 6 file(s) - no banned imports`
- `rtk rg -n 'template_id|authoring_ready|diagnostic_code|not-authoring-ready|Project\\.templates|paradev templates|/projects/templates' docs/user-manual docs/architecture/interfaces.md docs/workflows/build-flow.md src/paradev/sdk/project.py src/paradev/cli.py src/paradev/surfaces/rest.py tests/test_project.py tests/test_cli.py tests/test_architecture.py`
  - Confirmed SDK, CLI, REST, tests, and manual/architecture coverage.
- `rtk git diff --check`
  - Passed.
- `rtk bash scripts/flake.bash --ci`
  - Passed.
- `rtk bash scripts/test.bash`
  - `397 passed`
- `rtk uv build`
  - Built `dist/paradev-0.1.0.0.dev0.tar.gz` and `dist/paradev-0.1.0.0.dev0-py3-none-any.whl`.

## Review

- The change is additive to `paradev.sdk.templates.v1`; callers that do not pass filters keep the same unfiltered rows.
- Filters are exact-match only and mirror the existing template index dimensions. This avoids adding a second query language.
- No PIHC3 migration or GUI implementation code was added.

## Linear

- `TAL-295` updated with comment `7262c9cb-a71f-4178-b1be-d9da59df2ccf`.
- `TAL-294` updated with comment `834d31ad-558b-4caa-afaa-a442a1771dcc`.
