# Build Registry And Manifests Progress

Date: 2026-06-06 18:47 CST

Linear: TAL-293

## Done

- Added `BuildRegistry` for registering module families and artifact writers.
- Added dry-run `plan_build(...)` with `BuildContext` so registered families can emit planned artifacts without writing game outputs.
- Added manifest helpers for `modules.json`, `collections.json`, `artifacts.json`, `diagnostics.json`, `source-map.json`, and `summary.json`.
- Added `write_manifests(...)` for stable JSON files under a supplied `.paradev/build` root.
- Added `.gitignore` exceptions so the intentional `src/paradev/build/` source package is no longer hidden by the broad `build/` ignore rule.

## Verification

- `rtk uv run pytest tests/test_build_manifest.py tests/test_build_records.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build tests/test_build_manifest.py tests/test_build_records.py`

## Risks Or Blockers

- Live Linear sync is still pending because no Linear MCP tool or `linear` CLI is available in this session.
- Existing local desktop and README edits remain outside this build-spine slice.

## Next

- Connect `Project` to dry-run build planning and start source/module discovery or slot matching for TAL-294.
