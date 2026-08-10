# Build Assets And Sprites API Progress

Date: 2026-06-08 08:03 CST

Linear: TAL-295, TAL-299

## Done

- Added canonical frontend API rows for `build.assets` and `build.sprites`, both backed by `Project.inspect(...)`, CLI `assets`/`sprites`, REST `GET /projects/inspect`, and MCP `project_inspect`.
- Extended architecture contract tests so OpenAPI, binding indexes, CLI adapter metadata, and generated frontend API docs keep asset and sprite rows maintained.
- Regenerated `docs/user-manual/frontend-api-reference.md` and updated English/Chinese user and developer manual sections for asset/sprite build inspections.

## Verification

- `rtk uv run pytest tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_openapi_seed_links_rest_operations_to_frontend_api_rows tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_binding_index_maps_surface_calls_to_operation_ids tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands -q`
- `rtk uv run paradev frontend-api --operation build.assets --values-json '{"path":"/workspace/mod","file_format":"png"}' --rest-request --json`
- `rtk uv run paradev frontend-api --operation build.sprites --values-json '{"path":"/workspace/mod","name":"GFX_idea_GER_industry_spirit"}' --rest-request --json`
- `rtk git diff --check`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py src/paradev/surfaces/cli.py tests/test_architecture.py`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk uv build`

## Risks Or Blockers

- None for this slice. The first scanner attempt used `rtk python` and failed to import `heavenbase`; rerunning the same scanner under `rtk uv run python` passed.

## Next

- Continue hardening frontend-facing build/compiler rows, then move to the generic module compilation system without adding GUI-side business logic.
