# Frontend API Option Sources Progress

Date: 2026-06-08 10:17 CST

Linear: TAL-295, TAL-299

## Done

- Added canonical frontend operation `module.templates`, backed by `Project.templates`, CLI `templates`, REST `GET /projects/templates`, and MCP `project_templates`.
- Added SDK-owned frontend field option-source metadata with schema `paradev.sdk.frontend-api.option-source.v1`.
- Wired dynamic provider hints for authoring templates, source roots, families, module ids, collection ids, source paths, artifact paths/types, and diagnostic codes.
- Regenerated [frontend API reference](../user-manual/frontend-api-reference.md) and updated English/Chinese frontend API, SDK, developer, architecture docs.

## Verification

- Red tests first: focused frontend API contract checks failed on missing `FRONTEND_API_OPTION_SOURCE_SCHEMA`, missing `module.templates`, and missing `/projects/templates` binding.
- Focused green: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_frontend_api_form_fields_expose_sdk_owned_option_sources tests/test_architecture.py::test_frontend_api_workspace_projection_groups_gui_actions tests/test_architecture.py::test_frontend_api_binding_index_maps_surface_calls_to_operation_ids tests/test_architecture.py::test_openapi_seed_links_rest_operations_to_frontend_api_rows -q`.
- Frontend subset: `rtk uv run pytest tests/test_architecture.py tests/test_cli.py -q -k "frontend_api"` -> 21 passed.
- SDK/docs examples: `rtk bash scripts/test.bash tests/test_architecture.py tests/test_cli.py tests/test_sdk_examples.py -q` -> 75 passed.
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py src/paradev/sdk/__init__.py tests/test_architecture.py tests/test_cli.py` -> OK.
- Full tests: `rtk bash scripts/test.bash` -> 476 passed.
- Full flake: `rtk bash scripts/flake.bash --ci` -> clean.
- Package build: `rtk uv build` -> built sdist and wheel.
- Diff hygiene: `git diff --check` -> clean.

## Risks Or Blockers

- Initial Linear issue fetch through the Codex apps connector returned `auth_revoked`; comment sync worked through the Linear connector.
- Linear comments: TAL-295 `6f25ae30-9c5e-4079-8e4f-013f80c7258e`, TAL-299 `77a37469-03f8-4c47-a561-548f069ff059`.
- Option sources are provider hints, not a query executor; clients still choose SDK, REST, CLI, or MCP through existing bindings.

## Next

- Add provider rows for narrower slot/name/language fields once those payloads expose stable list-shaped option rows.
- Continue frontend API coverage for generic module compilation system actions without moving business logic into the GUI.
