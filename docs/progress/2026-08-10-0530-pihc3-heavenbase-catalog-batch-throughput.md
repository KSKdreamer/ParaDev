# PIHC3 HeavenBase Catalog Batch Throughput

Status: completed slice

Date: 2026-08-10

## Outcome

PIHC3's first Catalog refresh now uses an explicit public HeavenBase
fresh-Catalog mode when the installed runtime supports it. The mode removes
only impossible prior-projection lookups for a caller-owned new database; it
does not bypass HeavenBase Entity materialization, derives, routing, backend
ordering, graph validation, Catalog persistence, or count verification.

The isolated 765,033-row PIHC3 write fell from 762.93 to 228.55 seconds while
retaining exact logical and physical counts, all 454,836 typed PDX symbols, zero
diagnostics, and the existing query/completion contract.

## Root cause

The current exact 20,000-row workload spent about 94% of its 16.155 seconds in
Catalog derivation/configuration and Catalog backend writes. A 5,000-row
profile found roughly 70,000 configuration reads:

- Catalog identifier length was resolved once per projected row.
- Each text-backed JSON column called the presentation-aware serializer, which
  resolved global indentation even though database storage must be compact.
- A new, empty Catalog still took the merge-safe prior-row lookup path for each
  upserted Entity.

These were HeavenBase ownership defects, so the optimization was implemented
upstream rather than as a ParaDev database shortcut.

## Owner-aligned changes

- HeavenBase resolves Catalog hash length once per upsert batch.
- SQLite's JSON fallback uses compact persistence encoding without consulting
  presentation configuration.
- `HeavenBase.upsert_many(..., catalog_mode="fresh")` explicitly asserts that
  no prior Catalog projection exists. `merge` remains the default and preserves
  lifecycle behavior for ordinary updates.
- ParaDev detects the public capability. Local refactored HeavenBase uses it;
  the currently published 0.1.2.2 wheel retains ParaDev's existing private
  compatibility path until a new upstream wheel is available.

No second database, shadow index, parallel writer, lossy symbol projection, or
additional cache was introduced.

## Exact workload proof

On the same 20,000 typed Entity workload through the public writer:

| Runtime | Seconds | SQLite bytes | Entity rows | Catalog rows |
| --- | ---: | ---: | ---: | ---: |
| Published 0.1.2.2 behavior | 16.155 | 22,962,176 | 20,000 | 20,000 |
| Local owner-aligned behavior | 3.298 | 21,819,392 | 20,000 | 20,000 |

That is a 79.6% time reduction and about a 5.0% size reduction. Chunk sizes of
1,000, 2,000, and 5,000 did not materially change the pre-fix cost, so ParaDev
keeps the bounded 1,000-row streaming chunk instead of trading memory for a
nonexistent throughput gain.

## Isolated PIHC3 proof

One fresh temporary SQLite Catalog was built from the live PIHC3 project with
local HeavenBase source. It did not touch PIHC3's canonical Catalog, sources,
build output, or hidden state.

- End-to-end Catalog write: 228.549 seconds, down 70.0% from 762.929 seconds.
- Catalog rows: 765,033 logical and 765,033 physical.
- Typed PDX symbols: 454,836 logical and 454,836 physical.
- Diagnostics: zero; write summary `ok=true`.
- Immutable SQLite size: 1,268,346,880 bytes, down 15,589,376 bytes.
- Hydrated typed query: three rows in 0.010 seconds.
- `ai_will_do` completion: one typed `hoi4-pdx-symbol` result in 0.761 seconds.
- Exact process peak RSS: 2,254,143,488 bytes.

The earlier 1.45 GB memory figure was sampled during the dominant streaming
phase; the new `ru_maxrss` number is a process peak. They are recorded as
different measurements, not presented as a regression or improvement without
a controlled phase-by-phase memory profile.

## Verification

- ParaDev focused public-fresh-mode gate: 5 passed.
- ParaDev Catalog/LSP gate with local HeavenBase: 103 passed.
- The same ParaDev Catalog/LSP gate with published HeavenBase 0.1.2.2: 103
  passed.
- HeavenBase focused and expanded writer/Catalog/SQL gates: 3 and 30 passed.
- HeavenBase fast tier: 963 passed with one expected environment skip.
- HeavenBase full tier: 1,158 passed with 60 expected external-service skips.
- HeavenBase Black/Flake8, documentation, and diff checks passed.
- ParaDev repository-wide standard tier: 2,422 passed with 9 expected native
  Windows filesystem skips on macOS.
- ParaDev slow-inclusive tier: 2,578 passed with the same 9 expected skips. The
  final PIHC3 mutation tests serialized on the project lock and completed; the
  five-minute faulthandler trace represented contention, not a deadlock or test
  failure.

## Remaining work

- Publish the next HeavenBase wheel before claiming this throughput on a clean
  installed ParaDev build; the capability-gated fallback keeps 0.1.2.2 working
  but cannot expose an API absent from that wheel.
- Profile PIHC3 build/planning and phase-specific peak memory independently.
- Continue the release-path and GUI work only after keeping full/cached/family-
  partial/module-partial output parity green.
