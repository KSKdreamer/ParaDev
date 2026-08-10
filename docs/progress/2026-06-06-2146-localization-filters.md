# Localization Filters Progress

Date: 2026-06-06 21:46 CST

Linear: TAL-294

## Done

- Added SDK filters to `Project.localization(...)` for language, key prefix, and module id.
- Normalized language aliases in the SDK filter, so `en` matches `l_english`.
- Added matching CLI flags: `--language`, `--key-prefix`, and `--module`.
- Covered SDK and CLI filtering against the minimal demo project.
- Documented localization filter usage in the build-flow workflow.

## Verification

- `rtk bash scripts/test.bash tests/test_project.py::test_project_localization_filters_rows_by_language_alias_key_prefix_and_module tests/test_project.py::test_project_cli_filters_localization_manifest_json -q`
- `rtk bash scripts/test.bash tests/test_project.py tests/test_sdk_examples.py tests/test_build_manifest.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py src/paradev/cli.py tests/test_project.py`
- `rtk uv run paradev localization demos/assets/projects/minimal --language en --key-prefix GER_sample_d --module focus/GER_sample --json`

## Risks Or Blockers

- Live Linear sync is still pending because no Linear MCP tool or `linear` CLI is available in this session.
- Filters are intentionally read-only and in-memory over the build payload; indexed search remains future work.
- Existing local desktop and README edits remain outside this SDK/CLI slice.

## Next

- Define the project-level localization collision policy before adding cross-module duplicate diagnostics or a persistent localization index.
