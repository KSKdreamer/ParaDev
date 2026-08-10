# Build Manifest Views

Date: 2026-06-07 21:04 Asia/Shanghai

Branch: `codex/scaffold-source-root-selection`

Issues: TAL-294, TAL-295

## Summary

- Added reusable build-layer manifest view helpers: `modules_view`, `collections_view`, `artifacts_view`, `localization_view`, `assets_view`, `sources_view`, `sprites_view`, `diagnostics_view`, `source_map_view`, and `dependencies_view`.
- Moved manifest row filtering and rebuilt-index logic out of `Project` private helpers into `paradev.build.views`.
- Kept SDK methods and CLI inspection payloads stable; `Project` now builds once and delegates filtered manifest projections to the build layer.
- Added direct build-layer tests for source inventory filters, artifact contributor filters, and diagnostics resolved-source matching.
- Updated English and Chinese SDK/developer manual guidance plus build-flow docs for GUI, MCP, REST, importer, and compiler-test authors.

## TDD Notes

- Red first:
  `rtk bash scripts/test.bash tests/test_manifest_views.py -q`
  failed with `ImportError: cannot import name 'artifacts_view' from 'paradev.build'`.
- Green focused set:
  `rtk bash scripts/test.bash tests/test_manifest_views.py tests/test_project.py::test_project_modules_returns_filtered_manifest_payload_without_writing tests/test_project.py::test_project_collections_returns_filtered_manifest_payload_without_writing tests/test_project.py::test_project_artifacts_returns_filtered_manifest_payload_without_writing tests/test_project.py::test_project_assets_returns_filtered_manifest_payload_without_writing tests/test_project.py::test_project_sources_returns_filtered_compiler_input_payload_without_writing tests/test_project.py::test_project_sprites_returns_filtered_manifest_payload_without_writing tests/test_project.py::test_project_diagnostics_returns_filtered_manifest_payload_without_writing tests/test_project.py::test_project_source_map_returns_filtered_manifest_payload_without_writing tests/test_project.py::test_project_dependencies_returns_filtered_manifest_payload_without_writing tests/test_project.py::test_project_inspections_describes_sdk_dispatch_contract tests/test_project.py::test_project_cli_outputs_inspections_contract_json -q`
  passed 14 tests.
- Wider project regression:
  `rtk bash scripts/test.bash tests/test_manifest_views.py tests/test_project.py -q`
  passed 128 tests.

## Verification

- `rtk uv run black src/paradev/build/views.py src/paradev/build/__init__.py src/paradev/sdk/project.py tests/test_manifest_views.py`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/views.py src/paradev/build/__init__.py src/paradev/sdk/project.py tests/test_manifest_views.py tests/test_project.py`
- `rtk git diff --check`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash` passed 377 tests.
- `rtk uv build`

## Review

Heaven-style diff review found no blocking findings. The public surface stays the same for HoI4 mod developers, while adapter and compiler authors now have one build-owned place to project filtered manifest payloads from a `BuildResult`.

## Next

- Continue TAL-294 by moving the next SDK-only build projection or generic compiler affordance into `paradev.build`.
- Keep TAL-295 manual guidance current for GUI/MCP and PIHC3 migration agents consuming these contracts.
