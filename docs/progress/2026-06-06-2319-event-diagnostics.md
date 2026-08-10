# Event Diagnostics Progress

Date: 2026-06-06 23:19 CST

Linear: TAL-294 local continuation; live Linear sync unavailable

## Done

- Added TDD coverage for duplicate HOI4 event ids across modules.
- Added TDD coverage for duplicate event ids inside one PDX source file.
- Added TDD coverage for event id namespace mismatch against the event collection id.
- Added a profile-specific `EventFamily` that extends generic collection source output with HOI4 event diagnostics.
- Kept event checks in `games/hoi4` instead of moving HOI4 event semantics into the generic collection helper.
- Documented duplicate event id and namespace diagnostics in the build-flow workflow.

## Verification

- Red duplicate cross-module/namespace: `rtk bash scripts/test.bash tests/test_project_build.py::test_hoi4_profile_blocks_duplicate_event_ids tests/test_project_build.py::test_hoi4_profile_blocks_event_namespace_mismatch -q`
- Red duplicate same-source: `rtk bash scripts/test.bash tests/test_project_build.py::test_hoi4_profile_blocks_duplicate_event_ids_inside_one_source -q`
- Green focused: `rtk bash scripts/test.bash tests/test_project_build.py::test_hoi4_profile_blocks_duplicate_event_ids tests/test_project_build.py::test_hoi4_profile_blocks_duplicate_event_ids_inside_one_source tests/test_project_build.py::test_hoi4_profile_blocks_event_namespace_mismatch -q`
- Related: `rtk bash scripts/test.bash tests/test_project_build.py tests/test_project.py tests/test_simple_source_family.py tests/test_build_manifest.py tests/test_module_sources.py -q`
- Full: `rtk bash scripts/test.bash`
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven-style: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/games/hoi4/__init__.py tests/test_project_build.py`
- CLI family smoke: `rtk uv run paradev families demos/assets/projects/minimal --json`
- CLI build smoke: `rtk uv run paradev build demos/assets/projects/minimal --json`
- Linear probe: `rtk command -v linear`
- Whitespace: `rtk git diff --check src/paradev/games/hoi4/__init__.py tests/test_project_build.py docs/workflows/build-flow.md docs/progress/2026-06-06-2319-event-diagnostics.md`

## Risks Or Blockers

- Live Linear sync is still blocked because no Linear MCP tool is exposed and `linear` is not available on `PATH`.
- Event diagnostics currently cover `country_event` and `news_event`; broader HOI4 event forms can be added when fixtures demand them.
- Existing local desktop, README, and script edits remain outside this slice.

## Next

- Add event localization completeness checks, or move to decision category collection compilation.
