# Project Browser API Progress

Date: 2026-06-08 07:00

Linear: TAL-295, TAL-299

## Done

- Added the read-only `Project.browser(...)` SDK payload `paradev.sdk.project-browser.v1` for frontend project trees over canonical module and collection build data.
- Exposed the same operation through CLI `project-browser`, REST/OpenAPI `GET /projects/browser`, MCP contract `project_browser`, and frontend API row `project.browser`.
- Added tests for SDK payload shape, CLI output, OpenAPI path metadata, frontend API bindings, reverse binding indexes, CLI contract, and MCP contract.
- Updated the bilingual user/developer manuals, quick-start command lists, architecture interface doc, and generated `docs/user-manual/frontend-api-reference.md`.

## Verification

- `rtk uv run pytest tests/test_project.py::test_project_browser_returns_frontend_ready_items_without_writing tests/test_project.py::test_project_cli_prints_project_browser_json tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_frontend_api_surface_bindings_are_machine_readable tests/test_architecture.py::test_frontend_api_binding_index_maps_surface_calls_to_operation_ids tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_mcp_surface_contract_lists_sdk_owned_tools`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py src/paradev/sdk/frontend_api.py src/paradev/cli.py src/paradev/surfaces/rest.py src/paradev/surfaces/cli.py src/paradev/surfaces/mcp.py tests/test_project.py tests/test_architecture.py`
- `rtk uv run paradev project-browser demos/assets/projects/minimal --kind module --module focus/GER_sample --json`
- `rtk uv run paradev frontend-api --operation project.browser --json`
- `rtk uv run paradev frontend-api --operation project.browser --values-json '{"path":"demos/assets/projects/minimal","kind":"module","module_id":"focus/GER_sample"}' --rest-request --json`
- `rtk git diff --check`
- `rtk bash scripts/test.bash` (`462 passed`)

## Risks Or Blockers

- `Project.browser(...)` is intentionally a build-model browser, not a general filesystem browser. GUI file panes should continue to use module and collection file APIs for text content.
- Synthetic collections created from module metadata may not have descriptor roots; the browser still indexes them and leaves path context absent until a descriptor source root exists.

## Next

- Continue module-management generalization: collection removal/rename and source-root-aware file panels should reuse the same frontend API contract pattern.
- Keep the manual and generated frontend API reference updated for every public SDK, CLI, REST, MCP, or LSP surface change.
