# PIHC3 source-derived metadata cleanup

Date: 2026-08-02

## Outcome

PIHC3 no longer stores repeated per-module compiler settings. The cleanup
removed all 577 hidden settings manifests from five Registry-owned families:

- 139 Trait routes now use the compiler's `country_leader` default; an
  explicit scientist or unit-leader subtype remains an advanced override.
- 79 State Lore ids and ordering values are derived from `STATE_LORE_<id>` or
  the authored `on_actions.pdx` source.
- 94 Doctrine routes are inferred from the authored doctrine PDX shape: grand,
  air subdoctrine, land subdoctrine, or sea subdoctrine.
- 130 Equipment Module categories and plane/tank aggregate routes are derived
  from the `category` in `def.txt`.
- 134 portable Entity records and their compiler aggregate derive route,
  owner, variant, and deterministic source order from source slots and
  canonical module ids. Repeated contracts, byte sizes, and SHA-256 values are
  gone; the real `record.json` and `.paradev/entities.json` sources remain.

Every deletion was preceded by an exact whole-corpus comparison between the
stored value and the proposed inference. Record and assignment byte sizes and
hashes were also checked against their current source bytes before removal.

The live tree now has 847 hidden module manifests, all of which express real
collection membership: 738 Focus nodes across 28 Focus Tree collections and
109 Modifier modules grouped by shared output. No live module has hidden
`settings`. The single visible module metadata file remains the normal disabled
bookmark with `inactive: true`.

## Core compiler support

`RoutedSourceFamily` gained a validated `default_route` contract. It is exposed
in the Registry family view, makes the corresponding route setting optional,
and remains overridable by explicit metadata. Declarative project families can
use the same contract.

PIHC3's project-local HeavenBase Entity extensions own all source inference;
ParaDev core gained no PIHC3 family switch. Templates for Trait, State Lore,
and Equipment Module no longer generate redundant hidden settings. State Lore
also derives its advanced state-id default from the module id, and Equipment
Module exposes only the authored category rather than a second designer field
that could disagree with it.

## Verification

- Core routed-family and Registry tests: 65 passed.
- Widened Registry/template/PIHC3 integration selection: 244 passed; its two
  stale metadata expectations were corrected and both focused reruns passed.
- Maintained Python gate: 2,312 passed with nine expected native-Windows-only
  skips and one warning.
- Desktop gate: 90 files and 1,462 tests passed; strict TypeScript and the Vite
  production build passed with only the existing chunk-size warning.
- Clean/full and cached/full strict PIHC3 plans: 14,617 active modules, 106
  collections, 35,131 artifacts, zero diagnostics and errors.
- Focus-family partial: 738 modules, 28 collections, 12,499 artifacts, zero
  diagnostics and errors.
- Focus-module partial (`FOCUS_C01_C02_EVERFREE_FIELDTRIP`): 83 modules, one
  collection, 11,161 artifacts, zero diagnostics and errors.
- Trait, State Lore, Doctrine, Equipment Module, and Entity family and module
  partial plans all completed with zero diagnostics.

All build verification used isolated temporary configuration and mod roots.
