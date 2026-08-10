# Diagnostic Source Manifest Progress

Date: 2026-06-06 20:44 CST

Linear: TAL-293

## Done

- Added manifest-only diagnostic source enrichment for `diagnostics.json`.
- Resolved diagnostic `module_id` plus `source_path` back to module source slots where available.
- Preserved existing diagnostic JSON fields and `BuildResult.to_dict()` behavior.
- Updated build-flow docs with the diagnostics/source-map traceability model.

## Verification

- `rtk bash scripts/test.bash tests/test_build_manifest.py -q`
- `rtk bash scripts/test.bash tests/test_build_manifest.py tests/test_project.py tests/test_project_build.py tests/test_sdk_examples.py tests/test_build_records.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/manifest.py tests/test_build_manifest.py`
- Temporary-project `rtk uv run paradev build <tmp>/minimal --emit-manifests --json`

## Risks Or Blockers

- Live Linear sync is still pending because no Linear MCP tool or `linear` CLI is available in this session.
- Diagnostics with no module/source path remain unchanged; diagnostics with unmatched source paths get best-effort path/module context only.
- Existing local desktop and README edits remain outside this diagnostics manifest slice.

## Next

- Start the layout-aware focus collection payload or add stricter source-map consistency diagnostics.
