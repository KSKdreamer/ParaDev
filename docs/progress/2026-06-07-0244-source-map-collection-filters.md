# 2026-06-07 02:44 CST - Source Map Collection Filters

## Done

- Added SDK filtering for `Project.source_map(collection_id=...)`.
- Added `paradev source-map --collection <collection_id>` for collection-owned source traceability.
- Updated the source-map manifest index to include collection-owned source rows using the same owner/slot shape as module-owned rows.
- Documented the collection source-map filter and owner/slot source-map index in the build-flow guide.

## Verification

- Red first: `rtk bash scripts/test.bash tests/test_project_build.py::test_project_build_tracks_registered_collection_copy_source_slots -q` failed because `Project.source_map()` did not accept `collection_id`.
- Red first: `rtk bash scripts/test.bash tests/test_project.py::test_project_cli_filters_collection_source_map_manifest_json -q` failed because `paradev source-map` did not accept `--collection`.
- Focused green: `rtk bash scripts/test.bash tests/test_project_build.py::test_project_build_tracks_registered_collection_copy_source_slots -q` passed 1 test.
- Focused green: `rtk bash scripts/test.bash tests/test_project.py::test_project_cli_filters_collection_source_map_manifest_json -q` passed 1 test.
- Related suite: `rtk bash scripts/test.bash tests/test_project.py tests/test_project_build.py tests/test_build_manifest.py -q` passed 82 tests.
- Full suite: `rtk bash scripts/test.bash` passed 166 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py src/paradev/cli.py src/paradev/build/manifest.py tests/test_project.py tests/test_project_build.py`
- CLI smoke: `rtk uv run paradev source-map demos/assets/projects/minimal --collection GER_main --json`
- Whitespace: `rtk git diff --check -- src/paradev/sdk/project.py src/paradev/cli.py src/paradev/build/manifest.py tests/test_project.py tests/test_project_build.py docs/workflows/build-flow.md docs/progress/2026-06-07-0244-source-map-collection-filters.md`

## Linear

- `rtk command -v linear` exits with status 1.
- Tool discovery for Linear issue management exposed Codex automation and GitHub tools only; no Linear connector is available in this session.

## Risks

- Source-map collection filters select rows with at least one matching resolved source entry; they do not prune non-matching sibling sources inside the returned artifact row.
- Existing unrelated desktop, README, and script changes remain intentionally untouched.

## Next

- Continue collection parity work on remaining inspection surfaces, then move toward generic module compilation entry points.
