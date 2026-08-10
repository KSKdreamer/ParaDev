# Frontend API Field Constraints Progress

Date: 2026-06-08 09:07 CST

Linear: TAL-295, TAL-299

## Done

- Extended canonical frontend API input rows with finite `choices` for project browser kind, authoring kind, source-slot/source statuses, collection source owner kind, build target roots, and diagnostic severity.
- Added numeric `minimum=0` constraints for LSP hover `line` and `character`.
- Updated `get_frontend_api_form(...)` so choices render as `select` controls and JSON Schema `enum`, while numeric lower bounds render as JSON Schema `minimum`.
- Updated `normalize_frontend_api_inputs(...)` and CLI `frontend-api --values-json` to reject invalid choices and lower-bound violations before an adapter calls SDK or REST.
- Updated English/Chinese user-manual examples and architecture notes so GUI, importer, REST, MCP, and VS Code clients treat choices/bounds as SDK-owned form metadata.

## Verification

- Red-first focused tests failed on missing `choices`, missing `minimum`, and missing normalizer validation.
- `rtk uv run pytest tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_frontend_api_form_contract_is_derived_from_operation_inputs tests/test_architecture.py::test_frontend_api_input_normalizer_maps_form_values_to_adapter_buckets tests/test_architecture.py::test_frontend_api_rest_request_planner_maps_values_to_query_and_body tests/test_cli.py::test_frontend_api_cli_normalizes_operation_values_json tests/test_cli.py::test_frontend_api_cli_outputs_operation_form_contract_json tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer`
- `rtk uv run paradev frontend-api --operation project.browser --form --json`
- `rtk uv run paradev frontend-api --operation project.browser --values-json '{"kind":"asset"}' --json`
- `rtk uv run paradev frontend-api --markdown > docs/user-manual/frontend-api-reference.md`
- `rtk git diff --check`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk uv build`

## Risks Or Blockers

- Choices are intentionally limited to SDK-owned finite domains. Extensible compiler fields such as dependency edge kind remain free-form until the registry can advertise safe per-project values.

## Next

- Continue improving frontend-facing API ergonomics by adding field labels/descriptions or project-derived enum providers where static choices are not enough.
