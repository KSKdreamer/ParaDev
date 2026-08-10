# 2026-06-08 05:40 CST - Frontend API Reference

Issues: TAL-299, TAL-295

## Scope

- Added an SDK-owned Markdown renderer for the canonical frontend API operation list: `render_frontend_api_reference_markdown()`.
- Added CLI projection `frontend-api --markdown` so agents can regenerate the full user-manual reference from the SDK contract.
- Added [docs/user-manual/frontend-api-reference.md](../user-manual/frontend-api-reference.md), a generated English/Chinese reference page with every project, module, collection, build, PDX, LSP, catalog, and surface operation.
- Linked the generated reference from the user manual index, frontend API guide, and developer manual.

## User-Facing Outcome

- GUI, importer, REST, MCP, VS Code, and desktop agents now have one visible full API table instead of relying on prose group summaries.
- The table is generated from `get_frontend_api_contract()`, so operation ids, modes, SDK/CLI/REST/MCP/LSP bindings, inputs, payload schemas, and summaries remain tied to the Python SDK contract.
- HoI4 mod developers and frontend developers can run:

```bash
rtk uv run paradev frontend-api --markdown
```

to regenerate the manual reference after a frontend-visible operation changes.

## Tests And Gates

- Red-first focused tests failed on the missing SDK renderer and missing CLI flag.
- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown -q` - `2 passed in 0.49s`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_lookup_helpers_return_canonical_rows tests/test_architecture.py::test_frontend_api_surface_bindings_are_machine_readable tests/test_architecture.py::test_frontend_api_form_contract_is_derived_from_operation_inputs tests/test_architecture.py::test_frontend_api_input_normalizer_maps_form_values_to_adapter_buckets tests/test_architecture.py::test_frontend_api_rest_request_planner_maps_values_to_query_and_body tests/test_cli.py::test_frontend_api_cli_outputs_sdk_contract_json tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown tests/test_cli.py::test_frontend_api_cli_outputs_selected_operation_and_group_json tests/test_cli.py::test_frontend_api_cli_outputs_operation_form_contract_json tests/test_cli.py::test_frontend_api_cli_normalizes_operation_values_json tests/test_cli.py::test_frontend_api_cli_plans_operation_rest_request_json -q` - `13 passed in 0.58s`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py src/paradev/sdk/__init__.py src/paradev/cli.py tests/test_architecture.py tests/test_cli.py` - `OK: 5 file(s) - no banned imports`
- `rtk bash scripts/flake.bash --ci` - passed
- `rtk bash scripts/test.bash` - `453 passed in 90.37s`

## Review

- The reference renderer is a read-only projection over `get_frontend_api_contract()`; it does not introduce another canonical operation registry.
- `frontend-api --markdown` is intentionally incompatible with selectors, form generation, value normalization, REST request planning, and JSON output, keeping it as a documentation projection only.
- The architecture test compares `docs/user-manual/frontend-api-reference.md` byte-for-byte with the SDK renderer output and checks that each operation id appears exactly once.
- Scope stayed on frontend-facing API maintainability; no GUI implementation or PIHC3 migration behavior was changed.

## Linear Sync

- TAL-299 comment: `c5599fad-5048-4a8f-a0b6-f6afd9c0a128`
- TAL-295 comment: `f1e991de-52f6-457b-afb9-4ae233967379`
