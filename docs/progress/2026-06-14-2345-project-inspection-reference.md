# 2026-06-14 23:45 - Project Inspection Reference

Linear: TAL-299

## Done

- Added typed project inspection contract rows, index rows, and copied lookup helpers:
  `get_project_inspection_kinds()`, `get_project_inspection_row(kind)`,
  `get_project_inspection_index_catalog()`, and
  `get_project_inspection_filter_kinds(filter_name)`.
- Added `render_project_inspection_reference_markdown()` and CLI
  `paradev inspections --markdown` for regenerating the project inspection
  kind/filter reference without loading a project.
- Generated `docs/user-manual/project-inspection-reference.md` and linked it
  from the user manual, SDK manual, architecture boundary, and developer manual.
- Updated the CLI surface contract so `inspections --markdown` is documented as
  a static projection.

## Verification

- `rtk uv run python -m py_compile src/paradev/sdk/project.py src/paradev/sdk/__init__.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py src/paradev/sdk/__init__.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/project.py src/paradev/sdk/__init__.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_project_inspection_reference_lists_contract_indexes tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_cli.py::test_inspections_cli_outputs_reference_markdown tests/test_cli.py::test_inspections_cli_rejects_markdown_json_combo -q`
- `rtk bash -lc 'uv run paradev inspections --markdown | diff -u docs/user-manual/project-inspection-reference.md -'`

## Notes

- Full-suite tests were deferred to keep CPU free while PIHC3 migration work is active in the shared tree.
- `node_modules/`, desktop generated output, PIHC3 migration files, and dirty `tests/test_project.py` remain outside this slice.
