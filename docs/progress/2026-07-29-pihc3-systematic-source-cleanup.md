# PIHC3 systematic source cleanup

## Outcome

PIHC3 now has one user-facing source layout:

- 14,618 physical module folders and 90 physical collection folders use
  `<logical id> - <preferred-language title>`;
- no file or directory remains under `_component`, `_asset_component`,
  `legacy`, or `inactive_modules`;
- the one intentionally disabled bookmark uses only `inactive: true`;
- Focus collections no longer duplicate member inventories in hidden metadata;
  each Focus module's `collection:` field is authoritative;
- the source normalizer prefers Chinese `*_NAME` and country `*_DEF`
  localization before identifier fallbacks and is idempotent.

Retired family identifiers remain only in extension compiler declarations so a
cached build can remove artifacts produced by the previous layout. They are
not registered source families and have no source folders.

## Verification

- strict full plan: 14,617 active modules, 106 discovered collections, 35,139
  artifacts, zero diagnostics;
- strict Focus family plan: 738 modules, 28 collections, zero diagnostics;
- strict `focus/C01_MAIN` collection plan: 83 modules, one collection, zero
  diagnostics;
- strict `intelligence_agency/INTEL_AGENCY_BOC` module plan: one module, zero
  diagnostics;
- consolidation gate: 81 passed, one optional external-reference test skipped;
- normalizer second pass: zero planned renames;
- formatting/static gate: 227 files unchanged.
