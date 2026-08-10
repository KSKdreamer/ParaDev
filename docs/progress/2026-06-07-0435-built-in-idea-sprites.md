# Built-In Idea Sprites Progress

Date: 2026-06-07 04:35 CST

Linear: unavailable; no Linear connector was exposed and `linear` is not on PATH.

## Done

- Verified local HOI4 `rawVersion` `1.18.2.0` and the live `GFX_idea_*` to `gfx/interface/ideas/idea_*.dds` convention in installed `interface/*.gfx` files.
- Enabled the built-in HOI4 idea family to emit `interface/paradev_idea.gfx` from authored `icon.png`, `icon.dds`, or `icon.tga` sources.
- Kept the implementation on the generic `SimpleSourceFamily` sprite template path instead of adding a separate idea-only writer.
- Exposed non-empty `sprite_slots` in family inspection payloads so SDK, CLI, GUI, and MCP clients can discover which copied slots also generate sprites.
- Updated the build-flow guide with the new idea sprite output contract.

## Verification

- Red check: focused tests failed because the idea profile emitted no `sprite_gfx` artifact and family inspection hid `sprite_slots`.
- Focused green: `rtk bash scripts/test.bash tests/test_project_build.py::test_hoi4_profile_emits_idea_pdx_localization_and_icon tests/test_project_build.py::test_hoi4_profile_validates_idea_game_id_override tests/test_project.py::test_project_families_returns_profile_family_contracts tests/test_project.py::test_project_families_exposes_sprite_slot_contracts -q`
- Related: `rtk bash scripts/test.bash tests/test_project.py tests/test_project_build.py tests/test_simple_source_family.py tests/test_artifact_writers.py -q`
- Full suite: `rtk bash scripts/test.bash`
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/registry.py src/paradev/games/hoi4/__init__.py tests/test_project.py tests/test_project_build.py`
- SDK smoke probe built an idea module with `icon.dds` and confirmed `interface/paradev_idea.gfx` contains `GFX_idea_GER_industry_spirit`.
- Whitespace: `rtk git diff --check -- src/paradev/build/registry.py src/paradev/games/hoi4/__init__.py tests/test_project.py tests/test_project_build.py docs/workflows/build-flow.md docs/progress/2026-06-07-0435-built-in-idea-sprites.md`

## Risks Or Blockers

- Image conversion is still out of scope; authored icons are copied as-is.
- Linear status could not be updated from this environment.

## Next

- Add manifest/source-map coverage for project-owned sprite GFX artifacts if GUI asset previews need direct sprite rows.
- Continue toward the next built-in asset family only after its HOI4 path and sprite convention are refreshed from local game files.
