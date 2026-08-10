# SDK CLI Feature Summary Reference Progress

Date: 2026-06-14 02:50 +0800

Linear: none

## Done

- Added a generated Feature Summary table to the SDK And CLI API reference renderer.
- The new table groups feature areas by operation count, Python SDK coverage, CLI coverage, read count, and write count using the existing frontend API summary contract.
- Regenerated `docs/user-manual/sdk-cli-reference.md`.
- Updated the Python SDK guide to mention that the generated SDK/CLI reference includes feature-level coverage.
- Added targeted architecture and CLI assertions for representative modules, LSP, and surfaces rows.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_sdk_cli_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_sdk_cli_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`

## Risks Or Blockers

- Full Python test suite was intentionally not run to avoid competing with concurrent PIHC3 migration work.
- The worktree still contains unrelated desktop, loader, PIHC3, and progress-note changes from other workers.

## Next

- Continue consolidating API reference pages around SDK-owned summary and index projections.
- Consider adding feature-summary links from desktop or REST docs once their generated surfaces are stable.
