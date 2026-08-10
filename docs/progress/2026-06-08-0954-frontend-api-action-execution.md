# Frontend API Action Execution Progress

Date: 2026-06-08 09:54 CST

Linear: TAL-295, TAL-299

## Done

- Added public `FRONTEND_API_ACTION_SCHEMA` for SDK-owned workspace action rows.
- Enriched `get_frontend_api_workspace()` action rows with derived execution hints, callable bindings, payload schema, form schema, normalizer schema, and REST request planner schema.
- Kept frontend-local actions such as `project.activate` in workspace state with no callable SDK or REST binding.
- Regenerated `docs/user-manual/frontend-api-reference.md` and updated English/Chinese frontend API, SDK, developer manual, and architecture guidance.

## Verification

- `rtk uv run pytest tests/test_architecture.py tests/test_cli.py -q -k "frontend_api"` -> 19 passed, 35 deselected
- `rtk uv run pytest tests/test_architecture.py tests/test_cli.py tests/test_sdk_examples.py -q -k "frontend_api or sdk_example"` -> 39 passed, 35 deselected
- `rtk git diff --check`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py src/paradev/sdk/__init__.py tests/test_architecture.py tests/test_cli.py` -> OK
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash` -> 475 passed
- `rtk uv build`
- Linear comments: TAL-295 `536c1220-333c-4fde-8738-6e4254967c34`, TAL-299 `d409c194-4556-44cf-8536-baff2c738553`

## Risks Or Blockers

- `execution.default_surface` is an SDK-owned default for GUI-style callers; other adapters should still use `execution.available_surfaces` and the copied `bindings` when they need SDK, MCP, LSP, or CLI execution.

## Next

- Continue frontend API maintenance with generated-client examples or project-derived option providers for values that cannot safely be static choices.
- Keep action execution metadata derived from canonical operation rows instead of adding GUI-only action registries.
