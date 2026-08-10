# PIHC3 All-family Template Fitness

Date: 2026-08-01

## Outcome

PIHC3's cleaned module layout now has a creation-to-compilation contract for
every user-visible family. An isolated project copies only PIHC3's
project-local HeavenBase extension bundles, begins without a source root,
creates the Focus collection, scaffolds all 51 module templates, and performs
a strict targeted build with artifact emission for every result.

The matrix covers 52 project templates across 51 registered families. Fifty
families create and compile without errors. The 3D `entity` family is the sole
intentional asset-required case and must report exactly the actionable
`entity.missing_mesh_asset` and `entity.missing_animation_asset` diagnostics;
the test does not mask those requirements with fake binaries.

## Corrected extension contracts

Five templates had previously put `{object_id}` inside another template
argument's default. ParaDev intentionally renders templates in one pass, so
those values became literal localization keys instead of the Entity-required
keys. The Achievement, Operation, Operation Phase, and Operation Token
templates now emit their identifiers directly. The Resource template now
emits both country-resource display keys in addition to its ordinary title and
description. Their hidden extension descriptor versions moved from `0.2.3`
to `0.2.4`; no visible per-module metadata was added.

Brand-new projects can also create their first collection safely. Reviewed
scaffold hashes record a missing configured source root as `None`. If another
process creates that root before apply, its identity changes and normal stale
plan rejection still protects the write.

Normal template catalog views now hide a generic built-in fallback whenever a
project-owned template targets the same family and authoring kind. PIHC3 users
therefore see one authoritative Idea template rather than two competing
choices. Exact template-id and explicit source-filter lookups retain access to
the built-in fallback.

## Physical source audit

The exact `projects/PIHC3/src/modules` path was rescanned after the changes:

- zero `_component`, `_asset_component`, `legacy`, or `inactive_modules`
  directories;
- zero files below any such forbidden path;
- 14,618 canonical direct module folders and 90 collection folders remain;
  and
- the architecture suite continues to require `id - preferred-language title`
  for every direct source unit.

Deleted legacy/component paths shown by the nested PIHC3 Git index are
historical removals, not live folders, Registry inputs, or compiler sources.

## Verification

- All-family isolated authoring matrix plus focused collection/template
  contracts: 17 passed.
- Exact extensible-layout audit: 23 passed.
- Standard Python gate: 2,282 passed, with nine expected native-Windows skips
  and one existing warning.
- Desktop gate: 89 files and 1,454 tests passed; strict TypeScript and the Vite
  production build also passed.
- Canonical Black and Flake8 repository gate: passed; root and nested PIHC3
  diff whitespace checks also passed.
- Clean/full: 14,617 modules, 106 collections, 35,131 artifacts, zero errors.
- Cached/full: identical to clean/full.
- Focus family partial: 738 modules, 28 collections, 12,499 artifacts, zero
  errors.
- Focus module partial (`FOCUS_C01_C02_EVERFREE_FIELDTRIP`): 83 modules, one
  collection, 11,161 artifacts, zero errors.
