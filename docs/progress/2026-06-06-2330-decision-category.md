# Decision Category Progress

Date: 2026-06-06 23:30 CST

Linear: TAL-294 local continuation; live Linear sync unavailable

## Done

- Checked the local HOI4 install before implementing decision behavior; `launcher-settings.json` reports `rawVersion` `1.18.2.0`.
- Verified current HOI4 decision entries under `common/decisions/*.txt` and category definitions under `common/decisions/categories/*.txt`.
- Added TDD coverage for merging decision modules in one collection into a single category block.
- Added TDD coverage for `decision.category_mismatch` when a source category block does not match module `collection`.
- Added TDD coverage for `decision.missing_collection` so decision modules cannot silently drop output.
- Added a HOI4-specific `DecisionFamily` that keeps decision category merging out of the generic collection helper.
- Documented the decision source shape and emitted artifact path in the build-flow workflow.

## Verification

- Red: `rtk bash scripts/test.bash tests/test_project_build.py::test_hoi4_profile_merges_decisions_into_category_artifact tests/test_project_build.py::test_hoi4_profile_blocks_decision_category_mismatch -q`
- Red missing collection: `rtk bash scripts/test.bash tests/test_project_build.py::test_hoi4_profile_blocks_decision_without_collection -q`
- Green focused: `rtk bash scripts/test.bash tests/test_project_build.py::test_hoi4_profile_merges_decisions_into_category_artifact tests/test_project_build.py::test_hoi4_profile_blocks_decision_category_mismatch tests/test_project_build.py::test_hoi4_profile_blocks_decision_without_collection -q`
- Related: `rtk bash scripts/test.bash tests/test_project_build.py tests/test_simple_source_family.py tests/test_module_sources.py tests/test_artifact_writers.py -q`
- Full: `rtk bash scripts/test.bash`
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven-style: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/games/hoi4/__init__.py tests/test_project_build.py tests/test_project.py`
- CLI family smoke: `rtk uv run paradev families demos/assets/projects/minimal --json`
- CLI build smoke: `rtk uv run paradev build demos/assets/projects/minimal --json`
- Linear probe: `rtk command -v linear`
- Linear connector probe: `tool_search` for Linear issue tools
- Whitespace: `rtk git diff --check src/paradev/games/hoi4/__init__.py tests/test_project_build.py tests/test_project.py docs/workflows/build-flow.md docs/progress/2026-06-06-2330-decision-category.md`

## Risks Or Blockers

- Live Linear sync is still blocked because no Linear MCP tool is exposed and `linear` is not available on `PATH`.
- This slice emits decision entries, but category definition artifacts under `common/decisions/categories/` remain a later collection-descriptor/compiler slice.
- Existing local desktop, README, and script edits remain outside this slice.

## Next

- Add decision duplicate-id validation, then add category descriptor PDX emission under `common/decisions/categories/`.
