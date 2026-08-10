# PIHC3 Cached Publication Progress

Date: 2026-08-10 01:10

Linear: none

## Done

- Profiled a real cached PIHC3 build under the published `heavenbase==0.1.2.2`
  wheel. Artifact publication was the largest measured build phase; it created
  and recursively removed one temporary tree per each of 33,437 artifacts.
- Changed the SDK-owned artifact writer to retain one private staging root per
  output batch while deleting each staged file immediately after its anchored
  comparison/publication. Directory structure is reused, but the staging
  footprint remains bounded even though PIHC3's generated output is about
  1.2 GB.
- Coalesced artifact progress to the first artifact, the last artifact, and
  integer-percent changes. The desktop JSONL stream now contains 98 total
  events and 15 writer checkpoints instead of tens of thousands of file
  append/open/close cycles.
- Preserved the pending publication ledger, per-batch confirmed-output
  checkpoints, retained-root safety, and full/cached/family/module output
  semantics. No GUI-side compiler, cache, or publication path was added.

## Verification

- Focused artifact, adversarial publication, structural-transition, progress,
  and interrupted-write recovery gate: 33 passed.
- Published-wheel fast Python gate: 2,410 passed; 9 native-Windows filesystem
  tests skipped on macOS. Desktop gate: 93 files and 1,510 tests passed.
- PIHC3 full rebuild: 14,573 modules, 106 collections, 33,437 artifacts, zero
  diagnostics/errors, 91.90 seconds.
- PIHC3 cached build: identical output/build digests, zero diagnostics/errors,
  66.33 seconds. This is 14.95 seconds (18.4%) faster than the recorded
  81.28-second baseline.
- Technology-family partial: 301 modules, 10,204 artifacts, zero errors, 40.14
  seconds. Single-Technology partial: one module, 9,300 artifacts, zero errors,
  39.47 seconds. Both retained the exact 33,441-file whole-output digest.
- `git diff --check` passed. The heaven-style scan reported only the existing
  deliberate `pathlib`/`os`/`json` filesystem and adversarial-test imports in
  the touched files; this slice adds no banned import.

## Risks Or Blockers

- Cached builds still plan the whole project and render/compare all planned
  artifacts. The profile also shows repeated 33,437-row ledger projection,
  ledger reloads between safe publication checkpoints, and full manifest
  serialization as the next dominant publication costs.
- Family and module builds remain close to 40 seconds because project-scoped
  Technology support artifacts and full-project planning dominate their much
  smaller selected-module result.

## Next

- Reuse validated in-memory publication rows across crash-safe checkpoints and
  avoid byte-identical manifest replacement, then re-profile before changing
  planning or introducing any additional cache.
- Keep full/cached/family/module digests, failure recovery, bounded temporary
  storage, and the single SDK publication path as non-negotiable gates.
