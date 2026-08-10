# Tauri-free System-WebView Release Checkpoint

Status: implemented and verified

Date: 2026-08-10

## Outcome

ParaDev now has one desktop distribution path: the Python wheel serves the
packaged React application and the same-origin FastAPI service, while the macOS
host is a thin system-WKWebView application installed by
`paradev-gui --install-app`. React and Vite remain build-time tools only.
`paradev-gui` prefers the system WebView on macOS; `--app` is the explicit
Chromium fallback. Native Windows packaging remains deferred.

The Rust application, Cargo manifests and caches, desktop command adapter,
sidecar bundle, installer-preview scripts, Windows installer workflow, npm
Tauri dependencies, frontend runtime branches, mocks, and current-authority
documentation were removed together. The reusable icon now belongs to
`apps/desktop/host/`. Generated Tauri output, including roughly 33 GB under the
old target directory, was discarded.

PIHC3's staged source-control tree also now contains its required portable
Entity assignment table. A clean staged-index export reports 70 module
families, 14,574 modules, 90 collections, 36,469 authored source files, and no
retired component, legacy, or inactive source tree. Unreferenced high-resolution
loading-screen originals remain local-only and ignored instead of inflating the
canonical source commit.

## Distribution evidence

- Wheel: `dist/tauri-free-final/paradev-0.1.0.0.dev0-py3-none-any.whl`
- Wheel bytes: `1,808,289`
- Wheel SHA-256:
  `0e02a8026fc4e4f2a0f1e365d99ff77d770ee697d146555574299f37f2e099ff`
- Installed-App evidence:
  `dist/evidence/2026-08-10-tauri-free-final-system-webview-app-smoke.json`
- Installed-wheel PIHC3 evidence:
  `dist/evidence/2026-08-10-tauri-free-final-four-mode-wheel-smoke.json`
- Rebuilt-sdist wheel evidence:
  `dist/evidence/2026-08-10-tauri-free-final-sdist-wheel-smoke.json`

The isolated installed-App smoke created `ParaDev.app` from the wheel, verified
its ad-hoc signature and isolated runtime binding, launched it through
LaunchServices, loaded the hashed same-origin frontend on dynamic port 59375,
proved a foreign listener on port 4817 survived, and observed both the app and
its owned server terminate after Quit.

The source distribution contains 184 deliberate entries and excludes tests,
docs, demos, projects, caches, and retired desktop sources. Its rebuilt wheel
has SHA-256
`0e555a063b8869a9ccd440bd7e937b7b3bcf5ab949ae5a3d2be1a716a2a4f4f1`.
Both wheels contain the exact 22-file frontend, three host files, typed API
facade, project-package catalog, and installed CLI entry points. Twine metadata
checks passed for the wheel, sdist, and rebuilt wheel.

## PIHC3 installed-wheel matrix

| Mode | Seconds | Modules | Collections | Planned artifacts |
| --- | ---: | ---: | ---: | ---: |
| Clean/full | 76.934 | 14,573 | 106 | 33,437 |
| Cached whole project | 30.433 | 14,573 | 106 | 33,437 |
| MIO family partial | 19.782 | 7 | 0 | 9,304 |
| `ai_bonus_weights` module partial | 19.776 | 1 | 0 | 9,298 |

Every mode completed with zero diagnostics and errors. Each preserved exactly
33,436 game files, 1,215,472,435 bytes, and SHA-256
`3e4f2e61d8393054fe5e9e4d766e030f7032e18459120c68bac48becd8f3bbe3`.
The isolated runtime used HeavenBase 0.1.2.2, FastMCP 4.0.0b2, and MCP 2.0.0;
the app had neither developer-path nor `uv` access.

## Verification

- Python: 2,638 passed; nine native-Windows semantics tests skipped on macOS.
- Desktop: 91 files and 1,493 tests passed.
- Source cache: 47 adversarial checksum, topology, symlink, filesystem, and
  ABA-race tests passed.
- Staged PIHC3: clean, cached, family-partial, and module-partial builds passed
  before the installed-wheel matrix.
- Black, Flake8, generated metadata, uv/Poetry locks, README synchronization,
  TypeScript, Vite, exact package sync, wheel inventory, sdist rebuild, Twine,
  and diff-whitespace gates passed.
- The heaven-style vendored-skill self-scan passed. Security-sensitive SDK
  code retains direct `Path`, descriptor-level `os`/`shutil`, incremental hash,
  and parser-exception APIs where HeavenBase utilities do not own an equivalent
  contract; the current heaven-style utility rule explicitly permits that
  ownership-boundary fallback.
- Active production source, E2E fixtures, npm metadata, built frontend, and
  packaged frontend contain no Tauri runtime or packaging reference.

The release workflow now pins Node 22 and makes publication depend on generated
metadata, Python/frontend behavior, formatting, exact source-distribution
inventory, and clean/cached/family/module publication parity. This checkpoint
remains an alpha development build; stable PyPI versioning and platform signing
or notarization are separate release decisions.
