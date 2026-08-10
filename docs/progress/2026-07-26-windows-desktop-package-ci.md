# 2026-07-26 Windows Desktop Release Path

## Scope

The native Windows path now has reusable release-kit and lifecycle-smoke
scripts instead of workflow-only packaging logic:

- `scripts/package-windows-preview.ps1` assembles or checks one fail-closed,
  unsigned Windows x64 release kit.
- `scripts/smoke-windows-preview.ps1` installs, launches, builds with, and
  uninstalls the release kit on native Windows while recording compact
  evidence.
- `.github/workflows/windows-desktop-package.yml` pins every action revision and
  build-tool version, installs an isolated uv-managed CPython `3.12.13`,
  downloads the exact PIHC3 companion from the current private repository by
  required immutable numeric `project_package_asset_id`, builds MSI and NSIS,
  and calls both scripts.

The workflow remains manual and read-only. It does not publish a GitHub
release, sign binaries, request credentials, or modify repository contents.
Its fixed GitHub release-asset API request uses only Actions' built-in read
token under `contents: read`; it accepts no arbitrary package URL or manually
configured secret. Curl keeps credentials on the API origin under its safe
redirect default and permits HTTPS redirects only. The exact catalog check
runs against the sibling `.partial` download before one same-volume rename
publishes `dist/projects/PIHC3-0.2.3-project.zip`.

Before installer creation it now runs the retained-Win32 publication and
source-draft contracts plus portable artifact-path, direct writer, manifest,
adversarial publication, path-index, and full project-build suites.
Native-only tests exercise actual Win32 replace/no-clobber, sharing, reparse,
case-normalization, deletion, full-clean, guarded source write/remove, and
transaction rollback behavior when the workflow reaches a Windows host.

## Generated Publication Backend

Windows no longer falls through the Unix `dir_fd` capability guard. The build
filesystem dispatches lazily to a private Win32 adapter while preserving the
existing `AnchoredDirectory` API and POSIX implementation.

The Win32 authority:

- retains verified directory/file handles without `FILE_SHARE_DELETE`;
- rejects reparse points, non-fixed drives, devices, cross-volume traversal,
  and filesystems other than NTFS/ReFS;
- records stable volume serial and 128-bit file identity;
- canonicalizes operations to a volume-GUID namespace while separately
  rechecking the original project-facing path;
- creates a sibling file with `CREATE_NEW`, flushes it, and atomically renames
  it by handle with explicit replace/no-clobber behavior; and
- deletes and clears through opened handles without following junctions.

Generated artifact paths also share one cross-platform policy that rejects
Windows device aliases, trailing spaces/dots, alternate data streams, invalid
characters, and controls before physical publication.

This backend covers emitted builds and manifests. Source reads and source-draft
write/remove batches now reuse the same retained Win32 authority, including
bounded stable snapshots, optimistic revision guards, rollback identity/content
checks, and original-path verification. Module directory rename/removal and
scaffold transactions still have Unix-only mutation gates, so Windows is not
yet fully authoring-capable.

## Fail-Closed Release Kit

The packaging script requires all of the following before it can publish
`dist/release/windows-x64/`:

- one exact `PIHC3-0.2.3-project.zip` matching the complete embedded catalog
  row;
- exactly one fresh MSI and one fresh NSIS EXE created after the workflow's
  build marker;
- matching fresh staged and bundled `paradev-backend.exe` bytes;
- a bundled backend that executes natively and reports the expected protocol,
  ParaDev version, HeavenBase `0.1.2.1`, `win32`, and x64 machine;
- a bundled project-package catalog logically identical to the repository
  catalog; and
- `NotSigned` Authenticode status for both explicitly unverified installers.

There is no missing-project escape hatch on this path. The workflow also no
longer passes `--allow-missing-project-package` to the Tauri build wrapper.
Its required input is one positive decimal GitHub release asset ID, never a URL.
The fixed current-repository API endpoint permits HTTPS redirects only; the
downloaded archive is published only after its full catalog check succeeds.

The release kit contains:

- the MSI and NSIS EXE;
- the exact PIHC3 ZIP;
- bilingual `START-HERE.html`;
- `backend-info.json`;
- canonical `release-manifest.json`; and
- `SHA256SUMS` covering every other public file.

Assembly happens in a private sibling directory followed by one directory
rename. Existing output is rejected by default. Explicit replacement first
proves the old directory is an owned, complete release kit and keeps a
recovery directory until the new kit is published.

After assembly, the workflow removes only build-time environments and
intermediates that the installed-runtime smoke cannot use: the repository
virtual environment, workspace uv-managed Python, Node modules, Nuitka output,
the staged backend, the target release tree, and the now-redundant source
archive link. It then requires at least 8 GiB free before extracting PIHC3 and
building the generated mod. The normally named release-kit and evidence
artifacts upload only after native smoke passes; a failed smoke leaves logs but
does not publish its candidate installers as a normal handoff.

