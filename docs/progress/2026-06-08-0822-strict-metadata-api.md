# Strict Metadata API Progress

Date: 2026-06-08 08:22 CST

Linear: TAL-295, TAL-299

## Done

- Added SDK-owned `strict_metadata` propagation from metadata loaders through project discovery, `Project.build(...)`, `Project.diagnostics(...)`, CLI `build --strict-metadata`, REST `POST /projects/build`, and frontend API rows `build.plan`, `build.emit`, and `build.diagnostics`.
- Regenerated the frontend API reference and updated English/Chinese user and developer manuals to document loose default warnings versus strict blocking diagnostics.
- Added regression coverage for loader severity promotion, project/CLI blocked builds, OpenAPI defaults, frontend input contracts, and REST request planning.

## Verification

- `rtk uv run pytest tests/test_build_loaders.py::test_metadata_loader_promotes_unknown_keys_when_strict tests/test_project.py::test_project_build_strict_metadata_blocks_unknown_module_keys tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_plans_operation_rest_request_json -q`
- `rtk uv run paradev frontend-api --operation build.plan --values-json '{"path":"/workspace/mod","strict_metadata":true}' --rest-request --json`
- `rtk uv run paradev build demos/assets/projects/minimal --strict-metadata --json`
- `rtk git diff --check`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/loaders.py src/paradev/build/discovery.py src/paradev/sdk/project.py src/paradev/cli.py src/paradev/surfaces/rest.py src/paradev/sdk/frontend_api.py tests/test_build_loaders.py tests/test_project.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk uv build`

## Risks Or Blockers

- Strict metadata currently covers unknown module and collection metadata keys. Future compiler-specific schema validation still needs family-owned rules beyond key allowlists.

## Next

- Continue the generic module compilation system by stabilizing compiler-family metadata contracts, source-slot authoring flows, and frontend-ready build graph views without adding surface-local rules.
