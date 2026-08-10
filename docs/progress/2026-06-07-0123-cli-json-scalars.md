# 2026-06-07 01:23 CST - CLI JSON Scalars

## Done

- Fixed CLI JSON mode so scalar command results serialize as valid JSON.
- Added regression coverage for `paradev cfg get paradev.project.name --json`.
- Preserved plain scalar output for non-JSON CLI use.
- Documented the machine-readable CLI output contract in the workflow guide.

## Verification

- Red first: `rtk bash scripts/test.bash tests/test_cli.py::test_config_get_serializes_scalar_json_option -q` failed because the command printed plain `ParaDev`.
- Focused green: `rtk bash scripts/test.bash tests/test_cli.py -q`
- CLI smoke: `rtk uv run paradev cfg get paradev.project.name --json`
- Plain text smoke: `rtk uv run paradev cfg get paradev.project.name`
- List JSON smoke: `rtk uv run paradev config list --json`
- Full suite: `rtk bash scripts/test.bash` passed 142 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/cli.py tests/test_cli.py`
- Whitespace: `rtk git diff --check -- src/paradev/cli.py tests/test_cli.py docs/workflows/README.md docs/progress/2026-06-07-0123-cli-json-scalars.md`

## Linear

- `rtk command -v linear` still exits with status 1.
- Tool discovery for Linear issue management exposed GitHub and Codex automation tools only; no Linear connector is available in this session.

## Risks

- This centralizes JSON mode in `_emit(...)`, so future scalar-returning commands now produce valid JSON under `--json`.
- Existing unrelated desktop, README, and script changes remain intentionally untouched.

## Next

- Continue tightening CLI and SDK machine-readable surfaces for desktop, MCP, and automation consumers.
- Keep progressing from config and parser foundations into reusable compiler contracts.
