# 2026-06-20 15:18 - Module batch edits skip unchanged writes

## Summary

Improved the Python SDK batch module update contract for rerunnable PIHC3 migration scripts. `Project.write_module_files(...)` now validates unchanged targets and includes them in the response, but skips rewriting files whose bytes already match the requested text.

This keeps `changed_count`, `unchanged_count`, and per-file `changed` reporting meaningful while avoiding timestamp churn and write-permission failures on no-op batch reruns.

## Changed

- Added a PIHC3-style SDK regression test using an unchanged read-only module metadata file.
- Updated `Project.write_module_files(...)` so write-mode batches skip rows with `changed == False`.
- Made per-file `written` reflect whether the target file was actually rewritten.
- Documented the no-op write behavior in the English and Chinese module authoring manual.

## Verification

- `rtk uv run pytest tests/test_project.py -q -k 'does_not_rewrite_unchanged_pihc3_targets'`
- `rtk uv run pytest tests/test_project.py -q -k 'module_files_batch_edit'`
- `rtk uv run pytest tests/test_cli.py -q -k 'module_batch_edit_cli'`
- `rtk uv run pytest tests/test_project.py tests/test_cli.py -q -k 'module_files_batch_edit or module_batch_edit_cli'`
- `rtk uv run black --check src/paradev/sdk/project.py tests/test_project.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py tests/test_project.py`
- `rtk git diff --check -- src/paradev/sdk/project.py tests/test_project.py docs/user-manual/modules-and-collections.md docs/progress/2026-06-20-1518-module-batch-skip-unchanged-writes.md`
