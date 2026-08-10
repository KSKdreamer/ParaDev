# PIHC3 Idea Template Progress

Date: 2026-06-08 08:02 CST

Linear: TAL-297

## Done

- Added the project-local `pihc3:idea/legacy-current` SDK authoring template to `projects/PIHC3/paradev.yaml`.
- Kept the template scoped to PIHC3 so PIHC-specific defaults stay out of `src/paradev`.
- Added an SDK example test that copies the PIHC3 manifest and scaffolds a legacy-compatible idea module.
- Updated `docs/user-manual/pihc3.md` and `projects/PIHC3/docs/migration/03-ideas.md` with the new authoring workflow.
- Added a Linear progress comment on TAL-297.

## Verification

- `rtk bash scripts/test.bash tests/test_sdk_examples.py -q`
- `rtk bash scripts/flake.bash --ci --paths tests/test_sdk_examples.py`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_sdk_examples.py`
- `rtk uv run paradev templates projects/PIHC3 --json`
- `rtk uv run paradev scaffold projects/PIHC3 pihc3:idea/legacy-current IDEA_TEST_FRIENDSHIP --value legacy_tag=TEST_FRIENDSHIP --value 'title=Friendship Committee' --value 'description=A small project-local idea.' --json`
- `rtk uv run paradev summary projects/PIHC3 --json`

## Risks Or Blockers

- The `codex_apps` Linear connector still reports an expired session; the update used the working `mcp__linear` connector.
- A bare `rtk python` Heaven-style scan cannot import `heavenbase`; the successful scan used `rtk uv run python`.
- Existing large desktop, SDK browser, copy-root, and PIHC3 migration edits remain in the working tree from prior work and were not reverted.

## Next

- Extend the same project-local template approach to the next native PIHC3 family once its importer and compiler defaults are stable.
- Consider a GUI/REST draft flow that can call `Project.templates()` and dry-run `Project.scaffold_module(...)` before writing.
