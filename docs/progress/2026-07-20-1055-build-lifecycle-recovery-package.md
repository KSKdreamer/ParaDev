# Build lifecycle recovery and verified package

Date: 2026-07-20 10:55 +08

## Outcome

ParaDev now treats a desktop build as an application-owned run rather than transient Build-page component state. An active run survives rail navigation, status reconciliation is isolated by project and partial-build selection, terminal events have causal ordering, and completed-run history is bounded without allowing a late poll from an older run to overwrite a newer result. Full-build success baselines, error ownership, and Run Game eligibility now follow the exact completed run.

The lifecycle hardening is committed and pushed as ParaDev `cd30d52c` (`fix(desktop): harden build lifecycle recovery`) on the existing draft PR #4 branch. The protected PIHC3 checkout at `/Users/magolor/Projects/ParaDev/ParaDev-3/projects/PIHC3` was not mutated; GUI investigation continues against the disposable `/Users/magolor/Projects/ParaDev/PIHC3-GUI-Smoke` project.

## Desktop recovery and isolation

The application-level controller owns active and terminal run state across Build-page unmounts. It reconciles interrupted polling, records causally ordered terminal snapshots through `terminalSequence`, retains a bounded recent history plus tombstones for evicted runs, and rejects stale async completions. Reloaded pages can recover the current run without treating an older terminal result as current.

Project identity and the selected module collection are part of lifecycle ownership. Switching projects, switching partial selections, leaving the Build rail, returning later, and overlapping status requests no longer leak progress, diagnostics, or success baselines between contexts. Collection-wide and project-wide wildcard ownership also prevents incompatible partial and full builds from racing over shared outputs.

The canonical frontend API, TypeScript transports, Rust Tauri commands, Python build registry, FastAPI routes, static OpenAPI seed, generated references, and user manuals now agree on exact run targeting:

- `build.status` and `build.interrupt` require a nonblank `run_id` at public REST/frontend boundaries;
- camel-case `runId` and snake-case `run_id` interrupt bodies are alias-aware, reject conflicts and extra fields, and share one live/static schema definition;
- explicit empty or whitespace identifiers are rejected at every transport boundary;
- only true omission in lower compatibility layers selects the deterministic oldest active run.

## Process ownership and shutdown

Python native-web builds use isolated POSIX sessions, fork-safe registry ownership, and `atexit` cleanup. Rust Tauri builds use command groups and, on Unix, now continue tracking the process group after its leader exits. Status, reap, interrupt, close, and wait paths do not report terminal completion until all descendants are quiescent. A real regression covers a leader that exits while a TERM-ignoring descendant remains alive, then verifies interrupt waits for group shutdown.

Rust retains Windows Job Object ownership for packaged Tauri builds. The Python native-web fallback on Windows still owns only its direct child; matching descendant-tree shutdown there remains a platform parity item rather than a macOS packaging blocker.

## Artifact mutation ownership

Build serialization is based on normalized filesystem identity rather than only logical project id. Each build locks all filesystem-equivalent output and build roots plus an eligible external HoI4 launcher descriptor target. This prevents two projects with custom output roots from concurrently mutating the same tree or `<mod_root>/<project_id>.mod` descriptor.

Lock identity is stable across deletion/recreation, Unicode NFC spelling, and case aliases on case-insensitive filesystems. Windows acquisition includes bounded contention retry. Locks are process-local coordination for live ParaDev sessions; recovery after a hard OS crash still relies on normal filesystem inspection rather than a durable cross-process lease journal.

## Verification

- ParaDev full fast gate: 1,509 passed, one expected live-PIHC3 fixture-sync skip, three warnings.
- Latest focused architecture/native-web contract gate after the shared OpenAPI schema refactor: 102 passed.
- Desktop frontend full unit gate: 1,036 passed across 58 files.
- Rust Tauri full unit gate: 58 passed; `cargo check` and `cargo fmt --check` passed.
- Project-build ownership suite: 89 passed, including shared external launcher descriptor contention.
- Black and Flake8 repository gate: passed across 161 Python files.
- TypeScript/Vite production build: passed; only the existing chunks-over-500-KB warning remains.
- Static/live OpenAPI schema parity and runtime alias/blank/conflict probes: passed.
- Commit hooks, generated-reference parity, and `git diff --check`: passed.
- Independent staged-diff audit found no build output, cache, conflict marker, debug residue, or PIHC3 file in the lifecycle commit.

## Package verification

The package was rebuilt from full commit `cd30d52c93e4751efe7237e201ddfbdc90863857` with:

```bash
rtk bash scripts/build-tauri.bash --headless-dmg --adhoc-sign
```

Nuitka successfully produced the self-contained arm64 backend for macOS 11 or newer, including the local HeavenBase package. Tauri built the optimized frontend and Rust application, ad-hoc signed the backend, executable, and app bundle, and created the headless DMG. The script then verified the DMG checksum, mounted it read-only, verified the mounted app signature, verified `Applications -> /Applications`, and cleanly detached it.

- DMG: `apps/desktop/src-tauri/target/release/bundle/dmg/ParaDev_0.1.0_aarch64.dmg`;
- size: `80,511,546` bytes;
- SHA-256: `da9ea65e0ec6866668c153fe62c80d9d5ab189295e6b0900011bce53b981f56a`.

The dependency install reported zero known npm vulnerabilities. Existing non-blocking package notices remain: the image editor's `styled-components` peer-range mismatch, Nuitka's unused optional dill/cloudpickle compatibility hint, and disabled unused pandas plotting/Numba acceleration. Developer ID signing, notarization, stapling, and clean-machine Gatekeeper testing remain required for public distribution; ad-hoc signing proves local bundle integrity only.

## Remaining release boundaries

The final hands-on packaged GUI pass is pending a macOS unlock. It will exercise malformed YAML rejection with disk preservation and retained drafts, invalid Entity scale rejection, repair and green Entity build, rail-away/return recovery with current progress and interrupt, project-switch isolation, and close-during-build descendant cleanup.

After that pass, the principal novice workflow remains structured Entity creation/editing: guided portable-record and legacy-assignment forms, convenient create/duplicate/rename/remove operations, domain explanations and previews, optimistic source revisions for external-editor conflicts, and safe transactional multi-file mutations. Other release work includes Windows native-web descendant ownership, frontend chunk splitting, Developer ID/notarization, and clean-machine package testing.
