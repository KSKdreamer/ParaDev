# Guided Entity editor packaged regression

Date: 2026-07-20 15:47 +08

## Outcome

ParaDev now has a generic, backend-described Guided source editor, with the first real provider covering migrated PIHC2 Entity records in the disposable PIHC3 GUI project. A novice can open an Entity record and edit existing mesh scale, entity scale, default state, and existing state animation/speed/blend/chance/looping/next-state values without touching raw JSON. State and entity names remain visible but read-only, absent optional values are not invented, and Advanced JSON remains available for unsupported structural, event, or propagation work.

The implementation keeps domain knowledge in the project family. Core ParaDev validates a versioned generic form envelope, the desktop renders it without PIHC-specific conditionals, and Save still applies the complete source draft through the existing project/family validation path.

## Safety and lifecycle hardening

- Guided controls perform exact JSON scalar-token replacement. Property order, whitespace, line endings, unknown fields, events, and unedited nested structures are preserved.
- The source-form endpoint is a POST with required raw string `text`; missing, null, unknown, duplicate-key, non-finite, and JavaScript-infinite numeric inputs fail consistently across Python, REST, native, and native-web paths.
- The public control model is a closed discriminated union with homogeneous scalar choices and recursively validated sections.
- Projection requests have a 20-second deadline, one active generation per project/root identity, supersession cancellation, process-group kill/reap, and shutdown cancellation.
- Stale source responses cannot replace the active record. Restore invalidates a structurally changed projection and keeps Guided unavailable until the restored text receives a fresh form.
- Empty source text survives native-web planning instead of being removed as a compacted optional value.

## PIHC2 Entity coverage

All 134 portable Entity records project successfully through `Project.source_form`:

| Measure | Count |
| --- | ---: |
| Records/forms | 134 |
| Recursive sections | 398 |
| Controls | 10,728 |

The provider uses the strict `pihc2.entity.record.v1` source contract. It does not expose add/delete/reorder operations, events, propagation, assignments, or any other compiler-significant structure in this slice.

The production aggregate safety rule was also revalidated: building `entity/HOI4DEV_ENTITIES` alone is correctly blocked because its generated PDX depends on all 134 record modules. The full Entity-family plan succeeds and preserves the aggregate's 182 owned outputs: nine generated PDX artifacts and 173 copied assets.

## Packaged native regression

The fresh release bundle remembered `/Users/magolor/Projects/ParaDev/PIHC3-GUI-Smoke` and discovered 136 Entity entries without preparing the optional 14-minute full-project index. In the Chinese UI:

1. Opened `VIENTO_AIR_AIRSHIP_C40` → `record` → Guided.
2. Confirmed mesh scale `3.0`, entity scale `1.0`, default state `idle`, and six migrated states.
3. Entered mesh scale `3.25`; the draft indicator and Apply action became active while the source file remained unchanged.
4. Applied the draft. The 3,465-byte baseline became 3,466 bytes and matched exactly the baseline with only `"scale": 3.0` replaced by `"scale": 3.25`.
5. Ran the affected Entity-family action through the existing mutation confirmation. Build History recorded success in 20 seconds with exit code 0.
6. Reopened Guided, changed the value back to `3.0`, and applied it.
7. Confirmed the source was byte-for-byte identical to the baseline, then rebuilt the Entity family again. The final cached build succeeded in 12 seconds with exit code 0.

Final family payload:

| Measure | Result |
| --- | ---: |
| Modules | 136 |
| Artifacts | 189 |
| Diagnostics | 0 |
| Errors | 0 |
| Blocked | false |

The final C40 source remained 3,465 bytes with SHA-256 `f20e10581e770eca7a4bc843c7d2e0a2c5d884a7ab2985f96a374a7ea25f53a9`.

## Verification

- Final Python source-form, architecture, and CLI contracts: 267 passed.
- Earlier full Python regression before the final narrow parity edits: 1,528 passed, one skipped; the edited contracts were rerun in the final 267-test gate.
- Full desktop frontend: 62 files and 1,118 tests passed.
- TypeScript typecheck and Vite production build: passed; only the existing large-chunk advisory remains.
- Rust desktop bridge/lifecycle: 63 passed.
- Python Tauri bridge: 21 passed.
- Disposable Entity provider/compiler suite: 18 passed.
- Repository lint and diff whitespace gates: passed.
- Independent final review: no remaining P0/P1 finding in this slice.

## Package

- App: `apps/desktop/src-tauri/target/release/bundle/macos/ParaDev.app` (79 MiB on disk).
- DMG: `apps/desktop/src-tauri/target/release/bundle/dmg/ParaDev_0.1.0_aarch64.dmg` (80,567,798 bytes).
- DMG SHA-256: `641beea68f6bffc1d07480d50568ca94578be8e49a2f72b82939646c0d43b0e8`.
- The app and embedded sidecar passed ad-hoc signature validation. The DMG passed image checksum, mount, mounted-app signature, and Applications-link verification.

This remains a local/test package. Public macOS distribution still requires Developer ID signing, notarization, and Gatekeeper validation.

## Findings and next boundary

- A completed partial Entity rebuild is recorded correctly as successful in Build History, but the overview header then returns to the previous full-build status. In this test that status was an older interrupted full build, which can make a novice think the successful family build failed. A clear last-partial-build success treatment is the next Build UX follow-up.
- Generic numeric controls still need an explicit safe-integer policy before a future provider exposes very large integers.
- The Entity descriptions say scale must be positive, but the first provider does not yet attach a form-level minimum.
- Project-root keys trim but do not canonicalize symlink aliases.
- The provider remains only in the disposable PIHC3 GUI project. Porting it into the protected PIHC3 checkout requires an isolated project branch/worktree; that checkout's pre-existing dirty work was not changed.
- Structural Entity creation, deletion, event editing, propagation editing, and assignment editing remain intentionally outside this safe scalar slice.
