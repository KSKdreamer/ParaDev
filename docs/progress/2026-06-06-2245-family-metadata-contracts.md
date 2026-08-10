# Family Metadata Contracts Progress

Date: 2026-06-06 22:45 CST

Linear: TAL-294 local continuation; live Linear sync unavailable

## Done

- Added TDD coverage for metadata contracts in `Project.families(...)`.
- Added family-owned `metadata_keys` and `settings_keys` declarations to generic family helpers.
- Exposed per-family metadata contracts in the family inspection payload, including routed setting allowed values.
- Threaded family metadata keys into discovery and `load_module_sources(...)` so declared family keys do not produce unknown-key warnings.
- Documented metadata/settings contracts in the final architecture and build-flow workflow.

## Verification

- Red: `rtk bash scripts/test.bash tests/test_project.py::test_project_families_returns_profile_family_contracts tests/test_project.py::test_project_families_prefers_family_source_slot_contracts tests/test_project_build.py::test_project_build_uses_registered_family_source_slots -q`
- Green: `rtk bash scripts/test.bash tests/test_project.py::test_project_families_returns_profile_family_contracts tests/test_project.py::test_project_families_prefers_family_source_slot_contracts tests/test_project_build.py::test_project_build_uses_registered_family_source_slots -q`
- `rtk bash scripts/test.bash tests/test_project.py tests/test_project_build.py tests/test_module_sources.py tests/test_simple_source_family.py tests/test_build_manifest.py tests/test_build_slots.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/families.py src/paradev/build/registry.py src/paradev/build/loaders.py src/paradev/build/discovery.py src/paradev/sdk/project.py tests/test_project.py tests/test_project_build.py`
- `rtk uv run paradev families demos/assets/projects/minimal --json`
- `rtk uv run paradev build demos/assets/projects/minimal --json`
- `rtk git diff --check src/paradev/build/families.py src/paradev/build/registry.py src/paradev/build/loaders.py src/paradev/build/discovery.py src/paradev/sdk/project.py tests/test_project.py tests/test_project_build.py docs/goals/final-architecture.md docs/workflows/build-flow.md docs/progress/2026-06-06-2245-family-metadata-contracts.md`

## Risks Or Blockers

- Live Linear sync is still blocked because no Linear MCP tool is exposed and `linear` is not available on `PATH`.
- Settings contracts are inspectable in this slice; settings value validation beyond routed settings remains future work.
- Existing local desktop and README edits remain outside this slice.

## Next

- Start the next generic compiler slice by validating settings contracts where values are explicitly declared.
