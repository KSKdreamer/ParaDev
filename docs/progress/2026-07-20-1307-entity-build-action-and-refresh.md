# Entity affected-output action and Build refresh profiling

Date: 2026-07-20 13:07 +08

## Outcome

The Entity editor now offers a novice-facing `Build affected Entity output` action after a clean Apply. The action always resolves the build-authoritative compiler family, moves to Build, waits for project/config/recovery eligibility, opens the existing generated `build.start` confirmation, and starts the normal durable lifecycle only after confirmation. For PIHC3 Entity records and the `HOI4DEV_ENTITIES` aggregate, the resulting target is exactly `{kind: "family", family: "entity", id: "entity"}`; record-only and module-only no-op routes are not exposed.

The previously observed roughly 80-second Build refresh was profiled to a full dry diagnostics inspection that was being launched repeatedly for browser-object merges. Diagnostics requests are now generation-owned, cached across rail remounts, shared while in flight, and serialized when newer refresh generations arrive. Browser-only merges and locale changes launch no diagnostics request. A completed build now invalidates only Build diagnostics instead of clearing and rebuilding the authoring browser, and hidden workspace tabs do not rehydrate scoped Entity data while Build is visible.

## Dependency-aware Entity output

The action preserves the existing Apply/Build boundary:

1. Dirty or applying drafts keep the action disabled.
2. The selected entity's raw compiler family is preferred over display aliases.
3. The current project path and a monotonic intent nonce scope the handoff.
4. Build waits for the target family to exist in the current model and for config, recovery, diagnostics summary, and conflicting runs to permit a request.
5. The existing generated confirmation panel remains mandatory.
6. The lifecycle request remains a cached family build and reaches the CLI as `--family entity`, never `--module entity`.

Exact raw-family matching takes precedence over canonical display aliases, preventing ambiguous groups such as Focus from selecting the wrong compiler family. A missing or stale target waits for a refreshed model instead of issuing an invalid build. English and Chinese labels name the affected family, and the three editor footer actions wrap in narrow split panes.

## Refresh root cause

Measurements on `/Users/magolor/Projects/ParaDev/PIHC3-GUI-Smoke` isolated the expensive route:

| Operation | SDK time | Process wall |
|---|---:|---:|
| Desktop state without browser | 1.060 s | 1.43 s |
| Unfiltered browser summary | 6.260 s | 7.21 s |
| Scoped Entity browser | 6.496 s | 7.11 s |
| Entity-only summary | 0.006 s | 0.248 s |
| Full diagnostics dry inspection | **81.635 s** | about 82 s |
| Parse emitted diagnostics manifest | 0.000253 s | — |

The Build diagnostics effect depended on the entire merged browser object even though the request did not use it. One terminal refresh cleared scopes, committed a retained base, committed a new summary, and could rehydrate the preserved Entity tab while Build was active. Each new browser identity launched another uncancellable Python dry build; rail re-entry launched another and repeated four config reads.

## Refresh repair

The frontend now applies these ownership rules:

- an App-owned project generation changes once per committed authoring refresh;
- terminal builds increment only the Build diagnostics generation because builds do not mutate authoring sources;
- diagnostics are keyed by project and strict-metadata mode;
- unchanged generations reuse settled results and rail remounts share an in-flight request;
- a newer generation waits behind the current inspection, and multiple queued generations collapse to the newest;
- config and project loading must settle before the first inspection, preventing concurrent relaxed/strict startup scans;
- a refreshed generation immediately falls back to current browser diagnostics rather than treating stale clean diagnostics as authoritative;
- malformed diagnostics payloads fail explicitly and are never cached as an empty clean result;
- diagnostics failures are project/generation/settings scoped, localized at render time, and cleared by a later successful generation;
- scoped workspace browser hydration runs only while the Projects workspace is visible.

The native inspection contract still has no cancellation mechanism, so an already-running dry inspection cannot be stopped. The cache guarantees at most one active inspection per project/settings key and coalesces later work instead of overlapping it.

## Verification

- Focused affected-output model, lifecycle, editor, and catalog tests: 101 passed.
- Focused diagnostics cache, Build lifecycle, and App tests: 86 passed.
- Full desktop frontend gate: 1,066 passed across 59 files.
- TypeScript typecheck and Vite production build: passed; only the existing chunk-size warning remains.
- Diff whitespace validation: passed.

A Python regression assertion now fixes the family transport contract at `--family entity` with no module selector. The repository's uv-backed Python hook could not be rerun in this sandbox because external-cache escalation was rejected after the environment reached its approval usage quota. The previous full Python gate remains green at 1,509 passed and one expected skip; the added assertion covers unchanged backend transport code.

## Current boundary

The affected-output block is staged as one commit boundary, and the diagnostics-refresh block remains a separate unstaged boundary. Commit and push are pending only because the repository hook needs `/Users/magolor/.cache/uv`, which the current sandbox cannot access and the escalation service declined due to its usage quota. No hook bypass was used.

The next novice-authoring slice remains a backend-described guided form for existing Entity record scalar fields—mesh/entity scale, default state, and existing animation/state values—with Advanced JSON preserved as an escape hatch. Assignment editing should follow separately because tag and type ordering are compiler-significant. A rebuilt packaged-app regression is still required after these frontend changes.
