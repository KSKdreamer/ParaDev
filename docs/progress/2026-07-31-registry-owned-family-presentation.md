# Registry-owned family presentation

Date: 2026-07-31

## Outcome

- Family identity is now owned by the same HeavenBase Registry extension that
  owns each compiler family. The descriptor declares its stable UI id, title,
  semantic navigation group, translation key, and accepted selectors.
- All 73 PIHC3 build-family extensions declare that presentation contract in
  hidden `.paradev/meta.yaml` descriptors. User module metadata does not carry
  or duplicate system family identity.
- The Python SDK, project browser, templates, partial-build selectors, desktop
  navigation, editor tabs, and AI authoring handoff consume the Registry
  contract. The desktop no longer maintains separate family-id, title, or
  compatibility-alias maps.
- Registered families with no current modules remain visible and create-ready.
  Internal compiler-support families, including the mod descriptor, remain
  build-active but hidden from the normal authoring browser.
- Verified persistent extension receipts are checked before acquiring the
  HeavenBase catalog writer lock. Parallel GUI/SDK reads therefore reuse
  published state immediately, while stale or incomplete receipts still enter
  the serialized reinstall and compare-and-set recovery path.

## Physical project audit

- The live `projects/PIHC3/src/modules` tree contains 75 family directories and
  14,618 physical module directories.
- A symlink-following scan that includes ignored and untracked paths finds zero
  directories or files named `*_component`, `*_asset_component`, `legacy`, or
  `inactive_modules`.
- Eighteen retired family names remain only in hidden extension publication
  metadata under `meta.publication.replaces_families`. They are not folders,
  registered families, discovery inputs, browser rows, or compiler sources.
  They are migration tombstones that let an upgraded checkout retire artifacts
  previously published by the removed families instead of leaving stale mod
  output behind.

## PIHC3 compile parity

- Clean/full: 14,617 active modules, 106 collections, 35,139 artifacts, zero
  diagnostics.
- Cached: the exact same 14,617 modules, 106 collections, and 35,139 artifacts,
  with zero diagnostics.
- Focus-family partial: 738 modules, 28 collections, 12,499 artifacts, zero
  diagnostics.
- Focus-module partial (`FOCUS_C12_SHADOWS_OF_THE_PAST`): the complete
  129-module owning tree, one collection, 11,253 artifacts, zero diagnostics.

## Verification

- Registry/browser/template focused Python suite: 733 passed.
- Desktop suite: 1,415 passed across 87 files.
- TypeScript typecheck and production Vite build: passed.
- Complete Python gate before the concurrent-read repair: 2,337 passed, nine
  native-Windows tests skipped, and one writer-lock timeout reproduced.
- The receipt-reuse, incomplete-receipt recovery, and formerly timing-out PIHC3
  template tests pass after the repair.
- Final complete parallel Python gate: 2,338 passed, with only nine
  native-Windows tests skipped.
