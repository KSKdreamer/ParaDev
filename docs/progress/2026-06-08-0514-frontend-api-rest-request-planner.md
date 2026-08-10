# 2026-06-08 05:14 CST - Frontend API REST Request Planner

Issues: TAL-299, TAL-295

## Scope

- Added an SDK-owned REST request planner for frontend API operations so GUI, REST clients, and generated adapters can reuse one query/body split instead of duplicating route-specific mapping.
- Exposed the planner through `plan_frontend_api_rest_request(...)`, CLI `frontend-api --operation ... --values-json ... --rest-request`, and REST/OpenAPI `POST /frontend-api/rest-request?operation_id=...`.
- Added the canonical `surface.frontend_api.rest_request` operation row and kept it grouped with discovery, form derivation, and input normalization.
- Updated the frontend API contract, Python SDK manual, developer manual, and architecture interface boundary in English and Chinese.

## User-Facing Outcome

- A frontend can render a form with `get_frontend_api_form(...)`, normalize the submitted values with `normalize_frontend_api_inputs(...)`, then ask ParaDev to plan the exact REST call with `plan_frontend_api_rest_request(...)`.
- The CLI can now print the same request plan for scripts:

```bash
rtk uv run paradev frontend-api --operation module.edit \
  --values-json '{"path":"/workspace/mod","module_id":"modifier/test","relative_path":"def.pdx","text":"modifier = { value = 1 }"}' \
  --rest-request \
  --json
```

- The returned payload includes `schema`, `operation_id`, `method`, `path`, `query`, `body`, `binding`, and `normalized`, so desktop code does not need to infer where `text`, `path`, `kind`, or static route defaults belong.

## Tests And Gates

- Red-first focused tests initially failed while `/frontend-api/rest-request`, `surface.frontend_api.rest_request`, and `plan_frontend_api_rest_request(...)` were absent.
- `rtk bash scripts/test.bash tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_frontend_api_surface_bindings_are_machine_readable tests/test_architecture.py::test_frontend_api_rest_request_planner_maps_values_to_query_and_body tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_cli.py::test_frontend_api_cli_plans_operation_rest_request_json -q` - `6 passed in 0.38s`
- `rtk uv run paradev frontend-api --operation module.edit --values-json '{"path":"/workspace/mod","module_id":"modifier/test","relative_path":"def.pdx","text":"modifier = { value = 1 }"}' --rest-request --json` - returned `PATCH /projects/modules/file` with project/module query values and `body.text`.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py src/paradev/sdk/__init__.py src/paradev/cli.py src/paradev/surfaces/cli.py src/paradev/surfaces/rest.py tests/test_architecture.py tests/test_cli.py` - `OK: 7 file(s) - no banned imports`
- `rtk bash scripts/flake.bash --ci` - passed
- `rtk bash scripts/test.bash` - `450 passed in 77.41s`
- `rtk uv build` - built `dist/paradev-0.1.0.0.dev0.tar.gz` and `dist/paradev-0.1.0.0.dev0-py3-none-any.whl`

## Review

- Scope stayed on frontend-facing API generalization: one SDK planner, one CLI projection, one REST planning route, one contract row, and synchronized manuals.
- The planner rejects frontend-local operations and operations without REST bindings instead of guessing behavior.
- Static REST binding defaults remain authoritative unless a submitted value explicitly targets that query field, which keeps routes such as `build.emit` from losing their default query flags.
- Linear issue fetch through the Codex app returned an expired-session error; direct Linear comment sync succeeded.

## Linear Sync

- TAL-299 comment: `9e3a3d5d-d99c-4201-8c56-b122dbbb322f`
- TAL-295 comment: `ceb759d2-6b7e-4b1b-930f-d7296e784192`
