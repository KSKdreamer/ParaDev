# 2026-06-29 15:41 - Module Rename REST Planning

## Slice

Moved the native-web `renameModule(...)` path from a bespoke desktop bridge
route to the SDK-generated frontend API REST planning contract.

## Changes

- Kept the Tauri path on the direct Python SDK helper.
- Changed native-web `renameModule(...)` to plan `module.rename` through
  `/frontend-api/rest-request?operation_id=module.rename`, then execute the
  returned `PATCH /projects/modules/rename` request.
- Lazy-loaded the generated frontend API helper so the generated contract stays
  out of the main app bundle until this native-web path needs it.
- Added a regression test that rejects `/desktop/modules/rename` for
  native-web module rename calls.

## Verification

- Red check before the fix:
  `rtk npm --prefix apps/desktop test -- src/services/paradev.test.ts -t "renames modules through generated REST planning"`
  returned the REST-plan payload instead of the module rename payload.
- `rtk npm --prefix apps/desktop test -- src/services/paradev.test.ts -t "renames modules through generated REST planning"`
- `rtk npm --prefix apps/desktop test -- src/services/paradev.test.ts`
- `rtk npm --prefix apps/desktop run build`
- `rtk npm --prefix apps/desktop test`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- Read-only subagent review found no scoped findings.
- `rtk bash scripts/run.bash --tauri --port 5213`
- Captured native PIHC3 Tauri smoke screenshot:
  `/tmp/paradev-tauri-rename-rest-plan.png`.
- `rtk git diff --check`

## Notes

- Remaining related native-web alignment work includes source text, module draft,
  and draft apply routes, which still use bespoke `/desktop/...` bridge paths.
- PIHC3 remained clean during this slice.
