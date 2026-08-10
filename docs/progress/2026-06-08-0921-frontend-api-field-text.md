# Frontend API Field Text Progress

Date: 2026-06-08 09:21 CST

Linear: TAL-295, TAL-299

## Done

- Added SDK-owned form field `label` and `description` metadata to `get_frontend_api_form(...)` for GUI, importer, CLI, REST, MCP, VS Code, and desktop clients.
- Added deterministic label fallbacks with canonical API acronyms such as ID, API, PDX, LSP, MCP, REST, SDK, URI, and JSON.
- Added field descriptions for current frontend API inputs, with context-aware `path` wording for project, PDX, and LSP operations.
- Regenerated `docs/user-manual/frontend-api-reference.md` and updated English/Chinese frontend API and SDK manual guidance.

## Verification

- `rtk uv run pytest tests/test_architecture.py tests/test_cli.py -q -k "frontend_api"` -> 16 passed, 35 deselected
- `rtk uv run paradev frontend-api --operation build.artifacts --form --json`
- `rtk git diff --check`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py` -> OK
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash` -> 472 passed
- `rtk uv build`
- Linear comments: TAL-295 `a7e4cda3-b38e-4757-8c73-ea6adbb01ca4`, TAL-299 `fd8caf0c-415c-4a58-be86-395ef40c4a80`

## Risks Or Blockers

- Field descriptions are intentionally concise and generic; operation-specific overrides are supported by `_input(...)` but not yet needed by current rows.

## Next

- Continue tightening frontend API ergonomics around generated client shapes and GUI action surfaces.
- Keep adding SDK-owned form metadata when new project, module, collection, PDX, LSP, build, catalog, or surface rows land.
