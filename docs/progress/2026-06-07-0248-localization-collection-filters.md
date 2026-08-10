# 2026-06-07 02:48 CST - Localization Collection Filters

## Done

- Added SDK filtering for `Project.localization(collection_id=...)`.
- Added `paradev localization --collection <collection_id>` for collection-owned localization rows.
- Covered collection category localization through the default HOI4 profile instead of a patched test registry.
- Documented the collection localization filter in the build-flow guide.

## Verification

- Red first: `rtk bash scripts/test.bash tests/test_project_build.py::test_hoi4_profile_manifest_includes_decision_category_localization_rows -q` failed because `Project.localization()` did not accept `collection_id`.
- Red first: `rtk bash scripts/test.bash tests/test_project.py::test_project_cli_filters_collection_localization_manifest_json -q` failed because `paradev localization` did not accept `--collection`.
- Focused green: `rtk bash scripts/test.bash tests/test_project_build.py::test_hoi4_profile_manifest_includes_decision_category_localization_rows -q` passed 1 test.
- Focused green: `rtk bash scripts/test.bash tests/test_project.py::test_project_cli_filters_collection_localization_manifest_json -q` passed 1 test.
- Related suite: `rtk bash scripts/test.bash tests/test_project.py tests/test_project_build.py tests/test_build_manifest.py -q` passed 83 tests.
- Full suite: `rtk bash scripts/test.bash` passed 167 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py src/paradev/cli.py tests/test_project.py tests/test_project_build.py`
- CLI smoke: `rtk uv run paradev localization demos/assets/projects/minimal --collection GER_main --json`
- Whitespace: `rtk git diff --check -- src/paradev/sdk/project.py src/paradev/cli.py tests/test_project.py tests/test_project_build.py docs/workflows/build-flow.md docs/progress/2026-06-07-0248-localization-collection-filters.md`

## Linear

- `rtk command -v linear` exits with status 1.
- Tool discovery for Linear issue management exposed Codex automation and GitHub tools only; no Linear connector is available in this session.

## Risks

- Localization indexing remains language/key based, because duplicate detection and lookup are language/key concerns rather than owner concerns.
- Existing unrelated desktop, README, and script changes remain intentionally untouched.

## Next

- Continue collection parity on diagnostics and dependency-facing inspection, then move toward generic module compilation entry points.
