# Sprite Manifest Progress

Date: 2026-06-07 04:42 CST

Linear: unavailable; no Linear connector was exposed and `linear` is not on PATH.

## Done

- Added a `paradev.build.sprites.v1` manifest payload for planned `sprite_gfx` artifacts.
- Added `Project.sprites(...)` and `paradev sprites` filters for module, collection, family, slot, and exact sprite name.
- Kept sprite rows source-backed: each row includes the sprite name, texture file, generated GFX artifact, source metadata, and owner/slot index.
- Updated the build-flow guide with sprite inspection and `sprites.json` manifest coverage.

## Verification

- Red check: focused tests failed because `sprites.json`, `Project.sprites`, and `paradev sprites` did not exist.
- Focused green: `rtk bash scripts/test.bash tests/test_build_manifest.py::test_manifest_payloads_include_sprite_declaration_catalog tests/test_project.py::test_project_sprites_returns_filtered_manifest_payload_without_writing tests/test_project.py::test_project_cli_filters_sprite_manifest_json -q`
- Related: `rtk bash scripts/test.bash tests/test_build_manifest.py tests/test_project.py tests/test_project_build.py tests/test_simple_source_family.py tests/test_artifact_writers.py -q`
- Full suite: `rtk bash scripts/test.bash`
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/manifest.py src/paradev/build/__init__.py src/paradev/sdk/project.py src/paradev/cli.py tests/test_build_manifest.py tests/test_project.py`
- SDK smoke probe loaded a HOI4 idea module and confirmed `Project.sprites(name="GFX_idea_GER_industry_spirit")` returned one row.
- Whitespace: `rtk git diff --check -- src/paradev/build/manifest.py src/paradev/build/__init__.py src/paradev/sdk/project.py src/paradev/cli.py tests/test_build_manifest.py tests/test_project.py docs/workflows/build-flow.md docs/progress/2026-06-07-0442-sprite-manifest.md`

## Risks Or Blockers

- Sprite rows depend on `SpriteType` payloads; hand-authored `.gfx` parsing is still outside this slice.
- Linear status could not be updated from this environment.

## Next

- Use the sprite manifest from desktop or MCP previews when those surfaces need source-backed sprite rows.
- Continue extending built-in asset families only after refreshing each HOI4 path and sprite convention from installed game files.
