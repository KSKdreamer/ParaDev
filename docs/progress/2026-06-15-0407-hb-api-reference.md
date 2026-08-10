# 2026-06-15 04:07 - HeavenBase Facade API Reference

## Summary

- Added `paradev.hb.get_hb_api_table()` and `paradev.hb.render_hb_api_reference_markdown()` as the generated facade table for public HeavenBase imports.
- Added CLI `paradev hb-api` plus `paradev hb-api --markdown` and registered the table in the aggregate API catalog.
- Regenerated `hb-api-reference.md`, `api-catalog-reference.md`, `cli-api-reference.md`, and `surfaces-api-reference.md`.

## Verification

Targeted verification only, to avoid full-suite CPU load:

```bash
rtk uv run python -m py_compile src/paradev/hb/api.py src/paradev/hb/__init__.py src/paradev/cli.py src/paradev/surfaces/api_catalog.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py
rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/hb/api.py src/paradev/hb/__init__.py src/paradev/cli.py src/paradev/surfaces/api_catalog.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py
rtk bash scripts/flake.bash --ci --paths src/paradev/hb/api.py src/paradev/hb/__init__.py src/paradev/cli.py src/paradev/surfaces/api_catalog.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py
rtk uv run pytest tests/test_architecture.py::test_hb_api_table_lists_public_hb_facade tests/test_architecture.py::test_surfaces_api_table_lists_surface_facade tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_cli_api_table_lists_command_contract tests/test_cli.py::test_api_catalog_cli_outputs_table_json tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown tests/test_cli.py::test_hb_api_cli_outputs_table_json tests/test_cli.py::test_hb_api_cli_outputs_reference_markdown tests/test_cli.py::test_hb_api_cli_rejects_markdown_json_combo tests/test_cli.py::test_cli_api_cli_outputs_table_json tests/test_cli.py::test_cli_api_cli_outputs_reference_markdown
```

Result: all passed after Black reformatted one assertion in `tests/test_cli.py`.
