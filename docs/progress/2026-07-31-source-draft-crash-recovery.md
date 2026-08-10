# Source-draft crash recovery

Date: 2026-07-31

## Outcome

- Source edits, image/asset replacements, removals, validation hooks, and the
  optional module-folder rename now share a durable hidden transaction journal
  at `.paradev/source-draft-transaction/recovery.json`.
- ParaDev writes and fsyncs the bounded journal and verified backups before the
  first source mutation. Each file and rename step advances through
  `pending`, `applying`, and `applied`; the transaction is marked `committed`
  before its owned recovery files are removed.
- The next source apply or project build automatically handles an interrupted
  transaction under the existing whole-project source lock:
  - an exact ParaDev-authored after-state is restored to its verified backup;
  - an already restored before-state is accepted idempotently;
  - a committed transaction is cleaned without undoing its changes;
  - a file or module folder changed outside ParaDev is preserved and reported
    as a recovery conflict.
- Validation builds executed inside a live source transaction carry an explicit
  context boundary, so focus, technology, doctrine, and MIO editors validate
  their newly written drafts without misclassifying the current transaction as
  a restart.
- Recovery paths are project-relative, journal fields are closed and bounded,
  backup hashes are verified before restoration, module renames are bound to
  the retained directory identity, and cleanup removes only journal-owned
  files.
- Recovery schema v3 names every Unix guarded mutation's deterministic
  same-directory displacement before the first source write. The displacement
  is created with a no-clobber hard link, verified to remain the same inode,
  and removed only after the replacement or removal is durable.
- An abrupt exit after the target name is unlinked, including during rollback,
  leaves both the durable backup and the journal-owned adjacent file. The next
  build or source apply restores the exact before-state and removes the
  displacement. If another process creates a newer target first, recovery
  preserves both files and stops with an actionable conflict.
- Committed cleanup no longer reopens source paths after an intentional module
  rename or a retained-parent write. Every low-level guarded mutation proves
  its displacement was removed before returning, so a committed journal only
  clears its hidden backups and receipt.
- Desktop source and tree-editor applies now recognize recovery-class backend
  failures without trusting a pathname parsed from the error. ParaDev derives
  only the active project's fixed hidden transaction directory, preserves the
  unsaved editor draft, shows localized next-step guidance, and exposes the
  existing safe “Open recovery folder” workspace action.
- Successful Unix source publication, removal, rename, and rename rollback now
  fsync their containing directory when the host supports it.

The journal is system-owned hidden state. It adds no user-facing metadata and
does not require PIHC3 authors to maintain another file.

## Verification

- Complete Python gate: 2,367 passed; nine native-Windows cases skipped on
  macOS. This comprises 2,218 fast tests and 149 slow/integration tests.
- Desktop: 87 files and 1,420 tests passed; TypeScript typecheck and Vite
  production build passed.
- Source-draft crash/recovery selector: 76 passed; two native-Windows cases
  skipped on macOS. The combined project, metadata-cleanup, and retained-Windows
  source suite passed 360 tests with the same two skips.
- Project-build plus focus, technology, doctrine, and MIO editor regression
  suites: 382 passed; two native-Windows cases skipped on macOS.
- PIHC3 extensible-layout, retired-source, focus-tree, technology, and MIO
  consolidation gates: 28 passed.
- Fresh PIHC3 compilation:
  - clean and cached: 14,617 modules, 106 collections, 35,139 artifacts;
  - idea family: 392 modules, 12,187 artifacts;
  - asset-only `idea/HOI4_LAW_ICONS`: one module, 11,011 artifacts;
  - `focus/C01_MAIN`: 83 modules, one collection, 11,161 artifacts;
  - every run completed with zero diagnostics and zero errors.
- The last partial publication preserved the complete 35,139-file output
  closure, including its hidden publication receipt.
- Direct live-tree searches found zero `_component`, `_asset_component`,
  `legacy`, or `inactive_modules` directories.
- New regression coverage proves:
  - abrupt exit immediately after a source write is recovered before the next
    apply;
  - abrupt exit after a guarded write unlinks its target but before installing
    the replacement is recovered before the next build;
  - abrupt exit after a guarded removal unlinks its target but before deleting
    the displacement is recovered before the next build;
  - abrupt exit inside guarded rollback restores the original pre-transaction
    bytes on restart;
  - a newer external file created after abrupt displacement is preserved
    alongside the exact journal-owned original;
  - a tampered displacement pathname is rejected before any source or unrelated
    file is touched;
  - a dry project build recovers before source discovery;
  - abrupt exit immediately after a module-folder rename restores the original
    folder identity before the next edit;
  - a newer external edit wins over an interrupted ParaDev write;
  - a committed write survives an exit during journal cleanup;
  - malformed hidden recovery data fails closed without touching source files.

## Risk and next

- Native-Windows retained-handle semantics remain covered by unit dispatch
  contracts but are not crash-injected on this macOS host. Windows integration
  remains intentionally outside the current user-directed scope.
- A later recovery-center slice can expose structured per-file before/after
  state in the SDK. The current desktop path deliberately provides the safe
  minimum—localized guidance plus the fixed project-owned recovery folder—
  without teaching the frontend to parse or trust backend-supplied paths.
