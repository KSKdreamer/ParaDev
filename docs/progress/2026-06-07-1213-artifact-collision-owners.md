# Artifact Collision Owners Progress

Date: 2026-06-07 12:13

Linear: TAL-294. Read attempt returned `UNAUTHORIZED; Session expired. Please re-authenticate.`, so the Linear issue still needs manual re-authentication before this slice can be synced there.

## Summary

- Added owner context to duplicate artifact-path diagnostics.
- `build.artifact_path_collision` rows now include an `owners` list with both producing artifact owners.
- Added `Project.diagnostics(owner=...)` and `paradev diagnostics --owner` filtering so SDK, CLI, GUI, and future MCP callers can find collisions by either producer.
- Covered declarative project-local simple-source families that render the same artifact path.
- Updated the build-flow guide with the owner filter and collision-owner payload behavior.

## Verification

- Red first: `rtk bash scripts/test.bash tests/test_build_records.py::test_build_result_reports_duplicate_artifact_paths_as_blocking_diagnostics tests/test_project.py::test_project_diagnostics_filters_artifact_collision_by_owner -q` failed because collision rows lacked `owners` and `Project.diagnostics(..., owner=...)` was unsupported.
- Focused green: `rtk bash scripts/test.bash tests/test_build_records.py::test_build_result_reports_duplicate_artifact_paths_as_blocking_diagnostics tests/test_project.py::test_project_diagnostics_filters_artifact_collision_by_owner tests/test_project.py::test_project_cli_filters_diagnostics_manifest_json -q` passed `3 passed`.
- Related suite: `rtk bash scripts/test.bash tests/test_build_records.py tests/test_project.py tests/test_project_build.py tests/test_build_manifest.py -q` passed `180 passed`.
- Whitespace: `rtk git diff --check` passed.
- Flake: `rtk bash scripts/flake.bash --ci` passed.
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/records.py src/paradev/sdk/project.py src/paradev/cli.py tests/test_build_records.py tests/test_project.py` passed.
- Full tests: `rtk bash scripts/test.bash` passed `288 passed in 67.29s`.

## Review Notes

- The owner filter is additive: it matches `owners` on multi-producer diagnostics and can still match a scalar `owner` field if future diagnostics add one.
- Existing local README and desktop app edits were left outside this compiler/diagnostics slice.

## Next

- Continue improving diagnostics that are anchored to artifacts rather than direct source files.
- Keep build inspection payloads explainable by owner, module, collection, source, and artifact before expanding more compiler families.
