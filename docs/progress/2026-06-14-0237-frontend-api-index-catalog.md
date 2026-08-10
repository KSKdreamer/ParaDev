# Frontend API Index Catalog Progress

Date: 2026-06-14 02:37 +0800

Linear: none

## Done

- Added `get_frontend_api_index_catalog()` as a copied public SDK helper that documents each maintained frontend API index dimension.
- Rendered a generated Index Catalog table in the frontend API reference before the detailed group/status/mode/surface/binding/payload/workspace-section tables.
- Updated frontend API and Python SDK docs so users can find the helper when choosing an index path for generated clients, audits, or grouped API tables.
- Regenerated `docs/user-manual/frontend-api-reference.md`.
- Added targeted architecture and CLI assertions for the generated catalog rows.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_index_catalog_documents_lookup_helpers tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_index_catalog_documents_lookup_helpers tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py src/paradev/sdk/__init__.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py src/paradev/sdk/__init__.py tests/test_architecture.py tests/test_cli.py`

## Risks Or Blockers

- Full Python test suite was intentionally not run to avoid competing with concurrent PIHC3 migration work.
- The worktree still contains unrelated desktop, loader, PIHC3, and progress-note changes from other workers.

## Next

- Continue moving API-reference maintenance toward SDK-owned generated tables and copied helper APIs.
- Consider grouping REST/MCP/CLI operation tables by feature module once the contract index catalog is stable enough for downstream docs.
