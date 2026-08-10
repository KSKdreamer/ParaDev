# Emit Hook Boundary Progress

Date: 2026-06-07 09:24 CST

Linear: unavailable; tool discovery exposed no Linear connector and `rtk which linear` returned no executable.

## Done

- Continued generic module compiler hardening from the `check(...)` hook boundary slice.
- Confirmed that custom family `emit(...)` exceptions still escaped `plan_build(...)`.
- Changed the planner so `emit(...)` exceptions become `family.emit_failed` diagnostics.
- Skipped artifact registration for the family whose `emit(...)` failed, so downstream writer coverage and filesystem emission do not treat partial compiler state as trusted output.
- Documented the `check(...)` and `emit(...)` hook failure contract in the build workflow guide.

## Verification

- Red check: `rtk uv run pytest tests/test_project_build.py::test_project_build_reports_emit_hook_errors_without_emitting_family_artifacts -q` failed because `RuntimeError` escaped from `emit(...)`.
- Focused green: `rtk uv run pytest tests/test_project_build.py::test_project_build_reports_emit_hook_errors_without_emitting_family_artifacts tests/test_project_build.py::test_project_build_reports_check_hook_errors_without_emitting_family_artifacts -q` passed 2 tests.
- Smoke probe: `plan_build(...)` with a failing `emit(...)` returned `blocked=True`, no artifacts, and a `family.emit_failed` diagnostic.
- Related build suite: `rtk bash scripts/test.bash tests/test_project_build.py tests/test_simple_source_family.py tests/test_build_manifest.py -q` passed 87 tests.
- Full suite: `rtk bash scripts/test.bash` passed with 258 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/plan.py tests/test_project_build.py`

## Review

- The change stays in `plan_build(...)`, which already owns registered family hook orchestration.
- The diagnostic format reuses the existing `_family_hook_diagnostic(...)` helper and mirrors `family.check_failed`.
- Strict developer-facing validation remains unchanged: families that emit non-`Artifact` values still raise `ValueError`.
- Unrelated desktop, README, and runner-script work remains outside this slice and should stay unstaged.

## Risks Or Blockers

- Linear status could not be updated from this environment.
- A fresh `rtk which linear` check returned no executable, and tool discovery exposed no Linear connector.
- `normalize(...)` exceptions still escape; deciding whether normalizer hook crashes should become diagnostics needs care because normalization owns module identity invariants.

## Next

- Continue compiler hardening by evaluating the `normalize(...)` exception boundary or moving to user-facing build explainability for hook failures.
