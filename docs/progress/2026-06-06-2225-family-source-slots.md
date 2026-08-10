# Family Source Slots Progress

Date: 2026-06-06 22:25 CST

Linear: TAL-294 local continuation; live Linear sync unavailable

## Done

- Added failing SDK and CLI coverage for `source_slots` in the family inspection payload.
- Added `BuildRegistry.source_slots` and JSON-safe slot serialization through `BuildRegistry.to_view()`.
- Wired the HOI4 profile registry to `DEFAULT_MODULE_SLOTS`, keeping inspection aligned with module discovery.
- Updated the build-flow workflow so GUI, MCP, and script clients can discover module folder rules without hard-coding them.

## Verification

- `rtk bash scripts/test.bash tests/test_project.py::test_project_families_returns_profile_family_contracts tests/test_project.py::test_project_cli_outputs_profile_family_contracts -q`
- `rtk bash scripts/test.bash tests/test_project.py tests/test_project_build.py tests/test_simple_source_family.py tests/test_build_manifest.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/registry.py src/paradev/games/hoi4/__init__.py tests/test_project.py`
- `rtk uv run paradev families demos/assets/projects/minimal --json`
- `rtk git diff --check src/paradev/build/registry.py src/paradev/games/hoi4/__init__.py tests/test_project.py docs/workflows/build-flow.md docs/progress/2026-06-06-2225-family-source-slots.md`

## Risks Or Blockers

- Live Linear sync is still blocked because no Linear MCP tool is exposed and `linear` is not available on `PATH`.
- Source slots are currently profile-level defaults shared across registered HOI4 families; future family-specific slot schemas can extend the same view shape.
- Existing local desktop and README edits remain outside this slice.

## Next

- Start the next generic module compilation slice by making family-specific source contracts possible without changing the current beginner-facing module layout.
