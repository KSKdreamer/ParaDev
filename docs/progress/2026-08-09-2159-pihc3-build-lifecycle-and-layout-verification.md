# PIHC3 Build Lifecycle And Layout Verification

Date: 2026-08-09

## Outcome

The exact live PIHC3 source root at
`projects/PIHC3/src/modules/` contains no `_component`,
`_asset_component`, `legacy`, or `inactive_modules` directories. Both a direct
directory traversal and a complete source-path scan returned zero matches.
The dedicated PIHC3 contract suite also passed all 245 tests, including the
extensible-layout, retirement, project-contract, Focus, Technology, MIO,
Doctrine, and template gates.

The native-web ParaDev GUI was then exercised against that same live tree in
all supported compilation scopes:

- whole-project cached build: passed (about 1 minute 38 seconds on the recovery
  verification run);
- whole-project clean/full build: passed (about 2 minutes 33 seconds);
- `focus` family partial build: passed (about 48 seconds);
- exact `focus/FOCUS_C02_LOYALTY` module partial build: passed (about 1 minute
  28 seconds).

The hydrated project inventory remained 14,574 modules, 90 collections, and
36,469 source files with zero diagnostics. The publication ledger recorded a
complete whole-project baseline with 33,437 artifacts.

## Build lifecycle safety

A cached build into a pre-existing output root previously produced a valid
artifact ledger but intentionally did not claim whole-root ownership. A later
clean/full build therefore refused to proceed even though ParaDev knew every
artifact it had written.

Full rebuilds now distinguish whole-root ownership from complete
artifact-level ownership. When ParaDev cannot safely clear an entire root, it
removes only paths recorded in the complete whole-project publication ledger
and preserves unrelated files. The old ledger stays complete until every
idempotent deletion succeeds, so an interrupted clean is recoverable on the
next run rather than committing a partially reduced ownership record. Tests
cover pre-existing user files, a file appearing during cleanup, injected
interruption, and recovery.

## Desktop consistency

- The Build summary now consumes authoritative project-browser groups, so
  collections are counted separately instead of appearing as zero modules.
- Diagram presentation IDs no longer leak into compiler scope. Opening
  National Focuses now queries the registered `focus` Entity family, hydrates
  all 766 objects, and exposes its module build action.
- Scoped editor responses replace only the requested family. Their intentional
  zero rows for other families can no longer erase global Build counts.
- Failed and interrupted builds show the actionable backend error inline;
  opening build history is no longer required to discover the cause.

## HeavenBase 0.1.2.1 integration

The MCP authoring toolkit no longer imports `Tool` and `Toolkit` through
HeavenBase's process-global default resolver. Both Entity types are loaded
through ParaDev's isolated HeavenBase Registry context. This prevents an
unrelated local 0.1.2.2 development registry from contaminating the pinned
0.1.2.1 ParaDev subprocess and better follows the context-owned,
Registry-resolved extension architecture.

## Verification

- Exact retired-layout directory scan: zero matches.
- Exact retired-layout source-path scan: zero matches.
- PIHC3 contract suite: 245 passed.
- Complete Python fast gate: 2,405 passed, 9 skipped.
- Complete desktop gate: 93 files and 1,506 tests passed.
- TypeScript check and Vite production build passed; only the existing
  chunk-size advisory remains.
- Focused publication lifecycle suite: 178 passed.
- Focused desktop regression suite: 164 passed.
- Real HeavenBase MCP stdio negotiation test: passed.
- `git diff --check`: passed.

Windows integration and native macOS game launching were intentionally not
exercised, following the current product priority. The shared dirty worktree
was not staged or committed, and this checkpoint does not declare the broader
continuous ParaDev/PIHC3 objective complete.
