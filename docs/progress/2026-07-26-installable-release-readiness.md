# 2026-07-26 Installable Release Readiness

> **NOT RELEASE-READY.** A current Apple-silicon preview DMG now contains the
> ad-hoc-signed ParaDev app, the exact 1.84 GB PIHC3 0.2.3 project package,
> first-start guidance, and an Applications shortcut in one handoff. The
> packaged backend imported that bundled project into a fresh isolated user
> profile and completed clean/full, cached, family-partial, and module-partial
> PIHC3 builds without checkout Python, Conda, uv, or hidden-metadata edits.
> The new exact DMG passes mounted image, signature, architecture, catalog,
> manifest, checksum, and current packaged-backend four-mode verification.
> This is still development-host evidence: clean macOS acceptance is 0/1, no
> Windows installer exists, clean Windows acceptance is 0/1, the new DMG has
> not received a native GUI launch smoke, and the generated mod has not been
> launched in HOI4.

Clean-OS acceptance is therefore **0/2**.

## Release Checkpoint

Revised completion is **94% toward the install-and-run acceptance target**.
This percentage measures implementation and recorded verification evidence,
not public release approval. Packaging, clean-machine execution, signing, and
lifecycle behavior remain ahead of broad module/meta cleanup unless that
cleanup blocks installation or a PIHC3 build.

The macOS vertical slice now has a freshly rebuilt combined preview handoff in
a new non-overwriting artifact directory, exact-DMG verification, current
packaged-runtime four-mode build evidence, an authoritative backend
launch-readiness bridge, and prior installed-GUI/first-run evidence. A
retained-handle Win32 publication backend now removes the previous
compile-publication blocker, and generated paths are rejected before build if
they cannot be represented safely on Windows. The next critical path is an
exact final-DMG native GUI smoke with explicit at-action local-run approval,
then authorized commit/push and execution of the prepared native Windows
package/smoke workflow, followed by clean macOS and Windows
installation/import/build/game-launch/uninstall smoke tests.

## Installability Checklist

- [x] Preserve the crash-transaction data-safety fixes. The focused transaction
  gate passed 113 tests.
- [x] Bundle Python and HeavenBase rather than depend on a developer
  environment. The packaged backend reports Python `3.12.13`, ParaDev
  `0.1.0.000dev`, and HeavenBase `0.1.2.1`.
- [x] Produce an ad-hoc-signed Apple-silicon `.app` and DMG. The app,
  mounted-DMG app, and copied installed app passed
  `codesign --verify --deep --strict`; `hdiutil verify` passed and the DMG has
  the expected `/Applications` link.
- [x] Produce a single self-contained preview DMG containing `ParaDev.app`, the
  exact catalog-bound `PIHC3-0.2.3-project.zip`, `START-HERE.html`, and the
  `/Applications` link. Creation and a separate `--check` pass both mounted
  and verified the published 1.87 GB image.
- [x] Produce and fully verify a deterministic PIHC3 companion archive.
- [x] Generate a deterministic outer integrity manifest. It binds the exact
  installer, packaged-backend identity and runtime self-report, embedded
  project-package catalog, companion archive, canonical versions, the checkout
  state observed during generation, and explicit non-release limitations
  without copying the 1.84 GB payload.
- [x] Add a first-class “Install PIHC3 package” flow. The bundled catalog binds
  the exact archive size, digest, entry counts, project identity, and desktop
  version; the installer hashes selected bytes, validates portable ZIP paths
  and the per-file manifest, extracts to a sibling staging directory, and
  atomically publishes without overwriting unmanaged or edited installs.
- [x] Accept browser-renamed archive files by exact size and digest rather than
  by filename, and safely reopen a matching managed installation.
- [x] Verify and install the real PIHC3 companion through the current packaged
  backend. Its atomic install completed in 20.04 seconds at
  `Documents/ParaDev/Projects/PIHC3-0.2.3` under a fresh isolated user profile;
  desktop version `0.1.0-0`, archive size, SHA-256, portable paths, contents,
  and project identity all matched the embedded catalog.
- [x] Present the native first-run PIHC3 action and existing-project fallback;
  native ZIP picker cancellation is neutral and duplicate actions remain
  locked while work is pending. Selecting the real archive verified/reopened
  the managed install and automatically opened its 47 module families. English
  and Chinese copy are covered.
