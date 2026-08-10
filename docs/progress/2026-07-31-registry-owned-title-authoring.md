# Registry-owned module title authoring

Date: 2026-07-31

## Outcome

- The desktop Name field now edits the active Registry family's ordered
  localization title key in the preferred language. It no longer creates a
  title-only `meta.yaml`.
- A successful title edit synchronizes the physical authoring folder to
  `id - localized title`, including title-only renames where the logical
  module id does not change.
- The project browser publishes `title_keys` from the resolved Registry
  family, so desktop code contains no family-name title switch.
- SDK, CLI, REST, frontend API, MCP, Tauri, and generated contract surfaces
  accept the optional readable title consistently.
- Existing authored source bytes are not rewritten by folder synchronization.

## PIHC3 physical audit

- 75 module families contain 14,618 physical module folders.
- Two collection families contain 90 physical collection folders; Registry
  expansion compiles 106 collection instances.
- The live project contains zero `_component`, `_asset_component`, `legacy`,
  or `inactive_modules` directories.
- Every direct module and collection folder has a non-empty `id - title`
  identity and matches its preferred localization when one is available.
- All 1,306 visible `meta.yaml` files contain only the allowed user-facing
  `collection`, `inactive`, and `comment` keys.

## Verification

- Python: 2,200 passed; nine native-Windows tests skipped on macOS.
- Desktop: 87 files and 1,417 tests passed.
- Rust/Tauri: 93 tests passed.
- TypeScript/Vite production build passed.
- Black and Flake8 repository gate passed.
- PIHC3 layout, metadata, and canonical-title suite: 13 passed.
- Clean and cached PIHC3 builds: 14,617 active modules, 106 collections,
  35,139 artifacts, zero diagnostics.
- Focus-family partial: 738 modules, 28 collections, 12,499 artifacts, zero
  diagnostics.
- Focus-module partial (`FOCUS_C12_SHADOWS_OF_THE_PAST`): 129 modules, one
  collection, 11,253 artifacts, zero diagnostics.

## Risk and next

- Localization source application and folder synchronization are currently
  two guarded desktop operations. If folder synchronization fails after the
  localization write, the live editor keeps the title draft retryable, but a
  process crash between those calls can leave a temporary source/folder-title
  mismatch.
- The next data-safety slice should expose one SDK-owned transactional module
  identity operation that applies localization and folder synchronization
  atomically.
- The Heaven-style scanner still reports pre-existing direct infrastructure
  imports in the large `Project` and CLI modules. Continue moving those
  responsibilities behind ParaDev/HeavenBase-owned utilities without
  expanding this focused authoring transaction.
