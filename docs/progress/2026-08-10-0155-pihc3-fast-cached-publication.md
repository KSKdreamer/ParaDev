# PIHC3 Fast Cached Publication

Date: 2026-08-10 01:55

Linear: none

## Done

- Added an internal projected-publication plan and typed in-memory checkpoint
  transaction to the existing SDK publication path. Current and planned
  artifact rows are projected once, then the exact state written after each
  output/build/postprocessor checkpoint is retained for the next durable
  write. Direct helper fallbacks still reload the ledger when no transaction
  is supplied.
- Preserved the pending-ledger recovery protocol, per-batch durable writes,
  structural-blocker ordering, renamed-predecessor handling, retained-root
  authorities, and exact-content retry adoption. No second compiler,
  publication cache, or GUI-owned build path was introduced.
- Made unchanged manifest publication compare deterministic bytes before an
  atomic replacement. `summary_view()` now constructs only `summary.json`, and
  desktop builds pass `--summary --json` instead of serializing the full build
  plan into an unread temporary stdout file.
- Used the measured profile to remove redundant filesystem resolution from the
  private artifact staging loop. Artifact batches still validate traversal and
  Windows portability, built-in writers still resolve their direct target
  beneath the staging root, custom writer return paths remain checked, and
  final publication remains descriptor-anchored.

## Verification

- Focused artifact writer, publication recovery, path-index, manifest, project,
  and desktop-command gate: 210 passed. The broader recovery/project subset
  also passed 194 tests.
- Published-wheel Python gate: 2,414 passed with 9 native-Windows filesystem
  tests skipped on macOS. Desktop gate: 93 files and 1,510 tests passed.
- PIHC3 clean build: 14,573 modules, 106 collections, 33,437 artifacts, zero
  diagnostics/errors, 94.79 seconds.
- PIHC3 cached build with desktop JSONL: the same counts, zero errors, 52.89
  seconds, and 98 progress events. This is 20.3% faster than the 66.33-second
  reference and 34.9% faster than the original 81.28-second baseline.
- PIHC3 cached build without progress: 53.12 seconds. The 0.4% difference is
  within the queued 5% progress-overhead limit.
- Technology-family partial: 301 modules, 10,204 artifacts, zero errors, 43.30
  seconds. `technology/TECHNOLOGY_FIREARM_I` module partial: one module, 9,300
  artifacts, zero errors, 43.02 seconds.
- Clean/full, cached, family, and module builds preserved the same 33,436
  compiler-owned output artifacts. Their digest is
  `ba17e0ffda128cc5b142f244d36de0ced7775335635fdd530ab4bee47ef83038`.
  The full ledger's one build-root artifact digest is
  `c6bbe093a0341bd460860a957331887ee95e9b1f0cdfe3278279a14a550e12b4`.
- Targeted Black, Flake8, `git diff --check`, generated-environment drift, and
  Python bytecode checks passed. The repository-wide Black gate remains
  blocked only by four unrelated dirty files outside this slice:
  `src/paradev/surfaces/mcp.py`, `src/paradev/sdk/source_forms.py`,
  `tests/test_pihc3_extensible_layout.py`, and `tests/test_cli.py`.

## Risks Or Blockers

- Cached builds still plan the whole project and render/compare all 33,437
  artifacts. The next meaningful performance work belongs in targeted planning
  and artifact comparison, not in another cache layer.
- Family and module builds remain near 43 seconds because Technology owns large
  project-scoped support artifacts and still starts from the full-project plan.
- Whole-directory digests include untracked macOS `.DS_Store` files and the
  hidden publication marker, so future parity gates should use ledger-owned
  artifact paths as this checkpoint does.

## Next

- Continue with the queued desktop build-lifecycle stabilization and preserve
  the compact summary contract across Tauri and native-web hosts.
- Profile targeted planning and project-scoped Technology support emission
  before attempting another cached-build optimization; keep the existing SDK
  transaction and crash-recovery boundaries authoritative.
