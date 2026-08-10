# SDK Build Examples Progress

Date: 2026-06-06 19:54 CST

Linear: TAL-294

## Done

- Added public SDK coverage for `Project.load(...).build(...)` against the minimal HOI4 demo project.
- Covered dry manifest emission through `emit_manifests=True`, including source-map artifact types.
- Covered artifact emission through `emit_artifacts=True`, including generated PDX and localization outputs.
- Used a temporary demo copy for write-producing SDK examples so checked-in demo assets stay stable.

## Verification

- `rtk uv run pytest tests/test_sdk_examples.py -q`
- `rtk uv run pytest tests/test_sdk_examples.py tests/test_project.py tests/test_project_build.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_sdk_examples.py`

## Risks Or Blockers

- Live Linear sync is still pending because no Linear MCP tool or `linear` CLI is available in this session.
- Existing local desktop and README edits remain outside this SDK coverage slice.

## Next

- Add the next generic module compilation slice around artifact ownership and dependency ordering.
