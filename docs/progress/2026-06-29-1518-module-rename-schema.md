# 2026-06-29 15:18 - Module Rename Schema Alignment

## Slice

Aligned the desktop TypeScript module rename payload contract with the Python SDK
schema.

## Changes

- Changed `ModuleRenamePayload.schema` in the desktop service from the stale
  `paradev.sdk.module_rename.v1` literal to the SDK/generated frontend API
  literal, `paradev.module.rename.v1`.
- Added a desktop service regression fixture that types a Tauri
  `renameModule` payload with the canonical SDK schema and verifies the bridge
  request shape.

## Verification

- Red check before the fix: `rtk npm --prefix apps/desktop run build` failed
  because `paradev.module.rename.v1` was not assignable to the stale TypeScript
  literal.
- `rtk npm --prefix apps/desktop test -- src/services/paradev.test.ts`
- `rtk npm --prefix apps/desktop run build`
- `rtk npm --prefix apps/desktop test`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/run.bash --tauri --port 5209`
- Captured native Tauri smoke screenshot:
  `/tmp/paradev-tauri-module-rename-schema.png`.
- `rtk git diff --check`

## Notes

- A read-only subagent independently confirmed the canonical schema across the
  Python SDK, CLI, REST routes, MCP metadata, generated frontend API, Tauri
  bridge, and GUI caller.
- PIHC3 remained clean during this slice.
