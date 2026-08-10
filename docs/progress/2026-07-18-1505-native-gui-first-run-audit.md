# Native GUI First-Run Audit

Date: 2026-07-18 15:05 SGT

## Outcome

The migrated ParaDev Tauri shell compiles and launches against HeavenBase 0.1.2.0, and the real PIHC3 project loads cleanly through the same SDK commands used by the desktop bridge. The first native interaction pass found a release-blocking first-run bug: the visible **Open project** action only revealed the already-active folder in Finder and offered no way to choose or load an arbitrary project.

This checkpoint replaces that action with a native folder picker on macOS, Windows, and Linux, feeds the selected root through the existing SDK-owned desktop-state bridge, and persists the last successfully loaded project root. Cancelling the picker is a no-op, and a failed project load does not replace the saved working root.

The macOS accessibility pass remains incomplete because the machine locked after the native process started and the Computer Use runtime cannot unlock it. No write was attempted against the dirty PIHC3 checkout.

## Real PIHC3 Read-Only Probes

The project at `/Users/magolor/Projects/ParaDev/ParaDev-3/projects/PIHC3` was loaded directly with the migrated ParaDev environment.

| Probe | Result | Wall time |
| --- | --- | --- |
| Project-browser summary | 89 families, 18,038 modules, no diagnostics | 1.92s |
| Ideas family | 390 items, first item fully source-backed, no diagnostics | 3.94s |
| Characters family | 250 items, first item fully source-backed, no diagnostics | 4.11s |
| Focus-tree family | 28 aggregate items, first item fully source-backed, no diagnostics | 3.99s |

The summary confirms all current PIHC3 families are discoverable in the migrated runtime. It does not prove semantic parity or beginner-safe editing; the companion entity audit records those gaps.

## First-Run Fix

- Added an allowlisted `paradev_select_project` Tauri command.
- macOS uses the system folder chooser through AppleScript; Windows uses `FolderBrowserDialog`; Linux uses `zenity`.
- Kept folder selection in trusted Rust rather than exposing a general shell API to React.
- Added a typed frontend service that returns a selected path or `null` on cancellation.
- Changed the existing **Open project** action to select and load a project instead of revealing the current folder.
- Added `activeProjectPath` to desktop-owned app settings and restore it during boot.
- Kept persistence tied to the last successfully loaded desktop state so a slow first load cannot overwrite the saved root with the developer demo fallback.

The Project Management page still provides explicit path rows for revealing the active project, source, output, build, and manifest paths.

## Verification

| Gate | Result |
| --- | --- |
| Frontend service and app tests | 97 passed |
| Complete desktop Vitest gate | 782 passed across 52 files |
| Frontend typecheck and production Vite build | passed |
| Native picker Rust contract | passed |
| Complete Tauri Rust test gate | 25 passed across 3 suites |
| Cargo format check | passed |
| Git diff whitespace check | passed |
| Live Tauri rebuild after the change | passed without final compiler warnings |

## Remaining Release Blockers

1. The honest empty-project onboarding flow is still missing. An empty SDK registry falls back to a relative developer demo instead of showing **Open existing project** and **Create project** choices.
2. The selected root is durable, but there is no SDK-owned recent-project registry or stale-path management UI yet.
3. The app bundle is not self-contained. Rust still derives the builder checkout from `CARGO_MANIFEST_DIR` and launches `uv`; no Python/HeavenBase sidecar is bundled.
4. The current packaged smoke only proves that a terminal-launched process stays alive while its source checkout and `uv` remain present. It does not prove relocation or Finder launch.
5. Native visual checks for Ideas, Characters, Focuses, draft creation, focus diagrams, and Build remain pending until macOS is unlocked.
6. CI cannot clone the private HeavenBase pin without a read-only repository credential. The workflow change is intentionally waiting for explicit approval and secret provisioning.
7. The ParaDev wheel declares unpublished `heavenbase==0.1.2.0`; a general Python release remains blocked until that exact HeavenBase build is published.

## Next

- Resume the native PIHC3 accessibility and screenshot pass after macOS is unlocked.
- Add honest empty-state onboarding and project creation before expanding recent-project management.
- Extract the Rust-embedded Python helper dispatcher into a versioned backend protocol, centralize development versus packaged backend resolution, and bundle a Nuitka sidecar through Tauri `externalBin`.
- Replace the packaged smoke with a relocated app test whose `PATH` contains neither `uv` nor Python.
