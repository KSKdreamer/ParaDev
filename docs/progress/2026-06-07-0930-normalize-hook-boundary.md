# Normalize Hook Boundary Progress

Date: 2026-06-07 09:30 CST

Linear: unavailable; tool discovery exposed no Linear connector and `rtk which linear` returned no executable.

## Done

- Continued generic module compiler hardening from the `check(...)` and `emit(...)` hook boundary slices.
- Confirmed that custom family `normalize(...)` exceptions escaped `plan_build(...)`.
- Changed the planner so `normalize(...)` exceptions become `family.normalize_failed` diagnostics.
- Skipped later `check(...)` and `emit(...)` work for the failed family, so unnormalized modules do not produce trusted artifacts.
- Documented the difference between settings normalizer diagnostics and family-level `normalize(...)` hook failures.

## Verification

- Red check: `rtk uv run pytest tests/test_project_build.py::test_project_build_reports_normalize_hook_errors_without_emitting_family_artifacts -q` failed because `RuntimeError` escaped from `normalize(...)`.
- Focused green: `rtk uv run pytest tests/test_project_build.py::test_project_build_reports_normalize_hook_errors_without_emitting_family_artifacts tests/test_project_build.py::test_project_build_rejects_normalize_hooks_that_drop_modules tests/test_project_build.py::test_project_build_reports_check_hook_errors_without_emitting_family_artifacts tests/test_project_build.py::test_project_build_reports_emit_hook_errors_without_emitting_family_artifacts -q` passed 4 tests.
- Smoke probe: `plan_build(...)` with a failing `normalize(...)` returned `blocked=True`, no artifacts, and a `family.normalize_failed` diagnostic without running `emit(...)`.
- Related build suite: `rtk bash scripts/test.bash tests/test_project_build.py tests/test_simple_source_family.py tests/test_build_manifest.py -q` passed 88 tests.
- Full suite: `rtk bash scripts/test.bash` passed with 259 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/plan.py tests/test_project_build.py`

## Review

- The change adds one failed-family set in `plan_build(...)`, keeping hook orchestration centralized.
- Malformed `normalize(...)` return values still raise developer-facing `ValueError`s, preserving the strict module identity contract.
- Families whose normalizer crashes remain visible in the build result modules and diagnostics, but their later compiler stages are skipped.
- Unrelated desktop, README, and runner-script work remains outside this slice and should stay unstaged.

## Risks Or Blockers

- Linear status could not be updated from this environment.
- A fresh `rtk which linear` check returned no executable, and tool discovery exposed no Linear connector.
- More granular source anchors for family hook crashes may be useful later, but the hook boundary is now structured enough for SDK, CLI, and GUI clients to report the failure without crashing.

## Next

- Continue toward user-facing build explainability for hook failures and compiler inspection payloads.
