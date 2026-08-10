# Desktop Backend Output Safety

Date: 2026-07-18 19:08 SGT

## Outcome

Every one-shot Tauri subprocess now runs through one bounded, deadline-aware process-group runner. ParaDev no longer uses `Command.output()` in production desktop commands, and a backend cannot freeze or exhaust the GUI by retaining pipes, refusing stdin, or emitting unbounded stdout/stderr. Desktop state and project-browser requests now also travel through `paradev.desktop.backend.v1` and delegate directly to the Python SDK instead of bypassing the versioned protocol through duplicate CLI subprocesses.

This safety layer deliberately rejects the roughly 584 MB unscoped PIHC3 catalog preview. It still permits the measured 37.7 MiB `scripted_effect` family response as a compatibility bridge, but SQL-backed paging remains the real fix for novice-safe entity browsing.

## Process Safety

- Added operation-specific stdout caps from 8 MiB for ordinary calls through 144 MiB for validated project-browser caches, plus a 1 MiB stderr cap.
- Reads stdout and stderr concurrently and stops retaining bytes at the configured limit.
- Writes large stdin payloads on a worker governed by the same deadline, preventing a child that never reads stdin from blocking the Tauri command indefinitely.
- Keeps the deadline active until the process and both output streams finish, including the case where a parent exits while a descendant retains its pipes.
- Reaps failed children and returns immediately if an I/O worker terminates unexpectedly.
- Uses `command-group` 5.0.1 for POSIX process groups and Windows Job Objects. Windows groups use kill-on-close ownership, so timeout cleanup remains attached to descendants after the root process exits. This follows the platform's documented process-tree mechanism: <https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects>.
- Applies the same 144 MiB response policy to browser-cache reads and writes. A valid large cache can no longer be written successfully and then reported as an 8 MiB transport failure.
- Applies the 96 MiB binary-response policy to thumbnail cache reads and writes instead of the previous fixed 2 MiB read cap.

## Protocol Consolidation

- Added strict `desktop_state` and `project_browser` request adapters to the allowlisted Python backend.
- Preserves optional profile, kind, family, module, collection, and summary scopes without reconstructing CLI flags in Rust.
- Delegates to `desktop_state`, `Project.browser_summary`, and `Project.browser` and returns the raw SDK payload.
- Rejects unsupported fields, invalid scalar types, empty project roots, and summary requests combined with module/collection scopes at one typed Python boundary.

## Regression Evidence

| Probe | Result |
| --- | --- |
| Child emits exactly 128 KiB on stdout and stderr concurrently | both streams preserved without deadlock |
| Child emits unlimited stdout | stopped at 64 KiB; complete process group killed and reaped in under two seconds |
| Parent exits while a 30-second descendant retains stdout/stderr | deadline fires; descendant process group is gone in under two seconds |
| Child never reads an 8 MiB stdin request | deadline fires and cleanup completes in under two seconds |
| Output reader channel disconnects before reporting both streams | deterministic failure and cleanup; no retry loop |
| Valid browser-cache write response | receives the same 144 MiB budget as cache reads |

## Verification

| Gate | Result |
| --- | --- |
| Focused backend/protocol/static tests | 54 passed |
| Complete fast Python suite | passed in parallel and serial modes |
| Repository Black and Flake gates | passed across 142 files |
| Frontend Vitest gate | 782 passed across 52 files |
| Frontend typecheck and production build | passed; existing chunk-size warnings only |
| Rust tests, default feature set | 40 passed |
| Rust tests, bundled backend | 39 passed |
| Rust production Clippy, default and bundled | passed with warnings denied |
| Rust release/bundled production check | passed |
| Rust format and diff checks | passed |
| Windows x64 default-feature compile check from macOS | passed, including the Job Object implementation |
| Independent read-only re-review | no actionable findings; all four prior P1s resolved |

The Windows x64 bundled-feature check still stops in the existing Tauri packaging configuration because `package.metadata` is not staged outside the native build overlay. That is a packaging-input blocker, not a process-runner compile failure; a native Windows sidecar/installer build remains required.

## Remaining Risks and Next Work

- Materialize PIHC3's catalog explicitly and add SQL filtering, counts, offsets, mandatory limits, and lazy data hydration. The GUI must not request the full catalog preview.
- Add bounded entity pages and lazy details in the React editor so the 8,279-item scripted-effects family does not mount every row or thumbnail.
- Give `paradev.desktop.thumbnail_cache.max_kb` an explicit generated maximum that matches the 96 MiB JSON transport budget; the default and normal PIHC3 range are now supported, but the configuration itself is still unbounded.
- Repair or stage the Windows Tauri `package.metadata` overlay, then build and exercise the native x64 sidecar and installer.
- Resume native visual PIHC3 editing/build smoke tests when macOS is unlocked.
