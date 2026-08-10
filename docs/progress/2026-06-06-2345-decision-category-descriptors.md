# Decision Category Descriptor Progress

Date: 2026-06-06 23:45 CST

Linear: TAL-294 local continuation; live Linear sync unavailable

## Done

- Added TDD coverage for `collections/decision/<collection_id>/def.pdx` emitting `common/decisions/categories/<collection_id>.txt`.
- Added TDD coverage for `decision.category_descriptor_mismatch` when a descriptor top-level key does not match the collection id.
- Added a generic collection source bundle so collection descriptors can carry parsed PDX payloads without exposing payloads in JSON views.
- Preserved collection descriptor inputs in build input traceability to avoid untracked-source warnings.
- Updated the HOI4 `DecisionFamily` to emit category descriptors before merged decision entries.
- Documented decision category descriptor authoring in the build-flow workflow.

## Verification

- Red descriptor tests: `rtk bash scripts/test.bash tests/test_project_build.py::test_hoi4_profile_emits_decision_category_descriptor_artifact tests/test_project_build.py::test_hoi4_profile_blocks_decision_category_descriptor_mismatch -q`
- Green descriptor tests: `rtk bash scripts/test.bash tests/test_project_build.py::test_hoi4_profile_emits_decision_category_descriptor_artifact tests/test_project_build.py::test_hoi4_profile_blocks_decision_category_descriptor_mismatch -q`
- Related: `rtk bash scripts/test.bash tests/test_project_build.py tests/test_project.py tests/test_build_loaders.py tests/test_build_records.py tests/test_build_manifest.py -q`
- Full: `rtk bash scripts/test.bash`
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven-style: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build src/paradev/games/hoi4/__init__.py tests/test_project_build.py`
- CLI family smoke: `rtk uv run paradev families demos/assets/projects/minimal --json`
- CLI build smoke: `rtk uv run paradev build demos/assets/projects/minimal --json`
- Linear probe: `rtk command -v linear`
- Linear connector probe: `tool_search` for Linear issue tools
- Whitespace: `rtk git diff --check src/paradev/build/__init__.py src/paradev/build/discovery.py src/paradev/build/loaders.py src/paradev/build/records.py src/paradev/games/hoi4/__init__.py tests/test_project_build.py docs/workflows/build-flow.md docs/progress/2026-06-06-2345-decision-category-descriptors.md`

## Risks Or Blockers

- Live Linear sync is still blocked because no Linear MCP tool is exposed and `linear` is not available on `PATH`.
- Collection descriptors currently parse `def.pdx`; richer collection-owned localization/copy slots can follow when a family needs them.
- Existing local desktop, README, and script edits remain outside this slice.

## Next

- Add decision category localization requirements or move to the first idea/achievement asset-family slice.
