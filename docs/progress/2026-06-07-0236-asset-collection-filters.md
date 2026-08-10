# 2026-06-07 02:36 CST - Asset Collection Filters

## Done

- Added SDK filtering for `Project.assets(collection_id=...)`.
- Added `paradev assets --collection <collection_id>` for collection-owned copy asset inspection.
- Updated the asset manifest index to include collection-owned rows using the same owner/slot shape as module-owned rows.
- Documented the collection asset filter and owner/slot asset index in the build-flow guide.

## Verification

- Red first: `rtk bash scripts/test.bash tests/test_project_build.py::test_project_build_tracks_registered_collection_copy_source_slots -q` failed because `Project.assets()` did not accept `collection_id`.
- Red first: `rtk bash scripts/test.bash tests/test_project.py::test_project_cli_filters_collection_asset_manifest_json -q` failed because `paradev assets` did not accept `--collection`.
- Focused green: `rtk bash scripts/test.bash tests/test_project_build.py::test_project_build_tracks_registered_collection_copy_source_slots -q` passed 1 test.
- Focused green: `rtk bash scripts/test.bash tests/test_project.py::test_project_cli_filters_collection_asset_manifest_json -q` passed 1 test.
- Related suite: `rtk bash scripts/test.bash tests/test_project.py tests/test_project_build.py tests/test_build_manifest.py -q` passed 81 tests.
- Full suite: `rtk bash scripts/test.bash` passed 165 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py src/paradev/cli.py src/paradev/build/manifest.py tests/test_project.py tests/test_project_build.py`
- CLI smoke: `rtk uv run paradev assets demos/assets/projects/minimal --collection GER_main --json`
- Whitespace: `rtk git diff --check -- src/paradev/sdk/project.py src/paradev/cli.py src/paradev/build/manifest.py tests/test_project.py tests/test_project_build.py docs/workflows/build-flow.md docs/progress/2026-06-07-0236-asset-collection-filters.md`

## Linear

- `rtk command -v linear` exits with status 1.
- Tool discovery for Linear issue management exposed Codex automation and GitHub tools only; no Linear connector is available in this session.

## Risks

- Default HOI4 collection copy slots remain opt-in at the family registry layer; this slice only exposes filtering and indexing for collection-owned assets once a family emits them.
- Existing unrelated desktop, README, and script changes remain intentionally untouched.

## Next

- Continue aligning collection-owned source-map/dependency surfaces where user-facing traceability is still module-centric.
