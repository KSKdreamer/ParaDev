# Scaffold Source Root Selection

Status: completed slice

Issues: TAL-298, TAL-295

## Summary

- Worked in isolated branch `codex/scaffold-source-root-selection` because the main checkout contained parallel-agent SDK, desktop, and PIHC-related dirty changes.
- Added `source_root` selection to `Project.scaffold_module(...)` for projects with multiple configured source roots.
- Added `--source-root` to `paradev scaffold` and kept CLI behavior as a thin SDK wrapper.
- Included the selected `source_root` in the JSON-safe scaffold plan so GUI, scripts, and future MCP tools can show where files will be written before `--write`.
- Added `source_roots` rows to `Project.templates()` / `paradev templates` so clients can discover valid scaffold targets before writing.
- Updated English and Chinese user-manual notes plus the build-flow contract.

## Verification

- Red check: focused SDK/CLI tests failed because `Project.scaffold_module(...)` rejected `source_root` and CLI rejected `--source-root`.
- Focused green:
  - `rtk uv run pytest tests/test_project.py::test_project_scaffold_module_can_select_source_root tests/test_project.py::test_project_scaffold_module_rejects_unknown_source_root tests/test_cli.py::test_scaffold_cli_can_select_source_root -q`
- Template source-root payload:
  - `rtk uv run pytest tests/test_project.py::test_project_templates_list_builtin_authoring_templates tests/test_cli.py::test_templates_cli_lists_available_authoring_templates -q`
- Broader scaffold/template suite:
  - `rtk uv run pytest tests/test_project.py::test_project_templates_list_builtin_authoring_templates tests/test_project.py::test_project_scaffold_module_writes_builtin_idea_template tests/test_project.py::test_project_scaffold_module_can_select_source_root tests/test_project.py::test_project_scaffold_module_rejects_unknown_source_root tests/test_project.py::test_project_scaffold_module_supports_project_local_template_args tests/test_project.py::test_project_scaffold_module_blocks_missing_required_args tests/test_project.py::test_project_manifest_rejects_unsafe_scaffold_template_file_path tests/test_cli.py::test_templates_cli_lists_available_authoring_templates tests/test_cli.py::test_scaffold_cli_plans_and_writes_authoring_template tests/test_cli.py::test_scaffold_cli_can_select_source_root tests/test_cli.py::test_scaffold_cli_rejects_invalid_template_value tests/test_sdk_examples.py::test_project_add_two_ideas_with_sdk_templates_example -q` (`12 passed`)
- CLI smoke: temp multi-root project, `paradev scaffold --source-root imports` dry-run writes nothing, `--write` writes under `imports/`.
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/cli.py src/paradev/sdk/project.py src/paradev/sdk/templates.py tests/test_cli.py tests/test_project.py`
- Diff whitespace: `rtk git diff --check` (clean)
- Lint: `rtk bash scripts/flake.bash --ci` (`48 files would be left unchanged`)
- Full tests: `rtk bash scripts/test.bash` (`341 passed in 69.42s`)
- Package build: `rtk uv build` (`dist/paradev-0.1.0.0.dev0.tar.gz`, `dist/paradev-0.1.0.0.dev0-py3-none-any.whl`)

## Linear

Linear auth was still expired during the final `TAL-295` fetch attempt (`UNAUTHORIZED; Session expired`). Local progress docs remain the durable sync artifact until auth is refreshed.
