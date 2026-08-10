# Slot Loader Roles Progress

Date: 2026-06-06 22:38 CST

Linear: TAL-294 local continuation; live Linear sync unavailable

## Done

- Added TDD coverage for custom slot names with explicit loader roles in `load_module_sources(...)`.
- Updated the custom family build test so a registered `event` family compiles `body.txt` through `Slot(kind="pdx")`.
- Added optional `Slot.kind` and exposed it in family inspection payloads when declared.
- Threaded family slot declarations from discovery into `load_module_sources(...)`.
- Updated the source loader to combine existing default slot names with explicit `pdx`, `loc`, and `copy` role annotations.
- Documented loader roles in the final architecture and build-flow workflow.

## Verification

- Red: `rtk bash scripts/test.bash tests/test_module_sources.py::test_load_module_sources_uses_slot_loader_roles tests/test_project.py::test_project_families_prefers_family_source_slot_contracts tests/test_project_build.py::test_project_build_uses_registered_family_source_slots -q`
- Green: `rtk bash scripts/test.bash tests/test_module_sources.py::test_load_module_sources_uses_slot_loader_roles tests/test_project.py::test_project_families_prefers_family_source_slot_contracts tests/test_project_build.py::test_project_build_uses_registered_family_source_slots -q`
- `rtk bash scripts/test.bash tests/test_build_slots.py tests/test_module_sources.py tests/test_project.py tests/test_project_build.py tests/test_simple_source_family.py tests/test_build_manifest.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/slots.py src/paradev/build/loaders.py src/paradev/build/discovery.py src/paradev/build/registry.py tests/test_module_sources.py tests/test_project.py tests/test_project_build.py`
- `rtk uv run paradev families demos/assets/projects/minimal --json`
- `rtk uv run paradev build demos/assets/projects/minimal --json`
- `rtk git diff --check src/paradev/build/slots.py src/paradev/build/loaders.py src/paradev/build/discovery.py src/paradev/build/registry.py tests/test_module_sources.py tests/test_project.py tests/test_project_build.py docs/goals/final-architecture.md docs/workflows/build-flow.md docs/progress/2026-06-06-2238-slot-loader-roles.md`

## Risks Or Blockers

- Live Linear sync is still blocked because no Linear MCP tool is exposed and `linear` is not available on `PATH`.
- `Slot.kind` currently covers the generic loaders available in this slice: `pdx`, `loc`, and `copy`.
- Existing local desktop and README edits remain outside this slice.

## Next

- Start the next generic compiler slice by making family validation and metadata contracts inspectable without adding new author-facing concepts.
