# Simple HOI4 Families Progress

Date: 2026-06-06 22:09 CST

Linear: TAL-294

## Done

- Registered HOI4 `modifier` modules through the generic `SimpleSourceFamily`, writing PDX to `common/modifiers/<object_id>.txt`.
- Registered HOI4 `opinion_modifier` modules through the same generic family, writing PDX to `common/opinion_modifiers/<object_id>.txt`.
- Kept localization and static-copy behavior aligned with the existing source-slot compilers.
- Verified the output folders against the local HOI4 install on 2026-06-06 before documenting the profile contract.
- Deferred `trait` registration because local game files split trait outputs across country and unit leader folders, requiring a subtype policy first.

## Verification

- `rtk bash scripts/test.bash tests/test_project_build.py::test_hoi4_profile_plans_simple_modifier_artifacts tests/test_project_build.py::test_hoi4_profile_emits_simple_modifier_files tests/test_project_build.py::test_hoi4_profile_plans_simple_opinion_modifier_artifacts -q`
- `rtk bash scripts/test.bash tests/test_project_build.py tests/test_project.py tests/test_simple_source_family.py tests/test_sdk_examples.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/games/hoi4/__init__.py tests/test_project_build.py`
- `rtk rg --files '/Users/magolor/Library/Application Support/Steam/steamapps/common/Hearts of Iron IV/common/modifiers'`
- `rtk rg --files '/Users/magolor/Library/Application Support/Steam/steamapps/common/Hearts of Iron IV/common/opinion_modifiers'`
- `rtk rg --files '/Users/magolor/Library/Application Support/Steam/steamapps/common/Hearts of Iron IV/common/country_leader'`

## Risks Or Blockers

- Live Linear sync is still pending because no Linear MCP tool or `linear` CLI is available in this session.
- `modifier` and `opinion_modifier` are intentionally thin PDX-plus-loc scaffolds; semantic validation and reference indexes remain later work.
- `trait` remains unregistered until ParaDev has a user-facing subtype policy for country-leader versus unit-leader outputs.
- Existing local desktop and README edits remain outside this HOI4 profile slice.

## Next

- Add subtype-aware simple-family configuration for traits or start the next simple family only after its HOI4 path and source semantics are checked.
