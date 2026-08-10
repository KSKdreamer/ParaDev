# Project Inspection API Table Helper Progress

Date: 2026-06-15 08:32 CST

Linear: none

## Done

- Migrated the Project inspection reference renderer to the shared API-table Markdown helpers.
- Preserved the generated inspection contract, filter indexes, manual reference output, CLI Markdown output, and CLI validation behavior.

## Verification

- `rtk uv run black src/paradev/sdk/project.py`
- `rtk uv run python -m py_compile src/paradev/sdk/project.py`
- `rtk uv run pytest tests/test_architecture.py::test_project_inspection_reference_lists_contract_indexes tests/test_cli.py::test_inspections_cli_outputs_reference_markdown tests/test_cli.py::test_inspections_cli_rejects_markdown_json_combo`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/project.py`
- `rtk git diff --check -- src/paradev/sdk/project.py`

## Risks Or Blockers

- Full-suite tests were intentionally not run to avoid competing with concurrent PIHC3 migration work.
- The worktree still contains unrelated Heaven-style skill, desktop app, PIHC3, logo, loader, and `node_modules/` changes from other workers.

## Next

- Evaluate the remaining `src/paradev/sdk/frontend_api.py` local Markdown helpers carefully; its helpers handle more input shapes than the standard API-table helper.
- Keep avoiding build loader, HoI4 package internals, desktop app files, and PIHC3 progress files while those slices remain active elsewhere.
