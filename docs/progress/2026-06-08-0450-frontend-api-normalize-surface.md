# 2026-06-08 04:50 CST - Frontend API Normalize Surface

## Scope

- Issues: TAL-299 frontend API contract, TAL-295 user manual maintenance.
- Branch: `codex/scaffold-source-root-selection`.
- Focus: make submitted frontend API form normalization callable through the public SDK-owned surface list, CLI, and REST/OpenAPI so GUI/importer agents do not reimplement field bucketing.

## Changes

- Added canonical `surface.frontend_api.normalize` operation metadata with `operation_id` and `values` inputs, SDK helper, CLI projection, REST route, and `paradev.sdk.frontend-api.inputs.v1` payload.
- Added CLI `frontend-api --operation ... --values-json ...` for normalizing one submitted frontend form JSON object through `normalize_frontend_api_inputs(...)`.
- Added REST/OpenAPI `POST /frontend-api/normalize?operation_id=...` over the same SDK helper.
- Updated CLI surface contract projections to publish both `form` and `values-json`.
- Updated frontend API, Python SDK, developer, and architecture manuals in English and Chinese with the same discovery -> form -> normalize mental model.

## Tests And Gates

- Focused contract tests: `rtk bash scripts/test.bash tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_cli.py::test_frontend_api_cli_normalizes_operation_values_json -q` -> `4 passed in 0.45s`.
- Docs/API search: `rtk rg -n "values-json|frontend-api/normalize|surface\.frontend_api\.normalize|normalize_frontend_api_inputs|Normalized frontend API input payload" src tests docs/user-manual docs/architecture/interfaces.md`.
- Diff hygiene: `rtk git diff --check`.
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/cli.py src/paradev/surfaces/rest.py src/paradev/surfaces/cli.py src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py` -> `OK: 6 file(s) - no banned imports`.
- Lint wrapper: `rtk bash scripts/flake.bash --ci` -> `54 files would be left unchanged`.
- CLI probe: `rtk uv run paradev frontend-api --operation build.artifacts --values-json '{"path":"/workspace/mod","artifact_path":"common/modifiers/test.txt"}' --json` -> project path and `artifact_path -> parameters.path` alias normalized as expected.
- Full tests: `rtk bash scripts/test.bash` -> `447 passed in 77.63s`.
- Build: `rtk uv build` -> source distribution and wheel built successfully.

## Review

- Reviewed the diff for surface drift and duplicate frontend schemas.
- No blocking findings found.
- The route is intentionally a thin adapter over `normalize_frontend_api_inputs(...)`; GUI, REST, and CLI callers still share the same SDK-owned validation and alias handling.

## Linear

- TAL-299 comment: `c333fdc3-b687-4ef9-9d23-5488b615ae7f`.
- TAL-295 comment: `bb5f5dc0-aa47-44d1-b066-5a4cc8470ab9`.
