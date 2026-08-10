# Localization Contract Progress

Date: 2026-06-07 00:25 CST

Linear: TAL-294 local continuation; live Linear sync unavailable

## Done

- Added generic `required_loc_keys` support to simple, routed, collection PDX, and collection source families.
- Added reusable `<family>.missing_localization` diagnostics for modules that author localization but omit required rendered keys for a language.
- Added family inspection output for localization contracts so SDK, CLI, desktop, MCP, and scripts can discover required key templates instead of hard-coding them.
- Swapped HOI4 idea missing-localization checks onto the generic contract while preserving its `def.pdx` source anchor and PDX span.
- Documented the family localization contract in `docs/workflows/build-flow.md`.

## Verification

- Red: `rtk bash scripts/test.bash tests/test_simple_source_family.py::test_simple_source_family_reports_missing_required_localization_keys tests/test_project.py::test_project_families_returns_profile_family_contracts tests/test_project.py::test_project_families_prefers_family_source_slot_contracts -q`
- Focused green: `rtk bash scripts/test.bash tests/test_simple_source_family.py::test_simple_source_family_reports_missing_required_localization_keys tests/test_project.py::test_project_families_returns_profile_family_contracts tests/test_project.py::test_project_families_prefers_family_source_slot_contracts tests/test_project_build.py::test_hoi4_profile_blocks_missing_idea_localization_keys -q`
- Related: `rtk bash scripts/test.bash tests/test_project.py tests/test_project_build.py tests/test_simple_source_family.py tests/test_build_manifest.py tests/test_build_records.py tests/test_build_loaders.py tests/test_module_sources.py -q`
- Full: `rtk bash scripts/test.bash`
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven-style: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/families.py src/paradev/build/registry.py src/paradev/games/hoi4/__init__.py tests/test_project.py tests/test_simple_source_family.py`
- CLI family smoke: `rtk uv run paradev families demos/assets/projects/minimal --json`
- CLI build smoke: `rtk uv run paradev build demos/assets/projects/minimal --json`
- Whitespace: `rtk git diff --check -- src/paradev/build/families.py src/paradev/build/registry.py src/paradev/games/hoi4/__init__.py tests/test_project.py tests/test_simple_source_family.py docs/workflows/build-flow.md docs/progress/2026-06-07-0025-localization-contracts.md`
- Linear probe: `rtk command -v linear`
- Linear connector probe: `tool_search` for Linear issue tools

## Risks Or Blockers

- Live Linear sync remains blocked because no Linear MCP tool is exposed and `linear` is not available on `PATH`.
- The generic localization contract validates module-owned localization only. Collection-owned localization, such as decision category descriptors, still uses collection-specific checks.
- Existing local desktop, README, and script edits remain outside this slice.

## Next

- Extend the generic compiler contract toward asset metadata or sprite declaration manifests so idea and achievement-style families can share more of the asset pipeline.
