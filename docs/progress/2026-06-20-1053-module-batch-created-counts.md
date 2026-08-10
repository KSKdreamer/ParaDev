# 2026-06-20 10:53 - Module Batch Created Counts

## Scope

Improved the Python SDK and CLI module batch-edit contract for PIHC3 migration scripts. Batch responses now report which resolved module files are new migration artifacts versus updates to existing files, so callers can show accurate progress without rescanning the project tree.

## Changes

- Added per-file `created` flags to SDK module file write payloads when the file did not exist before the write or dry-run preview.
- Added `created_count` and `updated_count` to `Project.write_module_files` batch responses.
- Kept the bookkeeping in the SDK payload path so `paradev module-batch-edit --json` inherits the same contract.
- Documented the new batch-edit response fields in the English and Chinese module authoring manual.
- Extended PIHC3-style SDK tests and CLI JSON tests for created versus updated targets.

## Verification

- Red test first: focused SDK/CLI batch-edit tests failed on missing `created_count`.
- `rtk bash scripts/test.bash tests/test_project.py::test_module_files_batch_edit_writes_pihc3_style_updates tests/test_project.py::test_module_files_batch_edit_can_preview_pihc3_style_updates tests/test_cli.py::test_module_batch_edit_cli_writes_json_request -q`
- `rtk bash scripts/test.bash tests/test_project.py::test_module_files_batch_edit_writes_pihc3_style_updates tests/test_project.py::test_module_files_batch_edit_can_preview_pihc3_style_updates tests/test_project.py::test_module_file_rejects_path_escape_and_missing_write_target tests/test_cli.py::test_module_batch_edit_cli_writes_json_request tests/test_cli.py::test_module_batch_edit_cli_reads_json_request_from_stdin tests/test_cli.py::test_module_batch_edit_cli_can_preview_json_request tests/test_cli.py::test_module_batch_edit_cli_uses_json_request_defaults -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py tests/test_project.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/project.py tests/test_project.py`
- `rtk bash scripts/flake.bash --flake --paths src/paradev/sdk/project.py tests/test_project.py tests/test_cli.py`
- `rtk git diff --check -- src/paradev/sdk/project.py tests/test_project.py tests/test_cli.py docs/user-manual/modules-and-collections.md`

## Notes

The main worktree still contains many unrelated dirty files from parallel GUI, generated-reference, and module-batch work. This slice only touched the SDK payload builder, focused SDK/CLI tests, the module authoring manual, and this progress note.

`rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/project.py tests/test_project.py tests/test_cli.py` was attempted, but Black reported pre-existing formatting drift in unrelated `tests/test_cli.py` API-reference assertions. That file was not auto-formatted in this slice to avoid mixing a broad test cleanup with the batch-edit payload change.
