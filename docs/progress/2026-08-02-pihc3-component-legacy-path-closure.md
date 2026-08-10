# PIHC3 Component And Legacy Path Closure

Date: 2026-08-02

## Done

- Re-audited the exact live PIHC3 project, then enforced the result across the
  whole project tree: 14,618 physical module folders, no component or
  asset-component directories, no `inactive_modules`, no legacy-named
  directories or source files, no symlinks, and every source unit named
  `id - title`.
- Normalized the remaining live legacy-labelled gameplay identities without
  deleting referenced content: the C09 preservation Focus, C23 Storm Empire
  heritage Idea, C08 focus-refresh Decision, and C08 Eastern Equestria
  Decision collection now use descriptive IDs, localization keys, image names,
  and references.
- Renamed the remaining generic legacy-labelled localization source and keys to
  `OLD_ORDER`; exact old identifiers and keys no longer occur under `src`.
- Made collection removal data-safe and Registry-consistent: dry-run plans use
  an exact hash; apply preserves member modules, clears explicit visible or
  hidden collection pointers, preserves unrelated settings, and uses the v5
  crash-recovery journal for pre- and post-commit recovery.
- Kept metadata compact: only one user-visible source-unit `meta.yaml` remains;
  the 847 Focus/Modifier grouping manifests are hidden and Registry-maintained.

## Verification

- Python: 2,493 passed; 9 native-Windows-only skips.
- Desktop: 90 files and 1,465 tests passed; TypeScript/Vite build and Rust
  `cargo check` passed.
- Black and targeted `git diff --check` passed; the five stale generated API
  expectations found by the first aggregate run were synchronized and the
  complete Python suite then passed.
- Strict PIHC3 compilation reported zero diagnostics and zero errors:
  - clean full and cached full: 14,617 active modules, 106 collections, 35,131
    artifacts;
  - Focus family: 738 modules, 28 collections, 12,499 artifacts;
  - Idea family: 392 modules, 12,187 artifacts;
  - Decision family: 460 modules, 62 collections, 12,044 artifacts;
  - C09 preservation Focus partial: 63 modules, one collection, 11,121
    artifacts;
  - C08 Eastern Equestria Decision collection partial: one module, one
    collection, 11,000 artifacts.

## Risks Or Blockers

- None for the physical cleanup or collection-removal safety slice. Remaining
  occurrences of the English word `legacy` are authored narrative text or the
  valid HOI4 engine field `legacy_lazy_load`; MIO identifiers ending in
  `components` are gameplay tokens, not retired module-family architecture.
- Native Win32 retained-handle and publication cases remain intentionally
  skipped on macOS, matching the current no-Windows-integration priority.

## Next

- Continue the Registry-owned authoring/diagram UX work from this clean source
  baseline, prioritizing intuitive creation and editing of PIHC3 modules and
  collection/tree relationships.
