# 2026-06-07 02:02 CST - PDX Parse Source Diagnostics

## Done

- Added `pdx.source_not_found` JSON diagnostics for `paradev parse` missing files.
- Kept missing file, parser failure, and success responses on the same `paradev.pdx.parse.v1` payload shape.
- Documented parse source diagnostics in the build-flow guide.

## Verification

- Red first: `rtk bash scripts/test.bash tests/test_cli.py::test_parse_outputs_diagnostics_json_for_missing_source -q` failed because the command emitted no JSON payload for a missing source file.
- Focused green: `rtk bash scripts/test.bash tests/test_cli.py::test_parse_outputs_diagnostics_json_for_missing_source tests/test_cli.py::test_parse_outputs_pdx_projection_json tests/test_cli.py::test_parse_outputs_diagnostics_json_for_invalid_pdx -q` passed 3 tests.
- Related suite: `rtk bash scripts/test.bash tests/test_cli.py tests/test_pdx_token.py tests/test_pdx_roundtrip.py tests/test_build_loaders.py -q` passed 32 tests.
- Full suite: `rtk bash scripts/test.bash` passed 156 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/cli.py tests/test_cli.py`
- CLI smoke: `rtk uv run paradev parse demos/assets/projects/minimal/src/modules/focus/GER_sample/missing.pdx --json` printed `pdx.source_not_found` JSON and exited with expected status 1.
- Whitespace: `rtk git diff --check -- src/paradev/cli.py tests/test_cli.py docs/workflows/build-flow.md docs/progress/2026-06-07-0202-pdx-parse-source-diagnostics.md`

## Linear

- `rtk command -v linear` exits with status 1.
- Tool discovery for Linear issue management exposed Codex automation and GitHub tools only; no Linear connector is available in this session.

## Risks

- Directory and permission errors map to `pdx.source_unreadable`; only missing-file behavior has direct test coverage in this slice.
- Existing unrelated desktop, README, and script changes remain intentionally untouched.

## Next

- Keep parse payloads aligned between CLI, future MCP tools, and LSP diagnostics.