- [x] Add review-first natural-language module batches for PIHC3 authoring.
  Create-module chat accepts only a structured, single-family proposal,
  validates it with `Project.create_modules(..., write=False)`, and opens the
  existing batch editor only after explicit review. Chat never writes files;
  stale project/template/source context, unsafe numbers, duplicate ids, and
  open batch planners fail closed. The A–E idea example produces one exact
  five-module dry plan and retains explicit Apply as the only write boundary.
- [x] Eliminate the exact `TECHNOLOGY_FIREARM_I` React error 185 crash. The
  packaged debug app remained stable for an additional 30 seconds and the
  copied release app rendered the exact six-source detail for 15 seconds.
- [x] Run clean/full, cached, `technology` family-partial, and
  `technology/TECHNOLOGY_FIREARM_I` module-partial builds through the exact
  backend packaged into the current app with only `/usr/bin:/bin` available.
  The backend executed directly from the release app bundle.
- [x] Preserve current-candidate count parity: clean/full and cached both report
  17,802 modules, 78 collections, and 37,501 artifacts with no diagnostics or
  errors; the prior installed-GUI candidate retains byte-parity evidence.
- [x] Preserve the complete 37,501-file published mod after both partial modes.
- [x] Preserve publication launch safety after partial builds. The emitted
  artifact ledger is schema v3, state `complete`, retains all 37,501 owned
  artifacts, and records `whole_project_baseline: true`.
- [x] Make the publication ledger—not renderer localStorage—the durable
  authority for the GUI Run action. The packaged backend reports stable,
  actionable readiness codes and still reports `ready` after both partial
  builds retain the whole-project baseline.
- [x] Render live compiler detail and `index / total` in the Build page so
  long PIHC3 discovery/publication work is visible instead of appearing
  stalled.
- [x] Make Build-page scope and cache behavior explicit. Whole-project builds
  now distinguish “Update existing output” from “Clean output and rebuild”;
  every running family/module partial has an exact target row, live elapsed
  time, target-qualified interrupt action, and stable confirmation behavior.
  Launcher-readiness failures are localized and actionable in English and
  Chinese.
- [x] Give synchronous REST builds selector parity with the SDK and desktop
  bridge. `POST /projects/build` now forwards family, module, collection,
  full-rebuild, and parallelism inputs and reports user-correctable
  SDK/manifest/path errors as HTTP 400.
- [x] Remove the changed-ledger quadratic publication preflight. The real
  37,501-row PIHC3 upgrade case with 3,338 new paths now validates in 1.79
  seconds; the prior pairwise scan exceeded 180 seconds.
- [x] Generate valid isolated launcher ownership, `PIHC3.mod`, and
  `descriptor.mod` files pointing at the isolated published mod.
- [x] Add first-run recovery for an invalid remembered project path and
  actionable game/mod-root errors.
- [x] Harden the pending Windows bundle configuration: no release console
  window, offline WebView2 provisioning, downgrade prevention, stable WiX
  upgrade code, current-user NSIS installation, uv-managed CPython `3.12.13`,
  full-SHA action pins, a pre-smoke 8 GiB capacity gate, and success-only
  release-kit upload. Native installer behavior remains unverified.
- [x] Replace the Unix-only generated-publication gate with a private Win32
  retained-handle backend on Windows. It rejects reparse points and unsupported
  filesystems, retains stable file identities, operates through volume-GUID
  paths, flushes sibling temporary files, and uses handle-based atomic
  rename/delete. The existing POSIX descriptor backend and public
  `AnchoredDirectory` API remain unchanged. Native behavior is still gated on
  a real Windows run.
- [x] Reject generated paths that alias or fail on Windows, including reserved
  device names, trailing spaces/dots, alternate-data-stream colons, invalid
  characters, and control characters. The exact PIHC3 plan has no violations.
- [x] Add the Win32 publication, portable-path, artifact, manifest,
  adversarial-publication, path-index, and full project-build suites to the
  native Windows workflow before installer creation.
