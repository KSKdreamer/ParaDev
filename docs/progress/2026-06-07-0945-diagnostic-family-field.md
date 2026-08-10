# Diagnostic Family Field Progress

Date: 2026-06-07 09:45 CST

Linear: connector discovered, but `_save_comment` on `TAL-293` failed with `UNAUTHORIZED`; the session needs re-authentication.

## Done

- Made build diagnostics capable of carrying a structured `family` field.
- Added the failing family id to `family.normalize_failed`, `family.check_failed`, and `family.emit_failed` diagnostics.
- Updated build explanation coverage so unanchored hook failures expose the family without requiring clients to parse diagnostic messages.
- Updated hook-boundary tests to assert the structured family metadata.
- Documented the family field in the build workflow guide.

## Verification

- Red check: `rtk uv run pytest tests/test_project.py::test_project_build_explain_returns_diagnostic_context_without_writing -q` failed because the diagnostic payload did not include `family`.
- Focused green: `rtk uv run pytest tests/test_project.py::test_project_build_explain_returns_diagnostic_context_without_writing tests/test_project_build.py::test_project_build_reports_normalize_hook_errors_without_emitting_family_artifacts tests/test_project_build.py::test_project_build_reports_check_hook_errors_without_emitting_family_artifacts tests/test_project_build.py::test_project_build_reports_emit_hook_errors_without_emitting_family_artifacts tests/test_build_records.py -q` passed 16 tests.
- CLI smoke: `paradev build-explain --diagnostic-code family.normalize_failed --json` against a temporary project-local failing family exited 0 and returned `family: notice` in the diagnostic row.
- Related project/build suite: `rtk bash scripts/test.bash tests/test_project.py tests/test_project_build.py tests/test_build_records.py -q` passed 151 tests.
- Full suite: `rtk bash scripts/test.bash` passed with 263 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/records.py src/paradev/build/plan.py tests/test_project.py tests/test_project_build.py`

## Review

- The `family` field is optional, so existing diagnostics without family context keep their current payload shape.
- Family hook diagnostics now provide machine-readable routing context for SDK, CLI, GUI, and future MCP clients.
- The change avoids introducing a new diagnostics API or message parser.
- Unrelated desktop, README, and runner-script work remains outside this slice and should stay unstaged.

## Risks Or Blockers

- Linear status could not be updated because the connector session is expired.
- Family filters for `paradev diagnostics` are still not exposed; this slice only makes the diagnostic payload more complete.

## Next

- Consider adding a `family` filter to diagnostic inspection once the payload field has settled.
