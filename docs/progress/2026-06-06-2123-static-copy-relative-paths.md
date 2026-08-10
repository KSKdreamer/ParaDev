# Static Copy Relative Paths Progress

Date: 2026-06-06 21:23 CST

Linear: TAL-294

## Done

- Preserved matched static-copy source paths in the default HOI4 scaffold.
- Covered nested `assets/` and `copy/` files with the same basename so they no longer collide.
- Verified emitted copy artifact bytes and SHA-256 metadata.
- Updated build-flow docs with the static-copy output path policy.

## Verification

- `rtk bash scripts/test.bash tests/test_project_build.py::test_hoi4_profile_preserves_static_copy_relative_paths -q`
- `rtk bash scripts/test.bash tests/test_project_build.py tests/test_project.py tests/test_sdk_examples.py tests/test_simple_source_family.py tests/test_module_sources.py tests/test_artifact_writers.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/games/hoi4/__init__.py tests/test_project_build.py`
- `rtk uv run paradev build demos/assets/projects/minimal --emit-artifacts --json`

## Risks Or Blockers

- Live Linear sync is still pending because no Linear MCP tool or `linear` CLI is available in this session.
- Static copies are still raw file copies; DDS/TGA conversion and asset-specific HOI4 validation remain deferred.
- Existing local desktop and README edits remain outside this compiler slice.

## Next

- Add stronger static-copy diagnostics or writer policies only when asset-specific families need them.
