# Project API Reference Sync Progress

Date: 2026-06-21 09:45 CST

Linear: TAL-000

## Done

- Re-ran the generated Project API reference through `paradev project-api --markdown` after the SDK batch-update work changed the public `Project` surface.
- Synced `docs/user-manual/project-api-reference.md` so it lists `Project.module_batch_edit_request`, `paradev module-batch-request`, and the filtered `discover_modules` / `discover_collections` parameters.
- Confirmed the PIHC3 batch-update contracts still pass after the docs sync.

## Verification

- `rtk uv run pytest tests/test_architecture.py -q`
- `rtk uv run pytest tests/test_project.py tests/test_cli.py tests/test_pihc3_migration_contracts.py -q -k 'module_batch or api_reference or architecture or generated'`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_project.py tests/test_cli.py tests/test_pihc3_migration_contracts.py tests/test_architecture.py`
- `rtk git diff --check -- src/paradev/sdk/project.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_project.py tests/test_cli.py tests/test_pihc3_migration_contracts.py tests/test_architecture.py docs/user-manual/project-api-reference.md`

## Risks Or Blockers

- The broader goal remains open; this slice only fixes generated Project API reference drift for the current SDK/CLI module-batch surface.

## Next

- Continue GUI usability and PIHC3 cleanup slices with rendered smoke checks and PIHC3 migration contracts.
