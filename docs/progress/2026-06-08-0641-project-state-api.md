# Project State API Progress

Date: 2026-06-08 06:41 CST

Linear: TAL-299, TAL-295

## Done

- Added SDK-owned `registered_projects(...)` and `desktop_state(...)` payloads for project switchers and desktop shells.
- Exposed the payloads through CLI `projects` and `desktop-state`, REST/OpenAPI `GET /projects/list` and `GET /desktop/state`, and frontend API rows `project.list` and `project.state`.
- Extended frontend form contracts with array inputs for repeated project paths and search roots.
- Updated architecture docs, bilingual user/developer manuals, getting-started commands, and the generated frontend API reference.

## Verification

- `rtk bash scripts/test.bash tests/test_project.py::test_registered_projects_accepts_explicit_and_search_root_projects tests/test_project.py::test_registered_projects_reports_missing_explicit_and_search_roots tests/test_project.py::test_desktop_state_returns_active_project_view_and_registry tests/test_cli.py::test_projects_cli_lists_explicit_and_searched_projects tests/test_cli.py::test_desktop_state_cli_returns_active_project_view tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_openapi_seed_links_rest_operations_to_frontend_api_rows tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_frontend_api_surface_bindings_are_machine_readable tests/test_architecture.py::test_frontend_api_binding_index_maps_surface_calls_to_operation_ids tests/test_architecture.py::test_frontend_api_form_contract_is_derived_from_operation_inputs tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands -q`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py src/paradev/sdk/__init__.py src/paradev/cli.py src/paradev/sdk/frontend_api.py src/paradev/surfaces/rest.py src/paradev/surfaces/cli.py tests/test_project.py tests/test_cli.py tests/test_architecture.py`
- `rtk uv run paradev projects --root demos/assets/projects --json`
- `rtk uv run paradev desktop-state --project demos/assets/projects/minimal --root demos/assets/projects --json`
- `rtk bash scripts/test.bash`

## Risks Or Blockers

- The project registry intentionally stays filesystem-backed and read-only. Persistent workspace activation remains frontend-local until ParaDev defines a cross-surface workspace store.

## Next

- Continue stabilizing project browser and module-management affordances needed by GUI and PIHC3 migration agents, keeping filesystem browsing separate from compiler-owned module contracts.
