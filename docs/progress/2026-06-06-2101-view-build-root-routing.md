# View Build Root Routing Progress

Date: 2026-06-06 21:01 CST

Linear: TAL-293

## Done

- Routed `view` artifacts from `Project.build(..., emit_artifacts=True)` to `build_root`.
- Kept PDX, localization, copy, and other game artifacts writing under `output_root`.
- Covered mixed PDX plus view emission with a Project SDK test.
- Updated build-flow docs with the output-root versus build-root split.

## Verification

- `rtk bash scripts/test.bash tests/test_project_build.py -q`
- `rtk bash scripts/test.bash tests/test_project_build.py tests/test_artifact_writers.py tests/test_sdk_examples.py tests/test_project.py tests/test_simple_source_family.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py tests/test_project_build.py`
- `rtk uv run paradev build demos/assets/projects/minimal --json`

## Risks Or Blockers

- Live Linear sync is still pending because no Linear MCP tool or `linear` CLI is available in this session.
- Only `view` artifacts are routed to `build_root`; future build-owned artifact types should make this root policy explicit.
- Existing local desktop and README edits remain outside this SDK routing slice.

## Next

- Enable focus-tree view emission in the HOI4 scaffold now that view artifacts write to `build_root`.
