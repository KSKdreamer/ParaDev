# 2026-06-14 10:05 - Frontend API Sorted List Cells

## Scope

- Added `_frontend_api_sorted_code_list_cell(...)` for shared sorted markdown code-list rendering.
- Routed REST, binding, control, option-source, input-target, validation, default, required, alias, and option-provider summaries through the helper.
- Preserved generated API table text, sorted ordering, and existing count-list helper behavior.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
  - 2 passed in 1.03s.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
  - OK: 1 file(s) - no banned imports.
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py`
  - All done; 1 file would be left unchanged.
- `rtk git diff --check -- src/paradev/sdk/frontend_api.py docs/progress/2026-06-14-1005-frontend-api-sorted-list-cells.md`
  - Passed with no whitespace errors.

## Risks Or Blockers

- Full-suite test intentionally skipped to reduce CPU during parallel PIHC3 migration work.
- Shared worktree still contains unrelated desktop, SDK, and PIHC3 files; stage exact paths only.

## Next

- Continue consolidating frontend API renderer helpers around repeated generated table patterns.
