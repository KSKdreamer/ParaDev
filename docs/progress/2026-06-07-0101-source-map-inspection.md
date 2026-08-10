# 2026-06-07 01:01 CST - Source Map Inspection

## Done

- Added public `source_map_index(...)` for deterministic module/slot source-map lookup payloads.
- Added `Project.source_map(...)` to return artifact-to-source traceability without writing build files.
- Added `paradev source-map` with `--module`, `--family`, `--slot`, `--type`, and `--target-root` filters.
- Added SDK, CLI, and manifest tests for filtered PDX and localization artifact traceability.
- Updated build-flow docs with the source-map inspection command and SDK example.

## Verification

- Red first: `rtk bash scripts/test.bash tests/test_build_manifest.py::test_manifest_payloads_and_writes_include_source_map_and_summary tests/test_project.py::test_project_source_map_returns_filtered_manifest_payload_without_writing tests/test_project.py::test_project_cli_filters_source_map_manifest_json -q` failed because source maps had no index, `Project.source_map` did not exist, and the `source-map` command did not exist.
- Focused green: `rtk bash scripts/test.bash tests/test_build_manifest.py::test_manifest_payloads_and_writes_include_source_map_and_summary tests/test_project.py::test_project_source_map_returns_filtered_manifest_payload_without_writing tests/test_project.py::test_project_cli_filters_source_map_manifest_json -q`
- Related suite: `rtk bash scripts/test.bash tests/test_project.py tests/test_build_manifest.py tests/test_project_build.py -q` passed 73 tests.
- Full suite: `rtk bash scripts/test.bash` passed 137 tests.
- CI lint: `rtk bash scripts/flake.bash --ci`
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/manifest.py src/paradev/build/__init__.py src/paradev/sdk/project.py src/paradev/cli.py tests/test_project.py tests/test_build_manifest.py`
- CLI smoke: `rtk uv run paradev source-map demos/assets/projects/minimal --module focus/GER_sample --slot def --type pdx --target-root output --json`
- Whitespace check: `rtk git diff --check -- src/paradev/build/manifest.py src/paradev/build/__init__.py src/paradev/sdk/project.py src/paradev/cli.py tests/test_project.py tests/test_build_manifest.py docs/workflows/build-flow.md docs/progress/2026-06-07-0101-source-map-inspection.md`

## Linear

- `rtk command -v linear` still exits with status 1.
- Tool discovery for Linear issue management exposed Codex automation and GitHub tools only; no Linear connector is available in this session.

## Risks

- Source-map inspection currently indexes module-backed sources; collection-only source rows remain visible but are not in the module/slot index.
- Existing unrelated desktop, README, and script changes remain intentionally untouched.

## Next

- Feed localization, assets, diagnostics, and source-map inspection payloads into desktop/MCP surfaces once those clients consume live SDK data.
- Continue hardening first real game-family constraints after verifying HOI4 icon and sprite policy from game data.
