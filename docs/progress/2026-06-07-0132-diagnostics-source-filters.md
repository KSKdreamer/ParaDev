# 2026-06-07 01:32 CST - Diagnostics Source Filters

## Done

- Added SDK diagnostics filters for `source_path` and `slot`.
- Added CLI diagnostics filters through `--source` and `--slot`.
- Updated the build-flow guide so users can inspect only diagnostics for the file or source slot they are fixing.

## Verification

- Red first: `rtk bash scripts/test.bash tests/test_project.py::test_project_diagnostics_returns_filtered_manifest_payload_without_writing tests/test_project.py::test_project_cli_filters_diagnostics_manifest_json -q` failed because `source_path` and `--source` did not exist.
- Focused green: `rtk bash scripts/test.bash tests/test_project.py::test_project_diagnostics_returns_filtered_manifest_payload_without_writing tests/test_project.py::test_project_cli_filters_diagnostics_manifest_json -q`
- Related suite: `rtk bash scripts/test.bash tests/test_project.py tests/test_build_manifest.py -q` passed 33 tests.
- Full suite: `rtk bash scripts/test.bash` passed 142 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py src/paradev/cli.py tests/test_project.py`
- CLI smoke: `rtk uv run paradev diagnostics demos/assets/projects/minimal --source def.pdx --slot loc --json`
- Whitespace: `rtk git diff --check -- src/paradev/sdk/project.py src/paradev/cli.py tests/test_project.py docs/workflows/build-flow.md docs/progress/2026-06-07-0132-diagnostics-source-filters.md`

## Linear

- `rtk command -v linear` exits with status 1.
- Tool discovery for Linear issue management exposed GitHub and Codex automation tools only; no Linear connector is available in this session.

## Risks

- Filters match the diagnostic row fields (`source_path` and `slot`), not the resolved `source.slot`. This keeps the API aligned with what the compiler reports, but some diagnostics can have `slot="loc"` and `source.slot="def"` when the localization requirement is anchored to a PDX object span.
- Existing unrelated desktop, README, and script changes remain intentionally untouched.

## Next

- Continue tightening diagnostic inspection around blocked builds before moving deeper into generic compilation.
- Keep the CLI and SDK manifest filters aligned so desktop and future MCP surfaces can reuse the same minimal mental model.