## Native Lifecycle And PIHC3 Smoke Contract

The native smoke script refuses to run when it detects an existing ParaDev
installation, so it cannot silently uninstall a user's app. With a fresh host
it performs the following sequence:

1. install MSI silently, discover the installed GUI and backend, and verify
   backend identity;
2. import the exact companion through
   `desktop_install_project_package`, persist the managed PIHC3 path, show a
   visible ParaDev window, and close it gracefully;
3. run the installed backend directly—without checkout Python, Conda, or
   uv—for clean/full, cached full, `technology` family-partial, and
   `technology/TECHNOLOGY_FIREARM_I` module-partial builds;
4. require the established 17,802-module / 78-collection / 37,501-artifact
   whole-project counts and 300 / 11,899 and 1 / 10,997 partial counts, all
   with zero diagnostics, zero errors, and no blocking state;
5. require byte-identical clean/full and cached structured results, plus a
   complete v3 37,501-artifact publication ledger with a whole-project
   baseline;
6. uninstall MSI and prove the managed project and generated mod remain;
7. install NSIS, reopen the same managed project, launch and close the GUI,
   uninstall, and prove the user data remains again.

Only installations created after the no-existing-app preflight are eligible
for failure cleanup. Test project and mod roots are randomized children of the
OS temporary directory, carry a run-specific ownership marker, and are removed
only after their ownership and location are revalidated.

Passing evidence is written separately under
`dist/release/windows-x64-smoke/native-smoke-evidence.json`. It records
installer identities, installed executable identities, GUI visibility and
graceful close, import/reopen results, four build summaries and timings,
publication state, and uninstall retention. It deliberately keeps
`releaseReady: false` and names remaining limitations: unsigned authenticity,
interactive SmartScreen behavior, button-driven build interaction, actual
Hearts of Iron IV launch, and clean-OS-image provenance.

## Reproducibility

- Python is fixed to `3.12.13`; uv is fixed to `0.11.31`. Because CPython
  `3.12.13` has no official Windows installer, the pinned setup-uv action
  installs uv's checksum-verified managed x64 distribution under
  `build/uv-python`, resolves it with downloads disabled, and gives that exact
  interpreter to the frozen sync.
- `uv sync --frozen --extra bundle --extra desktop --extra dev` installs from
  `uv.lock`.
- `requirements.txt` and the lock resolve public
  `heavenbase==0.1.2.1`; no local HeavenBase override is used.
- Node.js is fixed to `24.18.0`; Rust is fixed to `1.97.0` and uses
  `Cargo.lock`.
- Checkout, setup-uv, setup-node, the Rust toolchain/cache actions, and both
  upload-artifact calls use reviewed full commit SHAs rather than movable tags.
- The target is explicitly `x86_64-pc-windows-msvc`.
- The Tauri build remains unsigned and uses the repository's all-in-one
  sidecar-first build wrapper.
- Only a passing release kit and smoke evidence upload, without recompressing
  the approximately 1.8 GB PIHC3 package.

The standard `windows-latest` image remains a moving GitHub-hosted environment,
so these controls make dependency selection auditable but do not claim
byte-for-byte installer reproducibility across runner-image revisions.

## Current Validation Status

The PowerShell lifecycle is deterministic source code, but it has not yet executed
on a real Windows host in this worktree. This macOS host has no
native Windows toolchain, Windows VM, PowerShell runtime, WiX/NSIS execution
environment, or Windows GUI subsystem. Static workflow/script contracts,
portable-path contracts, and the complete POSIX publication/project suite pass
here. Six Win32 behavior tests are intentionally skipped: four generated
publication cases and two source-draft transaction cases. Installer creation,
installation, visible-window probing, uninstall, and the installed four-mode
PIHC3 build cannot run on this host.

No Windows MSI, NSIS EXE, release kit, or native smoke evidence is claimed by
this note. The manual workflow still needs the already cataloged PIHC3 ZIP to
exist as a release asset in this repository and its immutable numeric
`project_package_asset_id`, then a successful native run. The workflow's
built-in read token retrieves private asset bytes; no manual authentication or
signing credential is required.

**Do not claim Windows release-ready until both installers launch and the
installed runtime completes the PIHC3 build contract on clean supported
Windows environments.** Signing is intentionally deferred and is not a
blocker for the user's accepted unverified-app preview, but native execution
evidence remains mandatory.

## Primary References

- [Tauri GitHub Actions pipeline](https://v2.tauri.app/distribute/pipelines/github/)
- [Tauri Windows installer guide](https://v2.tauri.app/distribute/windows-installer/)
- [Tauri Windows signing guide](https://v2.tauri.app/distribute/sign/windows/)
