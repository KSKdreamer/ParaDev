# Batch Request File Validation Progress

Date: 2026-06-21 05:41 +0800

Linear: TAL-000

## Done

- Made `Project.module_batch_edit_request(...)` validate each resolved target file before emitting canonical batch edit request JSON.
- Preserved explicit creation opt-in: missing files are accepted only when the request or edit sets `create=true`.
- Added SDK and CLI regressions for PIHC3-style generated update requests that accidentally target missing files without creation enabled.
- Updated the module batch-edit manual text in English and Chinese to state that request generation validates missing-file creation intent.

## Verification

- Red checks: the new SDK and CLI regressions failed because request generation emitted JSON for missing files.
- Green focused SDK check: `rtk bash scripts/test.bash tests/test_project.py -k "module_batch_edit_request_rejects_missing_pihc3_file_targets_without_create" -q`.
- Green focused CLI check: `rtk bash scripts/test.bash tests/test_cli.py -k "module_batch_request_cli_rejects_missing_targets_without_create" -q`.
- Batch SDK group: `rtk bash scripts/test.bash tests/test_project.py -k "module_batch_edit_request or module_files_batch_edit" -q`.
- Batch CLI group: `rtk bash scripts/test.bash tests/test_cli.py -k "module_batch_request or module_batch_edit" -q`.
- PIHC3 batch-related contracts: `rtk bash scripts/test.bash tests/test_pihc3_migration_contracts.py -k "batch" -q`.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py tests/test_project.py tests/test_cli.py`.
- Whitespace check: `rtk git diff --check -- src/paradev/sdk/project.py tests/test_project.py tests/test_cli.py docs/user-manual/modules-and-collections.md docs/progress/README.md docs/progress/2026-06-21-0541-batch-request-file-validation.md`.

## Risks Or Blockers

- The broader worktree still includes earlier active-goal GUI, PIHC3, and reference changes. This checkpoint only tightens SDK/CLI batch request validation.

## Next

- Continue reducing PIHC3 migration scripts toward SDK/CLI request generation instead of hand-authored JSON payloads.
