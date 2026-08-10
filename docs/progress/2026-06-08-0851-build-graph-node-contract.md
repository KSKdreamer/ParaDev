# Build Graph Node Contract Progress

Date: 2026-06-08 08:51 CST

Linear: TAL-295, TAL-299

## Done

- Extended `paradev.build.graph.v1` nodes with stable frontend display fields: `group`, `display_label`, `display_detail`, and `display_path`.
- Added `summary["nodes_by_group"]` and `index["nodes_by_group"]` so GUI, importer, catalog, and REST clients can render graph lanes and side-panel filters without parsing node ids.
- Kept existing graph ids, `type`, `label`, source/artifact fields, edge ordering, and filters additive and backwards compatible.
- Updated the SDK-owned frontend API row plus English/Chinese user-manual and architecture docs; regenerated `docs/user-manual/frontend-api-reference.md` from `paradev frontend-api --markdown`.

## Verification

- Red-first focused graph/catalog tests failed on missing graph node display fields and group indexes.
- `rtk uv run pytest tests/test_project.py::test_project_build_graph_returns_source_artifact_and_dependency_edges_without_writing tests/test_project.py::test_project_cli_filters_build_graph_json tests/test_project.py::test_project_build_explain_scopes_diagnostic_artifacts_by_target_root tests/test_hb.py::test_hb_catalog_preview_indexes_build_graph_nodes_and_edges`
- `rtk uv run pytest tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_surface_bindings_are_machine_readable tests/test_architecture.py::test_frontend_api_binding_index_maps_surface_calls_to_operation_ids tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- `rtk uv run paradev build-graph demos/assets/projects/minimal --module focus/GER_sample --json`
- `rtk uv run paradev frontend-api --operation build.graph --json`
- `rtk git diff --check`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/graph.py src/paradev/sdk/frontend_api.py tests/test_project.py tests/test_hb.py`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk uv build`

## Risks Or Blockers

- Graph grouping is intentionally derived from current node metadata (`artifact:<target_root>`, `module:<family>`, `source:<family>`, `reference:<target_kind>`). Future richer dependency targets may need extra explicit node fields rather than overloading the group key.

## Next

- Continue frontend-facing API stabilization by adding richer field descriptions and examples to the canonical `get_frontend_api_contract()` rows, then keep PDX/LSP/editor payloads aligned with that same manual surface.
