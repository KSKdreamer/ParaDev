# Required Settings Contracts Progress

Date: 2026-06-06 22:54 CST

Linear: TAL-294 local continuation; live Linear sync unavailable

## Done

- Added TDD coverage for required non-routed settings in the family inspection payload.
- Added TDD coverage for blocking diagnostics when a module omits a required family setting.
- Added `required_settings` to generic simple, routed, and collection family helpers.
- Extended generic settings-contract diagnostics to report `family.missing_setting`.
- Updated the family inspection payload so required non-routed settings render with `required: true`.
- Documented required settings contracts in the final architecture and build-flow workflow.

## Verification

- Red: `rtk bash scripts/test.bash tests/test_project.py::test_project_families_prefers_family_source_slot_contracts tests/test_project_build.py::test_project_build_uses_registered_family_source_slots tests/test_project_build.py::test_project_build_requires_registered_family_settings -q`
- Green: `rtk bash scripts/test.bash tests/test_project.py::test_project_families_prefers_family_source_slot_contracts tests/test_project_build.py::test_project_build_uses_registered_family_source_slots tests/test_project_build.py::test_project_build_requires_registered_family_settings -q`
- Related: `rtk bash scripts/test.bash tests/test_project.py tests/test_project_build.py tests/test_simple_source_family.py tests/test_module_sources.py tests/test_build_manifest.py tests/test_build_slots.py -q`
- Full: `rtk bash scripts/test.bash`
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven-style: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/families.py src/paradev/build/registry.py tests/test_project.py tests/test_project_build.py`
- CLI family smoke: `rtk uv run paradev families demos/assets/projects/minimal --json`
- CLI build smoke: `rtk uv run paradev build demos/assets/projects/minimal --json`
- Whitespace: `rtk git diff --check src/paradev/build/families.py src/paradev/build/registry.py tests/test_project.py tests/test_project_build.py docs/goals/final-architecture.md docs/workflows/build-flow.md docs/progress/2026-06-06-2254-required-settings-contracts.md`

## Risks Or Blockers

- Live Linear sync is still blocked because no Linear MCP tool is exposed and `linear` is not available on `PATH`.
- Required settings currently validate presence of a non-empty string value; richer type validation remains a future contract.
- Existing local desktop and README edits remain outside this slice.

## Next

- Start the next generic compiler slice by giving family authors a small typed hook for module-level settings normalization before artifact planning.
