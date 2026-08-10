# 2026-06-14 21:55 - Frontend API binding key lookup

## Scope

- Continued the SDK-owned frontend API contract refactor loop on the current `origin/master` base.
- Kept the slice isolated from concurrent desktop, generated frontend contract, skill, logo, surface-summary, and PIHC3 migration edits.

## Changes

- Routed `get_frontend_api_binding_operation_ids(...)` through `_frontend_api_binding_surface_index(...)` directly.
- Preserved the public binding lookup behavior while avoiding a full copied binding-index map when callers need only one surface call key.

## Verification

- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --all --paths src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_sdk_cli_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_binding_lookup_helpers_return_operation_ids tests/test_cli.py::test_frontend_api_cli_outputs_sdk_contract_json tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown tests/test_cli.py::test_frontend_api_cli_outputs_sdk_cli_reference_markdown`
- Binding helper probe preserved REST hits, unknown-key misses, copied-list behavior, REST query disambiguation, and unsupported binding-surface errors.
- Renderer digests stayed stable:
  - reference markdown: `1ee5ee30997708f65830ba2d73f7a0b0a9bb094506407c2818fe6ac1ce94ab0c`
  - SDK CLI markdown: `a7da2e30892cf8530b8c18ac26ca5442b7f5d92fb0a3bd3793347b26b251c92e`
  - TypeScript contract: `78587211e9ea7beeed26da0d4b6c935cff0f30e1438cf40ce74efb6dfb261304`
