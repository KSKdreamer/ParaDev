# Decision Category Localization Progress

Date: 2026-06-06 23:56 CST

Linear: TAL-294 local continuation; live Linear sync unavailable

## Done

- Added TDD coverage for `collections/decision/<collection_id>/*.loc` emitting collection-owned localization artifacts.
- Added TDD coverage for `decision.category_missing_localization` when authored category localization omits `<collection_id>` or `<collection_id>_desc`.
- Loaded root-level collection `.loc` files through the generic localization loader.
- Included collection localization in project-wide duplicate-key checks, artifact input traceability, `localization.json`, and `source-map.json`.
- Updated the HOI4 decision family to emit category localization alongside category and decision PDX artifacts.
- Documented decision category localization authoring in the build-flow workflow.

## Verification

- Red: `rtk bash scripts/test.bash tests/test_project_build.py::test_hoi4_profile_emits_decision_category_localization_artifact tests/test_project_build.py::test_hoi4_profile_blocks_missing_decision_category_localization_keys tests/test_project_build.py::test_hoi4_profile_manifest_includes_decision_category_localization_rows -q`
- Green: `rtk bash scripts/test.bash tests/test_project_build.py::test_hoi4_profile_emits_decision_category_localization_artifact tests/test_project_build.py::test_hoi4_profile_blocks_missing_decision_category_localization_keys tests/test_project_build.py::test_hoi4_profile_manifest_includes_decision_category_localization_rows -q`
- Related: `rtk bash scripts/test.bash tests/test_project_build.py tests/test_project.py tests/test_build_manifest.py tests/test_build_records.py tests/test_build_loaders.py tests/test_module_sources.py tests/test_simple_source_family.py -q`
- Full: `rtk bash scripts/test.bash`
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven-style: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build src/paradev/games/hoi4/__init__.py tests/test_project_build.py`
- CLI family smoke: `rtk uv run paradev families demos/assets/projects/minimal --json`
- CLI build smoke: `rtk uv run paradev build demos/assets/projects/minimal --json`
- Linear probe: `rtk command -v linear`
- Linear connector probe: `tool_search` for Linear issue tools

## Risks Or Blockers

- Live Linear sync is still blocked because no Linear MCP tool is exposed and `linear` is not available on `PATH`.
- Collection localization is root-level `*.loc` only for now; nested collection localization slots can follow if another family needs them.
- Existing local desktop, README, and script edits remain outside this slice.

## Next

- Add first asset-family proof for ideas or achievements after refreshing local HOI4 path and icon behavior.
