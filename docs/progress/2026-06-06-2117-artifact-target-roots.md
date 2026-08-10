# Artifact Target Roots Progress

Date: 2026-06-06 21:17 CST

Linear: TAL-293

## Done

- Added explicit `Artifact.target_root` values for `output` and `build`.
- Routed SDK artifact emission by `target_root` instead of artifact type.
- Marked focus-tree view artifacts as build-root artifacts.
- Added target-root validation, root-scoped artifact collision checks, and source-map output fields.
- Guarded the low-level artifact writer against mixed-root write calls.
- Updated build-flow docs so dry-run and manifest consumers can see where artifacts land.

## Verification

- `rtk bash scripts/test.bash tests/test_project_build.py::test_project_build_routes_artifacts_by_target_root -q`
- `rtk bash scripts/test.bash tests/test_build_records.py tests/test_build_manifest.py tests/test_project_build.py tests/test_project.py tests/test_sdk_examples.py tests/test_simple_source_family.py tests/test_artifact_writers.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/records.py src/paradev/build/manifest.py src/paradev/build/families.py src/paradev/build/artifacts.py src/paradev/sdk/project.py tests/test_build_records.py tests/test_build_manifest.py tests/test_project.py tests/test_project_build.py tests/test_artifact_writers.py`
- `rtk uv run paradev build demos/assets/projects/minimal --emit-manifests --json`

## Risks Or Blockers

- Live Linear sync is still pending because no Linear MCP tool or `linear` CLI is available in this session.
- Only `output` and `build` target roots are supported; cache/index roots should be added deliberately if future stages need them.
- Existing local desktop and README edits remain outside this build-record slice.

## Next

- Use the explicit target-root field when adding richer artifact manifests or editor/index outputs.
