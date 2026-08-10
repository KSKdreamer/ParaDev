# 2026-06-07 18:55 SDK Inspection Dispatcher

## Scope

- Continued foundation work on `codex/scaffold-source-root-selection`.
- Focused on SDK generality for GUI, MCP, REST, importer, and CLI adapters.
- Added a single read-only project inspection dispatcher so adapter code can route by user-selected kind without duplicating CLI command tables or build-surface logic.

## Changes

- Added `Project.inspect(kind, **filters)` for SDK-owned read-only inspection payloads.
- Supported `summary`, `manifests`, `modules`, `collections`, `artifacts`, `localization`, `assets`, `sprites`, `diagnostics`, `source-map`, `dependencies`, `build-graph`, `build-explain`, and `families`.
- Made the `kind` selector positional-only so inspection filters can still include `kind`, such as dependency edge kind or family compiler kind.
- Validated unsupported filters before dispatch while preserving internal `TypeError` failures from the selected SDK method.
- Routed read-only build inspection CLI commands through `Project.inspect(...)` while preserving their command names, options, and payload shapes.
- Updated the English and Chinese SDK/developer manuals plus build-flow docs for adapter authors.

## Verification

- Red tests first:
  - `rtk uv run pytest tests/test_project.py::test_project_inspect_dispatches_filtered_modules_payload_without_writing tests/test_project.py::test_project_cli_modules_uses_sdk_inspection_dispatcher` failed with missing `Project.inspect` and direct CLI `.modules(...)` routing.
  - `rtk uv run pytest tests/test_project.py::test_project_inspect_rejects_unsupported_filter_without_hiding_method_errors` failed while the dispatcher caught an internal `TypeError`.
  - Full `rtk bash scripts/test.bash` initially failed three CLI tests because the selector name conflicted with `kind` filters.
- Focused green:
  - `rtk uv run pytest tests/test_project.py::test_project_inspect_dispatches_filtered_modules_payload_without_writing tests/test_project.py::test_project_inspect_rejects_unknown_kind tests/test_project.py::test_project_inspect_rejects_unsupported_filter_without_hiding_method_errors tests/test_project.py::test_project_cli_modules_uses_sdk_inspection_dispatcher`.
  - `rtk uv run pytest tests/test_project.py::test_project_inspect_allows_kind_as_filter_name tests/test_project.py::test_project_cli_outputs_profile_family_contracts tests/test_project.py::test_project_cli_filters_profile_family_contracts tests/test_project.py::test_project_cli_filters_dependency_manifest_json`.
  - `rtk uv run pytest tests/test_project.py -k 'inspect or modules_manifest or filters_modules or collections_manifest or artifacts_manifest or localization_manifest or diagnostics or source_map or dependencies or build_graph or build_explain or families'` (`69 passed`).
- SDK smoke:
  - `rtk uv run python` loading the minimal project and calling `Project.inspect("source-map", module_id="focus/GER_sample")`.
  - `rtk uv run python` calling `Project.inspect("modules", family="focus")` and `Project.inspect("build_graph", module_id="focus/GER_sample")`.
- CLI smoke:
  - `rtk uv run paradev modules demos/assets/projects/minimal --family focus --module focus/GER_sample --slot def --json`.
- Format:
  - `rtk uv run black src/paradev/sdk/project.py src/paradev/cli.py tests/test_project.py`.
- Heaven-style scan:
  - `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py src/paradev/cli.py tests/test_project.py`.
- Whitespace review:
  - `rtk git diff --check`.
- Lint gate:
  - `rtk bash scripts/flake.bash --ci`.
- Test gate:
  - `rtk bash scripts/test.bash` (`355 passed`).
- Build gate:
  - `rtk uv build`.

## Review

- The dispatcher reduces adapter surface area without removing direct SDK methods for normal Python scripts.
- CLI commands remain stable for mod authors; the change is internal routing through the SDK.
- The positional-only selector preserves filter names that already exist in build payloads.
- No PIHC3 migration or GUI files were touched.

## Linear

- Attempted to read `TAL-295`; Linear MCP returned `UNAUTHORIZED` / `Session expired`.
- Attempted to read `TAL-293`; Linear MCP returned the same auth error.
- Linear updates could not be posted from this session until the app is re-authenticated.
