# Missing Emit Diagnostics Progress

Date: 2026-06-07 14:51

Linear: TAL-294

## Done

- Added regression coverage for registered Python-backed families that have matching modules but no callable `emit(...)` hook.
- Changed the build planner to return a blocking `family.emit_failed` diagnostic for missing `emit(...)` instead of aborting the dry build with a raw `ValueError`.
- Updated the build workflow docs so family authors see missing `emit(...)` as part of the hook diagnostic contract.

## Verification

- `rtk uv run pytest tests/test_project_build.py::test_project_build_reports_missing_emit_hooks_without_aborting_build` failed before the fix with raw `ValueError`, then passed after the fix.
- `rtk uv run pytest tests/test_project_build.py::test_project_build_reports_emit_hook_errors_without_emitting_family_artifacts tests/test_project_build.py::test_project_build_reports_emit_contract_errors_without_emitting_family_artifacts` passed.
- `rtk uv run pytest tests/test_project_build.py` passed: 68 tests.
- `rtk git diff --check` passed.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/plan.py tests/test_project_build.py` passed.
- `rtk bash scripts/flake.bash --ci` passed.
- `rtk bash scripts/test.bash` passed: 323 tests.

## Risks Or Blockers

- Linear API access still needs re-authentication before TAL-294 can receive live comments from this environment.

## Next

- Continue tightening compiler diagnostics, then move toward the reusable module compilation system.
