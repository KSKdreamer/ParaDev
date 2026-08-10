# 2026-06-07 02:11 CST - Collection Source Slots

## Done

- Added `collection_source_slots` to collection-owning family contracts so descriptor files can use family-declared names.
- Routed project collection discovery through the selected build registry, matching descriptor slots before loading collection payloads.
- Preserved collection localization source attribution with the declared slot name for family, localization, and future MCP/GUI clients.
- Documented collection descriptor source slots in the build-flow guide.

## Verification

- Red first: `rtk bash scripts/test.bash tests/test_project_build.py::test_project_build_uses_registered_collection_source_slots -q` failed because `CollectionSourceFamily` did not accept `collection_source_slots`.
- Focused green: `rtk bash scripts/test.bash tests/test_module_sources.py::test_load_collection_sources_uses_slot_loader_roles tests/test_project_build.py::test_project_build_uses_registered_collection_source_slots tests/test_project.py::test_project_families_exposes_collection_source_slot_contracts -q` passed 3 tests.
- Related suite: `rtk bash scripts/test.bash tests/test_module_sources.py tests/test_project_build.py tests/test_project.py tests/test_build_manifest.py tests/test_simple_source_family.py -q` passed 96 tests.
- Full suite: `rtk bash scripts/test.bash` passed 159 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/loaders.py src/paradev/build/discovery.py src/paradev/build/registry.py src/paradev/build/families.py src/paradev/build/records.py src/paradev/build/manifest.py src/paradev/sdk/project.py tests/test_module_sources.py tests/test_project_build.py tests/test_project.py`
- SDK smoke: `rtk uv run python -c "from paradev.build import BuildRegistry, CollectionSourceFamily, Slot; ..."` confirmed `collection_source_slots` in the family payload with `pdx` and `loc` loader kinds.
- Whitespace: `rtk git diff --check -- src/paradev/build/loaders.py src/paradev/build/discovery.py src/paradev/build/registry.py src/paradev/build/families.py src/paradev/build/records.py src/paradev/build/manifest.py src/paradev/build/__init__.py src/paradev/sdk/project.py tests/test_module_sources.py tests/test_project_build.py tests/test_project.py docs/workflows/build-flow.md docs/progress/2026-06-07-0211-collection-source-slots.md`

## Linear

- `rtk command -v linear` exits with status 1.
- Tool discovery for Linear issue management exposed Codex automation and GitHub tools only; no Linear connector is available in this session.

## Risks

- Collection descriptor slots currently cover PDX and localization loader roles. Static copy sources remain module-owned until a collection asset family needs them.
- Existing unrelated desktop, README, and script changes remain intentionally untouched.

## Next

- Continue moving family contracts into registry-owned capability payloads so desktop, MCP, and CLI surfaces do not hard-code HOI4 source layout.
