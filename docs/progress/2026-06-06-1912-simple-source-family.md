# Simple Source Family Progress

Date: 2026-06-06 19:12 CST

Linear: TAL-294

## Done

- Added internal `Module.payload` for compiler-stage state while keeping module manifests JSON-safe.
- Attached `ModuleSourceBundle` payloads from `ModuleSourceBundle.to_module()`.
- Added `SimpleSourceFamily`, a generic template-driven family helper that emits PDX and static copy artifacts from source bundles.
- Proved the build path from slot matching through loading, planning, writing PDX output, and copying static bytes.
- Kept the helper game-neutral; output locations are caller-provided templates.

## Verification

- `rtk uv run pytest tests/test_simple_source_family.py -q`
- `rtk uv run pytest tests/test_simple_source_family.py tests/test_module_sources.py tests/test_artifact_writers.py tests/test_build_manifest.py tests/test_project_build.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build tests/test_simple_source_family.py`

## Risks Or Blockers

- Live Linear sync is still pending because no Linear MCP tool or `linear` CLI is available in this session.
- Existing local desktop and README edits remain outside this family-helper slice.

## Next

- Add project/module discovery that can create source bundles from `Project.source_roots`, then use the generic family proof from the CLI build path.
