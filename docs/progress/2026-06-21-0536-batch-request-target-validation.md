# Batch Request Target Validation Progress

Date: 2026-06-21 05:36 +0800

Linear: TAL-000

## Done

- Made `Project.module_batch_edit_request(...)` validate each target module before emitting a canonical batch edit request.
- Added a PIHC3-style regression so generated batch requests fail fast on unknown migration targets instead of producing JSON that only fails when applied.
- Updated the module batch-edit manual text in English and Chinese to state that request generation validates existing target modules.

## Verification

- Red check: `rtk bash scripts/test.bash tests/test_project.py -k module_batch_edit_request_rejects_unknown_pihc3_module_targets -q` failed because no `ValueError` was raised.
- Green focused check: `rtk bash scripts/test.bash tests/test_project.py -k module_batch_edit_request_rejects_unknown_pihc3_module_targets -q`.
- Batch SDK group: `rtk bash scripts/test.bash tests/test_project.py -k "module_batch_edit_request or module_files_batch_edit" -q`.
- Batch CLI group: `rtk bash scripts/test.bash tests/test_cli.py -k "module_batch_request or module_batch_edit" -q`.
- PIHC3 batch-related contracts: `rtk bash scripts/test.bash tests/test_pihc3_migration_contracts.py -k "batch" -q`.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py tests/test_project.py`.

## Risks Or Blockers

- Existing generated API/manual files in the broader worktree remain dirty from earlier active-goal slices; this checkpoint only touched the SDK batch request validation path and the module manual text.

## Next

- Continue tightening SDK/CLI batch generation ergonomics and PIHC3 GUI apply behavior.
