# Frontend API Group Binding Summary Progress

Date: 2026-06-14 06:49

Linear: N/A

## Done

- Added a generated Group Binding Summary Index to the frontend API reference renderer.
- Documented the group binding-summary table in the user manual and regenerated `docs/user-manual/frontend-api-reference.md`.
- Added SDK renderer and CLI assertions for feature-level SDK, CLI, REST, MCP, LSP, and unbound operation keys.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- Generated-reference anchor and representative-row checks with `rtk rg`.
- `rtk git diff --check -- src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py docs/user-manual/frontend-api.md docs/user-manual/frontend-api-reference.md`

## Risks Or Blockers

- Full-suite tests intentionally not run to reduce CPU contention while PIHC3 migration work is active.

## Next

- Continue adding grouped frontend API reference summaries where feature-level tables reduce manual joins across global binding, payload, REST, and form indexes.
