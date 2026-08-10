# Normalize Contract Diagnostics Progress

Date: 2026-06-07 14:39

Linear: TAL-294

## Done

- Changed the build planner so invalid `normalize(...)` return contracts are reported as `family.normalize_failed` diagnostics.
- Preserved the original modules and skipped artifact emission for the failed family instead of aborting the SDK build call.
- Cleaned hook diagnostic message formatting to avoid doubled punctuation when wrapped exceptions already include a period.
- Updated the build workflow docs to state that dropped module ids, family changes, and invalid normalize return values are surfaced as diagnostics.

## Verification

- `rtk uv run pytest tests/test_project_build.py::test_project_build_reports_normalize_contract_errors_without_emitting_family_artifacts` failed before the fix with raw `ValueError`, then passed after the fix.
- `rtk uv run pytest tests/test_project_build.py::test_project_build_reports_normalize_hook_errors_without_emitting_family_artifacts tests/test_project_build.py::test_project_build_reports_check_hook_errors_without_emitting_family_artifacts tests/test_project_build.py::test_project_build_reports_emit_hook_errors_without_emitting_family_artifacts` passed.
- `rtk uv run pytest tests/test_project_build.py` passed: 65 tests.
- `rtk git diff --check` passed.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/plan.py tests/test_project_build.py` passed.
- `rtk bash scripts/flake.bash --ci` passed.
- `rtk bash scripts/test.bash` passed: 320 tests.

## Risks Or Blockers

- Linear API access still needs re-authentication before TAL-294 can receive live comments from this environment.

## Next

- Continue hardening generic compiler failure boundaries and then move toward the reusable module compilation system slices.