- [x] Reuse the retained Win32 authority for bounded source reads and
  transactional source-draft write/remove batches. Draft application now
  verifies the original project path after successful operations and preserves
  operation errors, while rollback checks exact parent/file identity and
  content before restoring backups. Native execution remains gated on Windows.
- [x] Align canonical version metadata. Python/backend
  `0.1.0.000dev` deterministically maps to desktop prerelease `0.1.0-0`;
  package-lock, Cargo lock, and Tauri metadata are checked by
  `scripts/sync-env.py`. Manual upgrade, uninstall, and retained-user-data
  behavior is documented for the first release.
- [x] Fail package builds early on release-input drift. The package preflight
  checks canonical metadata including the embedded PIHC3 catalog binding,
  `uv.lock`, the installed bundle/desktop dependency environment, and the exact
  companion row by default, and always forwards Cargo `--locked`. The native
  Windows workflow now requires the immutable numeric ID of a PIHC3 GitHub
  release asset in the current private repository. It retrieves that fixed API
  resource with Actions' built-in `contents: read` token, catalog-checks the
  sibling `.partial` file, and only then atomically publishes the exact
  companion. It accepts no arbitrary URL or manually configured secret.
- [ ] Launch and use the generated mod in HOI4. This host had existing
  Steam/Paradox activity and no configured HOI4 game root, so the GUI `Run`
  action was not used during the isolated build smoke.
- [ ] Exercise the packaged native-GUI AI proposal/review flow. The current
  backend and frontend contract/tests cover the dry proposal and explicit
  batch-editor Apply boundary, but the v4 backend-only smoke does not attest
  chat UI interaction.
- [ ] Install and run all four modes on a clean supported Apple-silicon macOS
  machine or VM.
- [ ] Produce fresh native Windows x64 MSI and NSIS/EXE artifacts with
  checksums and bundled-backend identity evidence.
- [ ] Install, launch, run all four modes, launch the generated mod, and
  uninstall on a real clean Windows x64 machine or VM.
- [ ] Exercise upgrade, rollback, retained-data, and uninstall behavior on
  clean macOS and Windows installations. No automatic updater is shipped.
- [ ] Sign and notarize macOS artifacts and Authenticode-sign Windows
  installers. This is intentionally deferred and is not a blocker for the
  requested unverified preview.

## Current Artifacts

| Artifact | Exact path | Size | SHA-256 |
| --- | --- | ---: | --- |
| preferred combined macOS preview DMG | `/Users/magolor/Projects/ParaDev/.worktrees/heavenbase-0116/dist/release/aarch64-apple-darwin/preview-2026-07-28-ai-batch-v4/ParaDev-0.1.0-0-PIHC3-0.2.3-macos-arm64-UNVERIFIED-PREVIEW.dmg` | 1,871,503,207 bytes | `68a8024a2a4d1769680cda19c7fa49f87ba3541453c431cd14c9d376cb2f0ef7` |
| release integrity manifest | `/Users/magolor/Projects/ParaDev/.worktrees/heavenbase-0116/dist/release/aarch64-apple-darwin/preview-2026-07-28-ai-batch-v4/release-manifest.json` | 2,047 bytes | `87837d045025ea6937c2cbb565ea6b041e27f13d28af9aae466c6ad6b6bdc621` |
| checksum ledger | `/Users/magolor/Projects/ParaDev/.worktrees/heavenbase-0116/dist/release/aarch64-apple-darwin/preview-2026-07-28-ai-batch-v4/SHA256SUMS` | 299 bytes | `524e7385cfc75e9985f322db4724c18d5014450f3140d64045ed05eaba50a5ea` |
| first-start guide | `/Users/magolor/Projects/ParaDev/.worktrees/heavenbase-0116/dist/release/aarch64-apple-darwin/preview-2026-07-28-ai-batch-v4/START-HERE.html` | 7,374 bytes | `d17c1d83362ba4c5ed271d79c9b8f4f7bb0ae37cd244d03b81c6f56e2a89cd14` |
| current bundled backend | combined DMG `ParaDev.app/Contents/MacOS/paradev-backend` | 84,517,616 bytes | `a667320dc023b52d4734036f9011ca7f5eceb6b7938b9c4fc80e625a3314898c` |
| packaged four-mode smoke evidence | `/Users/magolor/Projects/ParaDev/.worktrees/heavenbase-0116/dist/release/aarch64-apple-darwin/smoke-2026-07-28-ai-batch-v4/macos-smoke-evidence.json` | 8,422 bytes | `5d2b3ff068a956f135bea1bc9b973a79e84dd9cc2b7c8cd4bf7f068e6c0ba957` |
| PIHC3 companion | `/Users/magolor/Projects/ParaDev/.worktrees/heavenbase-0116/dist/projects/PIHC3-0.2.3-project.zip` | 1,844,557,429 bytes | `87c8f75834ca3b32bdf5124e924a3013d8948ebb189615eeba88ee42f65ef01d` |

