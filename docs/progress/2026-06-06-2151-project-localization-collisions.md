# Project Localization Collisions Progress

Date: 2026-06-06 21:51 CST

Linear: TAL-294

## Done

- Added blocking `loc.project_duplicate_key` diagnostics for duplicate canonical localization keys across discovered project modules.
- Kept module-local duplicate diagnostics in the loader and project-level duplicate diagnostics in build result validation.
- Changed `localization.json` duplicate state from module-local to project-wide.
- Covered synthetic build records, localization manifest rows, and the default HOI4 profile build path.
- Documented the project-wide localization collision policy in the build-flow workflow.

## Verification

- `rtk bash scripts/test.bash tests/test_build_records.py::test_build_result_reports_project_level_duplicate_localization_keys -q`
- `rtk bash scripts/test.bash tests/test_build_manifest.py::test_manifest_payloads_mark_project_level_duplicate_localization_rows -q`
- `rtk bash scripts/test.bash tests/test_project_build.py::test_hoi4_profile_blocks_project_level_duplicate_localization_keys -q`
- `rtk bash scripts/test.bash tests/test_build_records.py tests/test_build_manifest.py tests/test_project_build.py tests/test_project.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/records.py src/paradev/build/manifest.py tests/test_build_records.py tests/test_build_manifest.py tests/test_project_build.py`
- `rtk uv run paradev build demos/assets/projects/minimal --json`

## Risks Or Blockers

- Live Linear sync is still pending because no Linear MCP tool or `linear` CLI is available in this session.
- There is no `replace` or intentionally-shadowed localization policy yet, so all cross-module duplicate canonical keys are blocking.
- Existing local desktop and README edits remain outside this build validation slice.

## Next

- Start the next first-slot compiler surface by defining required localization keys for simple families or move into a persistent localization index once replace semantics are designed.
