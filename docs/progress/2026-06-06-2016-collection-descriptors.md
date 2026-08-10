# Collection Descriptors Progress

Date: 2026-06-06 20:16 CST

Linear: TAL-293

## Done

- Added a collection descriptor loader for `meta.yaml` and `collection.yaml`.
- Added collection descriptor discovery under `collections/<family>/<collection>/`.
- Merged descriptor metadata into derived collection records while preserving explicit SDK collections with module IDs.
- Wired `Project.build()` to discover collection descriptors when callers do not provide explicit collections.
- Updated build-flow docs with the current collection descriptor path.

## Verification

- `rtk uv run pytest tests/test_build_loaders.py tests/test_project_build.py tests/test_build_records.py tests/test_build_manifest.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/__init__.py src/paradev/build/discovery.py src/paradev/build/loaders.py src/paradev/build/records.py src/paradev/sdk/project.py tests/test_build_loaders.py tests/test_project_build.py`

## Risks Or Blockers

- Live Linear sync is still pending because no Linear MCP tool or `linear` CLI is available in this session.
- Descriptor metadata is attached to collections but no collection-aware focus compiler consumes it yet.
- Existing local desktop and README edits remain outside this collection descriptor slice.

## Next

- Add the first collection-aware focus family compiler that emits collection-owned PDX from grouped modules.
