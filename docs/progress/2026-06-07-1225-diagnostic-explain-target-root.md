# Diagnostic Explain Target Root Progress

Date: 2026-06-07 12:25

Linear: TAL-294. Read attempt returned `UNAUTHORIZED; Session expired. Please re-authenticate.`, so the Linear issue still needs manual re-authentication before this slice can be synced there.

## Summary

- Scoped diagnostic-code build explanations for artifact diagnostics by `target_root`.
- Artifact path collision explanations now include only source-map rows whose artifact path and target root match the diagnostic.
- Added a regression where an output-root collision shares the same artifact path with a build-root planning artifact.
- Updated the build-flow guide so GUI, MCP, SDK, and script users know diagnostic artifact context respects target root.

## Verification

- Red first: `rtk bash scripts/test.bash tests/test_project.py::test_project_build_explain_scopes_diagnostic_artifacts_by_target_root -q` failed because the diagnostic explanation returned 3 artifacts instead of the 2 output-root collision producers.
- Focused green: `rtk bash scripts/test.bash tests/test_project.py::test_project_build_explain_scopes_diagnostic_artifacts_by_target_root -q` passed.
- Related build-explain cluster: `rtk bash scripts/test.bash tests/test_project.py::test_project_build_explain_returns_diagnostic_context_without_writing tests/test_project.py::test_project_build_explain_scopes_diagnostic_artifacts_by_target_root tests/test_project.py::test_project_cli_build_explain_outputs_diagnostic_json tests/test_project.py::test_project_build_explain_returns_artifact_context_without_writing tests/test_project.py::test_project_build_explain_returns_source_context_without_writing tests/test_project.py::test_project_build_explain_returns_module_context_without_writing -q` passed `6 passed`.
- Related suite: `rtk bash scripts/test.bash tests/test_project.py tests/test_build_manifest.py tests/test_build_records.py -q` passed `116 passed`.
- Whitespace: `rtk git diff --check` passed.
- Flake: `rtk bash scripts/flake.bash --ci` passed.
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/explain.py tests/test_project.py` passed.
- Full tests: `rtk bash scripts/test.bash` passed `289 passed in 67.72s`.

## Review Notes

- Diagnostics without `target_root` keep the existing path-only artifact context behavior.
- Existing local README and desktop app edits were left outside this build-explain slice.

## Next

- Continue tightening artifact-anchored explanations so users can debug build conflicts without reading raw manifests.
- Keep build graph and source-map views aligned with diagnostics before expanding additional compiler families.
