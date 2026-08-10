# PIHC3 packaged cold-start and source-record QA

Date: 2026-07-20 00:43 +08

## Outcome

The fresh ARM64 macOS package now survives a genuinely cold first launch, opens the selected PIHC3 project, loads all 136 Entity modules, edits portable PIHC2 shadow records as JSON, rejects malformed record JSON before any artifact write, and completes a full PIHC3 build with zero diagnostics.

Two release-blocking package defects found during this pass are closed on `codex/tauri-backend-sidecar`:

- `3c30cc91` (`fix(desktop): serialize bundled backend warmup`) removes the cached Nuitka onefile extraction race that caused first-call EOF responses and macOS code-signature kills.
- `3469adea` (`fix(package): verify macOS bundle signatures`) adds an explicit local ad-hoc signing mode and makes packaging verify both the produced application and the application mounted from the DMG.

The package is suitable for local PIHC3 QA. Public distribution is still gated on a Developer ID Application identity, notarization, stapling, and Gatekeeper validation on a clean Mac.

## Cold-start defect and fix

The prior package let several initial GUI requests start the bundled Nuitka backend concurrently. Those processes raced while populating the shared cached onefile extraction at:

`/Users/magolor/.cache/Magolor/ParaDev/0.1.0.000/paradev-backend.bin`

The failed launch returned `ParaDev desktop backend returned invalid JSON: EOF while parsing a value at line 1 column 0`. macOS logs from that reproduction contained `cs_invalid_page`, an mtime mismatch, and a `SIGKILL` against the concurrently extracted backend.

The bundled runtime now runs one synchronous `backend-info` warmup inside `OnceLock<Result<...>>::get_or_init`. Tauri setup performs that initialization before showing the main window. Exactly one first caller therefore completes cached extraction; later desktop requests remain concurrent and are not placed behind a global request mutex. Warmup spawn and nonzero-exit failures also carry sidecar path, status, and recovery context.

The fixed package was tested after quitting every ParaDev instance and moving the active extraction cache to a recoverable temporary backup. The launch began at `2026-07-20 00:38:41 +0800`. During extraction, the hidden app briefly returned `AXError.cannotComplete`, then opened normally after approximately 20 seconds with the selected PIHC3 project and no EOF/backend error. Opening Entity completed with `136 objects` and `457 source files`, including `GUI_SMOKE_ENTITY`.

The cache was recreated at `00:38:53 +0800` with mode `0700`. Its extracted 315,142,032-byte ARM64 backend has mode `0745`, an intact ad-hoc signature, and passes strict `codesign` verification. Unified logs since launch contain zero `cs_invalid_page`, mtime-mismatch, or relevant ParaDev/backend `SIGKILL` matches. They contain only the expected unknown ad-hoc trust-chain entries and one non-fatal XProtect inspection message for the extracted Python dylib.

## macOS bundle signing

The earlier application had no `Contents/_CodeSignature/CodeResources`. It carried only the linker's ad-hoc Mach-O signature, left `Info.plist` unbound, sealed no resources, and failed strict bundle verification with `code has no resources but signature indicates they must be present`.

The package wrapper now accepts `--adhoc-sign`, which supplies Tauri's pseudo-identity `-` through a small config overlay. This is intentionally explicit: it seals resources for local QA but does not impersonate a trusted distribution build. A later caller-provided `--config` remains able to override the identity for a real release. On macOS the wrapper now fails unless strict deep verification succeeds for the built `.app` and, for a headless DMG build, the mounted copy as well.

No valid Developer ID code-signing identity is installed on this machine. Before public release, build with a Developer ID Application certificate, notarize the application/DMG, staple the ticket, and verify Gatekeeper acceptance on a clean enabled system.

## Native Entity acceptance

All mutation used the disposable checkout:

`/Users/magolor/Projects/ParaDev/PIHC3-GUI-Smoke`

The protected PIHC3 checkout was never selected for mutation.

Observed packaged workflow:

