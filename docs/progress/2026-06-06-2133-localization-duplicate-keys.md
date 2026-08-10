# Localization Duplicate Keys Progress

Date: 2026-06-06 21:33 CST

Linear: TAL-294

## Done

- Added blocking `loc.duplicate_key` diagnostics for duplicate canonical localization keys.
- Checked duplicates after language alias normalization, so `en` and `l_english` collide as the same HOI4 language.
- Preserved loaded localization entries in dry-run results while preventing artifact emission when duplicates exist.
- Covered the loader-level diagnostic and default HOI4 profile blocking path.
- Documented duplicate localization behavior in the build-flow workflow.

## Verification

- `rtk bash scripts/test.bash tests/test_localization_loader.py::test_loc_loader_reports_duplicate_canonical_keys -q`
- `rtk bash scripts/test.bash tests/test_project_build.py::test_hoi4_profile_blocks_duplicate_canonical_localization_keys -q`
- `rtk bash scripts/test.bash tests/test_localization_loader.py tests/test_project_build.py -q`
- `rtk bash scripts/test.bash tests/test_localization_loader.py tests/test_project_build.py tests/test_project.py tests/test_sdk_examples.py tests/test_simple_source_family.py tests/test_module_sources.py tests/test_artifact_writers.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/loaders.py tests/test_localization_loader.py tests/test_project_build.py`
- `rtk uv run paradev build demos/assets/projects/minimal --emit-artifacts --json`

## Risks Or Blockers

- Live Linear sync is still pending because no Linear MCP tool or `linear` CLI is available in this session.
- Duplicate-key diagnostics are module-local for now; broader cross-module localization collision policy should be defined before global localization indexes.
- Existing local desktop and README edits remain outside this localization slice.

## Next

- Add localization scan/editor payloads that expose canonical language, key, source path, and duplicate diagnostic state for UI and MCP surfaces.
