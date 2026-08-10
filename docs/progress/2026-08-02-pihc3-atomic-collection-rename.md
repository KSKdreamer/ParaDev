# PIHC3 Atomic Collection Rename

Date: 2026-08-02

## Done

- Generalized the durable source-draft rename journal from module-only folders
  to exact `modules` or `collections` Registry containers. New journals use v4;
  interrupted v3 module transactions remain readable and recoverable.
- Collection rename now rewrites every explicit member `collection` pointer in
  visible or hidden metadata and moves the descriptor folder in one guarded,
  crash-recoverable transaction.
- Conflicting visible/hidden pointers fail closed. Unrelated metadata and
  hidden settings are preserved.
- Re-audited the live PIHC3 tree: 71 families, 14,618 module folders, no
  component/asset-component/legacy/inactive-module folders, no symlinks, one
  intentional visible metadata file, and 847 hidden collection manifests.

## Verification

- Python: 2,484 passed; 9 native-Windows-only skips.
- Desktop: 90 files and 1,465 tests passed.
- TypeScript/Vite build, Rust `cargo check`, Black, Flake8, and focused
  SDK/CLI/POSIX/Win32 recovery regressions passed.
- Strict isolated PIHC3 dry plans and artifact-emitting builds remained exact
  and unblocked:
  - clean full and cached full: 14,617 active modules, 106 collections, 35,131
    artifacts;
  - Focus family: 738 modules, 28 collections, 12,499 artifacts;
  - `FOCUS_C01_C02_EVERFREE_FIELDTRIP`: 83 modules, one collection, 11,161
    artifacts.
- All four modes reported zero diagnostics and zero errors; the clean/full
  publication wrote exactly 35,131 files to the isolated mod root.

## Risks Or Blockers

- None for this transaction slice. Authored PDX identifiers and localization
  keys intentionally remain outside collection-container rename ownership.

## Next

- Continue reducing collection-versus-module cognitive load in the desktop and
  apply the same Registry-owned referential-safety standard to collection
  removal and future collection-tree editing operations.
