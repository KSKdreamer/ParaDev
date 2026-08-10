# Asset Metadata Progress

Date: 2026-06-07 00:30 CST

Linear: TAL-294 local continuation; live Linear sync unavailable

## Done

- Added lightweight PNG, DDS, and TGA header metadata sniffing to generic static copy source loading.
- Extended copy source and copy artifact metadata with media type, format, width, and height when the source header is readable.
- Kept unknown or malformed copy files on the existing hash-and-size path so static copy remains permissive.
- Covered loader-level metadata and end-to-end `SimpleSourceFamily` artifact metadata propagation.
- Documented copy asset metadata in `docs/workflows/build-flow.md`.

## Verification

- Red: `rtk bash scripts/test.bash tests/test_build_loaders.py::test_copy_loader_detects_image_metadata tests/test_simple_source_family.py::test_simple_source_family_copy_artifact_includes_image_metadata -q`
- Focused green: `rtk bash scripts/test.bash tests/test_build_loaders.py::test_copy_loader_detects_image_metadata tests/test_simple_source_family.py::test_simple_source_family_copy_artifact_includes_image_metadata -q`
- Related: `rtk bash scripts/test.bash tests/test_build_loaders.py tests/test_simple_source_family.py tests/test_project_build.py tests/test_build_manifest.py tests/test_build_records.py tests/test_module_sources.py -q`
- Full: `rtk bash scripts/test.bash`
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven-style: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/loaders.py tests/test_build_loaders.py tests/test_simple_source_family.py`
- CLI family smoke: `rtk uv run paradev families demos/assets/projects/minimal --json`
- CLI build smoke: `rtk uv run paradev build demos/assets/projects/minimal --json`
- Whitespace: `rtk git diff --check -- src/paradev/build/loaders.py tests/test_build_loaders.py tests/test_simple_source_family.py docs/workflows/build-flow.md docs/progress/2026-06-07-0030-asset-metadata.md`
- Linear probe: `rtk command -v linear`
- Linear connector probe: `tool_search` for Linear issue tools

## Risks Or Blockers

- Live Linear sync remains blocked because no Linear MCP tool is exposed and `linear` is not available on `PATH`.
- This is metadata sniffing only. It does not validate icon dimensions, convert formats, or generate sprite declarations yet.
- Existing local desktop, README, and script edits remain outside this slice.

## Next

- Add family-declared asset constraints, such as required dimensions or formats, so idea and achievement icons can report blocking diagnostics from the new copy metadata.
