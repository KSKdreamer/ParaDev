# PIHC3 Doctrine Compound Child Authoring

Date: 2026-08-02 15:48

## Done

- Added an optional provider-owned companion source plan to the generic
  `ModuleDiagramModuleCreation` contract. Existing Focus and Technology node
  planners remain source-plan-free and keep the same SDK/REST/MCP/desktop path.
- Made the Project SDK preflight the standalone module and companion drafts as
  one reviewed plan. Apply installs the new folder, writes existing sources
  through the durable source-draft journal, runs the registered family build,
  and commits only when the whole operation succeeds.
- Added explicit source-conflict and incomplete-recovery diagnostics. Normal
  build rejection or source failure rolls the existing source back and then
  rolls the new module scaffold back, leaving no half-linked tree node.
- Closed the hard-process-exit window with a generic hidden compound journal.
  It records exact parent before/after states, child inventory, and the scaffold
  transaction id before installation. Startup runs the existing source-journal
  recovery first, then removes an exact orphan/partial child when the parent is
  old or retains an exact child when the parent is committed. Changed or extra
  child data is never deleted and keeps the operation fail-closed for review.
- Extended the pure HoI4 Doctrine planner with bounded pending-node ids. Only a
  present directed path may target a pending node; unsupported pending mutual
  exclusions and duplicate ids fail closed.
- Upgraded the PIHC3 Doctrine extension to `0.2.6`. “Add from selected” now
  treats the selected doctrine as the parent, places the new child below it,
  creates the child with an empty outgoing path list, and records the outgoing
  edge only in the parent’s hidden diagram state.
- Re-audited the exact PIHC3 source tree: 70 family roots, 14,575 direct source
  units, zero `_component`, `_asset_component`, `legacy`, or
  `inactive_modules` directories, zero malformed direct `id - title` names,
  and zero symlinks.

## Verification

- Core and PIHC3 Doctrine planner/integration tests: 12 passed.
- Generic Project diagram, Focus, Technology, and public-surface regressions:
  40 passed.
- Generic desktop node-dialog and service regressions: 168 passed.
- The four-file whole PIHC3 migration/layout/template/retired-source aggregate
  reached 181 passed and exposed two verification-only mismatches: a Doctrine
  `__pycache__` created by an explicit `py_compile` command and the stale
  numeric-field total. The cache was removed, the total now verifies all 24
  fields, and the affected gates reran 1/1 and 4/4 green.
- Final post-hardening Python regression: 29 passed. `git diff --check` and
  Python compilation passed; the Heaven-style scan reported only existing
  whole-file standard-library import recommendations in `sdk/project.py`, not
  a new violation in this slice.
- Added real subprocess hard-exit coverage for the before-parent and
  after-parent commit boundaries, plus an externally changed-child case. All
  three recovery paths pass; the changed child and recovery marker are
  preserved. The complete Project SDK regression remains green at 364 tests,
  and the scaffold-directory regressions remain green at 34 tests.
- Strict live PIHC3 Doctrine compilation completed with zero diagnostics and
  zero errors:
  - fresh family: 52 modules, 10,968 artifacts;
  - cached family: 52 modules, 10,968 artifacts;
  - module partial: 1 module, 10,909 artifacts.
- Final live PIHC3 publication after the physical single-source cleanup passed
  all four GUI build modes with strict metadata and launcher synchronization
  disabled:
  - clean/full: 14,574 active modules, 106 collections, 35,049 artifacts;
  - cached full: 14,574 active modules, 106 collections, 35,049 artifacts;
  - Doctrine family partial: 52 modules, 10,968 artifacts;
  - Doctrine module partial: 1 module, 10,909 artifacts.
  Every mode reported zero diagnostics and zero errors. The one-folder gap
  between the 14,575 physical module inventory and the active build count is
  the intentionally disabled bookmark module using `inactive: true`.
- Updated the current macOS/Windows preview smoke expectations and bilingual
  start guides from the retired pre-cleanup counts to this verified active
  baseline. The packaging contract regression is 17/17 green.
- The final repository gates passed all 2,517 collected Python tests, all 1,453
  desktop tests, the production TypeScript/Vite build, Python bytecode
  compilation, and whitespace validation.

## Risks Or Blockers

- Compound diagram recovery currently requires the descriptor-anchored POSIX
  scaffold backend. It fails closed rather than using a path-based fallback on
  unsupported hosts. Windows integration remains intentionally outside this
  release slice.
- No Windows integration or macOS game-launch work was added, matching the
  current priority on the app, HeavenBase integration, and PIHC3 authoring.

## Next

- Apply the same Registry-owned compound authoring pattern only where another
  tree format’s existing node owns the new relationship.
- Continue reducing cognitive burden across MIO and the remaining extension
  entity types while preserving the clean physical module layout and four-mode
  compilation contract.
