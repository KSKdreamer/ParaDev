# Build Catalog And Surface Frontend API Inputs

Date: 2026-06-08 04:13 CST

Issues: TAL-299, TAL-295

Linear comments:

- TAL-299: `0cd773f8-6ccf-43b5-96ef-1d3840af356c`
- TAL-295: `787fa8b9-9635-49fb-9f62-e6740870933c`

## Summary

- Added canonical `inputs` metadata to build frontend API rows for plan, emit, summary, manifests, artifacts, localization, diagnostics, source map, dependencies, graph, explain, and families views.
- Added canonical `inputs` metadata to catalog rows for preview, write, refresh, and query flows.
- Added selector `inputs` to `surface.frontend_api` so GUI, importer, and PIHC3-facing agents can discover operation/group lookup fields from the SDK contract.
- Added `maps_to` metadata to support frontend-safe aliases such as `build.artifacts` `artifact_path -> path`, avoiding a collision with the loaded project `path`.
- Updated the English and Chinese frontend API manual, SDK manual, developer manual, and architecture interface contract.

## Verification

- Red test: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations -q` failed on missing `build.plan["inputs"]`.
- Focused green: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations -q` passed.
- Lookup coverage: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_frontend_api_lookup_helpers_return_canonical_rows -q` passed.
- SDK probe: `rtk uv run python - <<'PY' ... get_frontend_api_operation(...) ... PY` confirmed build, catalog, and surface inputs through the public SDK.
- Docs/source check: `rtk rg -n 'Build rows use project|build 行使用项目|build_artifacts_inputs|catalog_query_inputs|frontend_selector_inputs|Build, catalog, and surface rows|artifact_path.*maps_to|input_names\("build|input_names\("catalog|surface\.frontend_api.*inputs' src/paradev/sdk/frontend_api.py tests/test_architecture.py docs/user-manual docs/architecture/interfaces.md`
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py`
- Formatting: `rtk bash scripts/flake.bash --ci`
- Full tests: `rtk bash scripts/test.bash` (`443 passed`)
- Package build: `rtk uv build`

## Review

- This is contract metadata only; it does not change build execution, catalog persistence, REST routing, MCP behavior, or CLI command semantics.
- Build and catalog forms now have one maintained frontend source of truth beside the SDK methods they call.
- The `artifact_path` alias keeps user-facing build-artifact filters clear while preserving compatibility with existing SDK inspection filter names.
