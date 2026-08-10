# PIHC3 Cached Build Throughput

Status: implemented and verified

Date: 2026-08-10

## Outcome

PIHC3's normal module-partial build now completes in about 26.3 seconds on the
current development machine, down from the 46-second installed-wheel checkpoint.
The improvement preserves the complete planning, localization reconciliation,
publication-safety, and manifest pipeline rather than introducing a PIHC3-only
shortcut.

The rebuilt installed-wheel GUI host completed clean, cached, MIO-family, and
single-MIO-module builds against the real PIHC3 project with zero diagnostics.
The full and cached modes each produced 14,573 active modules, 106 collections,
and 33,437 artifacts. The family and module partials produced 9,304 and 9,298
artifacts respectively.

## Changes

- Artifact writers may expose `render_bytes(artifact)` when they own the exact
  final bytes. Unchanged outputs are compared in place and skip both the writer
  and private staging; writers with stage transforms keep the existing staging
  contract. PIHC3 localization uses this extension hook.
- Hidden build manifests use compact JSON after their payloads have already
  crossed the strict JSON-safe boundary.
- Independent module-family and collection-family source-cache discovery runs
  concurrently with a deterministic result order and a four-worker ceiling.
- Families with shared expensive validation/emission preparation may expose one
  typed `compile(...) -> FamilyCompileResult` hook. Existing `check`/`emit`
  families remain unchanged. PIHC3 Entity uses the combined hook and its
  HeavenBase Entity advertises it through the extension contract.
- The public Build API reference and aggregate API catalog were regenerated for
  `FamilyCompileResult`.

## Performance Evidence

The same `military_industrial_organization/ai_bonus_weights` module-partial build
was measured with artifact and manifest emission, launcher synchronization off,
and eight requested workers:

| Checkpoint | Seconds |
| --- | ---: |
| Previous installed-wheel checkpoint | 46.0 |
| Exact-byte publication plus compact manifests | 34.5 |
| Bounded parallel source discovery, warm cache | 26.3 |

The first cache-signature refresh remains slower (approximately 40 seconds), and
OS filesystem cache state introduces normal variation. Targeted builds still
plan all families because project-scoped localization reconciliation needs their
artifact plans. Family planning remains the largest warm cost at roughly 12
seconds; a validated artifact-plan cache is the next performance seam, not a
reason to weaken partial-build correctness.

## Installable Evidence

- Wheel: `dist/python/paradev-0.1.0.0.dev0-py3-none-any.whl`
- SHA-256: `4a1f5b26132f954b1b9b1e9fe9ded7f49ab0e26afc8a4ce0272d0f78b2f94a7c`
- Installed-host evidence:
  `dist/evidence/2026-08-10-pihc3-performance-wheel.json`
- Runtime: ParaDev `0.1.0.0.dev0`, HeavenBase `0.1.2.2`, FastMCP `4.0.0b2`,
  MCP `2.0.0`, isolated home/temp, no developer path, and no `uv` available to
  the app.

## Verification

- `rtk bash scripts/test.bash`: 2,455 passed, 9 expected native-Windows skips.
- `rtk npm --prefix apps/desktop test`: 1,515 passed across 93 files.
- `rtk bash scripts/flake.bash --ci`: 234 files format-clean.
- `rtk bash scripts/sync-env.bash --check`: generated metadata, lock, and README
  projections current.
- `rtk uv run python projects/PIHC3/scripts/check_source_layout.py --json`: zero
  errors across 70 module families, 14,574 source modules, and 36,469 files;
  only one visible metadata file remains.
- `rtk uv run python /Users/magolor/.agents/skills/heaven-style/scripts/index.py
  --check`: Heaven-style routing index current.

## Next

Design a bounded, validated artifact-plan cache keyed by the same complete
extension/source/runtime signature, then profile project-scoped localization and
inventory-item planning. Do not skip whole-project reconciliation or reuse
payloads without explicit corruption fallback and byte-parity tests.
