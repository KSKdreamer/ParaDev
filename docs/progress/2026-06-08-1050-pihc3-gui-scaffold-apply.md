# PIHC3 GUI Scaffold Apply Progress

Date: 2026-06-08 10:50 CST

Linear: TAL-297

## Done

- Added desktop model coverage for applying a written SDK scaffold plan to a local module entity.
- Added `canApplyScaffoldDraft(...)` and `applyScaffoldPlanToEntity(...)` so a written new-template draft becomes a clean entity with real source paths from the SDK plan.
- Wired the module editor Apply action for new scaffold drafts in Tauri:
  - reruns `createModuleDraft(...)` with `write: true`;
  - shows blocked SDK diagnostics inline;
  - marks the written draft clean when the plan reports `written: true`.
- Kept plain Vite and non-scaffold edits draft-only.
- Added a Tauri Rust test that creates a temporary project and verifies `paradev_create_module_draft` writes scaffold files without touching PIHC3.
- Updated `docs/architecture/interfaces.md` and `docs/techstack/ui/gui-spec.md`.

## Verification

- Red check: `rtk npm --prefix apps/desktop run test:model` failed first because `applyScaffoldPlanToEntity` was missing.
- `rtk npm --prefix apps/desktop run test:model`: 7 passed.
- `rtk npm --prefix apps/desktop run build`: passed.
- `rtk bash -lc 'cd apps/desktop/src-tauri && cargo test'`: 5 passed.
- Scaffold-facing Python subset: 8 passed.
- `rtk uv run paradev build projects/PIHC3 --emit-manifests --json`: 529 modules, 26892 artifacts, 0 diagnostics, not blocked.
- `rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json`: 0 diagnostics.
- Browser smoke on `http://127.0.0.1:4178/`: page rendered, Ideas tab opened, no console warnings/errors; plain Vite fallback shows SDK browser unavailable as expected.

## Risks Or Blockers

- The rendered Browser smoke cannot exercise the Tauri-only SDK browser or write bridge; Rust command coverage verifies the write path.
- Apply is intentionally limited to new scaffold drafts. Text edits, removals, and image replacement still need REST/OpenAPI apply routes.

## Next

- Add a backend-backed refresh after scaffold apply so the GUI can reload browser state instead of relying only on local applied entity state.
- Continue toward REST/OpenAPI draft apply for edited source slots, removals, and asset replacements.
