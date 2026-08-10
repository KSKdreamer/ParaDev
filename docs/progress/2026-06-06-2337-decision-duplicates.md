# Decision Duplicate Diagnostics Progress

Date: 2026-06-06 23:37 CST

Linear: TAL-294 local continuation; live Linear sync unavailable

## Done

- Added TDD coverage for duplicate HOI4 decision ids across modules.
- Added TDD coverage for duplicate decision ids inside one PDX source file.
- Added parser-span-backed `decision.duplicate_id` diagnostics to the HOI4 `DecisionFamily`.
- Kept duplicate decision semantics inside `games/hoi4` instead of the generic collection helper.
- Documented `decision.duplicate_id` in the build-flow workflow.

## Verification

- Red duplicates: `rtk bash scripts/test.bash tests/test_project_build.py::test_hoi4_profile_blocks_duplicate_decision_ids tests/test_project_build.py::test_hoi4_profile_blocks_duplicate_decision_ids_inside_one_source -q`
- Green focused: `rtk bash scripts/test.bash tests/test_project_build.py::test_hoi4_profile_merges_decisions_into_category_artifact tests/test_project_build.py::test_hoi4_profile_blocks_decision_category_mismatch tests/test_project_build.py::test_hoi4_profile_blocks_duplicate_decision_ids tests/test_project_build.py::test_hoi4_profile_blocks_duplicate_decision_ids_inside_one_source tests/test_project_build.py::test_hoi4_profile_blocks_decision_without_collection -q`
- Related: `rtk bash scripts/test.bash tests/test_project_build.py tests/test_project.py tests/test_simple_source_family.py -q`
- Full: `rtk bash scripts/test.bash`
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven-style: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/games/hoi4/__init__.py tests/test_project_build.py`
- CLI family smoke: `rtk uv run paradev families demos/assets/projects/minimal --json`
- CLI build smoke: `rtk uv run paradev build demos/assets/projects/minimal --json`
- Linear probe: `rtk command -v linear`
- Linear connector probe: `tool_search` for Linear issue tools
- Whitespace: `rtk git diff --check src/paradev/games/hoi4/__init__.py tests/test_project_build.py docs/workflows/build-flow.md docs/progress/2026-06-06-2337-decision-duplicates.md`

## Risks Or Blockers

- Live Linear sync is still blocked because no Linear MCP tool is exposed and `linear` is not available on `PATH`.
- Decision category descriptor artifacts under `common/decisions/categories/` remain a later collection-descriptor/compiler slice.
- Existing local desktop, README, and script edits remain outside this slice.

## Next

- Add decision category descriptor PDX emission under `common/decisions/categories/`.