The prior v3 and earlier known-good previews remain untouched. The current
build logged sidecar content fingerprint `660f138b7a2be1ea`. The packaged runtime
smoke proved Python `3.12.13`, ParaDev `0.1.0.000dev`, HeavenBase `0.1.2.1`, a
valid HeavenBase SQLite catalog, and the embedded exact PIHC3 package
id/digest. Bundle metadata and native output identify desktop `0.1.0-0`,
arm64, and macOS 11+ as the minimum. The app and backend carry valid ad-hoc
signatures; both the construction pass and the independent check mounted the
published image, passed deep/strict signature and arm64 verification, matched
the embedded backend catalog to the release catalog, passed `hdiutil verify`,
and found the expected app, PIHC3 archive, first-start guide, and
`/Applications` symlink.

The path-independent `paradev.release.artifact-manifest.v1` projection passed
its exact read-only check. It verifies the companion against the full embedded
catalog row, executes and hashes the packaged backend, and records only
portable basenames, sizes, hashes, stable runtime facts, and the checkout state
observed during generation. It deliberately reports
`release_ready: false`, `acceptance_attested: false`,
`artifact_source_attested: false`, dirty source, an unattested declaration
that the bundled application is ad-hoc signed, and the missing
clean-machine/game-launch/uninstall attestations. The separate deep/strict
`codesign` check is the evidence for the app signature. The manifest is itself
unsigned, so it provides integrity and version pairing rather than publisher
authenticity. Its conservative `pihc3-four-mode-build-not-attested` limitation
remains because build smoke is recorded in this engineering ledger rather than
cryptographically attached to the artifact.

The companion contains 137,566 entries: 57,876 directories and 79,690 files,
including `SHA256SUMS`. Its uncompressed size is 2,764,159,173 bytes.
`unzip -t` and the complete manifest/CRC check pass. Generated caches and
source-control metadata are excluded, and Windows portability validation caps
archive paths at 200 UTF-16 code units including the separator.

## Current Combined-DMG and Packaged-Build Evidence

The exact published combined DMG passed both its construction verifier and a
fresh independent `scripts/package-macos-preview.bash --check` run. Each pass
verified the image checksum, mounted contents, deep/strict app signature,
arm64 desktop and backend executables, embedded package catalog, 1.84 GB PIHC3
archive identity, release manifest, and outer checksum ledger.

The current packaged backend—not a checkout interpreter—then installed and
compiled a fresh extraction of the exact PIHC3 archive from the mounted
preferred DMG. The reusable fail-closed
`scripts/smoke-macos-preview.bash` harness supplied a fresh `HOME`,
`PARADEV_ROOT`, temporary directory, project destination, and isolated HOI4
mod root. Its packaged-backend child `PATH` was only `/usr/bin:/bin`; no
Conda, uv, checkout Python, or manually maintained hidden metadata was
available to that process. Import took 20.04 seconds. The harness persisted
the active-project setting, read it back, reopened the exact managed PIHC3
root through `paradev.desktop.state.v1`, detached the read-only DMG, and
removed its owned temporary tree before publishing the durable evidence file
listed above.

| Packaged build | Duration | Modules | Collections | Artifacts | Diagnostics/errors | Exit |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Clean/full | 107.69 sec | 17,802 | 78 | 37,501 | 0 / 0 | 0 |
| Cached full | 101.32 sec | 17,802 | 78 | 37,501 | 0 / 0 | 0 |
| Family partial: `technology` | 62.21 sec | 300 | 0 | 11,899 | 0 / 0 | 0 |
| Module partial: `technology/TECHNOLOGY_FIREARM_I` | 61.36 sec | 1 | 0 | 10,997 | 0 / 0 | 0 |

