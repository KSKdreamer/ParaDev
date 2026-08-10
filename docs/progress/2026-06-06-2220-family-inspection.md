# Family Inspection Progress

Date: 2026-06-06 22:20 CST

Linear: TAL-294

## Done

- Added a JSON-safe `BuildRegistry.to_view()` capability payload for registered families and artifact writers.
- Added `Project.families(...)` with schema `paradev.build.families.v1` so SDK callers can inspect a profile without running a build.
- Added `paradev families <path> --json` for CLI, MCP, and desktop-facing inspection flows.
- Exposed simple, collection, and routed family contracts including artifact templates and routed settings such as `settings.subtype`.
- Documented the family inspection command and SDK call in the build-flow workflow.

## Verification

- `rtk bash scripts/test.bash tests/test_project.py::test_project_families_returns_profile_family_contracts tests/test_project.py::test_project_cli_outputs_profile_family_contracts -q`
- `rtk bash scripts/test.bash tests/test_project.py tests/test_project_build.py tests/test_simple_source_family.py tests/test_build_manifest.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/registry.py src/paradev/sdk/project.py src/paradev/cli.py tests/test_project.py`
- `rtk uv run paradev families demos/assets/projects/minimal --json`

## Risks Or Blockers

- Live Linear sync is still pending because no Linear MCP tool or `linear` CLI is available in this session.
- The view is profile-level capability metadata only; it does not yet include per-family validation schemas or full source-slot declarations.
- Existing local desktop and README edits remain outside this family inspection slice.

## Next

- Add source-slot declarations to family inspection or start the next asset-family proof with idea/achievement once image-loader policy is ready.
