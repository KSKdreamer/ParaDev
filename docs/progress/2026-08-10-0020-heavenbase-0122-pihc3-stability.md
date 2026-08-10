# HeavenBase 0.1.2.2 And PIHC3 Stability Progress

Date: 2026-08-10 00:20

Linear: none

## Done

- Migrated the runtime lock, package checks, and current documentation to the published `heavenbase==0.1.2.2` wheel with FastMCP 4 and MCP 2; removed the exact-version 0.1.2.1 SQLite shim.
- Replaced ParaDev's manual string-only FastMCP wrapper with HeavenBase `Toolkit.to_fastmcp()`, preserving exact input schemas while returning native structured objects.
- Made malformed derived source-cache entries fall back to parsing and made cache-write failures visible without blocking a valid build.
- Added bounded searchable Guided projections for large Registry-owned JSON, PDX, and localization sources. Matching complete sections retain their full-source control identities across SDK, REST, MCP, desktop bridge, and React.
- Re-audited the live PIHC3 tree: all 14,574 immediate module directories use `id - preferred-language title`; live modules and collections contain no `_component`, `_asset_component`, `legacy`, or `inactive_modules` directory.

## Verification

- Isolated published-wheel compatibility: 188 passed; focused HeavenBase shim-removal gate: 71 passed; native MCP gate: 16 passed.
- PIHC3 full rebuild: 14,573 modules, 106 collections, 33,437 artifacts, zero diagnostics/errors. Cached full build has exact counts and completed in 81.28 seconds.
- PIHC3 family partial: 301 Technology modules and 10,204 artifacts; module partial: one Technology module and 9,300 artifacts; both zero diagnostics/errors.
- PIHC3 layout/extension/tree consolidation: 80 passed. Desktop: 93 files and 1,510 tests passed. Final published-wheel Python gate: 2,565 passed and 9 Windows-native semantics tests skipped on macOS.

## Risks Or Blockers

- Cached full publication remains too slow at 81.28 seconds because planning, artifact staging, and per-event JSONL writes still process the complete artifact set.
- The desktop still uses Tauri as its host; `paradev-gui` does not yet provide a simple wheel-hosted app/install command.

## Next

- Batch/coalesce artifact publication and progress events after adding phase timings, without changing full/cached/partial output parity.
- Continue simplifying first-run app hosting and project discovery. The
  redundant Idea/Event Entity wrappers were consolidated on 2026-08-10; see
  `2026-08-10-0234-pihc3-builtin-family-overlays.md`.
