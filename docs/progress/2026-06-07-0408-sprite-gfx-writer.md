# Sprite GFX Writer Progress

Date: 2026-06-07 04:08 CST

Linear: unavailable; no Linear connector was exposed and `linear` is not on PATH.

## Done

- Added typed `SpriteType` payloads and a `SpriteGFXWriter` for deterministic `interface/*.gfx` sprite declaration artifacts.
- Registered the `sprite_gfx` writer in the HOI4 profile so SDK/CLI family capability payloads expose the reusable writer.
- Grounded the emitted shape against the local HOI4 install at `interface/goals.gfx`: `spriteTypes = { SpriteType = { name = "..." texturefile = "..." } }`.
- Documented that built-in families do not auto-generate sprite declarations yet; custom Python compilers can plan `SpriteType` artifacts now.

## Verification

- Red check: `rtk bash scripts/test.bash tests/test_artifact_writers.py -q` failed because `SpriteGFXWriter` and `SpriteType` did not exist.
- Focused green: `rtk bash scripts/test.bash tests/test_artifact_writers.py tests/test_project.py::test_project_families_returns_profile_family_contracts -q`
- Related: `rtk bash scripts/test.bash tests/test_artifact_writers.py tests/test_project.py tests/test_build_manifest.py -q`
- Full suite: `rtk bash scripts/test.bash`
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/artifacts.py src/paradev/build/__init__.py src/paradev/games/hoi4/__init__.py tests/test_artifact_writers.py tests/test_project.py`
- SDK smoke probe wrote `interface/paradev_ideas.gfx` from a `SpriteType` payload.
- Whitespace: `rtk git diff --check -- src/paradev/build/artifacts.py src/paradev/build/__init__.py src/paradev/games/hoi4/__init__.py tests/test_artifact_writers.py tests/test_project.py docs/workflows/build-flow.md`

## Risks Or Blockers

- This is a writer-only slice. Family-specific sprite planning, duplicate sprite-name diagnostics, and image conversion remain future work.
- Linear status could not be updated from this environment.

## Next

- Add a generic sprite-planning contract for asset families once the first family policy is clear.
- Keep sprite declarations separate from raw image copy artifacts so source maps can explain both generated GFX and copied texture files.
