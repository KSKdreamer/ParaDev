# Desktop Batch Preview Bridge Progress

Date: 2026-06-21 16:34

Linear: continuous goal

## Done

- Added a Tauri command, `paradev_module_batch_request`, that calls the SDK-owned `paradev module-batch-request` CLI and returns canonical batch request payloads with per-edit target preview rows.
- Added TypeScript service/types for desktop callers: `createModuleBatchRequest(...)`, `ModuleBatchEdit`, `ModuleBatchRequestPayload`, and `ModuleBatchRequestTarget`.
- Covered the bridge in Rust with a temp project that writes a starter module, previews one unchanged file and one missing migration note, and verifies no file is written by the preview.
- Covered the frontend invoke wrapper in `apps/desktop/src/services/paradev.test.ts`.

## Verification

- `rtk npm --prefix apps/desktop exec vitest run src/services/paradev.test.ts`
- `rtk cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml module_batch_request_command_returns_target_preview -- --nocapture`
- `rtk cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml`
- `rtk npm --prefix apps/desktop run build`
- `rtk proxy find projects/PIHC3 -name __pycache__ -o -name '*.pyc'`

## Risks Or Blockers

- The command is a bridge and not yet wired into a visible apply-review panel. It creates the stable GUI-accessible contract for that next step.

## Next

- Use `createModuleBatchRequest(...)` in source-edit apply-review flows so users can see SDK-resolved create/change/no-op targets before writing PIHC3 files.