Clean/full and cached each emitted a 91,188,453-byte JSON result with identical
SHA-256 `d4037f24b978999e9174450e461597f651e5025cacc86d3d7ecd04e9b7b1244d`
and reported identical counts with zero diagnostics/errors. After both partial modes, the
published mod still contains exactly 37,501 files. The v3 emitted-artifact
ledger also contains 37,501 unique owned paths, state `complete`, and
`whole_project_baseline: true`; its output paths exactly match the 37,501
physical files, proving the partial builds preserved the whole-project launch
baseline.

The same packaged backend then served
`paradev.desktop.hoi4-launch-readiness.v1` for that post-partial state and
returned `ready: true`, code `ready`, and the isolated output root. This
directly verifies the new GUI Run authority without relying on renderer
history or localStorage.

Cache correctness is green. Cached full saves 6.37 seconds (5.9%) versus the
current clean build. Direct use of the core PDX tree and faster source
inventory reduce exact PIHC3 discovery from 40.13 to 22.72 seconds (43.4%)
without adding hidden cache invalidation state. A persistent content-addressed
parse cache is therefore deferred until after the native release path; cached,
family-partial, and module-partial semantics still compile the complete safe
dependency graph and use change-aware publication.

This is stronger than a development-runtime build, but it is not clean-machine
acceptance: the host is the same development Mac and the four current builds
were invoked directly through the packaged sidecar. The exact final unverified
DMG was not opened through Computer Use because that safety path requires an
explicit at-action confirmation. Native first-run and button-driven four-mode
evidence from the immediately preceding candidate remains documented below.
Neither path is clean-OS acceptance. The current GUI build and authoring
bridges are covered by 1,294 frontend and 92 Rust tests.

## Prior Installed-GUI PIHC3 Evidence

The preceding release candidate app was copied from its mounted DMG to:

`/private/tmp/paradev-final-installed.O5mUOH/Applications/ParaDev.app`

The independently extracted project and isolated launcher/mod roots were:

- `/private/tmp/paradev-pihc3-release-candidate.r2JCxl/PIHC3-0.2.3`
- `/private/tmp/paradev-pihc3-release-candidate.r2JCxl/mod-root`
- `/private/tmp/paradev-pihc3-release-candidate.r2JCxl/mod-root/PIHC3`

The installed process received only the supported
`PARADEV_HOI4_MOD_ROOT` override needed to keep smoke output away from the
user's live HOI4 mod directory. All four commands shown by the GUI build
history use the backend inside the installed app.

| GUI build | GUI duration | Modules | Collections | Artifacts | Diagnostics/errors | Exit |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Clean/full | 2 min 26 sec | 17,802 | 78 | 37,501 | 0 / 0 | 0 |
| Cached full | 2 min 9 sec | 17,802 | 78 | 37,501 | 0 / 0 | 0 |
| Family partial: `technology` | 1 min 36 sec | 300 | 0 | 11,899 | 0 / 0 | 0 |
| Module partial: `technology/TECHNOLOGY_FIREARM_I` | 1 min 36 sec | 1 | 0 | 10,997 | 0 / 0 | 0 |

The clean/full and cached structured results are byte-identical:

`216e0616f3687be00fd4bffc39effdf3e2813b474483f0fafa81455df8592815`

Each prior GUI history entry records the installed backend path, exact target,
duration, output JSON, empty stderr log, and exit code 0. The final output has
37,501 files and occupies about 1.3 GiB. Family and module builds update only
their selected scope while retaining the complete published mod.

Cache correctness is green. Warm-build performance remains a major usability
issue: cached full saved only 17 seconds, about 11.6%, and both partial modes
still spend roughly 1 minute 36 seconds in shared discovery/planning work.

## Clean-Machine and Platform Gaps

The bundled backend passed both a minimal-environment identity/catalog probe
and the real companion import plus four-mode build with `PATH=/usr/bin:/bin`,
without Conda, uv, ImageMagick, `convert`, or a checkout interpreter. That is
strong self-containment evidence, but a packaged sidecar on the development
host is not a clean-machine installation test.

