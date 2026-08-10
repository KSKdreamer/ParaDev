# Dependency Target Validation Progress

Date: 2026-06-06 20:08 CST

Linear: TAL-293

## Done

- Added blocking diagnostics for unresolved project-local dependency targets.
- Treated `module:<module_id>` and slash-form module IDs as project-local targets.
- Kept reference-style game symbols such as `focus:...` and `idea:...` as dependency graph data until reference indexes exist.
- Updated build-flow docs to explain the validation boundary.

## Verification

- `rtk uv run pytest tests/test_build_records.py -q`
- `rtk uv run pytest tests/test_build_records.py tests/test_build_manifest.py tests/test_project.py tests/test_sdk_examples.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/records.py tests/test_build_records.py`
- `rtk uv run paradev build demos/assets/projects/minimal --json`

## Risks Or Blockers

- Live Linear sync is still pending because no Linear MCP tool or `linear` CLI is available in this session.
- Game-reference targets are not validated until a local reference index exists.
- Existing local desktop and README edits remain outside this build graph slice.

## Next

- Add a first project-local symbol index manifest or move into collection-aware family compilation.
