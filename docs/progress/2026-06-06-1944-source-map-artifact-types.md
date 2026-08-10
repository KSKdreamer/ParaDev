# Source Map Artifact Types Progress

Date: 2026-06-06 19:44 CST

Linear: TAL-294

## Done

- Added artifact `type` to build source-map manifest rows.
- Expanded manifest coverage to include both PDX and localization artifacts.
- Preserved input provenance so surfaces can trace localization outputs back to `.loc` files.

## Verification

- `rtk uv run pytest tests/test_build_manifest.py -q`
- `rtk uv run pytest tests/test_build_manifest.py tests/test_build_records.py tests/test_project.py tests/test_project_build.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/manifest.py tests/test_build_manifest.py`

## Risks Or Blockers

- Live Linear sync is still pending because no Linear MCP tool or `linear` CLI is available in this session.
- Existing local desktop and README edits remain outside this source-map slice.

## Next

- Add build manifest emission coverage for the demo project so `.paradev/build/source-map.json` records PDX and localization artifacts together.