The current DMG is arm64-only, declares macOS 11.0 as its minimum, is ad-hoc
signed, and is not notarized. Gatekeeper acceptance is unproven.

The Windows packaging workflow pins uv-managed CPython `3.12.13`, uv
`0.11.31`, Node `24.18.0`, Rust `1.97.0`, and
`x86_64-pc-windows-msvc`; every third-party action is referenced by a reviewed
full commit SHA. It is configured to build MSI and NSIS targets, validate the
bundled backend, embed the offline WebView2 runtime installer, suppress the
release console, disallow downgrades, use stable WiX upgrade code
`2e0e1526-b457-5328-b3f2-e583e27ff2c3`, and select current-user NSIS
installation. It reclaims compiler environments after kit assembly, requires
8 GiB free before native smoke, and uploads the normal kit/evidence artifacts
only after success. It calls fail-closed reusable PowerShell release-kit and
native lifecycle smoke scripts. The smoke installs both MSI and NSIS variants,
opens the GUI, imports the exact PIHC3 package, runs clean/cached/family/module
builds, verifies the complete ledger, and uninstalls without deleting managed
projects or generated mods. A development-host smoke caught and corrected the
module selector to the canonical
`technology/TECHNOLOGY_FIREARM_I` form before any native run.

The runtime now has a Windows generated-publication implementation rather than
failing on Unix-only `dir_fd` capabilities. It uses `CreateFileW`,
`GetFileInformationByHandleEx`, `GetFinalPathNameByHandleW`,
`FlushFileBuffers`, and `SetFileInformationByHandle`; rejects reparse points,
non-fixed drives, and filesystems other than NTFS/ReFS; and keeps the original
project-facing path separate from its stable volume-GUID operation path.
Mac-runnable dispatch/structure/error-propagation tests pass, while six
behavioral tests remain correctly skipped until a native Windows host can
exercise real rename, sharing, reparse, case-only rename, deletion, clear,
retained source-read, and rollback semantics.

The workflow and its static control-plane/publication tests are still local and
untracked, and remote `master` does not contain this workflow, so it cannot
dispatch until an authorized coherent commit/push. It also requires the exact
1.84 GB PIHC3 archive to be uploaded as a release asset in the private
repository and the workflow to receive that asset's immutable numeric ID.
GitHub Actions reads it with its built-in repository token, so no manual
authentication secret or signing credential is required for the unsigned
path. This is not an accepted native run and neither expected Windows
installer exists (0/2). Expected output paths are:

- `apps/desktop/src-tauri/target/x86_64-pc-windows-msvc/release/bundle/msi/*.msi`
- `apps/desktop/src-tauri/target/x86_64-pc-windows-msvc/release/bundle/nsis/*.exe`
- `dist/release/windows-x64/`
- `dist/release/windows-x64-smoke/native-smoke-evidence.json`

GitHub Actions is enabled and a hosted `windows-latest` runner is the viable
native packaging path once the workflow lands on the default branch. The
repository has zero self-hosted runners, hosted-minute availability could not
be read, and this Apple-silicon host has no usable Windows VM/runtime. Windows
extraction must be exercised under a realistic user/OneDrive path and
long-path policy.

Additional release-system gaps remain:

- the combined 1.87 GB DMG now carries the app, exact PIHC3 companion, guide,
  and Applications link in one file. There is still no immutable download
  host or detached publisher signature over that handoff;
- the current artifacts come from a very dirty/uncommitted worktree, so
  source-commit provenance and clean reproducibility are not established;
- owned stale sibling staging cleanup after a terminated import is not yet
  implemented; incomplete staging remains hidden and never publishes;
- the Tauri content-security policy is still `null`;
- Windows generated builds and guarded source-draft batches are now
  implemented, but module-directory rename/removal and scaffold transactions
  still use Unix-only descriptor mutation gates. Windows is therefore
  build-capable and file-edit-capable in source but not yet fully
  authoring-capable until those directory operations reuse the Win32 authority;
- the canonical version mapping is aligned and manual lifecycle behavior is
  documented, but updater, rollback, upgrade, and uninstall acceptance are not
  yet exercised on clean hosts.

