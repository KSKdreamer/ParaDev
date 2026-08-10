# 2026-06-14 08:03 - Frontend API group mode/status index

## Scope

- Added a generated Group Mode Status Index to the frontend API reference, parallel to the existing workspace-section mode/status table.
- Extracted shared mode/status cell rendering so workspace-section and group tables count read/write and implementation status consistently.
- Updated frontend API architecture and CLI assertions for the generated heading plus representative projects/surfaces rows.
- Updated the hand-written frontend API manual note and regenerated `docs/user-manual/frontend-api-reference.md`.

## Verification

- RED: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown` failed because `### Group Mode Status Index / Group Mode Status 索引` was absent from SDK-rendered and CLI markdown.
- GREEN: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown` passed with 2 tests.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py` passed.
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py` passed.
- The scoped `rtk rg -n` probe confirmed the helper, generated Group Mode Status sections, and projects/surfaces rows.
- `rtk git diff --check -- src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py docs/user-manual/frontend-api.md docs/user-manual/frontend-api-reference.md` passed.

## Notes

- Full-suite tests were intentionally not run to keep CPU free for concurrent PIHC2 to PIHC3 migration work.
- These files already include earlier uncommitted frontend API reference slices; this entry documents only the group mode/status addition.
