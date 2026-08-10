# Frontend API Input Bucket Names Progress

Date: 2026-06-14 20:11 CST

Linear: N/A

## Done

- Centralized normalized frontend input bucket names behind one private SDK constant.
- Reused that bucket order when building normalized input payloads and REST request candidates.
- Preserved normalized payload keys, REST query/body placement, generated contract output, and CLI behavior.
- Checked the current GitHub PR queue with `gh pr status`; no PR review threads were available in this checkout.

## Verification

- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --all --paths src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_input_normalizer_maps_form_values_to_adapter_buckets tests/test_architecture.py::test_frontend_api_rest_request_planner_maps_values_to_query_and_body tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_sdk_cli_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_typescript_renderer_matches_desktop_contract_file tests/test_cli.py::test_frontend_api_cli_normalizes_operation_values_json`
- Direct probe confirmed normalized payload bucket key order and REST request query/body placement.
- Renderer digest check stayed unchanged for reference markdown, SDK/CLI markdown, and TypeScript output.

## Risks Or Blockers

- Full test suite intentionally skipped to reduce CPU pressure during concurrent PIHC3 migration work.
- Shared worktree still has unrelated untracked PIHC3 progress notes and `node_modules/`; this checkpoint stages only the SDK helper and this note.

## Next

- Continue extracting small SDK-owned frontend API helper boundaries while keeping generated contract artifacts stable.
