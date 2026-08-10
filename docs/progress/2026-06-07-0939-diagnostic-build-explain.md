# Diagnostic Build Explain Progress

Date: 2026-06-07 09:39 CST

Linear: unavailable; tool discovery exposed no Linear connector and `rtk which linear` returned no executable.

## Done

- Extended build explanations with a diagnostic-code target for SDK and CLI callers.
- Added `Project.build_explain(diagnostic_code=...)` and `paradev build-explain --diagnostic-code ...`.
- Returned matching diagnostic rows even when the diagnostic has no module, source, or artifact anchor.
- Kept anchored diagnostics useful by carrying resolved source and artifact context when present.
- Documented diagnostic-code explanations in the build workflow guide.

## Verification

- Red SDK check: `rtk uv run pytest tests/test_project.py::test_project_build_explain_returns_diagnostic_context_without_writing -q` failed because `Project.build_explain(...)` did not accept `diagnostic_code`.
- Red CLI check: `rtk uv run pytest tests/test_project.py::test_project_cli_build_explain_outputs_diagnostic_json -q` failed because `--diagnostic-code` was not a known option.
- Focused green: `rtk uv run pytest tests/test_project.py::test_project_build_explain_returns_diagnostic_context_without_writing tests/test_project.py::test_project_cli_build_explain_outputs_diagnostic_json tests/test_project.py::test_project_build_explain_rejects_empty_targets tests/test_project.py::test_project_cli_build_explain_rejects_empty_targets tests/test_project.py::test_project_cli_build_explain_reports_unknown_targets -q` passed 11 tests.
- Explain regression: `rtk uv run pytest tests/test_project.py::test_project_build_explain_returns_module_context_without_writing tests/test_project.py::test_project_cli_build_explain_outputs_json tests/test_project.py::test_project_build_explain_returns_artifact_context_without_writing tests/test_project.py::test_project_cli_build_explain_outputs_artifact_json tests/test_project.py::test_project_build_explain_returns_source_context_without_writing tests/test_project.py::test_project_cli_build_explain_outputs_source_json tests/test_project.py::test_project_build_explain_returns_diagnostic_context_without_writing tests/test_project.py::test_project_cli_build_explain_outputs_diagnostic_json tests/test_project.py::test_project_build_explain_rejects_empty_targets tests/test_project.py::test_project_cli_build_explain_rejects_empty_targets tests/test_project.py::test_project_build_explain_reports_unknown_source_with_requested_path tests/test_project.py::test_project_cli_build_explain_reports_unknown_targets -q` passed 18 tests.
- CLI smoke: `rtk uv run python ...` invoked `paradev build-explain --diagnostic-code family.normalize_failed --json` through Typer against a temporary project-local failing family, exited 0, and returned a blocking diagnostic explanation with no graph nodes.
- Related project/build suite: `rtk bash scripts/test.bash tests/test_project.py tests/test_project_build.py -q` passed 139 tests.
- Full suite: `rtk bash scripts/test.bash` passed with 263 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/explain.py src/paradev/sdk/project.py src/paradev/cli.py tests/test_project.py`

## Review

- The change extends the existing build-explain target model instead of adding a parallel diagnostics command.
- Diagnostic explanations preserve the existing payload schema and summary contract.
- The CLI parameter hint stays short so Rich keeps target errors readable.
- Unrelated desktop, README, and runner-script work remains outside this slice and should stay unstaged.

## Risks Or Blockers

- Linear status could not be updated from this environment.
- A fresh `rtk which linear` check returned no executable, and tool discovery exposed no Linear connector.
- Diagnostic-code targets can return multiple rows for repeated codes; future GUI clients may want a row index target if they need to focus one diagnostic instance.

## Next

- Continue tying diagnostics to source spans and compiler inspection payloads where the build has enough context.
