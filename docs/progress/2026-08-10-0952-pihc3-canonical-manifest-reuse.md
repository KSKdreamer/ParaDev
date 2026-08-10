# PIHC3 Canonical Manifest Reuse And Installed App Host

Status: implemented and verified

Date: 2026-08-10

## Outcome

ParaDev now reuses already-published canonical build manifests only when a
checksum-bound hidden receipt proves that the finalized artifact plan,
manifest projector, complete manifest inventory, and every retained manifest
file are unchanged. A stale, corrupt, incomplete, mismatched, or unwritable
receipt falls back to the normal canonical projection without blocking a
build. External edits to a generated manifest are repaired.

The combined Python wheel also contains the React application and thin macOS
system-WebView hosts. `paradev-gui` is the default installed application
boundary, serves the same-origin REST/UI surface on loopback, supports explicit
Chromium or browser modes, and can install a user-local `ParaDev.app`. Tauri is
now an optional compatibility host rather than the required runtime.

## Manifest Publication Contract

- `CachedArtifactPlan.signature` carries the exact validated plan identity from
  the generic artifact-plan cache; no PIHC3-specific branch was added.
- Receipts live under `.paradev/cache/manifest-publications/`, keyed by the
  resolved build root. They are disposable system state, not user metadata.
- Each bounded receipt has its own payload checksum and records the exact
  canonical manifest-name-to-SHA-256 mapping.
- A receipt hit streams and validates every current manifest before projection
  is skipped. Missing files, extra or malformed receipt rows, changed projector
  code, a changed plan signature, and target tampering all use the ordinary
  projection path.
- Receipt read and write failures are observable but nonblocking. Successful
  fallback publication atomically refreshes the receipt.
- Public manifest inspection remains canonical and unchanged; only redundant
  materialization work is avoided.

This follows the Heaven-style evidence boundary: reusable state is hidden,
checksummed, disposable, and fail-safe, while authored PIHC3 sources and the
HeavenBase Registry remain the semantic owners.

## Measurement And Determinism

PIHC3's eleven canonical manifest files encode about 120.3 MB. Before this
slice, projecting their payloads took about 2.99 seconds and encoding took
about 0.39 seconds on the current machine. A true warm source-checkout build
after receipt creation completed in 25.322 seconds, versus 26.782 seconds at
the preceding exact-copy checkpoint.

Two clean PIHC3 builds in separate Python processes at the same fixed output
and build roots produced zero changed files across 33,437 compiler artifacts.
Release evidence excludes the single `.paradev-publication.json` control file
from the game-file digest but reports its count and byte size separately. The
digest remains intentionally root-specific because `descriptor.mod` contains
the configured absolute output path; it is used to prove exact clean/cached/
partial parity inside one isolated runtime, not to claim false cross-root byte
identity.

## Installed-wheel Evidence

- Wheel: `dist/python/paradev-0.1.0.0.dev0-py3-none-any.whl`
- Wheel SHA-256:
  `8c5de86ae1f6a4520de58c203491cfd6f1ad45041347383f56b3973c3d9181fc`
- Evidence:
  `dist/evidence/2026-08-10-094548-pihc3-manifest-reuse-wheel.json`
- Evidence SHA-256:
  `95e13d97b95c3e09676743f9ca440bfd13259f982544a0cc1693c7771976d803`
- Runtime: isolated venv/home/temp, no developer checkout import, no `uv`
  available to the app; ParaDev `0.1.0.0.dev0`, HeavenBase `0.1.2.2`, FastMCP
  `4.0.0b2`, MCP `2.0.0`.
- Frontend: exact 22-file packaged React inventory, three exact host assets, and
  same-origin runtime bootstrap.

| Mode | Seconds | Modules | Collections | Artifacts |
| --- | ---: | ---: | ---: | ---: |
| Clean/full | 77.811 | 14,573 | 106 | 33,437 |
| Cached whole project | 29.333 | 14,573 | 106 | 33,437 |
| MIO family partial | 23.235 | 7 | 0 | 9,304 |
| `ai_bonus_weights` module partial | 20.684 | 1 | 0 | 9,298 |

All four modes completed with zero errors and diagnostics and preserved the
same 33,436 game files, 1,215,728,316 bytes, and exact run-local SHA-256
`6793927141002c51ff39f04ee9c68df0607058bb7c2009d77104581abbad7f14`.
The one hidden publication marker was validated as a regular file and excluded
from that game-file snapshot.

## Verification

- Manifest/cache/wheel/GUI focused gate: 52 passed; the final wheel-snapshot
  contract has 16 focused passing tests.
- Publication/cache regression gate: 234 passed, with 6 expected native-Windows
  skips.
- Full Python gate at the combined checkpoint: 2,495 passed, 9 expected
  native-Windows skips.
- PIHC3 retired-layout, HeavenBase extension, and macOS-host gate: 48 passed.
- Desktop: 1,515 passed across 93 files.
- Wheel builder: exact 22 frontend files and 3 host files.
- Black/Flake8 gate: 238 files format-clean.
- Environment lock, generated metadata, README projections, and packaged GUI
  inventory: current.
- Heaven-style scan: no new production findings; only existing advisory flags
  in Windows test fixtures.

## Next

The largest remaining cached-build costs are source discovery, retained-file
validation/publication, and progress I/O. Any next optimization should preserve
the same exact plan identity, target closure, transactional publication,
manifest receipt fallback, and installed-wheel four-mode evidence gate.
