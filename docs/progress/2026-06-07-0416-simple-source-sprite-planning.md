# Simple Source Sprite Planning Progress

Date: 2026-06-07 04:16 CST

Linear: unavailable; no Linear connector was exposed and `linear` is not on PATH.

## Done

- Added optional sprite planning to `SimpleSourceFamily` through `sprite_gfx_path_template`, `sprite_name_template`, and `sprite_slots`.
- Planned one aggregate `sprite_gfx` artifact per simple-source family, using copied texture artifact paths as each `SpriteType.texturefile`.
- Preserved source-map attribution by attaching every contributing authored asset as an input to the aggregate sprite artifact.
- Exposed sprite templates in `Project.families()` capability payloads so SDK, CLI, GUI, and MCP clients can discover the contract.
- Documented the copy-slot-to-sprite mental model in the build-flow guide.

## Verification

- Red check: `rtk bash scripts/test.bash tests/test_simple_source_family.py::test_simple_source_family_emits_aggregate_sprite_gfx_for_declared_sprite_slots -q` failed because `SimpleSourceFamily` did not accept sprite template arguments.
- Focused green: `rtk bash scripts/test.bash tests/test_simple_source_family.py::test_simple_source_family_emits_aggregate_sprite_gfx_for_declared_sprite_slots tests/test_project.py::test_project_families_prefers_family_source_slot_contracts -q`
- Related: `rtk bash scripts/test.bash tests/test_simple_source_family.py tests/test_artifact_writers.py tests/test_project.py tests/test_build_manifest.py -q`
- Full suite: `rtk bash scripts/test.bash`
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/families.py src/paradev/build/registry.py tests/test_simple_source_family.py tests/test_project.py`
- SDK smoke probe wrote copied idea icons plus `interface/paradev_idea.gfx` from a simple-source family.
- Whitespace: `rtk git diff --check -- src/paradev/build/families.py src/paradev/build/registry.py tests/test_simple_source_family.py tests/test_project.py docs/workflows/build-flow.md`

## Risks Or Blockers

- Declarative `paradev.yaml` does not expose sprite templates yet; this slice proves the Python family API first.
- Built-in HOI4 families still do not auto-generate sprites until their family-specific sprite policy is selected.
- Linear status could not be updated from this environment.

## Next

- Expose sprite planning in declarative project-local families after the Python API proves stable.
- Add duplicate sprite-name diagnostics before broadening sprite generation to built-in asset families.
