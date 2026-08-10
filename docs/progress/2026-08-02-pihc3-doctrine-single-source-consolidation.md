# PIHC3 Doctrine single-source consolidation

Date: 2026-08-02

## Outcome

PIHC3 Doctrine content now has one physical source root, one project-local
HeavenBase Entity, one Registry compiler, and one diagram provider.

The audit found that all 94 folders under `src/modules/doctrine/` looked
editable, but the routed compiler emitted definitions for only 43 of them.
Fifty-one folders containing a `folder` field were routed as localization-only
grand doctrines. A separate hidden `doctrine_definition` family continued to
emit stale aggregate land/air definitions, so a clean zero-diagnostic build
could silently ignore current standalone gameplay edits.

The sources were classified with the real PDX parser:

- 8 current grand doctrines use scalar `folder = land|air`;
- 43 current subdoctrines use scalar `track` plus `xp_type`;
- 43 pre-1.17 nodes use a block-shaped `folder = { ... }`, emitted no PDX, and
  had zero references outside the Doctrine family.

The 43 non-compiling nodes and four duplicate aggregate land/air files were
removed after a guarded dry run. Every removed file and every rewritten active
diagram state was copied first to
`/var/folders/hx/r9cz0qls4m5dt6k6rl08lftw0000gn/T/paradev-pihc3-doctrine-legacy-20260802-h_cahv9c`.
The active graph was collapsed through removed nodes from 97 mixed path edges
to 54 active-only paths; all 25 reviewed mutual-exclusion relationships remain.

## Extension architecture

`extensions/doctrine/` now owns:

- the concrete `PIHC3Doctrine` HeavenBase Entity;
- optional authored `def.txt`, localization, preview, shared PDX, and shared
  reward-localization resource slots;
- source-derived grand/land/air/sea routing;
- path-preserving emission for the single
  `PIHC_DOCTRINE_SUPPORT - 教义共享支持` module;
- a project-local diagram projection that exposes 51 editable nodes and omits
  the shared support module;
- template-created hidden diagram layout only, with no repeated subtype
  metadata.

The former `extensions/doctrine_definition/` and
`src/modules/doctrine_definition/` roots are gone. The shared folder, track,
sea definitions, and two reward-localization files moved intact into the
Doctrine support module. The land/air aggregate definitions no longer shadow
the 51 standalone modules.

Four repeated gameplay modifier assignments became visible after the stale
aggregate source was removed. Each was a base-level duplicate of a reward
modifier; only the duplicate base assignment was removed, preserving every
other standalone edit and the reviewed reward value.

## Verification

- Whole-project source hygiene: no `_component`, `_asset_component`, `legacy`,
  `inactive_modules`, malformed `id - preferred localization` folder, or
  legacy shadow asset.
- Focused Doctrine/Registry/template/source tests passed, including 51 exact
  node artifact paths, 9 exact shared PDX support paths, 2 exact shared
  localization paths, 54 path edges, 25 mutual exclusions, and no duplicate
  logged modifier keys.
- Latest clean/full and cached/full publication: 14,574 modules, 106
  collections, 33,438 artifacts, zero diagnostics/errors, not blocked.
- Latest Doctrine family partial: 52 modules, 9,357 artifacts, zero
  diagnostics/errors.
- Latest Doctrine support-module partial: 1 module, 9,306 artifacts, zero
  diagnostics/errors; all 11 owned PDX/localization resources are present.
- Complete Python inventory in lock-safe serial verification: 2,499 passed
  (2,346 fast plus 153 slow), with 9 expected native-Windows-only skips.
- Desktop: 89 files and 1,453 tests passed; strict TypeScript and Vite build
  passed with only the existing large-chunk warning; Cargo check passed.

## Next

Add standalone subdoctrine creation to the registered Doctrine diagram
provider. It should reuse generic diagram-node plan/apply/build rollback and
derive folder, track, XP type, localization, image, and diagram relationships
from one module scaffold; no Doctrine-specific desktop dispatch is needed.
