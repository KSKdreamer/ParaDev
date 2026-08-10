# PIHC3 canonical folder titles

Date: 2026-07-31

## Outcome

- Corrected seven focus collection folders whose suffix had been taken from an
  unrelated tooltip instead of the collection identity.
- Removed live Clausewitz expressions and icon codes from 15 decision and two
  modifier folder suffixes. Authored localization remains byte-for-byte
  unchanged.
- The complete live PIHC3 tree now passes one canonical naming contract over
  14,618 physical module folders and 106 collections.
- New scaffolds automatically project real titles into readable portable
  folder suffixes without asking users to understand path restrictions.

## Registry contract

- Build families may declare ordered `title_loc_keys` in their hidden
  extension descriptor. Omission keeps generic inference; an empty list
  intentionally falls back to the persisted folder title.
- PIHC3 countries now prefer `{object_id}_DEF`, intelligence agencies prefer
  `{object_id}_NAME`, operative codenames prefer
  `{object_id}_NAME_THEME`, and dynamic building titles use their readable
  folder suffix.
- The Python browser resolves these keys from the active Registry family.
  Desktop and other clients receive the same `localized_titles` payload and
  keep no family-name switch.

## Verification

- Folder/template/Registry focused suite: 34 passed.
- Broader Registry, extension, localization, and browser suite: 74 passed.
- Clean and cached PIHC3 builds: 14,617 active modules, 106 collections,
  35,139 artifacts, zero diagnostics.
- Focus-family partial: 738 modules, 28 collections, 12,499 artifacts, zero
  diagnostics.
- Focus-module partial (`FOCUS_C12_SHADOWS_OF_THE_PAST`): 129 modules, one
  collection, 11,253 artifacts, zero diagnostics.
- Full Python regression gate: 2,193 passed, nine native-Windows-only tests
  skipped on macOS.

## Next

- Continue from literal folder duplication toward an extension-owned
  identity-aware copy capability; do not put HoI4 family rewrite rules in the
  generic SDK or desktop.
