# Frontend API Group Option Source Summary Index Progress

Date: 2026-06-14 07:15

Linear: none

## Done

- Added a generated Group Option Source Summary Index table for dynamic option-source dependencies by operation group.
- Reused the same option-source aggregation for workspace-section and group summary rows.
- Updated the frontend API manual and regenerated the reference markdown.

## Verification

- RED: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown` failed on the missing Group Option Source Summary heading.
- GREEN: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown` passed.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- Anchor check with `rtk rg -n` confirmed the Group Option Source Summary heading, helper names, and representative `projects`/`modules` rows in source, tests, manual, and generated reference.
- `rtk git diff --check -- src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py docs/user-manual/frontend-api.md docs/user-manual/frontend-api-reference.md`

## Risks Or Blockers

- Full-suite tests were intentionally skipped to preserve CPU for parallel PIHC3 migration work.
- The same files contain earlier uncommitted frontend API reference changes, so this note records only the group option-source summary slice.

## Next

- Continue adding feature-level generated API summaries where they reduce GUI, REST, MCP, CLI, or LSP contract drift.