1. Entity loaded the portable-record corpus as `136 objects` and `457 source files`.
2. Selecting record-only `VIENTO_MIRROR` showed `Info`, `meta.yaml`, and `record` tabs with no misleading Assets tab.
3. The JSON editor changed `scale` from `4.0` to `4.25`, persisted it, and reloaded the valid record.
4. The intentionally malformed text `{"mesh":` persisted as source, but Build stopped at 1% before artifact writes with blocking diagnostic `entity.invalid_record_source`: `PIHC2 entity record is not strict duplicate-free JSON` and `Expecting value: line 1 column 9 (char 8)`.
5. Restoring valid JSON and refreshing cleared the diagnostic.
6. A full cached PIHC3 build completed in 3 minutes 7 seconds: 18,238 modules, 81,761 source files, 100% success, zero errors, and zero diagnostics.

The disposable checkout intentionally retains its smoke-test project settings, `GUI_SMOKE_ENTITY`, and the valid `VIENTO_MIRROR` scale change. None of those QA mutations were committed.

## Fresh package artifacts

The all-in-one ARM64 artifacts were built at `3469adea` with:

`bash scripts/build-tauri.bash --headless-dmg --adhoc-sign`

| Artifact | Bytes | Modified (+08) | SHA-256 |
|---|---:|---|---|
| Raw `target/release/paradev-desktop` | 4,029,488 | 2026-07-20 00:36:16 | `b2ed38e7f3898077be19aca43e9ac1805eb4f9c31df675793ab42f24f54c4a06` |
| Bundled `ParaDev.app/Contents/MacOS/paradev-backend` | 78,016,880 | 2026-07-20 00:36:08 | `cd0360a8df8870e1afef083cd018633d3f09b6217f4045a8cf2c140fe0468d5b` |
| `ParaDev_0.1.0_aarch64.dmg` | 80,408,191 | 2026-07-20 00:36:16 | `56d6b735218f83bd7c76565e3c42f9d4fa9c388cd4539dcb9e569ef072d3e4fa` |

Strict deep verification passes for `ParaDev.app`; its signature is `adhoc,runtime`, its bundle identifier is `com.magolor.paradev`, and its sealed-resource envelope contains 13 rules and two files. The bundled backend independently passes strict verification. Both intentionally have no TeamIdentifier.

`hdiutil verify` passes with overall DMG CRC32 `$4EBA5AEC`. The mounted application also passes strict deep signature verification and the DMG contains the expected `/Applications` link.

## Verification gates

- Bundled Rust backend tests: 20 passed, 26 filtered, including successful/nonzero/missing warmup cases and eight concurrent first callers sharing one initializer.
- Rust formatting and `cargo clippy --lib --all-features -- -D warnings`: passed.
- Full desktop Rust library suite: 43 passed; four pre-existing draft-source tests still fail with `Source path is outside the project root.` and are unrelated to the warmup change.
- Focused Entity desktop tests: 70 passed; full desktop Vitest suite: 963 passed.
- TypeScript checking and production Vite build: passed.
- Portable PIHC2 Entity-record tests: 50 passed; full PIHC3 script suite: 215 passed; formatting and lint gates passed.
- Full native PIHC3 GUI build: 18,238 modules and 81,761 source files, zero errors and zero diagnostics.
- Fresh Tauri/Nuitka/Vite/Rust package build, strict app and mounted-app signature verification, DMG integrity, and cold launch: passed.

## Safety invariant

The protected checkout at `ParaDev-3/projects/PIHC3` remains at exact HEAD `7a4efe41bf07084ffe8fe56c2ba2f158ea14527f`. Its 21 pre-existing modified paths and 12 untracked paths remain present and were not altered. The PIHC3 migration worktree is clean at `10b379168cc7a79bcf746331ff29fdcaf0bae648`.

## Next migration boundary

The 134 portable PIHC2 shadow records are now discoverable, editable, strictly validated, stable in the packaged GUI, and safely non-emitting. The next Entity slice is to make the deterministic compiler consume those records while continuously comparing all 182 generated Entity artifacts against the aggregate-owned golden output. The aggregate must remain the sole artifact owner until that shadow compilation proves byte-exact and order-exact.

Public packaging remains a separate release boundary: provision Developer ID credentials, notarize and staple, then test Gatekeeper acceptance. The unrelated draft-source root failures and repeat-build sidecar reproducibility also remain open follow-up work.
