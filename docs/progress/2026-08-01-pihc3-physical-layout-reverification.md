# PIHC3 physical layout reverification

Date: 2026-08-01

## Outcome

- Rechecked the exact live path
  `/Users/magolor/Projects/ParaDev/ParaDev-3/projects/PIHC3/src/modules`.
  It contains 71 semantic family folders and 14,618 physical module folders.
- No live directory anywhere in the PIHC3 project outside `.git` is named
  `legacy` or `inactive_modules`, contains `_asset_component`, or ends in
  `_component`, including case variants. No symlink aliases exist below
  `src/modules`.
- All direct module and collection folders use the
  `<logical id> - <preferred-language title>` convention. The one disabled
  bookmark remains in its normal family and uses only `inactive: true`.
- Former definition, localization, preview, GFX, and compiled image resources
  are colocated under their semantic owner. For example,
  `TECHNOLOGY_AIR_AIRSHIP` owns `def.txt`, `main.loc`, `icon.png`, its `.gfx`,
  and its `.dds` in one Technology module folder.
- PIHC3's nested Git index still knows about 46,354 pre-cutover paths until the
  migration is committed: 25,635 files below 42 retired component-family roots
  and 20,719 files below retired `legacy/` children of semantic families. All
  46,354 paths are absent from the working tree. They are historical deletion
  records, not physical directories, discovery inputs, extension families,
  cache aliases, or compiler sources.

## Retired payload reconciliation

- The 25,635 historical component-family files comprise 10,728 retired
  metadata/import records and 14,907 payload files.
- Of those payloads, 12,496 still compile to the same game-relative path and
  1,898 remain byte-for-byte in the live semantic-owner source tree.
- The remaining 513 are fully classified: 509 disposable migration previews,
  two aggregate localization inputs, one aggregate achievement definition,
  and one aggregate intelligence-agency definition. The four aggregate inputs
  are now split or merged by their semantic family compilers; the clean and
  partial build corpus contains their current outputs.
- A module-partial build left the isolated output closure at all 35,139 files,
  confirming that targeted publication did not resurrect component folders or
  discard unrelated semantic-owner artifacts.

## Guardrail

The PIHC3 extensible-layout integration gate now walks the entire live project
outside `.git` and rejects forbidden directory names case-insensitively. It
also continues to assert that every retired component family is absent from
the project Registry.

The follow-up shadow-asset sweep removed eight unreferenced `_legacy.dds`
backups from the consolidated Interface module. Each had an identically named
canonical sibling, and none was referenced by project source. The hygiene gate
now rejects that duplicate-backup pattern while preserving active gameplay
objects whose stable HoI4 ids legitimately contain `LEGACY`.

## Verification

- Complete PIHC3 layout, migration, Registry, ownership, template, and corpus
  contract set: 198 passed.
- Standard repository gate: 2,263 passed, with nine native-Windows tests
  skipped.
- Desktop: 1,438 tests passed; strict TypeScript and production Vite build
  passed. Rust formatting passed and all 95 library tests passed.
- Clean/full build: 14,617 active modules, 106 collections, 35,139 artifacts,
  zero diagnostics.
- Cached full build: identical counts and zero diagnostics.
- Focus family partial: 738 modules, 28 collections, 12,499 artifacts, zero
  diagnostics.
- Focus module partial (`FOCUS_C12_SHADOWS_OF_THE_PAST`): its complete
  129-module owning tree, one collection, 11,253 artifacts, zero diagnostics.
- Consolidated Technology module partial (`TECHNOLOGY_AIR_AIRSHIP`): one
  module, 10,997 publication artifacts, zero diagnostics.
- Post-sweep strict full plan: 14,617 active modules, 106 collections, 35,131
  artifacts, zero diagnostics. Focus family partial remained 738 modules, 28
  collections, and 12,499 artifacts; Technology and MIO module partial plans
  remained unblocked with zero diagnostics.
- The fresh isolated four-mode publication root is
  `/tmp/paradev-pihc3-structure-audit.2VOB1c/mod/PIHC3`: it contains exactly
  35,139 files and zero component, legacy, or inactive paths. Its v3 ownership
  ledger is complete, has 35,139 unique rows, and retains
  `whole_project_baseline: true` after module-partial publication.
