# Duplicate Sprite Names Progress

Date: 2026-06-07 04:28 CST

Linear: unavailable; no Linear connector was exposed and `linear` is not on PATH.

## Done

- Added blocking duplicate sprite-name diagnostics for simple-source sprite planning.
- Anchored duplicate diagnostics to the later copied source with module id, slot, and source path.
- Covered both direct `SimpleSourceFamily` planning and manifest-declared project-local families.
- Updated the build-flow and project-manifest docs with the duplicate sprite-name contract.

## Verification

- Red check: focused simple-source test failed because duplicate sprite names did not block the build.
- Focused green: `rtk bash scripts/test.bash tests/test_simple_source_family.py::test_simple_source_family_reports_duplicate_sprite_names tests/test_simple_source_family.py::test_simple_source_family_emits_aggregate_sprite_gfx_for_declared_sprite_slots tests/test_project_build.py::test_project_build_blocks_manifest_duplicate_sprite_names -q`
- Related: `rtk bash scripts/test.bash tests/test_simple_source_family.py tests/test_project_build.py tests/test_build_manifest.py -q`
- Full suite: `rtk bash scripts/test.bash`
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/families.py tests/test_simple_source_family.py tests/test_project_build.py`
- SDK smoke probe loaded a manifest-declared `badge` family and confirmed duplicate `GFX_badge_shared` sprites block output.
- Whitespace: `rtk git diff --check -- src/paradev/build/families.py tests/test_simple_source_family.py tests/test_project_build.py docs/workflows/build-flow.md docs/resources/05-project-manifest.md docs/progress/2026-06-07-0428-duplicate-sprite-names.md`

## Risks Or Blockers

- Built-in HOI4 idea sprites still need a separate profile policy before automatic sprite output is enabled.
- Linear status could not be updated from this environment.

## Next

- Enable the first built-in sprite policy for the idea asset family.
- Keep generic sprite generation opt-in for project-local families until collection-owned asset use cases are clearer.
