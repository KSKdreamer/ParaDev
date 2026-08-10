# Frontend API Form Contract

Date: 2026-06-08 04:25 CST

Issues: TAL-299, TAL-295

Linear comments:

- TAL-299: `d42d6c4a-cd9d-4f71-8fa5-1ba73f90afb1`
- TAL-295: `f4c931ff-0de5-47ae-8367-e0471b940752`

## Summary

- Added SDK-owned `get_frontend_api_form(operation_id)` with schema `paradev.sdk.frontend-api.form.v1`.
- Derived ordered `fields`, `required`, `defaults`, `aliases`, controls, and `json_schema` from existing operation `inputs` so GUI and importer agents do not maintain a second form schema.
- Exposed the same form projection through CLI `frontend-api --operation ... --form --json` and REST/OpenAPI `GET /frontend-api?operation_id=...&form=true`.
- Recorded `frontend-api` CLI projections in `get_cli_contract()` and added the `form=false` input to `surface.frontend_api`.
- Updated the English and Chinese frontend API manual, SDK manual, developer manual, and architecture interface contract.

## Verification

- Red test: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_form_contract_is_derived_from_operation_inputs -q` failed on missing `get_frontend_api_form`.
- Red test: `rtk bash scripts/test.bash tests/test_cli.py::test_frontend_api_cli_outputs_operation_form_contract_json -q` failed on missing `--form`.
- Focused green: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_form_contract_is_derived_from_operation_inputs tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands -q` passed.
- CLI focused green: `rtk bash scripts/test.bash tests/test_cli.py::test_frontend_api_cli_outputs_operation_form_contract_json tests/test_cli.py::test_frontend_api_cli_outputs_selected_operation_and_group_json -q` passed.
- SDK probe: `rtk uv run python - <<'PY' ... get_frontend_api_form(...) ... PY` confirmed module, build artifact, and frontend API form payloads.
- Docs/source check: `rtk rg -n 'get_frontend_api_form|FRONTEND_API_FORM_SCHEMA|--form|form=true|form=false|json_schema|projections' src tests docs/user-manual docs/architecture/interfaces.md`
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py src/paradev/sdk/__init__.py src/paradev/cli.py src/paradev/surfaces/rest.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py`
- Formatting: `rtk bash scripts/flake.bash --ci`
- CLI probe: `rtk uv run paradev frontend-api --operation build.artifacts --form --json`
- Full tests: `rtk bash scripts/test.bash` (`445 passed`)
- Package build: `rtk uv build`

## Review

- The helper is derived from canonical operation rows; the frontend API still has one maintained source of truth.
- `form` is treated as an operation projection, not a third selector, so `FRONTEND_API_SELECTORS` remains `operation_id` and `group_id`.
- This changes API metadata and surface discovery only; it does not change project mutation, build execution, parser behavior, or catalog persistence.
