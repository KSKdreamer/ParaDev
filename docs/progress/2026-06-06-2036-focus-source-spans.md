# Focus Source Span Progress

Date: 2026-06-06 20:36 CST

Linear: TAL-293

## Done

- Added parser-backed scalar span annotations for PDX values.
- Threaded focus ID and prerequisite value spans into focus collection diagnostics.
- Covered duplicate focus ID and missing project-local prerequisite diagnostics with line/column assertions.
- Updated the build-flow docs with the diagnostic source-span boundary.

## Verification

- `rtk bash scripts/test.bash tests/test_pdx_roundtrip.py tests/test_simple_source_family.py -q`
- `rtk bash scripts/test.bash tests/test_pdx_token.py tests/test_pdx_roundtrip.py tests/test_build_loaders.py tests/test_simple_source_family.py tests/test_build_manifest.py tests/test_project.py tests/test_project_build.py tests/test_sdk_examples.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/pdx/parser.py src/paradev/build/families.py tests/test_pdx_roundtrip.py tests/test_simple_source_family.py`
- `rtk uv run paradev build demos/assets/projects/minimal --json`

## Risks Or Blockers

- Live Linear sync is still pending because no Linear MCP tool or `linear` CLI is available in this session.
- Spans are scalar start positions, not full ranges; richer source maps remain a future LSP/editor slice.
- Existing local desktop and README edits remain outside this source-span slice.

## Next

- Add source-map entries for diagnostic owners or artifact input slots, then move toward layout-aware focus collection compilation.
