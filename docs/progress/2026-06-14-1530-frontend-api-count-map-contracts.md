# Frontend API Count Map Contracts Progress

Date: 2026-06-14 15:30

Linear: N/A

## Done

- Continued tightening private contracts inside the SDK-owned frontend API reference renderer.
- Added `_FrontendApiGroupCountMap` and reused `_FrontendApiCountMap` across summary, REST, payload, surface, control, target, execution, confirmation, and form-footprint counters.
- Replaced repeated local `dict[str, int]` and grouped count-map annotations without changing count keys, count increments, table rows, row ordering, or generated reference output.

## Verification

- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_sdk_cli_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown tests/test_cli.py::test_frontend_api_cli_outputs_sdk_cli_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style-0.1.1.1/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py`

## Risks Or Blockers

- Full-suite tests are deferred to keep CPU available for parallel PIHC2-to-PIHC3 migration work.
- Staging remains limited to `src/paradev/sdk/frontend_api.py` and this progress note; desktop files, PIHC3 migration files, generated frontend assets, skill-directory churn, and `node_modules` are intentionally untouched.

## Next

- Continue consolidating private renderer contracts and repeated table helpers while preserving the public SDK, CLI, REST, MCP, and generated documentation surfaces.
