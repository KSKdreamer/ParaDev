# Build Explain Validation Progress

Date: 2026-06-07 06:23 CST

Linear: unavailable; no Linear connector was exposed by tool discovery and `linear` is not on PATH.

## Done

- Added SDK and CLI coverage for empty `build-explain` target values.
- Normalized `--module`, `--source`, and `--artifact` target values before target lookup.
- Moved source-path empty-string validation ahead of source path resolution, so `" "` no longer resolves to the project root.
- Documented the single-target and non-empty target rules for `build-explain`.

## Verification

- Red check: `rtk bash scripts/test.bash tests/test_project.py::test_project_build_explain_rejects_empty_targets tests/test_project.py::test_project_cli_build_explain_rejects_empty_targets -q` failed because whitespace targets were reported as unknown modules, sources, or artifacts.
- Focused green: `rtk bash scripts/test.bash tests/test_project.py::test_project_build_explain_rejects_empty_targets tests/test_project.py::test_project_cli_build_explain_rejects_empty_targets -q`
- Explain regression: `rtk bash scripts/test.bash tests/test_project.py::test_project_build_explain_returns_module_context_without_writing tests/test_project.py::test_project_cli_build_explain_outputs_json tests/test_project.py::test_project_build_explain_returns_artifact_context_without_writing tests/test_project.py::test_project_cli_build_explain_outputs_artifact_json tests/test_project.py::test_project_build_explain_returns_source_context_without_writing tests/test_project.py::test_project_cli_build_explain_outputs_source_json tests/test_project.py::test_project_build_explain_rejects_empty_targets tests/test_project.py::test_project_cli_build_explain_rejects_empty_targets -q`
- CLI smoke: `rtk uv run paradev build-explain demos/assets/projects/minimal --module ' ' --json` exited 2 with `--module must be non-empty`.
- Related: `rtk bash scripts/test.bash tests/test_project.py tests/test_build_manifest.py tests/test_build_records.py tests/test_cli.py tests/test_architecture.py -q`
- Full suite: `rtk bash scripts/test.bash`
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/explain.py src/paradev/sdk/project.py tests/test_project.py`
- Diff hygiene: `rtk git diff --check`

## Review

- Validation stays in both the SDK-facing project method and the lower-level build helper, so direct build-layer callers get the same non-empty target errors.
- The CLI still catches these as Typer parameter errors without introducing another command or output mode.
- Unrelated desktop and README work remains outside this slice and should stay unstaged.

## Risks Or Blockers

- Missing-target and multi-target validation already existed; this slice only made blank target values predictable.
- Linear status could not be updated from this environment.

## Next

- Add unknown-target tests for module, source, and artifact explanations so lookup failures remain stable.
- Continue pushing generic compiler diagnostics toward source slots rather than raw path guessing.
