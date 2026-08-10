# 2026-06-07 01:19 CST - CLI Blocked Emission

## Done

- Added CLI preflight for `paradev build --emit-artifacts`.
- When a build is blocked, the CLI now prints the structured dry-run payload with diagnostics, exits non-zero, and does not write output artifacts.
- Preserved the SDK `Project.build(emit_artifacts=True)` fail-fast contract for direct callers.
- Added a regression test for blocked CLI emission and a successful emit regression check.
- Updated build-flow docs with the blocked-emission behavior.

## Verification

- Red first: `rtk bash scripts/test.bash tests/test_project.py::test_demo_project_build_cli_reports_blocked_emit_payload_without_writing -q` failed because the CLI exited non-zero with empty output.
- Focused green: `rtk bash scripts/test.bash tests/test_project.py::test_demo_project_build_cli_reports_blocked_emit_payload_without_writing tests/test_project.py::test_demo_project_build_cli_can_emit_profile_files -q`
- Related suite: `rtk bash scripts/test.bash tests/test_project.py tests/test_project_build.py tests/test_sdk_examples.py -q` passed 71 tests.
- Full suite: `rtk bash scripts/test.bash` passed 141 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/cli.py tests/test_project.py`
- Blocked CLI smoke: `rtk bash scripts/test.bash tests/test_project.py::test_demo_project_build_cli_reports_blocked_emit_payload_without_writing -q`
- Whitespace: `rtk git diff --check -- src/paradev/cli.py tests/test_project.py docs/workflows/build-flow.md docs/progress/2026-06-07-0119-cli-blocked-emission.md`

## Linear

- `rtk command -v linear` still exits with status 1.
- Tool discovery for Linear issue management exposed GitHub and Codex automation tools only; no Linear connector is available in this session.

## Risks

- The CLI preflight performs a dry build before successful artifact emission, so successful emit commands plan twice.
- Existing unrelated desktop, README, and script changes remain intentionally untouched.

## Next

- Continue improving diagnostics and CLI/SDK surfaces so blocked builds explain source fixes before write attempts.
- Keep generic compiler behavior documented for future desktop and MCP consumers.
