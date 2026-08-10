# PIHC3 live-tree cleanup audit

Date: 2026-07-31

## Outcome

- Scanned the complete live PIHC3 project, excluding only Git's object
  database: zero retired `_component`, `_asset_component`, `legacy/`, or
  `inactive_modules/` source-layout paths remain. Semantic HoI4 content may
  still use the word `legacy` in an in-game id, localization key, or engine
  property; those are game data rather than migration architecture.
- The live authoring tree contains 75 module families, 14,618 physical module
  folders, and two real collection families: 28 focus trees and 62 decision
  categories. Every direct module and collection folder uses
  `id - preferred-language title`.
- All 1,306 visible module `meta.yaml` files remain minimal; none contains more
  than one top-level user field.
- The source-control index still knows the former paths as deleted entries
  until the large PIHC3 cutover is committed. They are historical Git state,
  not live folders, discovery inputs, cache entries, or compiler sources.
- Audited the 16 pre-cutover staged edits. Thirteen are preserved byte-for-byte
  under their new semantic owner. Two verbose decision metadata records were
  intentionally reduced to their `collection` field, and the interface source
  preserves the newer working-tree removal of three obsolete notification
  widgets.

## Guardrails and UX

- Strengthened the PIHC3 hygiene test to scan the whole live project and to
  enforce readable naming for both modules and collections.
- `Project.build`, the CLI, and `compile.bash` now accept a bare module object
  id when `--family` is explicit.
- PIHC3's wrapper accepts `--family`, `--module`, and `--collection` directly;
  a `--` forwarding separator is no longer required for normal partial builds.
- Invalid CLI selector combinations render an actionable command error instead
  of a Python traceback.
- Corrected the PIHC3 authoring manual to describe Registry-owned identity
  rewriting during duplication; the former literal-copy guidance was stale.

## Verification

- Focused hygiene, Registry, and consolidation suite: 28 passed.
- Selector and wrapper regressions: 6 passed.
- Complete Python gate: 2,333 passed, with nine native-Windows tests skipped.
- Clean/full and cached PIHC3 builds: 14,617 active modules, 106 collections,
  35,139 artifacts, zero diagnostics.
- Focus family partial: 738 modules, 28 collections, 12,499 artifacts, zero
  diagnostics.
- Focus module partial (`FOCUS_C12_SHADOWS_OF_THE_PAST`): its complete
  129-node owning tree, one collection, 11,253 artifacts, zero diagnostics.

## Next

- Return to the Registry-owned family presentation contract so desktop
  navigation no longer keeps a central compatibility vocabulary.
