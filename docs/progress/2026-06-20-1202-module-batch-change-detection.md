# 2026-06-20 12:02 - Module Batch Change Detection

## Scope

Improved the SDK and CLI JSON module batch-edit payload for rerunnable PIHC3 migration scripts. Batch responses now identify which resolved targets would actually change bytes versus no-op updates, without changing the existing `created_count` and `updated_count` target-class semantics.

## Changes

- Added per-file `changed` flags to `Project.write_module_files` batch payload rows.
- Added `changed_count` and `unchanged_count` to `paradev.module.batch_edit.v1` responses.
- Kept `created_count` and `updated_count` as new-file versus existing-file counts so existing callers do not need to reinterpret those fields.
- Documented the new JSON fields in the English and Chinese module authoring manual.
- Added SDK and CLI JSON regression tests using PIHC3-style rerun batches.

## Verification

- Red tests first: `rtk bash scripts/test.bash tests/test_project.py::test_module_files_batch_edit_reports_changed_and_unchanged_pihc3_updates tests/test_cli.py::test_module_batch_edit_cli_json_reports_changed_and_unchanged_files -q` failed on missing `changed_count`.
- Focused green: same command passed after implementation.
- Batch-edit compatibility sweep: `rtk bash scripts/test.bash tests/test_project.py::test_module_files_batch_edit_writes_pihc3_style_updates tests/test_project.py::test_module_files_batch_edit_can_preview_pihc3_style_updates tests/test_project.py::test_module_files_batch_edit_reports_changed_and_unchanged_pihc3_updates tests/test_cli.py::test_module_batch_edit_cli_writes_json_request tests/test_cli.py::test_module_batch_edit_cli_plain_summary_counts_created_and_updated_files tests/test_cli.py::test_module_batch_edit_cli_accepts_inline_json_request tests/test_cli.py::test_module_batch_edit_cli_rejects_multiple_json_request_sources tests/test_cli.py::test_module_batch_edit_cli_reads_json_request_from_stdin tests/test_cli.py::test_module_batch_edit_cli_can_preview_json_request tests/test_cli.py::test_module_batch_edit_cli_json_reports_changed_and_unchanged_files tests/test_cli.py::test_module_batch_edit_cli_uses_json_request_defaults -q` passed.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py tests/test_project.py tests/test_cli.py` passed.
- Targeted functional flake: `rtk bash scripts/flake.bash --flake --paths src/paradev/sdk/project.py tests/test_project.py tests/test_cli.py` passed.
- Tracked whitespace check: `rtk git diff --check -- src/paradev/sdk/project.py tests/test_project.py tests/test_cli.py docs/user-manual/modules-and-collections.md docs/progress/2026-06-20-1202-module-batch-change-detection.md` passed.
- Direct whitespace scan: `rtk perl -ne 'print "$ARGV:$.:$_" if /[ \t]$/ || /\r$/; close ARGV if eof' src/paradev/sdk/project.py tests/test_project.py tests/test_cli.py docs/user-manual/modules-and-collections.md docs/progress/2026-06-20-1202-module-batch-change-detection.md` produced no output.
