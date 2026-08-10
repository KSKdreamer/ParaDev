# 2026-06-07 00:56 CST - Diagnostics Inspection

## Done

- Added public `diagnostic_index(...)` for deterministic severity/code diagnostic lookup payloads.
- Added `Project.diagnostics(...)` to return source-enriched diagnostics without writing build files.
- Added `paradev diagnostics` with `--severity`, `--code`, and `--module` filters.
- Added SDK, CLI, and manifest tests using a real missing-localization diagnostic with source span and resolved source metadata.
- Updated build-flow docs with the diagnostics inspection command and SDK example.

## Verification

- Red first: `rtk bash scripts/test.bash tests/test_build_manifest.py::test_manifest_payloads_and_writes_include_source_map_and_summary tests/test_project.py::test_project_diagnostics_returns_filtered_manifest_payload_without_writing tests/test_project.py::test_project_cli_filters_diagnostics_manifest_json -q` failed because diagnostics had no index, `Project.diagnostics` did not exist, and the `diagnostics` command did not exist.
- Focused green: `rtk bash scripts/test.bash tests/test_build_manifest.py::test_manifest_payloads_and_writes_include_source_map_and_summary tests/test_project.py::test_project_diagnostics_returns_filtered_manifest_payload_without_writing tests/test_project.py::test_project_cli_filters_diagnostics_manifest_json -q`
- Related suite: `rtk bash scripts/test.bash tests/test_project.py tests/test_build_manifest.py tests/test_project_build.py -q` passed 71 tests.
- Full suite: `rtk bash scripts/test.bash` passed 135 tests.
- CI lint: `rtk bash scripts/flake.bash --ci`
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/manifest.py src/paradev/build/__init__.py src/paradev/sdk/project.py src/paradev/cli.py tests/test_project.py tests/test_build_manifest.py`
- CLI smoke: `rtk uv run paradev diagnostics demos/assets/projects/minimal --json`
- Whitespace check: `rtk git diff --check -- src/paradev/build/manifest.py src/paradev/build/__init__.py src/paradev/sdk/project.py src/paradev/cli.py tests/test_project.py tests/test_build_manifest.py docs/workflows/build-flow.md docs/progress/2026-06-07-0056-diagnostics-inspection.md`

## Linear

- `rtk command -v linear` still exits with status 1.
- Tool discovery for Linear issue management exposed Codex automation and GitHub tools only; no Linear connector is available in this session.

## Risks

- Diagnostics inspection filters only by severity, code, and module id for now; richer family/source-slot filters can be added when clients need them.
- Existing unrelated desktop, README, and script changes remain intentionally untouched.

## Next

- Feed localization, assets, and diagnostics inspection payloads into desktop/MCP surfaces once those clients consume live SDK data.
- Continue hardening first real game-family constraints after verifying HOI4 icon and sprite policy from game data.
