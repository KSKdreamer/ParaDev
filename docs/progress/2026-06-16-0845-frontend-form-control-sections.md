# Frontend Form Control Sections Progress

Date: 2026-06-16 08:45 CST

Linear: N/A

## Done

- Extracted the frontend API reference workspace-section form summary table into `_frontend_api_workspace_section_form_summary_section(...)`.
- Extracted workspace-section and group control summary tables into `_frontend_api_workspace_section_control_summary_section(...)` and `_frontend_api_group_control_summary_section(...)`.
- Reused the helpers from the English and Chinese generated-reference sections without changing rendered output.

## Verification

- `rtk uv run black src/paradev/sdk/frontend_api.py`
- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer -q`
- `rtk bash scripts/test.bash tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown -q`
- Generated API reference parity check: 29 references matched checked-in docs.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py`

## Risks Or Blockers

- Full-suite tests were intentionally skipped to keep CPU free while PIHC migration work continues.
- Existing unrelated dirty files were left untouched.

## Next

- Continue extracting repeated frontend API reference sections into named helpers with generated-doc parity checks.
