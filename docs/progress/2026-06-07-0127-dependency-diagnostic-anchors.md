# 2026-06-07 01:27 CST - Dependency Diagnostic Anchors

## Done

- Anchored build dependency diagnostics to `meta.yaml`.
- Covered invalid dependency metadata, missing project-local dependency targets, and `after` dependency cycles.
- Updated the build-flow guide so users know dependency metadata errors point back to `meta.yaml`.

## Verification

- Red first: `rtk bash scripts/test.bash tests/test_build_records.py::test_build_result_reports_invalid_module_dependencies_as_blocking_diagnostics tests/test_build_records.py::test_build_result_reports_missing_project_local_dependency_targets tests/test_build_records.py::test_build_result_reports_module_after_cycles_as_blocking_diagnostics -q` failed because the diagnostics had no `source_path`.
- Focused green: `rtk bash scripts/test.bash tests/test_build_records.py::test_build_result_reports_invalid_module_dependencies_as_blocking_diagnostics tests/test_build_records.py::test_build_result_reports_missing_project_local_dependency_targets tests/test_build_records.py::test_build_result_reports_module_after_cycles_as_blocking_diagnostics -q`
- Related suite: `rtk bash scripts/test.bash tests/test_build_records.py tests/test_build_manifest.py tests/test_project.py tests/test_project_build.py -q` passed 88 tests.
- Full suite: `rtk bash scripts/test.bash` passed 142 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/records.py tests/test_build_records.py`
- CLI smoke: `rtk uv run paradev diagnostics demos/assets/projects/minimal --json`
- Whitespace: `rtk git diff --check -- src/paradev/build/records.py tests/test_build_records.py docs/workflows/build-flow.md docs/progress/2026-06-07-0127-dependency-diagnostic-anchors.md`

## Linear

- `rtk command -v linear` still exits with status 1.
- Tool discovery for Linear issue management exposed GitHub and Codex automation tools only; no Linear connector is available in this session.

## Risks

- Dependency diagnostics now point to the metadata file rather than a key-level span; key-level YAML spans remain future parser work.
- Existing unrelated desktop, README, and script changes remain intentionally untouched.

## Next

- Continue improving diagnostics so blocked builds tell users exactly which authored source file to fix.
- Keep dependency graph contracts ready for future game-reference indexes.
