# PIHC3 Validated Artifact-plan Cache

Status: implemented and verified

Date: 2026-08-10

## Outcome

ParaDev now reuses one checksum-validated finalized artifact plan when a normal
cached or targeted build proves that the complete project/compiler state is
unchanged. The real installed-wheel GUI host completes the PIHC3 MIO family and
single-module authoring loops in about 17.8 seconds while retaining full
project localization reconciliation, target closure, transactional publication,
and canonical manifests.

The same installed app completed clean/full, cached whole-project,
family-partial, and module-partial PIHC3 builds with zero diagnostics. A new
release-gate snapshot hashed every generated path and file byte after each mode;
all four modes produced the exact same 33,437-file, 1,215,728,772-byte mod
snapshot.

## Cache Contract

- Aggregate source-cache signatures cover the deterministic set of active
  module/collection families and their source roots.
- The finalized-plan signature also covers project/profile metadata, static
  copy artifacts and diagnostics, the Registry view, family/writer/postprocessor
  implementation files, Python and package versions, and core planning/writer
  code.
- A postprocessor that reads external state must expose
  `artifact_cache_key(context)`. PIHC3 localization fingerprints every resolved
  external reference localization path and byte. A missing, invalid, or failing
  key disables plan reuse instead of risking stale output.
- Entries live in hidden disposable state under
  `.paradev/cache/artifact-plans/`. They are bounded, checksum-protected
  JSON/Gzip written by fsync plus atomic replacement; they never contain pickle
  or executable code. The real PIHC3 entry is 9.8 MiB.
- Final PDX payloads are cached as their exact rendered text, which the existing
  writer publishes byte-for-byte. Current parsed-source bundles are reattached
  on read so source, localization, and asset inspection APIs retain their normal
  views.
- Missing, stale, corrupt, oversized, invalid, or unwritable entries fall back
  to normal planning. One external-input change during planning triggers one
  safe replan; repeated changes fail actionably rather than publishing a mixed
  snapshot.
- Full builds always bypass cache reads and refresh a valid entry. Cache hits
  skip unchanged family compilation and finalized planning only; target
  resolution, collection/publication closure, collision and retained-ledger
  validation, transactional emission, and canonical manifests still run.

This follows the Heaven-style extension boundary: core ParaDev contains no
PIHC3 branch, while the project-local localization extension declares the only
extra invalidation input it owns.

## Performance Evidence

The installed wheel was launched with an isolated home and temp directory, no
developer checkout on its import path, and no `uv` available to the app. Build
times are the desktop-hosted compiler duration; the subsequent 1.2 GB parity
snapshot is outside those values.

| Mode | Seconds | Modules | Collections | Artifacts |
| --- | ---: | ---: | ---: | ---: |
| Clean/full | 72.265 | 14,573 | 106 | 33,437 |
| Cached whole project | 38.685 | 14,573 | 106 | 33,437 |
| MIO family partial | 17.816 | 7 | 0 | 9,304 |
| `ai_bonus_weights` module partial | 17.828 | 1 | 0 | 9,298 |

The module authoring loop is 61% faster than the earlier 46.0-second installed
checkpoint and 32% faster than the immediately preceding 26.3-second warm
checkpoint. The cached whole-project build is 52% faster than the earlier
81.28-second baseline. A source-checkout cache refresh measured 48.10 seconds;
the cache deliberately optimizes repeated authoring, not the first build after
a source/compiler/runtime change.

All four generated snapshots share SHA-256
`734add5828a38792a63db27cea90dd3fee5620c2ae7f923099f120ddb8881f92`.

## Installable Evidence

- Wheel: `dist/python/paradev-0.1.0.0.dev0-py3-none-any.whl`
- Wheel SHA-256:
  `e3135e2706f8b8d12a22e75e3aae0a35b566aaec024d1bbbbe26f963ad711eed`
- Evidence:
  `dist/evidence/2026-08-10-081242-pihc3-artifact-plan-wheel.json`
- Installed runtime: ParaDev `0.1.0.0.dev0`, HeavenBase `0.1.2.2`, FastMCP
  `4.0.0b2`, and MCP `2.0.0`.
- Packaged frontend: 22-file exact inventory, same-origin runtime bootstrap,
  and hashed JavaScript asset load all passed.

## Verification

- `rtk bash scripts/test.bash`: 2,469 passed, 9 expected native-Windows skips.
- `rtk npm --prefix apps/desktop test`: 1,515 passed across 93 files.
- Focused cache/build/manifest/wheel contracts: 225 passed.
- `rtk bash scripts/flake.bash --ci`: 235 files format-clean.
- `rtk bash scripts/sync-env.bash --check`: lock, metadata, and README
  projections current.
- `rtk npm --prefix apps/desktop run check:package`: exact 22-file GUI
  inventory current.
- PIHC3 source-layout audit: zero errors across 70 module families, 14,574
  source modules, and 36,469 files; only one visible metadata file remains.
- Heaven-style routing index and `git diff --check`: passed.

## Next

Warm cached whole-project publication still takes 38.7 seconds because ParaDev
must discover current sources, validate retained output, and process canonical
whole-project publication/manifests. Profile those phases under the installed
host. The next safe optimization seam is a metadata-only source fingerprint
index or batched retained-file validation, with corruption fallback and the same
four-mode byte-parity gate. Do not weaken project-wide localization or
transactional publication to make targeted numbers look smaller.
