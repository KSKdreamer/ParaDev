# 2026-06-08 04:59 CST - Frontend API Structured Bindings

## Scope

- Issues: TAL-299 frontend API contract, TAL-295 user manual maintenance.
- Branch: `codex/scaffold-source-root-selection`.
- Focus: make the frontend API operation list safer for GUI, REST, importer, MCP, and codegen agents by adding machine-readable surface bindings to each operation row.

## Changes

- Added derived `bindings` to frontend API operation rows with SDK call, CLI command, REST method/path/static query defaults, MCP tool, and LSP method when those surfaces exist.
- Preserved the existing human-readable `sdk`, `cli`, `rest`, `mcp`, and `lsp` string fields for manual scanning.
- Added a maintenance invariant test so every row with a surface string has a matching structured binding, while frontend-local rows such as `project.activate` do not advertise callable SDK bindings.
- Updated English and Chinese frontend API, SDK, developer, and architecture manual sections to tell clients to use `bindings` rather than parsing display strings.

## Tests And Gates

- Red test: `test_frontend_api_surface_bindings_are_machine_readable` initially failed with missing `bindings`.
- Focused tests: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_frontend_api_lookup_helpers_return_canonical_rows tests/test_architecture.py::test_frontend_api_surface_bindings_are_machine_readable tests/test_architecture.py::test_frontend_api_form_contract_is_derived_from_operation_inputs tests/test_architecture.py::test_frontend_api_input_normalizer_maps_form_values_to_adapter_buckets tests/test_cli.py::test_frontend_api_cli_outputs_sdk_contract_json -q` -> `6 passed in 0.39s`.
- Docs/API search: `rtk rg -n "bindings|bindings\.rest|values-json|frontend-api/normalize" src/paradev/sdk/frontend_api.py tests/test_architecture.py docs/user-manual docs/architecture/interfaces.md`.
- CLI probe: `rtk uv run paradev frontend-api --operation module.list --json` -> row includes `bindings.rest.method=GET`, `bindings.rest.path=/projects/inspect`, and `bindings.rest.query.kind=modules`.
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py` -> `OK: 2 file(s) - no banned imports`.
- Lint wrapper: `rtk bash scripts/flake.bash --ci` -> `54 files would be left unchanged`.
- Diff hygiene: `rtk git diff --check`.
- Full tests: `rtk bash scripts/test.bash` -> `448 passed in 76.12s`.
- Build: `rtk uv build` -> source distribution and wheel built successfully.

## Review

- Reviewed the diff for contract drift and accidental frontend-local binding exposure.
- No blocking findings found.
- The new `bindings` object is derived from the same row fields already used by the frontend API contract, avoiding a second manually maintained surface map.

## Linear

- TAL-299 comment: `ac4f1192-2842-4e54-b893-3aac6fc038a8`.
- TAL-295 comment: `800adeb1-0049-4367-b397-3460b4d1d1fd`.
