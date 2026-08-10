# 2026-06-07 03:00 CST - Dependency Source Filter Normalization

## Done

- Normalized dependency source filters so bare module ids and `module:<id>` source values resolve to the same module-owned dependency rows.
- Covered SDK `Project.dependencies(...)` for bare `source` and prefixed `module_id` inputs.
- Covered CLI `paradev dependencies --module module:<id>` and `--source <bare-module-id>` inputs.
- Documented the dependency filter normalization in the build-flow guide.

## Verification

- Red first: `rtk bash scripts/test.bash tests/test_project.py::test_project_dependencies_returns_filtered_manifest_payload_without_writing -q` failed because `module_id="module:focus/GER_sample"` returned no dependencies.
- Red first: `rtk bash scripts/test.bash tests/test_project.py::test_project_cli_filters_dependency_manifest_json -q` failed because `--module module:focus/GER_sample` returned no dependencies.
- Focused green: `rtk bash scripts/test.bash tests/test_project.py::test_project_dependencies_returns_filtered_manifest_payload_without_writing -q` passed 1 test.
- Focused green: `rtk bash scripts/test.bash tests/test_project.py::test_project_cli_filters_dependency_manifest_json -q` passed 1 test.
- Related suite: `rtk bash scripts/test.bash tests/test_project.py tests/test_build_manifest.py -q` passed 38 tests.
- Full suite: `rtk bash scripts/test.bash` passed 168 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py tests/test_project.py`
- CLI smoke: `rtk uv run paradev dependencies demos/assets/projects/minimal --source focus/GER_sample --kind requires --target idea:GER_industrial_spirit --json`
- Whitespace: `rtk git diff --check -- src/paradev/sdk/project.py tests/test_project.py docs/workflows/build-flow.md docs/progress/2026-06-07-0300-dependency-source-filter-normalization.md`

## Linear

- `rtk command -v linear` exits with status 1.
- Tool discovery for Linear issue management exposed Codex automation and GitHub tools only; no Linear connector is available in this session.

## Risks

- Dependency sources remain manifest-owned strings; this slice only normalizes module-owned shorthand filters.
- Existing unrelated desktop, README, and script changes remain intentionally untouched.

## Next

- Continue toward generic module compilation entry points and collection-aware dependency ownership when collection-owned edges are introduced.
