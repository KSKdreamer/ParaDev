# 2026-06-07 21:13 CST - Summary Manifest Build Views

## Scope

- Continued the generic ParaDev SDK/build modularity track rather than PIHC3-specific migration work.
- Moved the remaining summary/manifests projection ownership into `paradev.build.views`.
- Kept `Project.summary(...)` and `Project.manifests(...)` as thin SDK adapters so CLI, SDK, GUI, MCP, REST, importer, and compiler tests can share the same build-layer payload contract.
- Updated the English and Chinese user/developer manual sections to expose `summary_view(...)` and `manifests_view(...)`.

## TDD

- Red test:
  - `rtk bash scripts/test.bash tests/test_manifest_views.py -q`
  - Failed as expected with `ImportError: cannot import name 'manifests_view' from 'paradev.build'`.
- Added direct build-layer tests for:
  - `summary_view(result)` returning the existing `summary.json` manifest payload shape.
  - `manifests_view(result)` wrapping all manifest payloads with the stable `paradev.build.manifests.v1` schema.

## Verification

- `rtk uv run black src/paradev/build/views.py src/paradev/build/__init__.py src/paradev/sdk/project.py tests/test_manifest_views.py`
- `rtk bash scripts/test.bash tests/test_manifest_views.py tests/test_project.py::test_project_summary_returns_manifest_payload_without_writing tests/test_project.py::test_project_cli_outputs_summary_manifest_json_without_writing tests/test_project.py::test_project_manifests_returns_all_manifest_payloads_without_writing tests/test_project.py::test_project_inspections_describes_sdk_dispatch_contract -q`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/views.py src/paradev/build/__init__.py src/paradev/sdk/project.py tests/test_manifest_views.py tests/test_project.py`
- `rtk git diff --check`
- `rtk bash scripts/test.bash tests/test_manifest_views.py tests/test_project.py -q`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk uv build`

Result: targeted tests passed, Heaven-style scan passed, diff whitespace passed, flake passed, full suite passed with 379 tests, and package build produced the source distribution plus wheel.

## Review

- Heaven-style diff review found no blocking findings.
- The payload schema stays compatible with the previous SDK wrapper.
- The change reduces adapter-specific filtering/projection logic and keeps future surfaces pointed at the build layer instead of SDK-private methods.

## Next

- Continue the generic compiler/module system track by moving remaining reusable projection or compiler orchestration logic behind build-layer helpers before adding broader module compiler slots.
- Keep TAL-294 focused on modular SDK/build foundations and TAL-295 focused on CLI/Python SDK/user-manual usability.
