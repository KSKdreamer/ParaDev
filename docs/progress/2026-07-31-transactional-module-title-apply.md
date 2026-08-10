# Transactional module title apply

Date: 2026-07-31

## Outcome

- `Project.apply_source_draft(...)` now accepts an optional
  `module_rename`. It preflights the final folder identity before writing and
  commits the folder move only after every text, removal, image, and asset
  mutation succeeds.
- A normal rename failure rolls every completed file mutation back. Source
  application, folder identity, and Catalog reconciliation now produce one
  aggregate payload and one editor acknowledgment.
- REST, CLI, the callable authoring MCP, desktop Python, Tauri, and TypeScript
  all route the combined request to that single SDK method. The module editor
  no longer performs a second standalone rename after applying localization.
- The MCP request schema is closed, revision-aware, and exposes
  `project_draft_apply` for agent authoring. Generated frontend, SDK/CLI, MCP,
  Project, and API-catalog references are synchronized.

## Verification

- Python: 2,207 passed; nine native-Windows tests skipped on macOS.
- Desktop: 87 files and 1,417 tests passed.
- Rust/Tauri: 94 tests passed.
- TypeScript/Vite production build passed.
- Black, Flake8, and Rust formatting gates passed.
- PIHC3 source-layout suite: 20 passed. The active source tree has zero
  `_component`, `_asset_component`, `legacy`, `inactive_modules`, or symlink
  directories under modules and collections.
- Clean and cached PIHC3 builds: 14,617 active modules, 106 collections,
  35,139 artifacts, zero diagnostics.
- Focus-family partial: 738 modules, 28 collections, 12,499 artifacts, zero
  diagnostics.
- Focus-module partial (`FOCUS_C12_SHADOWS_OF_THE_PAST`): 129 modules, one
  collection, 11,253 artifacts, zero diagnostics.

## Risk and next

- The transaction is failure-atomic for ordinary exceptions, including a
  guarded folder-rename failure. It is not yet process-crash atomic: abrupt
  termination after file publication but before the final folder move can
  still leave a temporary source/folder-title mismatch.
- The next data-safety slice should move draft recovery state from temporary
  backups into a project-local durable journal with startup recovery, then add
  subprocess-kill tests around every publication boundary.
- The Heaven-style scanner reports only pre-existing direct infrastructure
  imports in large test modules for this changed-path scan; production files
  introduced no new findings.
