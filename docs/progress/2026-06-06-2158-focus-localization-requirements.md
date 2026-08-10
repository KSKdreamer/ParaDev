# Focus Localization Requirements Progress

Date: 2026-06-06 21:58 CST

Linear: TAL-294

## Done

- Added blocking `focus.missing_localization` diagnostics for focus modules that provide localization entries but omit `<focus_id>` or `<focus_id>_desc`.
- Anchored missing-localization diagnostics to the focus id source span while keeping PDX-only modules allowed in the current scaffold.
- Covered the collection family helper and the default HOI4 profile build path.
- Updated the build-flow workflow with the current focus localization requirement and its PDX-only exception.

## Verification

- `rtk bash scripts/test.bash tests/test_simple_source_family.py::test_collection_pdx_family_reports_missing_focus_localization_keys tests/test_project_build.py::test_hoi4_profile_blocks_missing_focus_localization_keys -q`
- `rtk bash scripts/test.bash tests/test_simple_source_family.py tests/test_project_build.py tests/test_project.py tests/test_sdk_examples.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/families.py tests/test_simple_source_family.py tests/test_project_build.py`
- `rtk uv run paradev build demos/assets/projects/minimal --json`

## Risks Or Blockers

- Live Linear sync is still pending because no Linear MCP tool or `linear` CLI is available in this session.
- Modules with no localization source are still allowed; a stronger required-localization policy should wait for import and scaffold behavior to settle.
- Existing local desktop and README edits remain outside this first-slot compiler slice.

## Next

- Add a project localization index or define replace/shadow semantics before expanding required-key validation beyond focus modules.
