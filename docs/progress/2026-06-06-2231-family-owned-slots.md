# Family-Owned Slots Progress

Date: 2026-06-06 22:31 CST

Linear: TAL-294 local continuation; live Linear sync unavailable

## Done

- Added TDD coverage for family-specific `source_slots` in `Project.families(...)`.
- Added TDD coverage for registry-backed discovery with a custom `event` family that loads `script.txt` instead of `def.pdx`.
- Added `source_slots` fields to simple, routed, and collection family helpers.
- Added `BuildRegistry.source_slots_for(...)` and `source_slots_by_family()` so inspection and discovery use the same family contract.
- Updated `Project.build(...)` to discover modules with the selected registry when modules are not supplied.
- Updated the build-flow workflow with the family-owned slot behavior.

## Verification

- Red: `rtk bash scripts/test.bash tests/test_project.py::test_project_families_prefers_family_source_slot_contracts tests/test_project_build.py::test_project_build_uses_registered_family_source_slots -q`
- Green: `rtk bash scripts/test.bash tests/test_project.py::test_project_families_prefers_family_source_slot_contracts tests/test_project_build.py::test_project_build_uses_registered_family_source_slots -q`
- `rtk bash scripts/test.bash tests/test_project.py tests/test_project_build.py tests/test_simple_source_family.py tests/test_build_manifest.py tests/test_build_slots.py tests/test_module_sources.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/families.py src/paradev/build/registry.py src/paradev/build/discovery.py src/paradev/sdk/project.py tests/test_project.py tests/test_project_build.py`
- `rtk uv run paradev families demos/assets/projects/minimal --json`
- `rtk uv run paradev build demos/assets/projects/minimal --json`
- `rtk git diff --check src/paradev/build/families.py src/paradev/build/registry.py src/paradev/build/discovery.py src/paradev/sdk/project.py tests/test_project.py tests/test_project_build.py docs/workflows/build-flow.md docs/progress/2026-06-06-2231-family-owned-slots.md`

## Risks Or Blockers

- Live Linear sync is still blocked because no Linear MCP tool is exposed and `linear` is not available on `PATH`.
- Direct `Project.discover_modules()` keeps the generic default slots unless a profile or registry is supplied, preserving the current SDK behavior for callers that only want raw source discovery.
- Existing local desktop and README edits remain outside this slice.

## Next

- Start the next generic module compiler slice by exposing family-owned validation metadata without increasing the beginner-facing module model.
