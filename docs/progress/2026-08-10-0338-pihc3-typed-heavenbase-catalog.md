# PIHC3 Typed HeavenBase Catalog

Status: complete

Date: 2026-08-10

## Outcome

PIHC3 Catalog refresh keeps every source symbol as a first-class HeavenBase
row, but no longer stores the complete symbol payload as repeated generic JSON.
The built-in `hoi4` extension now registers one explicit `Hoi4PdxSymbol`
Entity with typed owner, document, path, key, value, kind, operator, and source
coordinate fields.

The Entity derives Catalog name, description, and tags directly from those
fields. Provider-reserved public payload names remain compatible through one
declared mapping: `key` is stored as `symbol_key`, while `line` and `column`
are stored as `source_line` and `source_column`. Catalog query hydration still
returns the original public field names and omits absent optional fields.

All other HoI4 Catalog entity types retain the existing generic projection.
No second database, shadow symbol index, GUI cache, or alternate writer was
introduced.

## Compatibility and consistency

- Fresh optimized writes match HeavenBase public `upsert_many` Entity and
  `sys_catalog` rows on both in-memory and SQLite backends.
- Catalog query and LSP completion detect pre-normalization JSON symbol tables
  and keep them readable until the user refreshes the derived Catalog.
- Unregistered future PDX-symbol fields fail explicitly instead of being
  silently discarded.
- Initial Catalog creation now creates the existing stale marker before the
  database. Query and completion surfaces therefore reject a partially written
  target; success clears the marker, while a clean failure removes the partial
  database and marker without masking the original error.

## Reproducible storage benchmark

The same 20,000 persisted source rows and same-length workspace identity were
replayed through the old generic and new typed schemas.

| Schema | SQLite bytes | PDX target-table bytes | Write time |
| --- | ---: | ---: | ---: |
| Generic JSON baseline | 38,596,608 | 16,289,792 | 22.245 s |
| Typed Entity | 29,167,616 | 5,480,448 | 21.249 s |

The complete database is 24.43% smaller, the symbol target table is 66.36%
smaller, and write time improved by about 4.5%. All 20,000 Entity and Catalog
rows were retained.

## Cold PIHC3 proof

An isolated cold PIHC3 Catalog write completed through the same public
HeavenBase extension/writer path:

- 765,033 total Catalog rows;
- 454,836 typed PDX-symbol rows;
- zero diagnostic rows and `ok=true` count parity;
- 1,283,936,256-byte immutable SQLite database;
- 762.93-second complete build/materialize/checkpoint time;
- approximately 1.45 GB resident memory observed during the dominant streaming
  phase, without growth proportional to the committed symbol count.

A real three-row typed hydration completed in 0.425 seconds. A real
`ai_will_do` completion query returned a `pdx-symbol` result in 2.263 seconds.
The isolated database and all synthetic fixtures were deleted after evidence
capture; no PIHC3 project Catalog, source, output, or hidden state was changed.

## Verification

- Focused normalized schema, parity, legacy-cache, fail-closed write, query,
  and completion gate: 102 tests passed.
- Standard repository Python gate: 2,421 tests passed with 9 expected native
  Windows filesystem tests skipped on macOS.
- Slow-inclusive repository Python gate: 2,577 tests passed with the same 9
  expected native-Windows skips, including PIHC3 extension, migration,
  doctrine, template, focus-tree, inactive-module, and direct-folder contracts.
- Repository-wide Black, Flake8, and whitespace checks passed after the
  wrapper normalized three pre-existing changed-file format drifts.
