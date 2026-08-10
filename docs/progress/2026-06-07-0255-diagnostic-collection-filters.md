# 2026-06-07 02:55 CST - Diagnostic Collection Filters

## Done

- Added optional `collection_id` to build diagnostics and diagnostic JSON payloads.
- Added SDK filtering for `Project.diagnostics(collection_id=...)`.
- Added `paradev diagnostics --collection <collection_id>` for collection-owned validation errors.
- Resolved collection diagnostic sources through collection descriptor roots so diagnostics point at authored collection files.
- Propagated collection identity through generic collection metadata, PDX, localization, and copy loader diagnostics.
- Documented collection diagnostic filtering in the build-flow guide.

## Verification

- Red first: `rtk bash scripts/test.bash tests/test_project_build.py::test_hoi4_profile_blocks_missing_decision_category_localization_keys -q` failed because `Project.diagnostics()` did not accept `collection_id`.
- Red first: `rtk bash scripts/test.bash tests/test_project.py::test_project_cli_filters_collection_diagnostics_manifest_json -q` failed because `paradev diagnostics` did not accept `--collection`.
- Focused green: `rtk bash scripts/test.bash tests/test_project_build.py::test_hoi4_profile_blocks_missing_decision_category_localization_keys -q` passed 1 test.
- Focused green: `rtk bash scripts/test.bash tests/test_project.py::test_project_cli_filters_collection_diagnostics_manifest_json -q` passed 1 test.
- Related suite: `rtk bash scripts/test.bash tests/test_project.py tests/test_project_build.py tests/test_build_manifest.py tests/test_module_sources.py -q` passed 88 tests.
- Full suite: `rtk bash scripts/test.bash` passed 168 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/records.py src/paradev/build/loaders.py src/paradev/build/manifest.py src/paradev/games/hoi4/__init__.py src/paradev/sdk/project.py src/paradev/cli.py tests/test_project.py tests/test_project_build.py`
- CLI smoke: `rtk uv run paradev diagnostics demos/assets/projects/minimal --collection GER_main --json`
- Whitespace: `rtk git diff --check -- src/paradev/build/records.py src/paradev/build/loaders.py src/paradev/build/manifest.py src/paradev/games/hoi4/__init__.py src/paradev/sdk/project.py src/paradev/cli.py tests/test_project.py tests/test_project_build.py docs/workflows/build-flow.md docs/progress/2026-06-07-0255-diagnostic-collection-filters.md`

## Linear

- `rtk command -v linear` exits with status 1.
- Tool discovery for Linear issue management exposed Codex automation and GitHub tools only; no Linear connector is available in this session.

## Risks

- Diagnostic indexing remains severity/code based because issue triage usually starts from error class and severity.
- Existing unrelated desktop, README, and script changes remain intentionally untouched.

## Next

- Continue collection parity on dependency-facing inspection and generic module compilation entry points.
