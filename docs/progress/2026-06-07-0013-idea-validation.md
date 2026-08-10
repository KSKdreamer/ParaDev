# Idea Validation Progress

Date: 2026-06-07 00:13 CST

Linear: TAL-294 local continuation; live Linear sync unavailable

## Done

- Added blocking HOI4 idea diagnostics for authored idea ids that do not match the module game-facing object id.
- Added localization checks for idea modules that author `*.loc`: each language must include `<object_id>` and `<object_id>_desc`.
- Added icon alignment checks so authored `icon.(png|dds|tga)` sources require `picture = <object_id>` in the idea PDX block.
- Covered `game_id` override behavior so legacy game-facing ids validate and emit consistently while the module folder identity remains stable.
- Kept idea output on the existing generic source path: `common/ideas/<object_id>.txt`, `localisation/<language>/<object_id>_<language>.yml`, and `gfx/interface/ideas/idea_<object_id>.<ext>`.
- Documented the stricter idea authoring contract in `docs/workflows/build-flow.md`.

## Verification

- Red: `rtk bash scripts/test.bash tests/test_project_build.py::test_hoi4_profile_blocks_idea_id_mismatch tests/test_project_build.py::test_hoi4_profile_blocks_missing_idea_localization_keys tests/test_project_build.py::test_hoi4_profile_blocks_idea_icon_picture_mismatch -q`
- Focused green: `rtk bash scripts/test.bash tests/test_project_build.py::test_hoi4_profile_blocks_idea_id_mismatch tests/test_project_build.py::test_hoi4_profile_blocks_missing_idea_localization_keys tests/test_project_build.py::test_hoi4_profile_blocks_idea_icon_picture_mismatch -q`
- Positive idea smoke: `rtk bash scripts/test.bash tests/test_project_build.py::test_hoi4_profile_emits_idea_pdx_localization_and_icon -q`
- Idea group: `rtk bash scripts/test.bash tests/test_project_build.py::test_hoi4_profile_emits_idea_pdx_localization_and_icon tests/test_project_build.py::test_hoi4_profile_validates_idea_game_id_override tests/test_project_build.py::test_hoi4_profile_blocks_idea_id_mismatch tests/test_project_build.py::test_hoi4_profile_blocks_missing_idea_localization_keys tests/test_project_build.py::test_hoi4_profile_blocks_idea_icon_picture_mismatch -q`
- Related: `rtk bash scripts/test.bash tests/test_project.py tests/test_project_build.py tests/test_simple_source_family.py tests/test_build_manifest.py tests/test_build_records.py tests/test_build_loaders.py tests/test_module_sources.py -q`
- Full: `rtk bash scripts/test.bash`
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven-style: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/games/hoi4/__init__.py tests/test_project_build.py`
- CLI family smoke: `rtk uv run paradev families demos/assets/projects/minimal --json`
- CLI build smoke: `rtk uv run paradev build demos/assets/projects/minimal --json`
- Whitespace: `rtk git diff --check -- src/paradev/games/hoi4/__init__.py tests/test_project_build.py docs/workflows/build-flow.md docs/progress/2026-06-07-0013-idea-validation.md`
- Linear probe: `rtk command -v linear`
- Linear connector probe: `tool_search` for Linear issue tools

## Risks Or Blockers

- Live Linear sync is still blocked because no Linear MCP tool is exposed and `linear` is not available on `PATH`.
- Local HOI4 files did not expose a stable `common/achievements` authoring root in the installed `1.18.2.0` tree, so this slice tightened the already-proven idea asset family instead of guessing an achievement compiler path.
- Icon support still preserves source files only; DDS/TGA conversion and interface sprite generation remain future image-pipeline work.
- Existing local desktop, README, and script edits remain outside this slice.

## Next

- Extend the generic module compilation system with a reusable source-family validation hook or a domain-specific record extractor once the next family needs similar id/localization/icon alignment.
