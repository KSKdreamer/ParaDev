# Focus Validation Progress

Date: 2026-06-06 20:29 CST

Linear: TAL-293

## Done

- Added the first optional family `check(ctx, modules, collections)` hook to `plan_build(...)`.
- Added collection-level focus diagnostics for duplicate focus IDs.
- Added project-local PDX prerequisite validation for focus collections.
- Kept collection-owned focus artifact planning and existing demo output behavior intact.
- Updated build-flow docs with the current validation boundary.

## Verification

- `rtk uv run pytest tests/test_simple_source_family.py tests/test_project.py tests/test_project_build.py tests/test_sdk_examples.py tests/test_build_manifest.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/families.py src/paradev/build/plan.py tests/test_simple_source_family.py`
- `rtk uv run paradev build demos/assets/projects/minimal --json`

## Risks Or Blockers

- Live Linear sync is still pending because no Linear MCP tool or `linear` CLI is available in this session.
- Prerequisite validation only checks project-local PDX focus IDs; game-reference-backed validation remains future work.
- Existing local desktop and README edits remain outside this validation slice.

## Next

- Add source-map or diagnostic payload detail for focus IDs and prerequisites, then move toward layout-aware collection compilation.
