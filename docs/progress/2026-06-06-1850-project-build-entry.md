# Project Build Entry Progress

Date: 2026-06-06 18:50 CST

Linear: TAL-293

## Done

- Added `Project.build(...)` as the SDK entry point over the generic dry-run planner.
- Added optional manifest emission under the project `build_root`; default builds remain read-only.
- Added `paradev build <path> --json` for a JSON-safe dry-run build result.
- Covered SDK, manifest emission, and CLI behavior with tests.

## Verification

- `rtk uv run pytest tests/test_project_build.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py src/paradev/cli.py tests/test_project_build.py`
- `rtk uv run paradev build demos/assets/projects/minimal --json`
- Temporary-project `Project.build(emit_manifests=True)` probe

## Risks Or Blockers

- Live Linear sync is still pending because no Linear MCP tool or `linear` CLI is available in this session.
- Existing local desktop and README edits remain outside this SDK/CLI build-entry slice.

## Next

- Start TAL-294 source slot matching so discovered module files can feed the build spine without hand-authored `Module` records.
