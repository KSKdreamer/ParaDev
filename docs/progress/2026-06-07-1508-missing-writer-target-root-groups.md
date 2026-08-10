# Missing Writer Target Root Group Diagnostics Progress

Date: 2026-06-07 15:08 +0800

Linear: TAL-293/TAL-294

## Done

- Added regression coverage for missing artifact writers when the same missing artifact type is planned under both `output` and `build` target roots.
- Updated `plan_build(...)` so `build.missing_artifact_writer` diagnostics are emitted once per missing artifact type and target root.
- Updated the build workflow diagnostics docs so SDK, CLI, GUI, and future MCP consumers can rely on target-root filtering for missing-writer failures.

## Verification

- `rtk uv run pytest tests/test_build_manifest.py::test_plan_build_reports_missing_artifact_writers_per_target_root` failed before the planner change because only one diagnostic was emitted.
- `rtk uv run pytest tests/test_build_manifest.py::test_plan_build_reports_missing_artifact_writers_per_target_root` passed after the planner change.
- `rtk uv run pytest tests/test_build_manifest.py` passed.
- `rtk git diff --check` passed.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/plan.py tests/test_build_manifest.py` passed.
- `rtk bash scripts/flake.bash --ci` passed.
- `rtk bash scripts/test.bash` passed: 324 tests.

## Linear Sync

- Comment attempts on TAL-293 and TAL-294 failed with `UNAUTHORIZED; Session expired. Please re-authenticate.`

## Risks Or Blockers

- Linear sync may still require re-authentication before issue comments can be posted.

## Next

- Continue hardening artifact writer and target-root contracts, then return to the reusable module compilation system.
