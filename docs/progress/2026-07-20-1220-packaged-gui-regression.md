# Packaged PIHC3 GUI regression pass

Date: 2026-07-20 12:20 +08

## Outcome

The rebuilt arm64 ParaDev package passed the highest-risk PIHC3 GUI checks against the disposable `/Users/magolor/Projects/ParaDev/PIHC3-GUI-Smoke` project. Source drafts survive validation failures without touching disk, scoped Entity browsing no longer corrupts the project-wide browser cache, an exact Entity-family rebuild succeeds and emits the edited value, active builds survive rail navigation, and closing ParaDev during a full build now recovers as one durable interrupted run after relaunch instead of returning to a misleading Ready state.

The two packaged defects found during this pass were fixed, fully gated, committed, and pushed on draft PR #4:

- `557729ac` (`fix(desktop): preserve scoped browser cache base`);
- `a3211408` (`fix(desktop): retain interrupted shutdown state`).

The protected PIHC3 checkout at `/Users/magolor/Projects/ParaDev/ParaDev-3/projects/PIHC3` was not used for GUI mutations. All hands-on edits and builds targeted the disposable smoke copy.

## Draft and disk-safety smoke

The earlier package in this pass rejected malformed `paradev.yaml` with a precise parse error while retaining the dirty editor draft. The manifest's disk hash did not change. It likewise rejected an Entity portable record whose scale was changed to `0`, retained the invalid draft for repair, and left the source file unchanged. Restoring the valid value allowed the draft to apply normally.

These checks exercise the novice failure path that matters most: a validation mistake remains visible and repairable in ParaDev and does not silently truncate or partially rewrite project files.

## Scoped browser/cache regression

Opening Manage -> Entity returned 136 objects and 458 sources. Moving to Build kept Entity in its canonical position between Doctrine Component and Equipment. Refreshing the Build rail kept the Entity row visible and restored the full summary rather than replacing the project-wide catalog with a scoped response.

The persisted browser cache remained project-wide after the scoped merge:

- `filters` was `{}`;
- 89 families were retained;
- the cached item count was 136;
- Entity remained 136 objects / 458 sources.

The fix makes the frontend payload's filters explicit, accepts only unfiltered responses as a cache base, rejects scoped or legacy missing-filter native cache entries, preserves family ordering during scoped replacement, and prevents a stale scoped response from winning a later refresh. Scoped results are persisted only after merging into a known unfiltered base.

## Exact Entity-family rebuild

The packaged Build rail requested and completed an exact Entity-family target. Its durable history entry records:

- target: `族 · entity · entity`;
- command selector: `--family entity`;
- result: success, exit code 0;
- duration: 12 seconds;
- post-build Entity summary: 136 modules / 459 sources;
- project diagnostics: 0 errors / 0 diagnostics.

The generated `gfx/models/00_hoi4dev_meshes.gfx` contains the repaired `VIENTO_MIRROR` mesh with `scale = 4.25`, proving that the family action emitted the edited Entity output rather than only reporting a green no-op.

## Lifecycle and shutdown regression

A full build was started through the packaged confirmation panel and observed in the Running state at 0–1%, with Build and Run disabled and Interrupt enabled. Quitting ParaDev removed the desktop process and compiler descendants. Relaunching the same package recovered:

- status `构建已中断` / Build interrupted;
- adverse/blocked presentation at the last observed 1% progress;
- Run disabled;
- no native `build` descendant;
- exactly one new interrupted full-build history row;
- the explicit reason: `This build was interrupted because ParaDev closed or relaunched before the native build registry reported a terminal result.`

The presentation checkpoint is a bounded, allowlisted local-storage record containing at most the newest concrete run for each project/target. Native recovery remains authoritative. A persisted Running id absent from a fresh native registry is converted once to the interrupted terminal state, while a native running or terminal result wins. Remount, duplicate suppression, storage read/write failure, and native-authority cases are covered by tests.

The earlier rail-away/return smoke also retained live full-build progress and allowed a successful interrupt. Partial Achievement and AI-family rebuilds completed successfully. A live multi-project switch was not exercised because only one smoke project was registered; project-isolation behavior remains covered by the automated lifecycle suite.

## Verification and package

- Python repository gate: 1,509 passed, one expected skip, one warning.
- Desktop frontend gate: 1,047 passed across 58 files.
- Focused browser-cache regression: 68 passed.
- Focused lifecycle/build regression: 81 passed.
- Rust Tauri gate: 58 passed across three suites.
- Black and Flake8 repository gate: passed.
- TypeScript/Vite production build: passed; only the existing chunk-size warning remains.
- npm audit: zero known vulnerabilities.

The package was rebuilt from full commit `a32114080d4b76e27c2cd760c49f9227879697ed` with `scripts/build-tauri.bash --headless-dmg --adhoc-sign`. Nuitka, the frontend build, Rust/Tauri release build, ad-hoc signatures, DMG checksum verification, read-only mount, mounted-app signature verification, Applications symlink, and detach all passed.

- DMG: `apps/desktop/src-tauri/target/release/bundle/dmg/ParaDev_0.1.0_aarch64.dmg`;
- size: 80,515,373 bytes;
- SHA-256: `c12ef1678de9ee43b51bbde26fe4f300f975f36555d49454965b65ff361c9994`.

Developer ID signing, notarization, stapling, and clean-machine Gatekeeper testing remain required before public distribution. The existing image-editor peer-range notice and unused optional dill/pandas acceleration notices remain non-blocking.

## Entity migration state

The current PIHC3 Entity corpus has 134 build-authoritative portable records owned across six source groups. It represents 859,846 record bytes, 264 concrete entities, and 2,124 states. Assignment metadata contributes 257 tags, 244 types, and 605 references. The compiler currently emits nine PDX files, 134 meshes, 8,871 entities, and 8,674 clones, while all 312 PIHC2-contracted source files match the migration evidence.

Canonical Entity verification is green: 91 PIHC3 Entity tests, four ParaDev acceptance tests, and a full Entity build of 135 modules with zero diagnostics/errors and 182 aggregate artifacts. PIHC3 PR #2 remains open and mergeable at `8cc1bf65f` with no reported CI checks, so this evidence is not yet on PIHC3's default branch.

## Remaining release boundaries

The most important novice-authoring gap is structured Entity editing. Portable record and assignment payloads are still exposed primarily as raw JSON. The safest next slice is a schema-backed editor for the fixed portable records, keeping raw source as an escape hatch, followed by duplicate/create/rename/remove once the current 134-record provenance invariant is deliberately generalized.

The GUI must treat an Entity edit as a dependency-aware full-family action; building a single record in isolation is currently non-emitting. Aggregate asset discovery, gameplay review, and 79 meaningful autodiffuse provenance files also remain incomplete.

One performance issue was observed after the Entity build invalidated catalog state: revisiting Build started several native `desktop-call` scans, and the largest-project refresh took roughly 80 seconds before the calls drained. No compiler orphan remained and the route eventually recovered, but cold/invalidated Build navigation needs profiling, request coalescing/cancellation, and a clear loading state before this can be considered comfortable for non-technical users.
