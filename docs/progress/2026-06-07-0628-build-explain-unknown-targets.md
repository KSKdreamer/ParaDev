# Build Explain Unknown Targets Progress

Date: 2026-06-07 06:28 CST

Linear: unavailable; no Linear connector was exposed by tool discovery and `linear` is not on PATH.

## Done

- Added SDK coverage for unknown source explanations, preserving the caller's project-relative source path in the error.
- Added CLI coverage for unknown module, source, and artifact explanation targets.
- Remapped project-level unknown source errors after absolute path lookup so users see the requested path, not a temp or local absolute path.
- Documented that unknown targets are reported against the requested target value.

## Verification

- Red check: `rtk bash scripts/test.bash tests/test_project.py::test_project_build_explain_reports_unknown_source_with_requested_path tests/test_project.py::test_project_cli_build_explain_reports_unknown_targets -q` failed because source lookup errors exposed resolved absolute paths and the CLI test had to account for Rich wrapping.
- Focused green: `rtk bash scripts/test.bash tests/test_project.py::test_project_build_explain_reports_unknown_source_with_requested_path tests/test_project.py::test_project_cli_build_explain_reports_unknown_targets -q`
- Explain regression: `rtk bash scripts/test.bash tests/test_project.py::test_project_build_explain_returns_module_context_without_writing tests/test_project.py::test_project_cli_build_explain_outputs_json tests/test_project.py::test_project_build_explain_returns_artifact_context_without_writing tests/test_project.py::test_project_cli_build_explain_outputs_artifact_json tests/test_project.py::test_project_build_explain_returns_source_context_without_writing tests/test_project.py::test_project_cli_build_explain_outputs_source_json tests/test_project.py::test_project_build_explain_rejects_empty_targets tests/test_project.py::test_project_cli_build_explain_rejects_empty_targets tests/test_project.py::test_project_build_explain_reports_unknown_source_with_requested_path tests/test_project.py::test_project_cli_build_explain_reports_unknown_targets -q`
- CLI smoke: `rtk uv run paradev build-explain demos/assets/projects/minimal --source src/modules/focus/GER_sample/missing.pdx --json` exited 2 with the relative source path in the error.
- Related: `rtk bash scripts/test.bash tests/test_project.py tests/test_build_manifest.py tests/test_build_records.py tests/test_cli.py tests/test_architecture.py -q`
- Full suite: `rtk bash scripts/test.bash`
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py tests/test_project.py`
- Diff hygiene: `rtk git diff --check`

## Review

- The build layer still receives resolved source paths for manifest matching; only the project-facing error is remapped to the requested path.
- CLI assertions check stable error fragments because Typer/Rich may wrap long messages across lines.
- Unrelated desktop and README work remains outside this slice and should stay unstaged.

## Risks Or Blockers

- Unknown module and artifact errors already used the requested value; this slice focused on source path remapping and coverage.
- Linear status could not be updated from this environment.

## Next

- Consolidate repeated explain payload construction to reduce helper duplication while preserving target-specific behavior.
- Continue pushing generic compiler diagnostics toward source slots rather than raw path guessing.
