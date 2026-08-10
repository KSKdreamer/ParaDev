# Tauri Backend Sidecar and Packaging Audit

Date: 2026-07-18 17:03 SGT (updated 17:36 SGT)

## Outcome

ParaDev now has a self-contained macOS ARM64 release-profile bundle whose Python and HeavenBase runtime travels with the Tauri app. A relocated copy ran with a deliberately reduced `PATH` containing neither `uv` nor Python, reported HeavenBase 0.1.2.0 from the bundled backend, loaded the real PIHC3 project without diagnostics, and kept the desktop process alive on the locked Mac.

This closes the earlier checkout-runtime blocker. It does **not** make the current artifact publishable: Apple signing, notarization, stapling, and a final unlocked visual pass are still required. The current app is an unsigned development artifact and fails strict code-signature verification.

## Backend Runtime

- Added the versioned `paradev.desktop.backend.v1` JSON/stdin protocol and `paradev.desktop.backend-info.v1` identity response.
- Kept helper calls allowlisted and forwards ordinary arguments to the existing ParaDev CLI instead of introducing a second CLI implementation.
- Sends helper arguments and large payloads through stdin, including a verified 200 KiB Unicode round trip.
- Forces strict UTF-8 for protocol and forwarded CLI/LSP stdio.
- Redirects incidental Python helper output to stderr so stdout remains valid JSON.
- Centralized backend command construction in Rust:
  - development runs `uv run python -m paradev.desktop.backend` from the checkout;
  - packaged builds resolve the sibling `paradev-backend[.exe]` executable and never derive a checkout path from `CARGO_MANIFEST_DIR`.
- Added concurrent stdout/stderr draining, bounded command timeouts, child cleanup after stdin failure, and detached-process stdio isolation.
- Release compilation fails with an actionable message unless the `bundled-backend` Cargo feature is enabled.

One known exception remains: project inspection still uses a separate Rust translation path instead of the versioned backend protocol. The entity-parity audit found that translation incomplete, so centralizing inspection is the next P1 migration block.

## Sidecar and Bundle

- Added native-host Nuitka builds for macOS ARM64 and an explicit Windows x64 contract.
- Uses a one-file sidecar for Tauri `externalBin`; standalone mode remains available for inspectable diagnostics.
- Uses Nuitka's persistent per-user extraction cache to reduce warm starts.
- Packages both ParaDev and HeavenBase code and package data from the repository's exact `.venv`.
- Adds explicit bundle/desktop dependencies, including zstandard for one-file compression.
- Forces reproducible Nuitka output and runtime file references on every native host.
- Scrubs credential-like environment variables before compilation and scans both the final executable and the uncompressed one-file payload for token markers, exact sensitive environment values, and the private HeavenBase source URL.
- Ignores the 3.0 GiB sidecar build tree, 74 MiB staged external binary, Tauri target output, and Nuitka crash report instead of allowing generated artifacts into Git.
- Sets the bundle's declared minimum macOS version to 11.0, matching both packaged Mach-O executables.
- Supports custom Cargo profiles when locating and reporting bundle output.

## Relocated PIHC3 Smoke

The optimized app was copied to `/private/tmp/ParaDev-release-relocated-20260718-173458.app` and tested with `PATH=/usr/bin:/bin`.

| Probe | Result | Wall time |
| --- | --- | --- |
| Bundle relocation | copied with `ditto`; no checkout-relative runtime needed | 0.03s |
| Backend identity, first run for this reproducible build | ParaDev 0.1.0.000dev, HeavenBase 0.1.2.0, Python 3.12.13, Darwin ARM64 | 3.63s |
| PIHC3 project-browser summary | correct PIHC3 title/profile, 90 family groups, zero diagnostics | 3.14s |
| Desktop executable | stayed alive silently on the locked Mac; stopped by the test after 20s; no lingering process | passed |

The first sandboxed backend launch was intentionally denied access to the user cache and failed clearly. Normal app permissions succeeded. This confirms that the cached one-file strategy requires user write access below `~/.cache` on first launch.

## Artifact Evidence

