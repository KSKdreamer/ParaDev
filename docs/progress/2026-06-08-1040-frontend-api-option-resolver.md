# 2026-06-08 10:40 Frontend API Option Resolver

## Scope

- Added `resolve_frontend_api_options(...)` as the canonical SDK executor for frontend `option_source` metadata.
- Added the public `paradev.sdk.frontend-api.options.v1` payload schema.
- Exposed the resolver through CLI `frontend-api --operation ... --option-field ... --values-json ...`.
- Exposed the resolver through REST/OpenAPI `POST /frontend-api/options?operation_id=...&field_name=...`.
- Added `surface.frontend_api.options` to the maintained frontend API contract, workspace surface-contract section, binding index, and CLI surface projections.
- Updated the English and Chinese user/developer manuals plus the generated frontend API reference.

## User-Facing Value

GUI, importer, and desktop clients no longer need to hand-call provider rows or hardcode templates, source roots, module ids, collection ids, artifact choices, or diagnostic codes. A client can render a form from `get_frontend_api_form(...)`, then call `resolve_frontend_api_options(operation_id, field_name, values)` for any field with `option_source`. If required upstream fields are missing, the payload returns `available=false` and `missing_requirements` instead of raising.

## Verification

- Red test confirmed the missing public schema, resolver export, and CLI flag.
- `rtk bash scripts/test.bash tests/test_architecture.py tests/test_cli.py -q`
- `rtk bash scripts/test.bash tests/test_sdk_examples.py -q`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py src/paradev/sdk/__init__.py src/paradev/cli.py src/paradev/surfaces/rest.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk uv build`

## Next

- Continue stabilizing frontend-facing APIs by adding more executable helpers where the contract still only describes behavior.
- Keep expanding user-manual examples from the perspective of a HoI4 mod developer and a GUI/importer implementer.
