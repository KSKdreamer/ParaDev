# PIHC3 Guided AI Authoring

Date: 2026-08-09

## Outcome

ParaDev's built-in AI can now propose guarded edits to existing PIHC3
sources selected in the desktop app. The `edit-selection` role receives only
the active HeavenBase Registry's Guided controls, current scalar values,
localized labels, bounds, choices, module identity, and exact project-relative
source identity. It cannot propose source text, write flags, force flags,
revision fields, or plan hashes.

The backend accepts at most 16 clean selected source files and 512 editable
controls, requires one module family, rejects unknown sources and controls,
and passes normalized scalar replacements to
`Project.plan_source_form_updates()`. The result remains a no-write SDK plan.
Malformed Registry choices now fail closed instead of disappearing from the AI
catalog.

The desktop parses the proposal as a strict discriminated contract, retains it
in the canonical module-editor session, blocks replacement when the family has
other unsaved work, and opens a localized review dialog. The dialog shows each
module, source path, Registry-owned control label, and old-to-new value. Only
an explicit confirmation applies the exact revision-guarded `sourceEdits`
transaction. The project and source views refresh after a successful write;
post-write refresh failure is reported without misrepresenting the committed
source transaction as failed.

## Physical PIHC3 cleanup

The live PIHC3 source audit remains fully canonical:

- 70 module families and 14,574 authored modules;
- two collection families and 90 authored collections;
- 36,469 authored files;
- 898 hidden metadata files and one visible metadata file;
- zero retired `_component`, `_asset_component`, `legacy`,
  `inactive_modules`, or `inactive_collections` source directories;
- zero layout errors.

Finder recreated `.DS_Store` while the project folder was open. The two
observed files were removed. The test contract now treats `.DS_Store` as
ignored macOS housekeeping, consistently with PIHC3's build preflight and
`.gitignore`, while still forbidding Python bytecode, pytest caches, and Ruff
caches. Finder may recreate its ignored file without changing compiler input
or making the build flaky.

## Verification

- Backend structured-chat and selection gate: 45 passed.
- Desktop gate: 93 files and 1,498 tests passed.
- TypeScript and Vite production build passed. The existing large-chunk
  advisory remains; the Guided form stays code-split from the main module
  editor.
- Expanded Python gate collected 2,568 tests. The full run produced 2,558
  passes, nine native-Windows skips, and only the Finder-housekeeping failure.
  After correcting that flaky contract, the revised cache/layout checks passed
  3/3. Every production-code test in the expanded run passed.
- Black and `git diff --check` passed.
- Clean/full and cached/full PIHC3 builds: 14,573 active modules, 106 compiler
  collections, 33,437 artifacts, zero diagnostics/errors.
- Focus-family partial: 738 modules, 28 collections, 10,802 artifacts, zero
  diagnostics/errors.
- Focus-module partial (`FOCUS_C12_SHADOWS_OF_THE_PAST`): 129 modules, one
  collection, 9,556 artifacts, zero diagnostics/errors.

## Remaining boundary

No Git staging or commit was performed in the shared worktree. Retired paths
can still appear as deletions in nested-PIHC3 Git history, but they are absent
from the physical compiler input. This checkpoint does not claim the broader
continuous release goal complete; it closes existing-module natural-language
editing through the same Registry, Entity, Guided-form, and atomic SDK
architecture used by manual ParaDev authoring.
