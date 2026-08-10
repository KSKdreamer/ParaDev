# Untracked Input Target Root Diagnostics Progress

Date: 2026-06-07 15:13 +0800

Linear: TAL-293/TAL-294

## Done

- Added regression coverage requiring `build.untracked_artifact_input` warnings to carry the owning artifact `target_root`.
- Updated the generic build records planner so untracked input warnings can be filtered and explained by output root versus build root.
- Updated the build workflow diagnostics and manifest docs for SDK, CLI, GUI, and future MCP consumers.

## Verification

- `rtk uv run pytest tests/test_build_records.py::test_build_result_reports_untracked_artifact_inputs_as_warnings` failed before the records change because `target_root` was `None`.
- `rtk uv run pytest tests/test_build_records.py::test_build_result_reports_untracked_artifact_inputs_as_warnings` passed after the records change.
- `rtk uv run pytest tests/test_build_records.py` passed.
- `rtk git diff --check` passed.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/records.py tests/test_build_records.py` passed.
- `rtk bash scripts/flake.bash --ci` passed.
- `rtk bash scripts/test.bash` passed: 324 tests.

## Linear Sync

- Comment attempts on TAL-293 and TAL-294 failed with `auth_revoked`: `Session expired. Please re-authenticate.`

## Risks Or Blockers

- Linear sync may require re-authentication before issue comments can be posted.

## Next

- Continue making artifact diagnostics consistently target-root aware, then move back into reusable module compiler behavior.
