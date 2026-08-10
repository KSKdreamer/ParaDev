# 2026-06-14 09:54 - Frontend API Input Name Helpers

## Scope

- Added shared frontend API helpers for input names, mapped names, target buckets, and alias cells.
- Routed REST query/route summaries, binding input rows, input target/alias tables, and input normalizer mapped names through the helpers.
- Preserved generated API table text and normalized frontend API payload behavior.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_input_normalizer_maps_form_values_to_adapter_buckets tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
  - 3 passed in 1.02s.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
  - OK: 1 file(s) - no banned imports.
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py`
  - All done; 1 file would be left unchanged.
- `rtk git diff --check -- src/paradev/sdk/frontend_api.py docs/progress/2026-06-14-0954-frontend-api-input-name-helpers.md`
  - Passed with no whitespace errors.

## Risks Or Blockers

- Full-suite test intentionally skipped to reduce CPU during parallel PIHC3 migration work.
- Shared worktree still contains unrelated desktop, SDK, and PIHC3 files; stage exact paths only.

## Next

- Continue tightening frontend API renderer helper boundaries around repeated table construction.
