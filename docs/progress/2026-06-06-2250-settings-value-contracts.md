# Settings Value Contracts Progress

Date: 2026-06-06 22:50 CST

Linear: TAL-294 local continuation; live Linear sync unavailable

## Done

- Added TDD coverage for allowed `settings_values` in the family inspection payload.
- Added TDD coverage for blocking diagnostics when a module uses an unsupported family setting value.
- Added `settings_values` to generic simple, routed, and collection family helpers.
- Added generic settings-contract diagnostics through family `check(...)` methods.
- Updated the family inspection payload so settings contracts include declared allowed values.
- Documented settings value contracts in the final architecture and build-flow workflow.

## Verification

- Red: `rtk bash scripts/test.bash tests/test_project.py::test_project_families_prefers_family_source_slot_contracts tests/test_project_build.py::test_project_build_uses_registered_family_source_slots tests/test_project_build.py::test_project_build_validates_registered_family_setting_values -q`
- Green: `rtk bash scripts/test.bash tests/test_project.py::test_project_families_prefers_family_source_slot_contracts tests/test_project_build.py::test_project_build_uses_registered_family_source_slots tests/test_project_build.py::test_project_build_validates_registered_family_setting_values -q`
- `rtk bash scripts/test.bash tests/test_project.py tests/test_project_build.py tests/test_simple_source_family.py tests/test_module_sources.py tests/test_build_manifest.py tests/test_build_slots.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/families.py src/paradev/build/registry.py tests/test_project.py tests/test_project_build.py`
- `rtk uv run paradev families demos/assets/projects/minimal --json`
- `rtk uv run paradev build demos/assets/projects/minimal --json`
- `rtk git diff --check src/paradev/build/families.py src/paradev/build/registry.py tests/test_project.py tests/test_project_build.py docs/goals/final-architecture.md docs/workflows/build-flow.md docs/progress/2026-06-06-2250-settings-value-contracts.md`

## Risks Or Blockers

- Live Linear sync is still blocked because no Linear MCP tool is exposed and `linear` is not available on `PATH`.
- This slice validates explicit allowed values only; required non-routed settings remain a future contract.
- Existing local desktop and README edits remain outside this slice.

## Next

- Start the next generic compiler slice by adding required non-routed setting diagnostics or source-slot requiredness into family inspection examples.
