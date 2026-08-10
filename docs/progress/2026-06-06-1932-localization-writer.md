# Localization Writer Progress

Date: 2026-06-06 19:32 CST

Linear: TAL-294

## Done

- Added `LocalizationYMLWriter` for `loc` artifacts backed by `LocalizationEntry` payloads.
- Extended `SimpleSourceFamily` to group localization entries by language and emit one artifact per language.
- Added language-aware path template fields: `{language}` and `{language_folder}`.
- Registered the localization writer and localization path template in the initial `hoi4` scaffold profile.
- Covered source-bundle localization artifact planning and file writing with a focused test.

## Verification

- `rtk uv run pytest tests/test_simple_source_family.py -q`
- `rtk uv run pytest tests/test_simple_source_family.py tests/test_artifact_writers.py tests/test_localization_loader.py tests/test_project_build.py tests/test_module_sources.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build src/paradev/games tests/test_simple_source_family.py`

## Risks Or Blockers

- Live Linear sync is still pending because no Linear MCP tool or `linear` CLI is available in this session.
- The localization writer currently emits a minimal deterministic YML shape; fuller HOI4 localization validation remains future work.
- Existing local desktop and README edits remain outside this localization-writer slice.

## Next

- Add project/demo localization fixtures so the default HOI4 scaffold profile can be smoke-tested from the CLI with planned PDX and localization artifacts.
