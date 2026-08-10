# PIHC3 Catalog Materialization and Paging Audit

Date: 2026-07-18 21:20 SGT

## Outcome

ParaDev can now materialize the complete real PIHC3 project into its canonical local HeavenBase catalog and browse the largest module family through bounded pages. The corrected refresh produced 1,116,679 Catalog rows and all projected counts matched their persisted Catalog counts. Before the final same-filesystem rename, the staged main database was checkpointed and the old catalog's WAL/SHM sidecars were removed.

The final run took 832.46 seconds (13 minutes 52 seconds) and peaked at 1,755,447,296 bytes of resident memory. That is inside the former 15-minute desktop deadline by only about one minute, so catalog refresh now has a dedicated 30-minute deadline. Ordinary desktop operations retain their existing shorter limits.

The canonical ignored cache is:

`ParaDev-3/projects/PIHC3/.paradev/.cache/hb/catalog.sqlite`

It is 2,164.3 MiB and has no WAL or SHM sidecars after finalization or repeated reads.

## Correctness Defect Found During the Real Run

The first fast-path database contained the right row counts but was not usable for family browsing. ParaDev encoded `sys_catalog.tags` before SQLite's JSON column encoded it again, so an intended array such as:

```json
["module", "scripted_effect", "scripted_effect/ADD_FOG_OF_WAR_BUILDING"]
```

was persisted as a JSON string. `json_each` therefore saw one string instead of three tags, module rows exposed an empty tag list, and `tag=scripted_effect` returned zero matches.

The fresh writer now follows HeavenBase's exact split contract:

- ordinary entity rows are encoded through the registered backend codec;
- system Catalog rows are passed to HeavenBase's backend in canonical form;
- system entities are explicitly rejected by the fresh-only helper;
- a fixed-clock contract test compares the fast helper with public `upsert_many` on both SQLite and in-memory backends;
- a raw-SQL regression asserts that persisted Catalog tags have JSON type `array`.

The corrected real database returns exactly 8,279 `scripted_effect` modules across the project's 18,038 modules.

## Materialization Counts

| Entity | Rows |
| --- | ---: |
| Asset | 15,437 |
| Build artifact | 37,589 |
| Build dependency | 0 |
| Build graph edge | 38,891 |
| Build graph node | 70,194 |
| Collection | 78 |
| Diagnostic | 0 |
| HOI4 entity | 18,038 |
| Localization entry | 122,529 |
| Module | 18,038 |
| PDX document | 13,909 |
| PDX symbol | 720,730 |
| Project | 1 |
| Source file | 32,979 |
| Source slot | 27,769 |
| Sprite | 497 |
| **Total** | **1,116,679** |

The HeavenBase metaschema contains 21 entity definitions and the refresh summary reported `ok: true`.

## Performance Changes

The original latest-HeavenBase public write path performed an existing-row lookup for every row even though the destination database was known to be new. A real PIHC3 probe reached only 18,437 rows after 10 minutes 24 seconds and was stopped without replacing the canonical database.

The contained fresh-database adapter keeps HeavenBase materialization, routing, derivation, codecs, backend ownership ordering, and Catalog creation, while skipping only those known-empty lookups. It writes 1,000-row chunks and deletes a partial database when a normal Python exception unwinds the refresh. An unconditional process kill still cannot run Python cleanup handlers, so the next refresh now acquires a target-scoped SQLite mutex and removes exact ParaDev-owned orphan staging files before rebuilding.

Additional peak-memory work in this checkpoint:

- build graph nodes and edges are projected only during their contiguous write phases and released before PDX symbols and source slots;
- source-slot inspection now materializes only `sources.json` rows instead of every manifest and every manifest index;
- final counts are read from SQLite rather than retaining all Catalog rows in Python.

| Real PIHC3 run | Wall time | Maximum RSS | Result |
| --- | ---: | ---: | --- |
| First optimized run, invalid tags | 796.10 s | 1,782,693,888 B | 1,116,679 rows, unusable tag filters |
| Corrected and memory-scoped run | 832.46 s | 1,755,447,296 B | 1,116,679 rows, valid tags |

Peak RSS fell by about 26 MiB. The modest reduction indicates that retained PIHC3 build/PDX data, rather than the graph and unrelated manifest indexes alone, dominates the peak. The final run was about 4.6% slower, so the refresh remains a manual/background operation rather than something to trigger after every edit.

## Paging and Hydration Acceptance

The post-refresh probe used the canonical database and the same query facade exposed to Tauri.

| Probe | Result |
| --- | --- |
| Page 1, `module` + `scripted_effect`, 50 rows, no data | 12.0 ms; 16,524-byte compact payload |
| Page 2, offset 50 | 11.7 ms; 16,056-byte compact payload |
| Cross-page identity | 50 unique IDs per page; zero overlap |
| Family count | 8,279 |
| Exact one-row hydration | 4.4 ms; 2,213-byte compact payload |
| Python desktop facade | 77.4 ms in-process; rows exactly matched the core page |
| Read side effects | no WAL or SHM before or after repeated queries |

