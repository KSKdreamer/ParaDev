# 2026-06-20 11:02 - Module Batch Inline JSON

## Scope

Improved the CLI module batch-edit authoring path for PIHC3 migration scripts. `paradev module-batch-edit` now accepts an inline JSON request via `--request-json`, so short one-liner batches do not need a temporary request file and do not need to pipe stdin.

## Changes

- Added `--request-json` to `paradev module-batch-edit`.
- Kept `--request <file>` and `--request -` behavior intact.
- Added shared request-source validation so callers cannot pass both `--request` and `--request-json`.
- Documented the inline JSON option in the English and Chinese module authoring manual examples.
- Added focused CLI tests for inline JSON success and duplicate request-source rejection.

## Verification

- Red test first: `rtk bash scripts/test.bash tests/test_cli.py::test_module_batch_edit_cli_accepts_inline_json_request tests/test_cli.py::test_module_batch_edit_cli_rejects_multiple_json_request_sources -q` failed because `--request-json` did not exist.
- `rtk bash scripts/test.bash tests/test_cli.py::test_module_batch_edit_cli_accepts_inline_json_request tests/test_cli.py::test_module_batch_edit_cli_rejects_multiple_json_request_sources -q`
- `rtk bash scripts/test.bash tests/test_cli.py::test_module_batch_edit_cli_writes_json_request tests/test_cli.py::test_module_batch_edit_cli_plain_summary_counts_created_and_updated_files tests/test_cli.py::test_module_batch_edit_cli_accepts_inline_json_request tests/test_cli.py::test_module_batch_edit_cli_rejects_multiple_json_request_sources tests/test_cli.py::test_module_batch_edit_cli_reads_json_request_from_stdin tests/test_cli.py::test_module_batch_edit_cli_can_preview_json_request tests/test_cli.py::test_module_batch_edit_cli_uses_json_request_defaults tests/test_project.py::test_module_files_batch_edit_writes_pihc3_style_updates tests/test_project.py::test_module_files_batch_edit_can_preview_pihc3_style_updates -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/cli.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --flake --paths src/paradev/cli.py tests/test_cli.py`
- `rtk git diff --check -- src/paradev/cli.py tests/test_cli.py docs/user-manual/modules-and-collections.md`

## Notes

The broader Black check for `src/paradev/cli.py` and `tests/test_cli.py` is still not used as a completion gate for this slice because both files already contain unrelated formatting drift in nearby API-reference sections. This change keeps the functional diff scoped to module batch-edit request parsing and its tests.
