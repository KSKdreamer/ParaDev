# 2026-06-14 08:14 - Frontend API owner row helper refactor

## Scope

- Extracted private frontend API renderer helpers for canonical operation rows, group-owned operation rows, and workspace-section-owned operation rows.
- Applied the helpers to the recent group/workspace mode-status and payload coverage summary renderers.
- Kept generated frontend API markdown behavior unchanged; no reference regeneration was needed beyond the existing checked-in generated file state.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown` passed with 2 tests.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py` passed.
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py` passed.
- The scoped `rtk rg -n` probe confirmed the new owner-row helpers and the summary renderers that now use them.
- `rtk git diff --check -- src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py docs/user-manual/frontend-api.md docs/user-manual/frontend-api-reference.md` passed.

## Notes

- This was a behavior-preserving refactor; the existing generated-reference and CLI markdown tests are the regression evidence.
- Full-suite tests were intentionally not run to keep CPU free for concurrent PIHC2 to PIHC3 migration work.
- These files already include earlier uncommitted frontend API reference slices; this entry documents only the owner-row helper extraction.