The selected row hydrated to `family=scripted_effect`, and its unhydrated tags were the expected module/family/module-ID array. The external desktop subprocess benchmark from the prior probe remained about 0.35-0.43 seconds including process startup; the SQL work itself is now a small fraction of that cost.

## Completion Paging Acceptance

Catalog-backed editor completion no longer reads and hydrates the full 1,116,679-row catalog before applying its limit. Prefix predicates run in SQLite, candidate rows stream from the cursor, and only accepted candidates are hydrated. The direct SDK entry point now defaults to 100 results; explicit unlimited calls and legacy WAL-backed catalogs bypass the result cache so a million-item result is not retained there.

| Real PIHC3 prefix | Limit | Result | First-call time |
| --- | ---: | ---: | ---: |
| `pihc` | 100 | 100 | 21.8 ms |
| `add_fog` | 100 | 1 | 2.538 s |
| absent prefix | 100 | 0 | 2.541 s |
| empty prefix | 100 | 100 | 1.6 ms |

The slow miss is CPU/scan time across the PDX-symbol JSON tail, not Python result growth. It remains bounded in memory, but an expression index or a compact completion-label table would be worthwhile if symbol-only completion latency becomes visible while typing.

## Related Hardening

- Finalized sidecar-free catalogs use SQLite immutable read-only URIs, preventing nominal reads from creating WAL/SHM files. Legacy databases with WAL/SHM sidecars fall back to normal read-only mode so committed WAL data remains visible until the next refresh; the regression writes committed schema/data into a live WAL and verifies that ParaDev reads the update.
- Catalog writes checkpoint and remove sidecars before returning.
- Refresh records conflicts before building so its `removed` report remains accurate even if closing an old engine removes stale sidecars during the long build.
- Same-target refreshes are serialized by a process-released SQLite mutex. A killed-process regression verifies that the next refresh can reacquire the mutex and recover exact `.refresh-<digest>-<nonce>.sqlite` main/WAL/SHM files without touching near-match files.
- Explicit CLI `--json` output now short-circuits the ParaDev output-config lookup.
- The Tauri refresh operation has a dedicated 30-minute timeout. Frontend forms, CLI, REST, desktop inspection, and MCP inspection queries now default to an unhydrated 100-row page, reject pages over 200 rows at the adapter edge, and restrict hydrated requests to one row. The direct Python `catalog_query` method retains its prior defaults for explicit SDK compatibility.

## Verification

| Gate | Result |
| --- | --- |
| Fast writer vs public HeavenBase writer, SQLite and in-memory | 2 passed |
| Full HeavenBase catalog regression suite | 40 passed |
| Streaming module family-tag and raw JSON storage regression | passed |
| Source-slot focused suite | 3 passed |
| Explicit CLI JSON/config regression | passed |
| Catalog write, cleanup, and staged refresh regressions | passed |
| Legacy non-empty WAL read regression | passed |
| Completion default/explicit hydration bounds | passed |
| Refresh mutex, killed-process release, and orphan recovery | passed |
| Frontend/CLI/REST/desktop/MCP bounded query edges | passed |
| Full frontend architecture/contract suite after bound changes | 91 passed |
| Broad Python adapter/LSP/desktop regression selection | 358 passed |
| Desktop backend and Tauri bridge suites | 73 passed |
| Rust desktop suites | 40 passed |
| TypeScript check and production Vite build | passed |
| Repository lint gate | passed |
| Real PIHC3 canonical refresh | `ok: true`; 1,116,679 rows |
| Real PIHC3 page/hydration acceptance | passed |

The full HeavenBase catalog file was also run as a pre-fix baseline: 36 tests passed and the one failure was the legacy-WAL visibility case. Re-running that exact failing test with the corrected reader passed.

The first sandboxed launch failed before project loading because HeavenBase's user config database was not accessible. Re-running with normal user-config permission succeeded; no catalog file was touched by the failed launch.

## Architectural Risk

The fresh-only helper necessarily mirrors a small private part of HeavenBase 0.1.2.0 because the public API has no `assume_fresh` or bulk-import mode. The exact HeavenBase pin and the flat, non-system ParaDev HOI4 schemas contain the immediate risk, and the cross-backend contract tests guard current behavior. The durable fix is to add a public bulk-import option upstream in HeavenBase and delete the ParaDev adapter.

## Next Work

- Wire the Tauri catalog query/refresh commands into the React service boundary.
- Make module tabs page by family and hydrate only the selected entity; preserve unsaved drafts while pages append.
- Stop ordinary module tabs from eagerly loading and caching a complete family through `Project.browser`; keep that path only where diagrams still require it.
- Keep the old catalog readable during a manual background refresh and add elapsed-time, retry, and cancellation UX before exposing refresh to beginners.
- Add novice-friendly display names to lightweight module rows; current unhydrated rows expose technical module IDs.
- Code-split the editor/image-editor bundles before release; the production Vite build passes but still warns about roughly 980-999 KiB minified chunks.
- Upstream a supported HeavenBase fresh bulk-import API.
- Resume native visual GUI testing when the macOS session is unlocked.
