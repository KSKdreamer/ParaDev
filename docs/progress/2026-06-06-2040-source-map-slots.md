# Source Map Slot Progress

Date: 2026-06-06 20:40 CST

Linear: TAL-293

## Done

- Added source-map `sources` entries beside the existing artifact `inputs` list.
- Derived source records from module `source_slots`, including module id, family, slot, and normalized source path.
- Covered both direct manifest payloads and CLI-emitted demo manifests.
- Updated build-flow docs with the enriched source-map contract.

## Verification

- `rtk bash scripts/test.bash tests/test_build_manifest.py tests/test_project.py -q`
- `rtk bash scripts/test.bash tests/test_build_manifest.py tests/test_project.py tests/test_project_build.py tests/test_sdk_examples.py tests/test_simple_source_family.py tests/test_build_loaders.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/manifest.py tests/test_build_manifest.py tests/test_project.py`
- Temporary-project `rtk uv run paradev build <tmp>/minimal --emit-manifests --json`

## Risks Or Blockers

- Live Linear sync is still pending because no Linear MCP tool or `linear` CLI is available in this session.
- Unmatched artifact inputs are preserved as path-only `sources`; stricter validation belongs in a later artifact/source-map check.
- Existing local desktop and README edits remain outside this source-map slice.

## Next

- Add diagnostic-to-source manifest rows or begin layout-aware focus collection payloads.
