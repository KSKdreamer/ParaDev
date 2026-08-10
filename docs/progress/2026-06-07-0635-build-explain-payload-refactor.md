# Build Explain Payload Refactor Progress

Date: 2026-06-07 06:35 CST

Linear: unavailable; no Linear connector was exposed by tool discovery and `linear` is not on PATH.

## Done

- Consolidated the repeated build-explain payload envelope into one private helper.
- Kept module, source, and artifact target branches responsible for their own filtering, diagnostics, and graph selection.
- Preserved the existing SDK and CLI build-explain behavior for module, source, artifact, validation, and unknown target cases.

## Verification

- Baseline explain regression: `rtk bash scripts/test.bash tests/test_project.py::test_project_build_explain_returns_module_context_without_writing tests/test_project.py::test_project_cli_build_explain_outputs_json tests/test_project.py::test_project_build_explain_returns_artifact_context_without_writing tests/test_project.py::test_project_cli_build_explain_outputs_artifact_json tests/test_project.py::test_project_build_explain_returns_source_context_without_writing tests/test_project.py::test_project_cli_build_explain_outputs_source_json tests/test_project.py::test_project_build_explain_rejects_empty_targets tests/test_project.py::test_project_cli_build_explain_rejects_empty_targets tests/test_project.py::test_project_build_explain_reports_unknown_source_with_requested_path tests/test_project.py::test_project_cli_build_explain_reports_unknown_targets -q`
- Post-refactor explain regression: same command, 14 passed.
- Related project tests: `rtk bash scripts/test.bash tests/test_project.py -q`
- Full suite: `rtk bash scripts/test.bash`
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/explain.py`
- Diff hygiene: `rtk git diff --check`

## Review

- The helper only centralizes schema, project id, profile passthrough, summary calculation, and payload field placement.
- Target-specific errors and graph filters still live in the module, source, and artifact branches.
- Unrelated desktop and README work remains outside this slice and should stay unstaged.

## Risks Or Blockers

- Linear status could not be updated from this environment.

## Next

- Continue pushing generic compiler diagnostics toward source slots rather than raw path guessing.
- Start the next compiler-system slice from the short-term plan once build-explain diagnostics are stable enough.
