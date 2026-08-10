# Frontend API Master Catalog Progress

Date: 2026-06-08 21:18 CST

Linear: TAL-299, TAL-295

## Done

- Added `src/paradev/sdk/frontend_api.py` as the master-line SDK-owned frontend-facing operation catalog.
- Exposed `get_frontend_api_contract()`, `get_frontend_api_group()`, `get_frontend_api_operation()`, and `render_frontend_api_markdown()` from `paradev.sdk`.
- Added `paradev frontend-api` with full JSON, `--group`, `--operation`, and `--markdown` projections.
- Generated `docs/user-manual/frontend-api-reference.md` from the CLI and added the bilingual [Frontend-Facing API](../user-manual/frontend-api.md) manual page.
- Updated the user manual index, Python SDK manual, developer manual, and architecture interfaces to make the SDK catalog the integration source of truth for GUI, REST, MCP, VS Code, LSP, importer, and desktop agents.
- Kept the catalog honest about current `master`: 65 operations, 50 implemented rows, 14 planned canonical target rows, and 1 frontend-local row.
- Posted Linear comments: `TAL-299` comment `59e73fb5-8b0f-4f4c-a037-89c0258a737c`; `TAL-295` comment `bd4156e6-ab10-4d8b-8a81-269eaefb68a3`.

## Verification

- `rtk python -m py_compile src/paradev/sdk/frontend_api.py src/paradev/sdk/__init__.py src/paradev/cli.py`: passed.
- `rtk uv run black --check src/paradev/sdk/frontend_api.py src/paradev/sdk/__init__.py src/paradev/cli.py tests/test_architecture.py tests/test_cli.py`: passed.
- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_catalog_lists_master_line_operations tests/test_cli.py::test_frontend_api_cli_outputs_contract_json tests/test_cli.py::test_frontend_api_cli_selects_operation_group_and_markdown -q`: passed, 3 tests.
- `rtk bash scripts/test.bash tests/test_architecture.py tests/test_cli.py -q`: passed, 29 tests and 1 skipped for missing optional `fastapi.testclient`.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py src/paradev/sdk/__init__.py src/paradev/cli.py tests/test_architecture.py tests/test_cli.py`: passed, 5 files.
- `rtk bash scripts/flake.bash --ci`: passed.
- `rtk git diff --check`: passed.
- `rtk uv build`: passed and included `paradev/sdk/frontend_api.py` in the wheel.

## Risks Or Blockers

- This is the compact master-line catalog, not the full `codex/frontend-api-master-reconcile` TypeScript/helper/REST-planner branch. That larger branch still needs a dedicated reconciliation gate.
- Rows marked `planned` are canonical target shapes only; frontend agents should not call them until a later SDK/CLI/REST slice changes them to `implemented`.
- The app-scoped Linear connector remains expired; use direct `mcp__linear` comments until OAuth is refreshed.

## Next

- Reconcile the large frontend API branch onto current `master`, or incrementally port its REST planner/workspace/action helpers into reviewable master-line slices.
- Promote the most important planned rows next: module edit/rename/remove, collection create/edit/rename/remove, and LSP text-buffer diagnostics/formatting.
