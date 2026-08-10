# 2026-06-07 19:02 SDK Inspection Contract

## Scope

- Continued foundation work on `codex/scaffold-source-root-selection`.
- Focused on SDK discoverability for GUI, MCP, REST, importer, and CLI adapter agents.
- Added a stable capability payload for the read-only `Project.inspect(...)` dispatcher.

## Changes

- Added `Project.inspections()` with schema `paradev.sdk.inspections.v1`.
- Added `Project.inspect("inspections")` so adapters can discover supported inspection kinds through the same dispatcher they use for payloads.
- Added `paradev inspections <project> --json` as a thin CLI wrapper over the SDK dispatcher.
- Exported `PROJECT_INSPECTIONS_SCHEMA` from `paradev.sdk`.
- Derived public filter names from the existing SDK method signatures and omitted Python-only `registry` filters from the adapter-facing contract.
- Added indexes by inspection kind and filter name so clients can find which payloads support `module_id`, `kind`, `target_root`, and other filters without scanning every row.
- Updated English and Chinese manuals plus build-flow docs to point adapter authors to `Project.inspections()` and `paradev inspections`.

## Verification

- Red tests first:
  - `rtk uv run pytest tests/test_project.py::test_project_inspections_describes_sdk_dispatch_contract tests/test_project.py::test_project_cli_outputs_inspections_contract_json` failed with missing `Project.inspections()` and missing `inspections` CLI command.
- Focused green:
  - `rtk uv run pytest tests/test_project.py::test_project_inspections_describes_sdk_dispatch_contract tests/test_project.py::test_project_cli_outputs_inspections_contract_json`.
  - `rtk uv run pytest tests/test_project.py -k 'inspections or inspect or modules_manifest or filters_modules or dependencies or build_graph or build_explain or families'` (`58 passed`).
- SDK smoke:
  - `rtk uv run python` loading the minimal project and asserting `Project.inspect("inspections")` exposes `build-graph` and `module_id` indexes.
- CLI smoke:
  - `rtk uv run paradev inspections demos/assets/projects/minimal --json`.
- Format:
  - `rtk uv run black src/paradev/sdk/project.py src/paradev/sdk/__init__.py src/paradev/cli.py tests/test_project.py`.
- Heaven-style scan:
  - `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py src/paradev/sdk/__init__.py src/paradev/cli.py tests/test_project.py`.
- Whitespace review:
  - `rtk git diff --check`.
- Lint gate:
  - `rtk bash scripts/flake.bash --ci`.
- Test gate:
  - `rtk bash scripts/test.bash` (`357 passed`).
- Build gate:
  - `rtk uv build`.

## Review

- The new payload describes existing SDK methods instead of creating a parallel schema language.
- CLI behavior remains adapter-thin and project-load errors still use the existing Typer error path.
- The contract intentionally hides `registry` because GUI/MCP/REST clients should not pass Python registry objects.
- No PIHC3 migration or GUI files were touched.

## Linear

- Attempted to read `TAL-295`; Linear MCP returned `UNAUTHORIZED` / `Session expired`.
- Attempted to read `TAL-293`; Linear MCP returned the same auth error.
- Linear updates could not be posted from this session until the app is re-authenticated.
