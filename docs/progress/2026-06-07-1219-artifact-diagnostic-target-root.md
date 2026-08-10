# Artifact Diagnostic Target Root Progress

Date: 2026-06-07 12:19

Linear: TAL-294. Read attempt returned `UNAUTHORIZED; Session expired. Please re-authenticate.`, so the Linear issue still needs manual re-authentication before this slice can be synced there.

## Summary

- Added `target_root` to artifact path collision diagnostics.
- `build.artifact_path_collision` rows now expose both the colliding artifact owners and the target root where the collision happened.
- Added `Project.diagnostics(target_root=...)` and `paradev diagnostics --target-root` filtering for artifact-anchored diagnostics.
- Updated the build-flow guide so SDK, CLI, GUI, and future MCP callers can use the same target-root filter as artifact inspection.

## Verification

- Red first: `rtk bash scripts/test.bash tests/test_build_records.py::test_build_result_reports_duplicate_artifact_paths_as_blocking_diagnostics tests/test_project.py::test_project_diagnostics_filters_artifact_collision_by_owner -q` failed because collision rows lacked `target_root` and `Project.diagnostics(..., target_root=...)` was unsupported.
- Focused green: `rtk bash scripts/test.bash tests/test_build_records.py::test_build_result_reports_duplicate_artifact_paths_as_blocking_diagnostics tests/test_project.py::test_project_diagnostics_filters_artifact_collision_by_owner -q` passed.
- Related diagnostics: `rtk bash scripts/test.bash tests/test_build_records.py tests/test_project.py::test_project_diagnostics_returns_filtered_manifest_payload_without_writing tests/test_project.py::test_project_diagnostics_filters_slot_collision_by_collided_slot tests/test_project.py::test_project_diagnostics_filters_artifact_collision_by_owner tests/test_project.py::test_project_cli_filters_diagnostics_manifest_json -q` passed `16 passed`.
- Related suite: `rtk bash scripts/test.bash tests/test_build_records.py tests/test_project.py tests/test_project_build.py tests/test_build_manifest.py -q` passed `180 passed`.
- Whitespace: `rtk git diff --check` passed.
- Flake: `rtk bash scripts/flake.bash --ci` passed.
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/records.py src/paradev/sdk/project.py src/paradev/cli.py tests/test_build_records.py tests/test_project.py` passed.
- Full tests: `rtk bash scripts/test.bash` passed `288 passed in 66.88s`.

## Review Notes

- `target_root` is added to the diagnostic row rather than inferred from the message, matching the artifact and source-map payload shape.
- Existing local README and desktop app edits were left outside this compiler/diagnostics slice.

## Next

- Continue tightening artifact-anchored diagnostics and build explanations so users can debug output conflicts without reading internal manifests.
- Keep progressing the generic module compilation system after diagnostics remain stable across output/build artifact roots.
