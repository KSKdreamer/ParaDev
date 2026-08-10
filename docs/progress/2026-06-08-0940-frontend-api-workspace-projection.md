# Frontend API Workspace Projection Progress

Date: 2026-06-08 09:40 CST

Linear: TAL-295, TAL-299

## Done

- Added SDK-owned `get_frontend_api_workspace()` and `FRONTEND_API_WORKSPACE_SCHEMA` as the maintained GUI navigation/action projection over canonical frontend operation ids.
- Exposed the same projection through `paradev frontend-api --workspace --json` and REST/OpenAPI `GET /frontend-api/workspace`.
- Grouped canonical rows into project switcher, project browser, authoring, source editor, build, catalog, and surface-contract sections.
- Regenerated `docs/user-manual/frontend-api-reference.md` and updated English/Chinese frontend API and Python SDK manual guidance.

## Verification

- `rtk uv run pytest tests/test_architecture.py tests/test_cli.py -q -k "frontend_api"` -> 18 passed, 35 deselected
- `rtk uv run paradev frontend-api --workspace --json`
- `rtk git diff --check`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py src/paradev/sdk/__init__.py src/paradev/cli.py src/paradev/surfaces/rest.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py` -> OK
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash` -> 474 passed
- `rtk uv build`
- Linear comments: TAL-295 `daedc807-a7d5-4c7c-a5d8-f7efaaa5ad6e`, TAL-299 `1693132e-5e8d-4398-a480-ceaeb85d9cad`

## Risks Or Blockers

- The projection intentionally carries section and action grouping only; richer generated client execution hints should still derive from the canonical operation rows.

## Next

- Continue frontend-facing API maintenance with SDK-derived generated client/action shapes if the GUI needs richer execution metadata.
- Keep project, module, collection, PDX, LSP, build, catalog, and surface rows as the source of truth for all frontend projections.
