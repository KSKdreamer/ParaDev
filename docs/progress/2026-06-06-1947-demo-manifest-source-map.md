# Demo Manifest Source Map Progress

Date: 2026-06-06 19:47 CST

Linear: TAL-294

## Done

- Added CLI coverage for `paradev build --emit-manifests` using a temporary copy of the minimal demo project.
- Verified `.paradev/build/source-map.json` records both PDX and localization artifacts.
- Verified source-map rows preserve artifact type, owner, and source input paths for `def.pdx` and `main.loc`.
- Kept generated manifest files out of the committed demo tree.

## Verification

- `rtk uv run pytest tests/test_project.py -q`
- `rtk uv run pytest tests/test_project.py tests/test_build_manifest.py tests/test_project_build.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_project.py`

## Risks Or Blockers

- Live Linear sync is still pending because no Linear MCP tool or `linear` CLI is available in this session.
- Existing local desktop and README edits remain outside this demo-manifest coverage slice.

## Next

- Add user-facing README or docs coverage for the minimal project build flow once the canonical README dirty state is resolved.
