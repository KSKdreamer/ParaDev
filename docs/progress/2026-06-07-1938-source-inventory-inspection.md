# 2026-06-07 19:38 Source Inventory Inspection

## Scope

- Continued foundation work on `codex/scaffold-source-root-selection`.
- Focused on generic SDK/build modularity for GUI, importer, MCP, REST, and CLI clients.
- Added a compiler-input inventory separate from artifact traceability, without touching PIHC3 migration or GUI files.

## Changes

- Added `sources.json` with schema `paradev.build.sources.v1`.
- Added source inventory rows for module-owned and collection-owned inputs, including owner, family, root, slot, resolved path, relative path, generic loader, load status, loader-specific summaries, and source-anchored diagnostic codes.
- Added `source_inventory_index(...)` and exported it from `paradev.build`.
- Added `Project.sources(...)`, `Project.inspect("sources", ...)`, and a `paradev sources` CLI command with `family`, `module`, `collection`, `slot`, `loader`, and `status` filters.
- Added `sources` to the CLI surface contract and project inspection contract.
- Updated the English and Chinese user/developer manuals, build workflow docs, and final architecture manifest list.

## Verification

- Red tests first:
  - `rtk uv run pytest tests/test_build_manifest.py::test_manifest_payloads_and_writes_include_source_map_and_summary tests/test_project.py::test_project_inspections_describes_sdk_dispatch_contract tests/test_project.py::test_project_sources_returns_filtered_compiler_input_payload_without_writing tests/test_project.py::test_project_cli_filters_sources_manifest_json` failed because `sources.json`, `Project.sources`, inspection metadata, and CLI command did not exist.
  - `rtk uv run pytest tests/test_build_manifest.py::test_sources_manifest_does_not_attach_unanchored_owner_diagnostics` failed before the diagnostic matcher fix because owner-level diagnostics were copied to source rows.
- Focused green:
  - `rtk uv run pytest tests/test_build_manifest.py::test_sources_manifest_does_not_attach_unanchored_owner_diagnostics tests/test_build_manifest.py tests/test_project.py tests/test_architecture.py tests/test_cli.py` (`151 passed`).
  - `rtk uv run paradev sources demos/assets/projects/minimal --module focus/GER_sample --loader pdx --json`.
- Format:
  - `rtk uv run black src/paradev/build/__init__.py src/paradev/build/manifest.py src/paradev/sdk/project.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_build_manifest.py tests/test_project.py tests/test_architecture.py`.
- Heaven-style scan:
  - `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/__init__.py src/paradev/build/manifest.py src/paradev/sdk/project.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_build_manifest.py tests/test_project.py tests/test_architecture.py`.
- Whitespace review:
  - `rtk git diff --check`.
- Lint gate:
  - `rtk bash scripts/flake.bash --ci`.
- Test gate:
  - `rtk bash scripts/test.bash` (`364 passed`).
- Build gate:
  - `rtk uv build`.

## Review

- `sources.json` answers "what did ParaDev recognize and load?" while `source-map.json` remains "which artifacts use which source inputs?".
- Source rows include source-anchored diagnostics only; module-level or family-level diagnostics without source path or slot do not attach to every source row.
- The SDK remains the single dispatch point for CLI and future adapters through `Project.inspect("sources", ...)`.
- No PIHC3 migration files or GUI files were touched.

## Linear

- Attempted to read `TAL-293`; Linear MCP returned `UNAUTHORIZED` / `Session expired`.
- Linear updates could not be posted from this session until the app is re-authenticated.
