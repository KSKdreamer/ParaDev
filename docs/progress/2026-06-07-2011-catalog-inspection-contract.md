# 2026-06-07 20:11 - Catalog Inspection Contract

## Scope

- Continued generic SDK/CLI stabilization on `codex/scaffold-source-root-selection`.
- Focused on shared adapter contracts for GUI, importer, MCP, REST, and CLI agents.
- Kept the slice read-only for the inspection dispatcher; catalog write/refresh remain explicit mutating commands/helpers.

## Changes

- Added `catalog-preview` and `catalog-query` to `Project.inspect(...)`.
- Added direct SDK methods `Project.catalog_preview(...)` and `Project.catalog_query(...)`.
- Updated `Project.inspections()` so adapters can discover the catalog kinds, filter names, and `hb catalog-*` CLI command labels.
- Routed read-only CLI commands `paradev hb catalog-preview` and `paradev hb catalog-query` through `Project.inspect(...)`.
- Updated the CLI surface contract metadata for the new SDK-owned HeavenBase adapter paths.
- Updated English and Chinese manual/developer docs plus the build-flow contract.

## Verification

- Red first:
  `rtk bash scripts/test.bash tests/test_project.py::test_project_inspections_describes_sdk_dispatch_contract tests/test_hb.py::test_project_inspect_catalog_preview_outputs_hb_payload tests/test_hb.py::test_project_inspect_catalog_query_reads_persisted_rows tests/test_hb.py::test_hb_catalog_query_cli_uses_sdk_inspection_dispatcher -q`
  failed because the SDK inspection contract had no catalog kinds and the CLI query still called the lower-level helper.
- Additional red:
  `rtk bash scripts/test.bash tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands -q`
  failed because the CLI surface contract did not advertise `hb catalog-preview` or `hb catalog-query`.
- Focused green:
  `rtk bash scripts/test.bash tests/test_project.py::test_project_inspections_describes_sdk_dispatch_contract tests/test_hb.py::test_project_inspect_catalog_preview_outputs_hb_payload tests/test_hb.py::test_project_inspect_catalog_query_reads_persisted_rows tests/test_hb.py::test_hb_catalog_query_cli_uses_sdk_inspection_dispatcher tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands -q`
  passed `5 passed`.
- Related:
  `rtk bash scripts/test.bash tests/test_architecture.py tests/test_project.py::test_project_cli_outputs_inspections_contract_json tests/test_hb.py -q`
  passed `27 passed`.
- Heaven-style scan:
  `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_hb.py tests/test_project.py tests/test_architecture.py`
  passed.
- Whitespace:
  `rtk git diff --check`
  passed.
- Lint:
  `rtk bash scripts/flake.bash --ci`
  passed.
- Full tests:
  `rtk bash scripts/test.bash`
  passed `368 passed`.
- SDK smoke:
  `rtk uv run python - <<'PY' ...`
  confirmed `Project.inspect("catalog-preview")` and `Project.inspect("catalog-query", entity="source-file", tag="loader:pdx")`.
- CLI smoke:
  `rtk zsh -lc 'tmp="$(mktemp -d)"; cp -R demos/assets/projects/minimal "$tmp/minimal"; rtk uv run paradev hb catalog-refresh "$tmp/minimal" --json >/dev/null; rtk uv run paradev hb catalog-query "$tmp/minimal" --entity source-file --tag loader:pdx --json >/dev/null; echo ok'`
  passed.
- Package build:
  `rtk uv build`
  built the sdist and wheel.
- Heaven-style review:
  Reviewed the final diff against the code-review checklist; no blocking findings.

## Notes

- This reduces special-case routing for external agents: catalog preview/query are now ordinary read-only inspection kinds.
- Users still see the simple CLI commands under `paradev hb`; developers can route GUI/MCP/REST actions through `Project.inspect(...)`.

## Next

- Continue keeping catalog rows, source inventory, source map, build graph, diagnostics, and generic compiler records aligned under the SDK inspection contract.
