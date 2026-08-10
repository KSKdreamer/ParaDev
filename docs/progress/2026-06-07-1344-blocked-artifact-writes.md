# 2026-06-07 13:44 - Blocked Artifact Writes

## Scope

- Hardened the direct SDK artifact writer boundary so `write_artifacts(...)` rejects `BuildResult` values with blocking diagnostics before dispatching any artifact writer.
- Added artifact-writer coverage that proves blocked build results do not write files.
- Kept the lower-level path-containment guard covered by using a raw `BuildResult`, since `BuildResult.plan(...)` now reports parent-traversal paths as blocking diagnostics before writer dispatch.
- Updated the build workflow docs to tell SDK callers to pass unblocked results and one `target_root` at a time.

## Verification

- Red: `rtk uv run pytest tests/test_artifact_writers.py::test_write_artifacts_rejects_blocked_build_results` failed because `write_artifacts(...)` did not raise.
- Green: `rtk uv run pytest tests/test_artifact_writers.py::test_write_artifacts_rejects_blocked_build_results` passed.
- Related: `rtk uv run pytest tests/test_artifact_writers.py tests/test_project_build.py tests/test_project.py` passed with 173 tests.
- Diff hygiene: `rtk git diff --check` passed.
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/artifacts.py tests/test_artifact_writers.py` passed with `OK: 2 file(s) - no banned imports`.
- Flake: `rtk bash scripts/flake.bash --ci` passed with 46 files unchanged.
- Full tests: `rtk bash scripts/test.bash` passed with 305 tests.

## Review Notes

- `Project.build(..., emit_artifacts=True)` already rejected blocked results; this slice extends the same safety contract to direct SDK callers.
- The direct writer path test intentionally bypasses `BuildResult.plan(...)` so the writer-level containment check still has regression coverage.
- Linear sync was not updated because the API session is expired and returns `UNAUTHORIZED`; local progress continues until the session is refreshed.
