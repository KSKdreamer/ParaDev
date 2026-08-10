# Declarative Sprite Templates Progress

Date: 2026-06-07 04:22 CST

Linear: unavailable; no Linear connector was exposed and `linear` is not on PATH.

## Done

- Exposed simple-source sprite planning through declarative `paradev.yaml` family declarations.
- Added `templates.sprite_gfx`, `templates.sprite_name`, and `sprite_slots` validation for project-local simple-source families.
- Rejected incomplete sprite declarations so missing copy, sprite GFX, sprite name, or selected copied slots cannot silently skip sprite output.
- Confirmed manifest-declared families can emit copied assets plus aggregate sprite GFX artifacts through the existing HOI4 registry.
- Updated the manifest reference and build-flow guide with the declarative sprite contract.

## Verification

- Red check: focused tests failed because manifest-declared sprite templates were ignored and incomplete sprite declarations were accepted.
- Focused green: `rtk bash scripts/test.bash tests/test_project_build.py::test_project_build_uses_manifest_declared_sprite_templates tests/test_project.py::test_project_manifest_rejects_incomplete_sprite_templates -q`
- Related: `rtk bash scripts/test.bash tests/test_project.py tests/test_project_build.py tests/test_simple_source_family.py tests/test_artifact_writers.py -q`
- Full suite: `rtk bash scripts/test.bash`
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/extensions.py tests/test_project.py tests/test_project_build.py`
- SDK smoke probe loaded a manifest-declared `badge` family, emitted `gfx/badges/GER_badge.dds`, and wrote `interface/paradev_badge.gfx`.
- Whitespace: `rtk git diff --check -- src/paradev/build/extensions.py tests/test_project.py tests/test_project_build.py docs/workflows/build-flow.md docs/resources/05-project-manifest.md`

## Risks Or Blockers

- Sprite planning is still opt-in per family; built-in HOI4 idea sprites need a separate policy decision.
- Duplicate sprite-name diagnostics are still future work.
- Linear status could not be updated from this environment.

## Next

- Add duplicate sprite-name diagnostics before enabling built-in asset-family sprite output.
- Consider collection-source sprite planning only when a collection-owned asset family needs it.
