# Frontend API Action Detail Progress

Date: 2026-06-08 11:07 CST

Linear: TAL-295

## Done

- Added `get_frontend_api_action(operation_id)` and `FRONTEND_API_ACTION_DETAIL_SCHEMA` as the SDK-owned selected-action payload for GUI, REST, CLI, and generated clients.
- Exposed the same payload through CLI `frontend-api --operation ... --action` and REST/OpenAPI `GET /frontend-api/action?operation_id=...`.
- Added the canonical `surface.frontend_api.action` operation row, workspace grouping, binding indexes, CLI contract projection, and generated frontend API reference entry.
- Updated English and Chinese user/developer manuals plus the architecture interface contract to route selected-action UI through the SDK helper.
- Self-reviewed the diff for duplicate frontend routing, stale hand-maintained maps, and docs/code drift; no blocking findings remained.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py tests/test_cli.py -q` -> 62 passed.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py -q` -> 20 passed.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py src/paradev/sdk/__init__.py src/paradev/cli.py src/paradev/surfaces/rest.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py` -> OK.
- `rtk bash scripts/flake.bash --ci` -> OK, 54 files unchanged.
- `rtk bash scripts/test.bash` -> 483 passed.
- `rtk uv build` -> source distribution and wheel built.
- `rtk git diff --check` -> clean.

## Risks Or Blockers

- Linear update is still blocked by revoked/expired authentication in this environment; `_save_comment` returned `UNAUTHORIZED` / session expired. Local TAL-295 progress is recorded here until auth is restored.

## Next

- Continue front-end-facing API stabilization by adding similarly SDK-owned detail/projection helpers only where they remove GUI-side stitching, starting with module/project action payload gaps.
- Keep `docs/user-manual/frontend-api-reference.md` regenerated whenever the canonical operation table changes.
