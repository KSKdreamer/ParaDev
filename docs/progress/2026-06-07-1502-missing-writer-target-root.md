# Missing Writer Target Root Diagnostics Progress

Date: 2026-06-07 15:02 +0800

Linear: TAL-293/TAL-294

## Done

- Added regression coverage requiring `build.missing_artifact_writer` diagnostics to carry the planned artifact `target_root`.
- Updated the build planner so missing writer errors serialize and filter consistently with other artifact diagnostics.
- Updated the build workflow diagnostics docs for SDK, CLI, GUI, and future MCP consumers.

## Verification

- `rtk uv run pytest tests/test_build_manifest.py::test_plan_build_reports_missing_artifact_writers_before_emission` failed before the planner change because `target_root` was `None`.
- `rtk uv run pytest tests/test_build_manifest.py::test_plan_build_reports_missing_artifact_writers_before_emission` passed after the planner change.
- `rtk uv run pytest tests/test_build_manifest.py` passed.
- `rtk git diff --check` passed.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/plan.py tests/test_build_manifest.py` passed.
- `rtk bash scripts/flake.bash --ci` passed.
- `rtk bash scripts/test.bash` passed: 323 tests.

## Linear Sync

- Comment attempts on TAL-293 and TAL-294 failed with `UNAUTHORIZED; Session expired. Please re-authenticate.`

## Risks Or Blockers

- Linear sync is still blocked by expired authentication in the local connector.

## Next

- Continue strengthening build diagnostics around artifact ownership and writer contracts before moving into the reusable module compilation system.
