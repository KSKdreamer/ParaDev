# Artifact Path Guard Progress

Date: 2026-06-07 13:19

Linear: TAL-294

## Done

- Added regression coverage for artifact paths that try to escape the selected output root.
- Rejected parent-traversing artifact paths in `write_artifacts(...)` before writer-specific file output.
- Added `build.invalid_artifact_path` planning diagnostics for absolute or parent-traversing artifact paths.
- Documented artifact path safety in `docs/workflows/build-flow.md`.

## Verification

- Red: `rtk bash scripts/test.bash tests/test_artifact_writers.py::test_write_artifacts_rejects_paths_that_escape_output_root -q` failed because no `ValueError` was raised.
- Red: `rtk bash scripts/test.bash tests/test_build_records.py::test_build_result_reports_invalid_artifact_paths -q` failed because `BuildResult.plan(...)` was not blocked.
- Green: `rtk bash scripts/test.bash tests/test_build_records.py::test_build_result_reports_invalid_artifact_paths -q` passed.
- Green: `rtk bash scripts/test.bash tests/test_artifact_writers.py::test_write_artifacts_rejects_paths_that_escape_output_root -q` passed.
- Build records and artifact writers: `rtk bash scripts/test.bash tests/test_build_records.py tests/test_artifact_writers.py -q` passed, `22 passed`.
- Related build path: `rtk bash scripts/test.bash tests/test_build_manifest.py tests/test_project_build.py tests/test_project.py -q` passed, `169 passed`.
- Style: `rtk git diff --check` passed.
- Style: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/artifacts.py src/paradev/build/records.py tests/test_artifact_writers.py tests/test_build_records.py` passed, `OK: 4 file(s) - no banned imports`.
- Style: `rtk bash scripts/flake.bash --ci` passed, `46 files would be left unchanged`.
- Full: `rtk bash scripts/test.bash` passed, `298 passed`.

## Risks Or Blockers

- Linear sync is blocked by expired auth: fetching `issue:TAL-294` returned `UNAUTHORIZED; Session expired. Please re-authenticate.`

## Next

- Continue tightening source-slot and artifact writer behavior before moving to the next generic module compilation slice.
