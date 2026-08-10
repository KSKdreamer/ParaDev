# Hook Contract Diagnostics Progress

Date: 2026-06-07 14:45

Linear: TAL-294

## Done

- Added regression coverage for Python-backed `check(...)` hooks returning non-`Diagnostic` values.
- Added regression coverage for Python-backed `emit(...)` hooks returning non-`Artifact` values.
- Moved check diagnostic coercion and emit artifact coercion inside the guarded hook blocks so bad return contracts become `family.check_failed` or `family.emit_failed` diagnostics.
- Updated the build workflow docs to describe check and emit return-contract diagnostics alongside normalize contract failures.

## Verification

- `rtk uv run pytest tests/test_project_build.py::test_project_build_reports_check_contract_errors_without_emitting_family_artifacts tests/test_project_build.py::test_project_build_reports_emit_contract_errors_without_emitting_family_artifacts` failed before the fix with raw `ValueError`, then passed after the fix.
- `rtk uv run pytest tests/test_project_build.py::test_project_build_reports_normalize_contract_errors_without_emitting_family_artifacts tests/test_project_build.py::test_project_build_reports_check_hook_errors_without_emitting_family_artifacts tests/test_project_build.py::test_project_build_reports_emit_hook_errors_without_emitting_family_artifacts` passed.
- `rtk uv run pytest tests/test_project_build.py` passed: 67 tests.
- `rtk git diff --check` passed.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/plan.py tests/test_project_build.py` passed.
- `rtk bash scripts/flake.bash --ci` passed.
- `rtk bash scripts/test.bash` passed: 322 tests.

## Risks Or Blockers

- Linear API access still needs re-authentication before TAL-294 can receive live comments from this environment.

## Next

- Continue hardening generic compiler surfaces, then proceed into the reusable module compilation system.
