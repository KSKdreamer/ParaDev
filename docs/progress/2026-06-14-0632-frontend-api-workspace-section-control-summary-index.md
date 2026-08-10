# Frontend API Workspace Section Control Summary Progress

Date: 2026-06-14 06:32

Linear: N/A

## Done

- Added a generated Workspace Section Control Summary Index to the frontend API reference renderer.
- Documented the control-summary table in the user manual and regenerated `docs/user-manual/frontend-api-reference.md`.
- Added SDK renderer and CLI assertions for dynamic option-backed controls, static-choice controls, textarea fields, and zero-dynamic sections.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- Generated-reference anchor and representative-row checks with `rtk rg`.
- `rtk git diff --check -- src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py docs/user-manual/frontend-api.md docs/user-manual/frontend-api-reference.md`

## Risks Or Blockers

- Full-suite tests intentionally not run to reduce CPU contention while PIHC3 migration work is active.

## Next

- Continue adding grouped frontend API reference summaries where they reduce manual scans across detailed field-level tables.
