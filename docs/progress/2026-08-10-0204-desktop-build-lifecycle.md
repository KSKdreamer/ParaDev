# Desktop Build Lifecycle

Status: complete

Date: 2026-08-10

## Outcome

ParaDev now owns build presentation at application-shell lifetime and build
processes at native-process lifetime. A PIHC3 author can start a full or
partial build, leave the Build rail, switch projects, return, and still see and
interrupt the correct run. Reloading the renderer within the same native
process reconciles every active and retained run before enabling new build
controls.

This deliberately does not continue a compiler across native-process exit,
crash, or relaunch. Best-effort renderer checkpoints only explain that an
unreconciled previous-process run was interrupted; the new native registry
never adopts it.

## Architecture

- The Python and Rust registries remain the sole process authorities.
- The React app-shell lifecycle is presentation state only: recovery, polling,
  history, terminal refresh, errors, and controls keyed by project root and run.
- Full, partial, and same-target conflicts compare normalized,
  filesystem-equivalent project roots. Independent projects can build
  concurrently.
- The SDK retains one stable source snapshot and cross-process locks for output
  roots, build roots, and eligible shared launcher descriptors.
- Terminal sequence, rather than wall-clock order, owns causal retention and
  full-build supersession within one registry lifetime.
- Graceful Tauri/native-web shutdown closes the registry first, interrupts all
  owned process groups, escalates if needed, reaps descendants, and cleans
  registry-owned temporary files.

## Verification

- Desktop unit suite: 93 files, 1,510 tests passed.
- App-shell/build-lifecycle focus: 3 files, 96 tests passed.
- Tauri Rust suite: 96 tests passed across three suites.
- Python desktop/native-web/Tauri bridge focus: 136 tests passed.
- Stable source snapshot and cross-process filesystem-lock focus: 6 tests
  passed.
- Production desktop TypeScript check and Vite build passed.

The production build retains Vite's existing large-chunk advisory; it is not a
build failure and is outside this lifecycle slice.

## User-manual checkpoint

The maintained [Build And Diagnostics](../user-manual/build-and-diagnostics.md)
page already explains the lifecycle without requiring process ids: a build
continues after leaving the Build rail, project status stays isolated, active
full and targeted runs remain interruptible, renderer reload recovery is
limited to the same native process, and closing the app cancels rather than
resumes its compilers.

Both copyable minimal-project checks passed against the current SDK: the CLI
and Python SDK returned `paradev.build.summary.v1` with one module, one
collection, five artifacts, and zero diagnostics.
