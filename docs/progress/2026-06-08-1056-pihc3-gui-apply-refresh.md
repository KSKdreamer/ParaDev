# PIHC3 GUI Apply Refresh Progress

Date: 2026-06-08 10:56 CST

Linear: TAL-297

## Done

- Centralized desktop-state reloads in `App` as a reusable refresh callback.
- Threaded the refresh callback through `AppShell`, `Workspace`, and `ModuleEditor`.
- Added `shouldRefreshAfterScaffoldApply(...)` and coverage for the refresh decision.
- After a successful scaffold Apply, `ModuleEditor` now:
  - marks the local draft clean from the written SDK plan;
  - refreshes desktop state for the active project root;
  - preserves selection when the refreshed backend browser includes the applied object.
- Updated `docs/techstack/ui/gui-spec.md`.

## Verification

- Red check: `rtk npm --prefix apps/desktop run test:model` failed first because `shouldRefreshAfterScaffoldApply` was missing.
- `rtk npm --prefix apps/desktop run test:model`: 8 passed.
- `rtk npm --prefix apps/desktop run build`: passed.
- `rtk bash -lc 'cd apps/desktop/src-tauri && cargo test'`: 5 passed.
- `rtk uv run paradev build projects/PIHC3 --emit-manifests --json`: 529 modules, 26892 artifacts, 0 diagnostics, not blocked.
- `rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json`: 0 diagnostics.
- Browser smoke on `http://127.0.0.1:4178/`: page rendered, Ideas tab opened, no console warnings/errors; plain Vite fallback shows SDK browser unavailable as expected.

## Risks Or Blockers

- Browser smoke still cannot exercise Tauri-only SDK browser refresh. The Tauri command tests verify backend command behavior; a full Tauri UI smoke remains a future manual or automation target.
- Text edits, removal drafts, and image replacement still need REST/OpenAPI apply routes.

## Next

- Add a visible low-noise applied/refreshed status in the module editor only if real users need confirmation beyond the draft changing to clean.
- Continue toward REST/OpenAPI apply for source-slot edits, removals, and assets.
