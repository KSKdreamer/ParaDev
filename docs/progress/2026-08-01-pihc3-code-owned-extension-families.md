# PIHC3 code-owned extension families

Date: 2026-08-01

## Outcome

PIHC3's physical source tree and compiler Registry now use the same semantic
module families. The project no longer depends on component folders or hidden
inline build-family definitions.

- `src/modules` contains 14,618 direct module folders. All 14,618 use the
  `<id> - <preferred-language title>` convention.
- The live project contains zero directories named `legacy` or
  `inactive_modules`, ending in `_component`, or containing
  `_asset_component`.
- The one disabled bookmark remains in its normal `bookmark` family and uses
  the visible `inactive: true` property.
- All 71 PIHC3 build-family Registry records resolve project-local Python
  targets. No build family remains `source: inline`, and no path-backed record
  retains a duplicate hidden compiler definition.
- Each code-backed family compiler reuses its Entity class's
  `resource_slots`. Resource discovery, browser ownership, desktop upload
  validation, and compilation therefore share one slot contract.
- Four specialized families (`entity`, `equipment`, `equipment_module`, and
  `state_lore`) resolve an Entity classmethod. The remaining families resolve
  a co-located `build_family()` target.

HeavenBase 0.1.2.1 Extension records remain hidden inline definitions by
design: its Extension loader resolves those records as declarative mappings.
They now contain only extension identity, dependency, and Entity registration
data; executable Entity and compiler behavior is imported from project-local
Python.

## Registry-owned resource authoring

Copy-resource destinations are declared with `Slot.authoring_path`. ParaDev's
SDK browser exposes the family slot declarations and source-level slot kinds;
the desktop editor uses those declarations instead of family-specific
`*_component` path rules.

Safe authoring destinations are present for the major independently editable
PIHC3 families, including achievements, bookmarks, characters, countries,
decisions, equipment, events, focuses, ideas, intelligence agencies,
inventory items, modifiers, portraits, superevents, technologies, and traits.

Five aggregate families intentionally do not invent a single upload path:
`game_asset`, `interface`, `localization`, `texticon`, and `ui`. Their copy
slots accept several structurally distinct destinations. Compilation remains
supported, and the desktop now derives destination choices from directories
already owned by the matching Registry copy slot. One valid destination is
selected automatically; several destinations produce a compact chooser. If no
existing directory fits, the draft remains visible and blocked until the user
enters a module-contained path that passes the same Registry slot validation.
The GUI does not parse family names or invent copy-layout rules.

## Guardrails

- The PIHC3 layout gate walks the live project and rejects component, legacy,
  and inactive-folder layouts.
- Every direct module and collection directory must retain the titled-folder
  convention.
- Every build-family descriptor must use a Python path target and must not
  contain `meta.definition` compiler data.
- The materializer fails closed if a future declarative compiler uses a key it
  cannot preserve, instead of silently generating an incomplete family.
- Split copy slots keep per-destination validation explicit while preserving
  their shared semantic slot name.
- Copy slots without a single `authoring_path` still expose the Assets tab.
  Ambiguous and unresolved additions remain non-applyable drafts rather than
  being rejected or written to a guessed location.

## Verification

- Full Python repository gate: 2,423 passed; nine native-Windows-only tests
  skipped on macOS; zero failures.
- The initial all-PIHC3 migration run passed 197 tests and exposed three
  focused slot/order regressions. All three targeted corrections passed, and
  the final full gate includes the corrected contracts.
- Desktop Vitest: 1,442 passed across 87 files.
- Strict TypeScript and production Vite build: passed. The established
  large-chunk advisory remains.
- Tauri Rust library gate: 95 passed; Cargo formatting passed.
- Fatal Ruff rules, Python formatting, and Git diff whitespace: passed.
