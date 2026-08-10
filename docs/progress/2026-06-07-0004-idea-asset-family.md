# Idea Asset Family Progress

Date: 2026-06-07 00:04 CST

Linear: TAL-294 local continuation; live Linear sync unavailable

## Done

- Refreshed local HOI4 idea paths from the installed game: `rawVersion` `1.18.2.0`, idea scripts under `common/ideas/*.txt`, and idea icons under `gfx/interface/ideas/*.dds`.
- Added TDD coverage for generic copy artifact templates using `{source_suffix}` so asset compilers can preserve source file extensions.
- Registered the HOI4 `idea` family as the first asset-family proof with narrow `def.pdx`, `*.loc`, and `icon.(png|dds|tga)` source slots.
- Planned and emitted idea PDX, localization, and icon-copy artifacts through the existing registry, loaders, and artifact writers.
- Updated family inspection so SDK, CLI, desktop, and future MCP clients can discover the idea family contract.
- Documented idea module authoring in the build-flow workflow.

## Verification

- Red: `rtk bash scripts/test.bash tests/test_simple_source_family.py::test_simple_source_family_copy_template_can_use_source_suffix tests/test_project.py::test_project_families_returns_profile_family_contracts tests/test_project_build.py::test_hoi4_profile_emits_idea_pdx_localization_and_icon -q`
- Green: `rtk bash scripts/test.bash tests/test_simple_source_family.py::test_simple_source_family_copy_template_can_use_source_suffix tests/test_project.py::test_project_families_returns_profile_family_contracts tests/test_project_build.py::test_hoi4_profile_emits_idea_pdx_localization_and_icon -q`
- Related: `rtk bash scripts/test.bash tests/test_project.py tests/test_project_build.py tests/test_simple_source_family.py tests/test_build_manifest.py tests/test_build_records.py tests/test_build_loaders.py tests/test_module_sources.py -q`
- Full: `rtk bash scripts/test.bash`
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven-style: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/families.py src/paradev/games/hoi4/__init__.py tests/test_project.py tests/test_project_build.py tests/test_simple_source_family.py`
- CLI family smoke: `rtk uv run paradev families demos/assets/projects/minimal --json`
- CLI build smoke: `rtk uv run paradev build demos/assets/projects/minimal --json`
- Linear probe: `rtk command -v linear`
- Linear connector probe: `tool_search` for Linear issue tools

## Risks Or Blockers

- Live Linear sync is still blocked because no Linear MCP tool is exposed and `linear` is not available on `PATH`.
- Idea icon support preserves and copies source files; DDS/TGA conversion and interface sprite generation remain later image-pipeline work.
- Existing local desktop, README, and script edits remain outside this slice.

## Next

- Add the achievement asset-family proof or add idea-specific validation for category/id/localization/icon alignment.
