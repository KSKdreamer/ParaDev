# Check Hook Boundary Progress

Date: 2026-06-07 09:20 CST

Linear: unavailable; tool discovery exposed no Linear connector and `rtk which linear` returned no executable.

## Done

- Continued generic module compiler hardening from the normalizer error-boundary slice.
- Found that custom family `check(...)` exceptions escaped `plan_build(...)` and `Project.build(...)`.
- Changed the planner so `check(...)` exceptions become `family.check_failed` diagnostics.
- Skipped artifact emission for the family whose `check(...)` failed, so invalid validation state does not produce trusted artifacts.
- Documented the `check(...)` failure contract in the build workflow guide.

## Verification

- Red check: `rtk uv run pytest tests/test_project_build.py::test_project_build_reports_check_hook_errors_without_emitting_family_artifacts -q` failed because `RuntimeError` escaped from `check(...)`.
- Focused green: `rtk uv run pytest tests/test_project_build.py::test_project_build_reports_check_hook_errors_without_emitting_family_artifacts tests/test_project_build.py::test_project_build_rejects_normalize_hooks_that_drop_modules -q` passed 2 tests.
- Smoke probe: `plan_build(...)` with a failing `check(...)` returned `blocked=True`, no artifacts, and a `family.check_failed` diagnostic.
- Related build suite: `rtk bash scripts/test.bash tests/test_project_build.py tests/test_simple_source_family.py tests/test_build_manifest.py -q` passed 86 tests.
- Full suite: `rtk bash scripts/test.bash` passed with 257 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/plan.py tests/test_project_build.py`

## Review

- The change stays in `plan_build(...)`, where all registered family hooks are already orchestrated.
- The family continues to appear in modules and diagnostics, but its artifacts are not emitted when its validation hook crashes.
- Return-shape validation remains strict: non-`Diagnostic` check results and malformed normalize returns still raise developer-facing `ValueError`s.
- Unrelated desktop and README work remains outside this slice and should stay unstaged.

## Risks Or Blockers

- Linear status could not be updated from this environment.
- `emit(...)` exceptions still escape; turning those into diagnostics needs a separate decision because partial artifact emission and writer coverage semantics need care.

## Next

- Decide whether `emit(...)` hook failures should become build diagnostics with per-family artifact suppression, or shift to compiler inspection payloads for user-facing explainability.
