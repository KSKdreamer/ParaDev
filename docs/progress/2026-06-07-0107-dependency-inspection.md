# 2026-06-07 01:07 CST - Dependency Inspection

## Done

- Added public `dependency_index(...)` for deterministic source/kind dependency lookup payloads.
- Added `Project.dependencies(...)` to return build dependency edges without writing build files.
- Added `paradev dependencies` with `--module`, `--source`, `--target`, and `--kind` filters.
- Added SDK, CLI, and manifest tests for filtered `requires` and `after` edges from the minimal demo.
- Updated build-flow docs with the dependency inspection command and SDK example.

## Verification

- Red first: `rtk bash scripts/test.bash tests/test_build_manifest.py::test_manifest_payloads_and_writes_include_source_map_and_summary tests/test_project.py::test_project_dependencies_returns_filtered_manifest_payload_without_writing tests/test_project.py::test_project_cli_filters_dependency_manifest_json -q` failed because dependencies had no index, `Project.dependencies` did not exist, and the `dependencies` command did not exist.
- Focused green: `rtk bash scripts/test.bash tests/test_build_manifest.py::test_manifest_payloads_and_writes_include_source_map_and_summary tests/test_project.py::test_project_dependencies_returns_filtered_manifest_payload_without_writing tests/test_project.py::test_project_cli_filters_dependency_manifest_json -q`
- Related suite: `rtk bash scripts/test.bash tests/test_project.py tests/test_build_manifest.py tests/test_project_build.py -q` passed 75 tests.
- Full suite: `rtk bash scripts/test.bash` passed 139 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/manifest.py src/paradev/build/__init__.py src/paradev/sdk/project.py src/paradev/cli.py tests/test_project.py tests/test_build_manifest.py`
- CLI smoke: `rtk uv run paradev dependencies demos/assets/projects/minimal --module focus/GER_sample --kind requires --target idea:GER_industrial_spirit --json`
- Whitespace: `rtk git diff --check -- src/paradev/build/manifest.py src/paradev/build/__init__.py src/paradev/sdk/project.py src/paradev/cli.py tests/test_project.py tests/test_build_manifest.py docs/workflows/build-flow.md docs/progress/2026-06-07-0107-dependency-inspection.md`

## Linear

- `rtk command -v linear` still exits with status 1.
- Tool discovery for Linear issue management exposed Codex automation and GitHub tools only; no Linear connector is available in this session.

## Risks

- Dependency inspection reflects current build-graph edges only; richer graph traversal remains future work.
- Existing unrelated desktop, README, and script changes remain intentionally untouched.

## Next

- Feed localization, assets, diagnostics, source-map, and dependency inspection payloads into desktop/MCP surfaces once those clients consume live SDK data.
- Continue hardening first real game-family constraints after verifying HOI4 icon and sprite policy from game data.
