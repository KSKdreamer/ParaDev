# PIHC3 Live Layout Closure

Date: 2026-08-09

## Outcome

PIHC3's live authoring tree is fully canonical. A whole-project directory
scan and the build preflight both report zero `*_component`,
`*_asset_component`, `legacy`, `inactive_modules`, or
`inactive_collections` directories. There are also no loose family files,
empty source directories, source symlinks, copy-marked source paths, or
retired component ids.

The current physical inventory is 70 module families with 14,574 authored
modules, and two collection families with 90 authored collections. All
14,664 source units use `id - preferred-language title`. Their 36,469
authored files include definitions, localization, images, and other resources
inside their semantic owner folders. System-maintained data is limited to 898
files below hidden `.paradev/` directories; only the Bookmark's optional
`inactive: true` remains in a user-visible `meta.yaml`.

`projects/PIHC3/scripts/check_source_layout.py` now rejects both module and
collection inactive trees, as well as every retired component/legacy form,
before discovery or caching. Its adversarial test builds non-empty retired
trees and proves the preflight rejects them while ignoring Finder
housekeeping files.

The retired folders may still appear in nested-PIHC3 Git history or a source
control changes view because the repository's pre-cutover `HEAD` contains
them. On disk they are deletions, while their semantic replacements are the
new canonical folders. The shared worktree was deliberately not staged or
committed, so history views must not be confused with compiler inputs.

## Related robustness work

Publication ownership now survives a macOS remount that changes `st_dev`
while preserving the canonical path and inode. ParaDev repairs only that
volatile device identity atomically and retains the safe artifact ledger;
path or inode changes remain hard failures.

The built-in desktop AI authoring role can now return either a Registry-owned
module batch or a collection scaffold. Focus trees, decision categories, and
future collection extensions use the existing SDK dry planner, exact plan
hash, retained review dialog, and explicit apply transaction rather than a
second frontend creation path.

## Verification

- Exact PIHC3 source-layout audit: 70 module families, 14,574 modules, two
  collection families, 90 collections, 36,469 authored files, 898 hidden
  metadata files, one visible metadata file, and zero errors.
- Focused cleanup, publication, desktop-chat, and selection tests: 137 passed.
- Supported repository Python gate: 2,398 passed and nine native-Windows tests
  skipped in 282.35 seconds.
- Desktop gate: 92 files and 1,489 tests passed.
- TypeScript and Vite production build passed; only the existing chunk-size
  advisory remains.
- Black and `git diff --check` passed for this slice.
- Clean/full and cached/full PIHC3 builds: 14,573 active modules, 106 compiler
  collections, 33,437 artifacts, zero diagnostics/errors.
- Focus-family partial: 738 modules, 28 collections, 10,802 artifacts, zero
  diagnostics/errors.
- Focus-module partial (`FOCUS_C12_SHADOWS_OF_THE_PAST`): 129 modules, one
  collection, 9,556 artifacts, zero diagnostics/errors.

## Remaining boundary

No Git staging or commit was performed in this shared worktree. The product is
not being declared release-ready here; this checkpoint establishes a clean,
enforced PIHC3 authoring source and a green build/test baseline for the next
GUI and Registry-extensibility slice.
