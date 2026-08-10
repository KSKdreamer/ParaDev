# Localization Index Progress

Date: 2026-06-06 22:04 CST

Linear: TAL-294

## Done

- Added a deterministic `index` section to `paradev.build.localization.v1` payloads, keyed by canonical language and localization key.
- Preserved all localization rows while letting the index point to row numbers and duplicate state, avoiding premature replace/shadow semantics.
- Added exact-key SDK and CLI filtering through `Project.localization(key=...)` and `paradev localization --key`.
- Documented the filtered lookup flow and manifest index contract in the build-flow workflow.

## Verification

- `rtk bash scripts/test.bash tests/test_build_manifest.py::test_manifest_payloads_include_localization_scan_rows_with_duplicate_state tests/test_project.py::test_project_localization_filters_rows_by_language_alias_key_prefix_and_module tests/test_project.py::test_project_cli_filters_localization_manifest_json -q`
- `rtk bash scripts/test.bash tests/test_build_manifest.py tests/test_project.py tests/test_project_build.py tests/test_sdk_examples.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/manifest.py src/paradev/build/__init__.py src/paradev/sdk/project.py src/paradev/cli.py tests/test_build_manifest.py tests/test_project.py`
- `rtk uv run paradev localization demos/assets/projects/minimal --language en --key GER_sample_desc --json`
- `rtk uv run paradev build demos/assets/projects/minimal --emit-manifests --json`

## Risks Or Blockers

- Live Linear sync is still pending because no Linear MCP tool or `linear` CLI is available in this session.
- The index intentionally references row numbers instead of choosing a winning translation; replace/shadow policy remains future work.
- Existing local desktop and README edits remain outside this localization index slice.

## Next

- Define replace/shadow semantics for localization collisions or move from localization lookup into the next simple PDX-plus-loc family.
