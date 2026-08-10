# Localization Language Aliases Progress

Date: 2026-06-06 21:28 CST

Linear: TAL-294

## Done

- Added canonical localization language resolution for common HOI4 aliases.
- Normalized `.loc` language keys such as `en`, `fr`, `de`, `ru`, and `zh` before artifact planning.
- Covered alias normalization in the loader and default HOI4 profile output.
- Documented alias support in the build-flow workflow.

## Verification

- `rtk bash scripts/test.bash tests/test_localization_loader.py::test_loc_loader_normalizes_language_aliases -q`
- `rtk bash scripts/test.bash tests/test_localization_loader.py tests/test_project_build.py tests/test_project.py tests/test_sdk_examples.py tests/test_simple_source_family.py tests/test_module_sources.py tests/test_artifact_writers.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/localization src/paradev/build/loaders.py tests/test_localization_loader.py tests/test_project_build.py`
- `rtk uv run paradev build demos/assets/projects/minimal --emit-artifacts --json`

## Risks Or Blockers

- Live Linear sync is still pending because no Linear MCP tool or `linear` CLI is available in this session.
- Alias coverage is intentionally small and common; fuller HOI4 localization validation remains future work.
- Existing local desktop and README edits remain outside this localization slice.

## Next

- Add duplicate-key localization diagnostics before broadening localization scan/editor payloads.
