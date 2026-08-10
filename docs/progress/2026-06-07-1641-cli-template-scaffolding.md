# CLI Template Scaffolding

Status: completed slice

Issues: TAL-298, TAL-295

## Summary

- Stopped the PIHC3 bootstrap slice after user direction that another agent owns PIHC3 migration.
- Added general CLI access to SDK authoring templates:
  - `paradev templates <project> --json`
  - `paradev scaffold <project> <template_id> <object_id> --value KEY=VALUE --write --json`
- Kept `scaffold` dry-run by default so scripts, GUI clients, and future MCP tools can preview files and diagnostics before writing.
- Updated English and Chinese user-manual pages plus the build-flow workflow to document the shared SDK/CLI creation contract.

## Verification

- Red check: focused CLI tests first failed because `templates` and `scaffold` commands did not exist.
- Focused green:
  - `rtk uv run pytest tests/test_cli.py::test_templates_cli_lists_available_authoring_templates tests/test_cli.py::test_scaffold_cli_plans_and_writes_authoring_template tests/test_cli.py::test_scaffold_cli_rejects_invalid_template_value tests/test_project.py::test_project_templates_list_builtin_authoring_templates tests/test_project.py::test_project_scaffold_module_writes_builtin_idea_template tests/test_project.py::test_project_scaffold_module_supports_project_local_template_args tests/test_project.py::test_project_scaffold_module_blocks_missing_required_args tests/test_project.py::test_project_manifest_rejects_unsafe_scaffold_template_file_path tests/test_sdk_examples.py::test_project_add_two_ideas_with_sdk_templates_example -q`
- CLI smoke:
  - Create temp starter project.
  - Run `paradev templates`.
  - Run `paradev scaffold` without `--write` and verify no files are written.
  - Run `paradev scaffold --write` and verify module files are written.
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/cli.py tests/test_cli.py`
- Lint: `rtk bash scripts/flake.bash --ci`
- Full tests: `rtk bash scripts/test.bash` (`338 passed`)
- Package build: `rtk uv build`

## Linear

The Linear connector still returned `UNAUTHORIZED; Session expired. Please re-authenticate.` when reading TAL-297 earlier in the loop. Local docs remain the durable sync record until auth is refreshed.
