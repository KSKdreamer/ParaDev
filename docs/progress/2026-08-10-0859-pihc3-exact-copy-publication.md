# PIHC3 Exact-copy Publication

Status: implemented and verified

Date: 2026-08-10

## Outcome

ParaDev now avoids redundant source reads and temporary staging for unchanged
static-copy artifacts while preserving exact full/cached/partial PIHC3 output
parity. The installed-wheel cached whole-project build fell from 38.685 to
28.498 seconds. This is 26.3% faster than the preceding validated-plan cache
checkpoint and 64.9% faster than the original 81.28-second publication
baseline.

The same isolated installed app completed clean/full, cached whole-project,
MIO family-partial, and single-module partial builds with zero diagnostics.
All four modes produced exactly 33,437 files and 1,215,728,772 bytes with the
same path-and-byte snapshot SHA-256
`98fd4769c119fee9ad88e730537b0fb27609864f08f2727d8cca71548dfcd11f`.

## Publication Contract

- Copy discovery records `content_sha256`, the SHA-256 of the exact source
  bytes, alongside the existing HeavenBase deterministic-object `sha256`.
  These hashes have different meanings and are never substituted for one
  another.
- `StaticCopyWriter.expected_sha256()` exposes only the raw-byte digest.
  Publication streams retained output and skips source rereading and staging
  only when that digest matches exactly.
- Missing or mismatched retained output uses the normal exact render/stage path.
  This repairs external target edits and preserves source-drift rejection.
- Invalid digest metadata fails closed. Unhashed and larger-than-64-MiB sources
  use ordinary staging, so memory use remains bounded.
- `render_bytes()` may return `None` for one artifact to request the ordinary
  writer path. `render_mode()` preserves source permission bits on direct
  publication.
- The HOI4 building-icon postprocessor declares its narrow transform scope.
  `common/buildings/*.txt` and `interface/*.gfx` remain staged; unrelated copy
  artifacts keep the direct path.
- The Windows directory authority implements the same handle-retained,
  streaming digest comparison as the POSIX authority.

This follows the Heaven-style extension boundary: the publication core exposes
typed optional writer and transform capabilities, while PIHC3 needs no branch
or special-case cache rule.

## Performance Evidence

The installed wheel ran with an isolated home and temporary directory, no
developer checkout on its import path, and no `uv` available to the app. Build
times are the compiler durations; the subsequent 1.2-GB parity snapshot is not
included.

| Mode | Seconds | Modules | Collections | Artifacts |
| --- | ---: | ---: | ---: | ---: |
| Clean/full | 65.143 | 14,573 | 106 | 33,437 |
| Cached whole project | 28.498 | 14,573 | 106 | 33,437 |
| MIO family partial | 18.338 | 7 | 0 | 9,304 |
| `ai_bonus_weights` module partial | 18.333 | 1 | 0 | 9,298 |

A source-checkout profile of the final cached whole build measured 26.782
seconds. The largest remaining phases were static publication and retained-file
hashing at 8.410 seconds, source discovery at 7.205 seconds, and canonical
manifest work at 3.242 seconds. The prior profile spent 19.587 seconds in
artifact writing; the exact-copy path reduced that phase by 57.1% without
removing retained-file validation.

## Installable Evidence

- Wheel: `dist/python/paradev-0.1.0.0.dev0-py3-none-any.whl`
- Wheel SHA-256:
  `65726cb682148f50aede22fb05f417a6479a928e37f998b606c2af64437742b6`
- Evidence:
  `dist/evidence/2026-08-10-084803-pihc3-exact-copy-wheel.json`
- Evidence SHA-256:
  `a4952b71b8614508767e5b957b6b6253ab6d4aa4cff22e2b4a43f3d6f33c159d`
- Installed runtime: ParaDev `0.1.0.0.dev0`, HeavenBase `0.1.2.2`, FastMCP
  `4.0.0b2`, and MCP `2.0.0`.
- Packaged frontend: exact 22-file inventory and same-origin runtime bootstrap
  checks passed.

## Verification

- Focused publication/cache/HOI4/Windows contracts: 346 passed, 6 expected
  native-Windows skips.
- `rtk bash scripts/test.bash`: 2,482 passed, 9 expected native-Windows skips.
- `rtk npm --prefix apps/desktop test`: 1,515 passed across 93 files.
- `rtk bash scripts/flake.bash --ci`: 235 files format-clean.
- `rtk bash scripts/sync-env.bash --check`: lock, metadata, and README
  projections current.
- `rtk npm --prefix apps/desktop run check:package`: exact 22-file GUI
  inventory current.
- PIHC3 source-layout audit: zero errors across 70 module families, 14,574
  source modules, and 36,469 files; only one visible metadata file remains.
- Heaven-style routing index and `git diff --check`: passed.

## Next

The next safe cached-build optimization seam is source discovery and canonical
manifest projection. A metadata-only source fingerprint index could avoid much
of the 7.2-second walk if it remains disposable and validates ambiguous or
changed state conservatively. Manifest projections may also be reused when
their complete inputs match. Neither optimization should weaken exact retained
output hashing, project-wide localization reconciliation, target closure, or
transactional publication.
