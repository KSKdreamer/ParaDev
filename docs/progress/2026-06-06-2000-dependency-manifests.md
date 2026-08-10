# Dependency Manifests Progress

Date: 2026-06-06 20:00 CST

Linear: TAL-293

## Done

- Added build dependency records derived from module `requires` and `after` metadata.
- Added blocking diagnostics for malformed dependency metadata.
- Added `dependencies.json` to build manifest payloads and manifest writes.
- Updated the minimal demo project with dependency metadata and covered CLI, SDK, and manifest output.
- Updated build-flow and architecture docs to include the dependency manifest contract.

## Verification

- `rtk uv run pytest tests/test_build_records.py tests/test_build_manifest.py -q`
- `rtk uv run pytest tests/test_build_records.py tests/test_build_manifest.py tests/test_project.py tests/test_project_build.py tests/test_sdk_examples.py tests/test_build_loaders.py tests/test_module_sources.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/__init__.py src/paradev/build/records.py src/paradev/build/manifest.py tests/test_build_records.py tests/test_build_manifest.py tests/test_project.py tests/test_sdk_examples.py`
- `rtk uv run paradev build demos/assets/projects/minimal --json`

## Risks Or Blockers

- Live Linear sync is still pending because no Linear MCP tool or `linear` CLI is available in this session.
- Dependency records expose graph edges but do not yet order build execution or validate missing targets.
- Existing local desktop and README edits remain outside this build graph slice.

## Next

- Add deterministic module ordering from `after` edges and report graph cycles as blocking diagnostics.