The embedded package catalog is derived deterministically from the PIHC3
archive by `scripts/package_project.py`; check mode proves the generated
`0.1.0-0` catalog is byte-identical to the bundled resource. Canonical sync now
updates/checks its ParaDev and desktop version binding, and subsequent Tauri
package builds automatically run the exact archive-row check when the companion
is present. The current DMG's metadata, archive, and installed-environment
checks were run explicitly before and after its build. Default Cargo
`--locked` forwarding was active, the lockfile did not drift, and the locked
Cargo metadata/test gates pass.

## Final Regression Gates

| Gate | Current evidence |
| --- | --- |
| Python | 2,305 passed, 35 explicitly skipped, 2 warnings, and zero failures/errors in 354.88 seconds. Skips require external PIHC2/PIHC_dev/live-checkout fixtures or native Windows. |
| Python formatting/lint/environment | Black passed for 191 files; the Flake8 compatibility script, Heaven-style architecture contracts, environment-sync check, generated REST/API catalog references, and lockfile check passed. The manual Heaven utility-import scan retains intentional boundary exceptions for direct Win32/descriptor operations, safe C YAML parsing, and fail-closed `os.walk`; these are core filesystem/parser boundaries rather than generic utility reimplementations. Critical release files still require coherent source integration. |
| Release packaging | Construction and independent check mode both verified the exact 2,047-byte manifest, preferred v4 combined DMG, packaged backend, catalog, PIHC3 companion, mounted contents, and checksums. The macOS packaging file passed 8 focused tests; the real v4 run published passing detached-image four-mode evidence. The Windows workflow gate passed 9 focused tests plus actionlint; six runtime semantics remain native-only. |
| Desktop frontend | 75 files, 1,294/1,294 tests passed; TypeScript and the production Vite build passed. |
| Tauri/Rust | 92/92 tests passed; formatting passed, and Clippy passed for all targets/features with warnings denied. |
| Packaging dependencies | `npm audit` reports zero vulnerabilities. |
| Bundled runtime | Minimal-environment backend identity, HeavenBase catalog, exact embedded PIHC3 catalog, fresh extraction of the real 1.84 GB archive, and all four mounted-preferred-DMG backend build modes passed. |
| Archive | 137,566-member CRC/manifest verification and `unzip -t` passed. |
| PIHC3 parity | Current packaged runtime and prior installed GUI: all four modes passed; full/cached report 17,802 modules, 78 collections, 37,501 artifacts, zero diagnostics/errors. |

## External Credentials and Infrastructure

Public release requires authority or infrastructure not present in the
repository:

- Apple Developer ID Application identity, team access, and notarization
  credentials for `notarytool` (deferred for the requested unverified preview);
- a Windows Authenticode code-signing certificate/private key or HSM and
  timestamp-service configuration (also deferred for the unsigned path);
- a clean supported Apple-silicon macOS machine or VM;
- a real clean Windows x64 machine or VM with its initial WebView2 state
  recorded—preferably absent or old enough to exercise offline provisioning—
  plus a usable HOI4 installation;
- a secure publication path for the combined 1.87 GB macOS preview and future
  Windows installers.

## Conditional ETA

- **Unsigned macOS developer handoff:** available now as one combined DMG with
  development-host packaged four-mode evidence, prior native
  first-run/installed-GUI evidence, and an exact outer integrity manifest;
  exact-final-DMG GUI launch, game launch, and clean-host acceptance are still
  outstanding.
- **First unsigned Windows artifacts:** approximately 0.5–1 engineering day
  after the current coherent workflow/backend slice is authorized for
  commit/push, the exact PIHC3 archive is a repository release asset with a
  known immutable numeric ID, and a native runner is available, assuming no
  runner-specific failure.
- **Both unsigned clean-machine acceptance paths:** approximately 1–3 working
  days after clean macOS and Windows hosts, HOI4 installations, and the PIHC3
  payload are available.
- **Signed public release:** approximately 1–3 additional working days after
  Apple and Windows signing credentials are available, provided
  notarization, SmartScreen/Gatekeeper, update, game-launch, and uninstall
  checks expose no new blocker.

These are conditional engineering estimates, not a release date. Signing is
not on the current unverified critical path. A Windows long-path failure,
offline WebView2 provisioning failure, or game-launch failure will extend
them.
