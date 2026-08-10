# Frontend API TypeScript Contract Progress

Date: 2026-06-08 11:27 CST

Linear: TAL-295

## Done

- Added `render_frontend_api_typescript()` as the SDK-owned generator for TypeScript frontend API contracts.
- Exposed CLI `frontend-api --typescript` and added `typescript` to the static CLI projection contract.
- Generated `apps/desktop/src/generated/frontendApi.ts` with operation id, group id, status, and workspace-section unions plus the full `PARADEV_FRONTEND_API_CONTRACT`.
- Updated English and Chinese user/developer manuals, architecture docs, and the generated frontend API reference so GUI agents import the generated contract instead of hand-maintaining action lists.
- Self-reviewed the diff for deterministic generation, CLI conflict handling, generated-file drift coverage, and GUI-side duplication risks; no blocking findings remained.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py tests/test_cli.py -q` -> 64 passed.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py -q` -> 20 passed.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py src/paradev/sdk/__init__.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py` -> OK.
- `rtk bash scripts/flake.bash --ci` -> OK, 54 files unchanged.
- `rtk npm --prefix apps/desktop run build` -> TypeScript check and Vite build passed.
- `rtk bash scripts/test.bash` -> 485 passed.
- `rtk uv build` -> source distribution and wheel built.
- `rtk git diff --check` -> clean.

## Risks Or Blockers

- Linear update is still blocked by revoked/expired authentication in this environment; `_save_comment` returned `UNAUTHORIZED` / session expired. Local TAL-295 progress is recorded here until auth is restored.

## Next

- Continue front-end-facing API stabilization by adding SDK-owned generated/client-facing projections only where they remove GUI-side stitching without creating a second router.
- Keep `docs/user-manual/frontend-api-reference.md` and `apps/desktop/src/generated/frontendApi.ts` regenerated whenever the canonical operation table changes.
