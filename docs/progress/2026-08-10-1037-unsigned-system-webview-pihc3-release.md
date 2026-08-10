# Unsigned System-WebView PIHC3 Release Checkpoint

Status: implemented and verified

Date: 2026-08-10

## Outcome

ParaDev now has one wheel-hosted Python application boundary for the default
macOS GUI. The installed `ParaDev.app` launches the packaged React frontend in
the system WebView over a same-origin loopback API, reports bounded child-server
startup errors, and terminates both the app and Python child after startup
failure or normal quit. Tauri remains an optional compatibility host.

The system-WebView host can select an existing project, import a verified
project ZIP into `~/Documents/ParaDev/Projects`, and scaffold collection
templates through the same Python SDK/REST operations as Tauri. The public
architecture payload now describes this real default path instead of the old
Nuitka/Tauri-first plan.

PIHC3's Focus, Decision, Modifier, Opinion Modifier, Trait, Idea, and Event
families are now thin project compiler overlays over canonical ParaDev/HoI4
entities. Their redundant `hb.Entity` shells and empty extension registrations
are gone, while project-specific compilation, source slots, presentation,
inference, shared emission, and diagram authoring remain. The project has 70
registered compiler families and 63 genuinely project-owned Entities.

This follows the Heaven-style ownership boundary: Python owns installation,
validation, lifecycle, and filesystem mutations; Registry/compiler overlays own
PIHC3 behavior; the frontend is a consumer of those contracts rather than a
second implementation.

## Installability Checklist

- [x] Build one pure-Python wheel containing all ParaDev code, the exact
  22-file frontend inventory, and three macOS host assets.
- [x] Install a user-local unsigned `~/Applications/ParaDev.app` with
  `paradev-gui --install-app --yes` from an isolated Python 3.12 runtime.
- [x] Verify the app's ad-hoc signature, runtime binding, packaged index,
  runtime bootstrap, hashed asset, loopback health, and child-server shutdown.
- [x] Open the current PIHC3 project in a wheel-only runtime with HeavenBase
  `0.1.2.2`, FastMCP `4.0.0b2`, and MCP `2.0.0`, without checkout imports,
  Conda, or `uv` visible to the app.
- [x] Verify clean/full, cached whole-project, family-partial, and module-partial
  PIHC3 compilation with exact output parity.
- [x] Re-audit the physical PIHC3 module tree: zero `_component`,
  `_asset_component`, `legacy`, or `inactive_modules` directories.
- [x] Document install, upgrade/reinstall, runtime lifetime, and removal.
- [ ] Publish a stable PyPI release and run the release workflow on a separate
  clean macOS runner. The local unsigned artifact is usable now; publication
  is not claimed by this checkpoint.

Windows integration and macOS game launch are intentionally outside the
current user-selected scope. Signing/notarization is not required for this
unsigned development release.

## Exact Artifacts And Evidence

- Wheel: `dist/python/paradev-0.1.0.0.dev0-py3-none-any.whl`
- Wheel bytes: `1,814,270`
- Wheel SHA-256:
  `7664bc58d7d6a2796b1c485ba60ab72b5d6c3fd0a7de1cc908f5689bb4d77c02`
- Installed-App evidence:
  `dist/evidence/2026-08-10-final-macos-installed-app-smoke.json`
- Installed-App evidence SHA-256:
  `ce9734746ec3913bb79f0767aca3611bec63336d7a480019c7cdfe2d516806a5`
- Four-mode PIHC3 evidence:
  `dist/evidence/2026-08-10-final-pihc3-four-mode-wheel-smoke.json`
- Four-mode evidence SHA-256:
  `72326478c6ae55b87bdc61e37437bb83440dc4560a21bdb07abd43a1b6343bed`

| Mode | Seconds | Modules | Collections | Artifacts |
| --- | ---: | ---: | ---: | ---: |
| Clean/full | 78.232 | 14,573 | 106 | 33,437 |
| Cached whole project | 33.801 | 14,573 | 106 | 33,437 |
| MIO family partial | 22.692 | 7 | 0 | 9,304 |
| `ai_bonus_weights` module partial | 23.225 | 1 | 0 | 9,298 |

Every mode completed with zero diagnostics and errors and preserved the same
33,436 game files, 1,215,728,316 bytes, and SHA-256
`6793927141002c51ff39f04ee9c68df0607058bb7c2009d77104581abbad7f14`.
The hidden publication marker is validated separately and excluded from this
game-file digest.

## Verification

- Full Python gate: 2,503 passed, 9 expected native-Windows skips.
- Desktop gate: 1,519 passed across 93 files.
- PIHC3 extensible-layout gate after the seven-overlay cleanup: 33 passed.
- Architecture contract gate: 92 passed; exact changed CLI assertions: 4
  passed.
- Wheel builder: exact 22 frontend files and 3 host files.
- Installed-App smoke: isolated install, valid ad-hoc signature, health/UI
  probes, and confirmed child exit.
- Black/Flake8 on the touched Python scope, packaged-GUI inventory,
  environment lock, generated metadata, README projections, JXA compilation,
  and `git diff --check`: clean.
- The Heaven-style scanner retains advisory findings for direct standard-library
  filesystem/process imports in the platform-bound installer and macOS launcher.
  These are explicit OS integration boundaries; replacing them without an
  equivalent HeavenBase primitive would reduce clarity and is not a release
  blocker.

## Scoped Follow-ups

- Cached PIHC3 builds still hash every byte of the 1.4 GB source tree before a
  family-cache hit. The next performance slice should add a checksummed,
  race-safe per-file fingerprint inventory with full fallback on ambiguous
  metadata or unsupported filesystems.
- Static Tauri imports and `scripts/run.bash` still retain the compatibility
  host as a developer path. They are not used by the installed wheel default
  and should be retired only after remaining compatibility users migrate.
- REST routing still reaches some desktop/SDK adapters directly. A later
  dependency-inversion pass should make one application-service boundary
  explicit without destabilizing this release.
- Vite reports two existing large frontend chunks. Code splitting is a load
  optimization, not an install, lifecycle, or PIHC3 compilation blocker.
