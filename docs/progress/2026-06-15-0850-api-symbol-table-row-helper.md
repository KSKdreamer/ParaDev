# API Symbol Table Row Helper Progress

Date: 2026-06-15 08:50 CST

Linear: none

## Done

- Added shared `api_symbol_table_row()` support for package-style API reference rows in `paradev._api_table_markdown`.
- Migrated the package, config, GUI, and project-facade API renderers from local row assembly to the shared helper.
- Verified all four generated references match the previous committed renderer output exactly.

## Verification

- `rtk uv run python - <<'PY' ... PY` old-vs-current renderer comparison for package, config, GUI, and project-facade API references
- `rtk uv run black src/paradev/_api_table_markdown.py src/paradev/config_api.py src/paradev/gui_api.py src/paradev/package_api.py src/paradev/project/api.py`
- `rtk uv run python -m py_compile src/paradev/_api_table_markdown.py src/paradev/config_api.py src/paradev/gui_api.py src/paradev/package_api.py src/paradev/project/api.py`
- `rtk uv run python - <<'PY' ... PY` helper probe for `api_symbol_table_row()`
- `rtk uv run pytest tests/test_architecture.py::test_package_api_table_lists_root_facade tests/test_architecture.py::test_config_api_table_lists_public_config_facade tests/test_architecture.py::test_gui_api_table_lists_public_gui_facade tests/test_architecture.py::test_project_facade_api_table_lists_project_package_facade tests/test_cli.py::test_package_api_cli_outputs_reference_markdown tests/test_cli.py::test_config_api_cli_outputs_reference_markdown tests/test_cli.py::test_gui_api_cli_outputs_reference_markdown tests/test_cli.py::test_project_facade_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table_markdown.py src/paradev/config_api.py src/paradev/gui_api.py src/paradev/package_api.py src/paradev/project/api.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/_api_table_markdown.py src/paradev/config_api.py src/paradev/gui_api.py src/paradev/package_api.py src/paradev/project/api.py`
- `rtk git diff --check -- src/paradev/_api_table_markdown.py src/paradev/config_api.py src/paradev/gui_api.py src/paradev/package_api.py src/paradev/project/api.py`

## Risks Or Blockers

- Full-suite tests were intentionally not run to avoid competing with concurrent PIHC3 migration work.
- The worktree still contains unrelated Heaven-style skill, desktop app, PIHC3, logo, loader, and `node_modules/` changes from other workers.

## Next

- Continue migrating package-style API renderers to the shared row helper in small groups with exact renderer comparisons.
- Keep avoiding build loader, HoI4 package internals, desktop app files, and PIHC3 progress files while those slices remain active elsewhere.
