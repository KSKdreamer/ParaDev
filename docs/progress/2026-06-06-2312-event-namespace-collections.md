# Event Namespace Collections Progress

Date: 2026-06-06 23:12 CST

Linear: TAL-294 local continuation; live Linear sync unavailable

## Done

- Added TDD coverage for a generic collection source family that aggregates non-focus PDX modules without focus diagnostics.
- Added TDD coverage for the HOI4 profile planning collection-owned event namespace artifacts.
- Added TDD coverage for the family inspection payload exposing the `event` collection family contract.
- Added `CollectionSourceFamily` for collection-owned PDX plus module-owned localization and static-copy side artifacts.
- Shared deterministic collection PDX artifact assembly between `CollectionPDXFamily` and `CollectionSourceFamily`.
- Registered the HOI4 `event` family with collection-owned `events/{collection_id}.txt` output and module fallback output.
- Documented event namespace output in the build-flow workflow.

## Verification

- Red: `rtk bash scripts/test.bash tests/test_simple_source_family.py::test_collection_source_family_emits_collection_pdx_without_focus_diagnostics tests/test_project_build.py::test_hoi4_profile_plans_event_namespace_collection_artifacts tests/test_project.py::test_project_families_returns_profile_family_contracts -q`
- Green: `rtk bash scripts/test.bash tests/test_simple_source_family.py::test_collection_source_family_emits_collection_pdx_without_focus_diagnostics tests/test_project_build.py::test_hoi4_profile_plans_event_namespace_collection_artifacts tests/test_project.py::test_project_families_returns_profile_family_contracts -q`
- Related: `rtk bash scripts/test.bash tests/test_simple_source_family.py tests/test_project_build.py tests/test_project.py tests/test_build_manifest.py tests/test_module_sources.py -q`
- Full: `rtk bash scripts/test.bash`
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven-style: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/__init__.py src/paradev/build/families.py src/paradev/build/registry.py src/paradev/games/hoi4/__init__.py tests/test_simple_source_family.py tests/test_project_build.py tests/test_project.py`
- CLI family smoke: `rtk uv run paradev families demos/assets/projects/minimal --json`
- CLI build smoke: `rtk uv run paradev build demos/assets/projects/minimal --json`
- Linear probe: `rtk command -v linear`
- Whitespace: `rtk git diff --check src/paradev/build/__init__.py src/paradev/build/families.py src/paradev/build/registry.py src/paradev/games/hoi4/__init__.py tests/test_simple_source_family.py tests/test_project_build.py tests/test_project.py docs/workflows/build-flow.md docs/progress/2026-06-06-2312-event-namespace-collections.md`

## Risks Or Blockers

- Live Linear sync is still blocked because no Linear MCP tool is exposed and `linear` is not available on `PATH`.
- Event validation is still scaffold-level: this slice proves namespace collection output, not event id collision or localization completeness checks.
- Existing local desktop, README, and script edits remain outside this slice.

## Next

- Add event-specific collection diagnostics for duplicate event ids and namespace consistency, or implement the next collection family for decisions/categories.