| Artifact | Evidence |
| --- | --- |
| Reproducible Nuitka sidecar | 77,819,888 bytes; SHA-256 `0734665aa579d351b466b84fd9d613fc965487292402ef508efba7e909097c34`; built, staged, and bundled copies match exactly |
| Debug macOS app | 105 MiB; contains a 30.9 MiB Tauri executable and 74.2 MiB bundled backend |
| Headless debug DMG | 85,753,238 bytes; SHA-256 `2beb61bda5ac610b60e49b54e0790c05a0062810fb65ca65c064cc0dcec48f85`; `hdiutil verify` passed |
| Release macOS app | 78 MiB; 3,963,168-byte optimized Tauri executable plus the exact 77,819,888-byte sidecar; minimum macOS 11.0 |
| Headless release DMG | 80,170,051 bytes; SHA-256 `6a2e1cc3e343e4b2b316226b3f1cafc1a3103cc3a84725913b7dcf5e393bd2d3`; CRC, read-only mount, app presence, and `Applications -> /Applications` verified |

The ordinary Tauri DMG step reached Finder cosmetic scripting and then timed out because macOS was locked. The source-controlled build wrapper now exposes `--headless-dmg`, uses Tauri's supported CI switch without invoking generated scripts itself, and verifies only fresh artifacts from that build. The resulting DMG is functionally installable but intentionally omits the custom Finder background and icon positioning.

## Verification

| Gate | Result |
| --- | --- |
| Complete Python suite | 1,279 passed; one existing warning |
| Focused packaging contract after audit hardening | 6 passed |
| Complete frontend Vitest gate | 782 passed across 52 files |
| Frontend typecheck and production Vite build | passed; existing large-chunk warnings only |
| Rust tests, default feature set | 35 passed |
| Rust tests, bundled backend | 34 passed |
| Rust debug/default, bundled, and release/bundled checks | passed |
| Rust Clippy with warnings denied, default and bundled | passed |
| Rust format check | passed |
| Repository Black and Flake gates | passed across 142 files |
| Dependency/document synchronization | passed for 121 packages |
| Sidecar shell syntax, dry-run, staging, and credential scan | passed |
| Relocated packaged runtime | passed with sanitized `PATH` |
| Complete release app plus headless DMG build | passed; image integrity and Applications link verified |

## Remaining Release Blockers

1. **Signing and notarization:** the development app is ad-hoc/linker signed and `codesign --verify --deep --strict` fails because resources are not sealed. A publishable macOS artifact needs Developer ID signing, notarization, stapling, Gatekeeper validation, and corresponding protected credentials. Windows needs Authenticode signing and a native x64 package/runtime test.
2. **Native visual QA:** the locked Mac prevents screenshot, keyboard, focus order, draft-creation, diagram, build, and beginner-usability checks in the actual app window.
3. **Inspection parity:** Rust currently recognizes only 15 of 19 inspection kinds and 11 of 36 filters, and drops `strictMetadata: false`. It should pass the complete inspection request through the Python backend and HeavenBase instead of duplicating the catalog.
4. **Large inspection payloads:** PIHC3 scripted effects alone return 8,279 items and about 37.7 MiB of JSON in 17.2s; an unscoped inspection exceeded two minutes. Pagination, lazy detail loading, summary caching, and bounded output are required for a novice-safe entity browser.
5. **Styled DMG visual QA:** the automated headless DMG is structurally verified, but the custom Finder background and icon positions still need an unlocked interactive release pass.
6. **Release provenance and identity:** the desktop artifact is version 0.1.0 while the backend still reports 0.1.0.000dev. A production build should reject development versions, verify a frozen environment and exact HeavenBase revision, build under a neutral Python prefix, emit input and detached artifact manifests, and checksum only artifacts created by that build.
7. **Windows validation:** the x64 filename/runtime contract exists, but the sidecar and installer have not been built, signed, relocated, or exercised on a native Windows host.
8. **CI private dependency access:** GitHub Actions still cannot fetch the private exact HeavenBase pin without an approved read-only credential workflow.
9. **Python distribution:** the ParaDev wheel still depends on unpublished `heavenbase==0.1.2.0`; this does not affect the exact-source sidecar but blocks a general Python package release.

Nuitka also reports optional exclusions for cloudpickle-compatible dill support and pandas numba/plotting integrations. They are not used by the PIHC3 workflows tested here, but they remain explicit follow-up items rather than silently claimed coverage.

## Next

- Route project inspection through the versioned backend protocol, preserve every filter value exactly, and delete the duplicated Rust inspection catalog.
- Add paginated/lazy entity browsing and re-run the large PIHC3 families through the packaged backend.
- Add a signed-release gate that refuses to publish unsigned or unstapled output and emits detached provenance.
- Resume the hands-on PIHC3 native GUI pass immediately after macOS is unlocked.
- Add honest empty-state onboarding, project creation, and recent-project management for first-time mod developers.
