# 2026-06-20 15:20 - Module batch request edits validation

## Summary

Improved `paradev module-batch-edit` request validation for generated PIHC3 migration scripts. The CLI now checks that the request object has an `edits` array before handing the payload to `Project.write_module_files(...)`, so malformed generated requests fail with a field-specific message.

## Changed

- Added a CLI regression test for a module batch request missing the `edits` array.
- Added a small JSON request array helper in the CLI.
- Wired `module-batch-edit` through the helper before opening the SDK batch adapter.

## Verification

- `rtk uv run pytest tests/test_cli.py -q -k 'rejects_request_without_edits_array'`
- `rtk uv run pytest tests/test_cli.py -q -k 'module_batch_edit_cli'`
- `rtk uv run pytest tests/test_project.py tests/test_cli.py -q -k 'module_files_batch_edit or module_batch_edit_cli'`
- `rtk uv run black --check src/paradev/sdk/project.py src/paradev/cli.py tests/test_project.py tests/test_cli.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py src/paradev/cli.py tests/test_project.py tests/test_cli.py`
- `rtk git diff --check -- src/paradev/sdk/project.py src/paradev/cli.py tests/test_project.py tests/test_cli.py docs/user-manual/modules-and-collections.md docs/progress/2026-06-20-1518-module-batch-skip-unchanged-writes.md docs/progress/2026-06-20-1520-module-batch-request-edits-validation.md`
