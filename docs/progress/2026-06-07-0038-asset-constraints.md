# 2026-06-07 00:38 CST - Asset Constraints

## Done

- Added generic `asset_constraints` support to simple, routed, and collection source families.
- Added blocking diagnostics for copy asset format, dimensions, and missing image metadata.
- Exposed family asset contracts through `Project.families()` and `paradev families --json`.
- Kept concrete HOI4 idea icon policy unchanged until target dimensions and formats are verified from game data or docs.
- Updated the build-flow docs so GUI, MCP, and script clients can discover asset contracts from the profile registry.

## Verification

- Red first: `rtk bash scripts/test.bash tests/test_simple_source_family.py::test_simple_source_family_reports_asset_constraint_diagnostics tests/test_project.py::test_project_families_returns_asset_contracts -q` failed because families did not accept `asset_constraints`.
- Focused green: `rtk bash scripts/test.bash tests/test_simple_source_family.py::test_simple_source_family_reports_asset_constraint_diagnostics tests/test_project.py::test_project_families_returns_asset_contracts -q`
- Related suite: `rtk bash scripts/test.bash tests/test_project.py tests/test_simple_source_family.py tests/test_project_build.py tests/test_build_loaders.py tests/test_build_manifest.py tests/test_build_records.py tests/test_module_sources.py -q`
- Full suite: `rtk bash scripts/test.bash` passed 130 tests.
- CI lint: `rtk bash scripts/flake.bash --ci`
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/families.py src/paradev/build/registry.py tests/test_project.py tests/test_simple_source_family.py`
- CLI smoke: `rtk uv run paradev families demos/assets/projects/minimal --json`
- CLI smoke: `rtk uv run paradev build demos/assets/projects/minimal --json`
- Whitespace check: `rtk git diff --check -- src/paradev/build/families.py src/paradev/build/registry.py tests/test_project.py tests/test_simple_source_family.py docs/workflows/build-flow.md docs/progress/2026-06-07-0038-asset-constraints.md`

## Linear

- `rtk command -v linear` still exits with status 1.
- Tool discovery for Linear issue management exposed Codex automation and GitHub tools only; no Linear connector is available in this session.

## Risks

- Asset contracts currently apply only to families that opt in; HOI4-specific idea and achievement icon policy still needs verified source data before hard-coding.
- The repository has unrelated dirty desktop and README work that remains intentionally untouched.

## Next

- Verify HOI4 icon dimensions and accepted texture formats, then attach family-level contracts to the first real game families.
- Extend asset planning toward sprite manifest generation once the target family policy is stable.
