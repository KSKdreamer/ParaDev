# PIHC3 source-layout preflight and residual-copy cleanup

Date: 2026-08-02

## Outcome

- Reconciled the exact live filesystem with PIHC3's nested Git history. The
  live `projects/PIHC3/src/modules/` tree has no `_component`,
  `_asset_component`, `legacy`, or `inactive_modules` directory. The current
  nested-Git `HEAD` still records 42 retired component-family roots, 25,635
  files below those roots, and 26,530 historical files below `legacy/`
  children. Those old paths are deletion records in the dirty migration
  worktree, not live folders, Registry families, cache entries, or compiler
  inputs.
- Added `projects/PIHC3/scripts/check_source_layout.py`, a fast no-write audit
  with human and JSON output. Every PIHC3 wrapper build now runs it quietly
  before compiler discovery.
- The preflight walks the project outside `.git` and rejects case-insensitive
  retired directory names, component-shaped object ids, source symlinks,
  copy-marked paths, malformed or duplicate `id - title` units, empty units,
  loose files at source/family roots, `meta.yml`, and system-owned keys in
  visible `meta.yaml`.
- The stricter audit found one real residual missed by the earlier gates:
  `texticon/unit_category_infantry_rockbreaker_small - unit category infantry rockbreaker small - 副本/`.
  Its only DDS was unreferenced and byte-identical to the existing
  `unit_category_infantry_motorized_icon_small.dds` (SHA-256
  `54019ed7005188045da25a14596b8c8df7e5720d63075b14cd6113e7b358f508`).
  The redundant module was moved to
  `/Users/magolor/.Trash/PIHC3-unreferenced-rockbreaker-texticon-2026-08-02/`
  so it remains recoverable.

## Current physical inventory

- 70 module-family roots and 14,574 physical module folders;
- two collection-family roots and 90 physical collection folders;
- 36,705 authored source files;
- 898 hidden module/collection YAML files, comprising genuine Registry-owned
  metadata/diagram state;
- one visible metadata file, containing only the intentionally inactive
  Bookmark flag;
- zero forbidden or copy-marked live paths and zero source symlinks.

PIHC3 has 14,573 active compiler modules because one of the 14,574 physical
modules is intentionally inactive.

## Compilation proof

The four artifact-emitting modes ran in one fresh isolated publication root,
`/tmp/paradev-pihc3-source-cleanup.RxuFum/mod/PIHC3`:

| Mode | Modules | Collections | Artifacts | Diagnostics | Blocked |
| --- | ---: | ---: | ---: | ---: | --- |
| clean/full | 14,573 | 106 | 33,437 | 0 | no |
| cached full | 14,573 | 106 | 33,437 | 0 | no |
| family partial: `technology` | 301 | 0 | 10,204 | 0 | no |
| module partial: `technology/TECHNOLOGY_FIREARM_I` | 1 | 0 | 9,300 | 0 | no |

After module-partial publication, the isolated mod still contained exactly
33,437 files and no component/asset-component/legacy/inactive/copy-marked
path. The removed DDS was absent.

## Regression guard

- Focused layout/extensibility suite: 41 passed.
- Wrapper-contract slice: 2 passed.
- Complete PIHC3-specific contract suite: 241 passed in 15:28 under the
  supported `uv` runtime.
- The PIHC3 manual now documents the standalone JSON audit and the automatic
  build preflight, and distinguishes physical from active module counts.

## Git-state caveat

This cleanup is intentionally not committed or staged as an isolated change:
PIHC3 is already a very large shared dirty migration worktree, and the
canonical replacements plus retired deletions must be reviewed and committed
as one coherent migration rather than partially committing unrelated user
work. A Git tree/history view can therefore still show the old content in
`HEAD`; the live filesystem, Registry discovery, caches, and compiled output
are the authoritative state verified above.

## 2026-08-03 revalidation

- Recounted the nested repository after a direct user audit: all 25,635 files
  below the 42 component-family roots stored by `HEAD` are reported by Git as
  deleted from the working tree, while the physical source tree contains zero
  matching paths. Ten rows are `MD` because an intermediate migration edit is
  staged in the index and the corresponding working-tree file is deleted; they
  are still absent from compiler discovery.
- Replaced the 122 KB intermediate migration inventory with
  `docs/resources/04-pihc3-source-cutover.md`, one current source-authority
  page, and removed three unreferenced state-temperature plans/specs that still
  prescribed component folders.
- The current audit reports 14,574 physical modules, 90 physical collections,
  36,469 authored files, 898 hidden metadata files, one visible inactive flag,
  and zero errors.
- The consolidated ownership/extensibility suite passed 184 tests in 7:01.
  Clean/full and cached full builds each produced 33,437 artifacts with zero
  diagnostics. Focus-family partial compilation produced 10,802 artifacts;
  the selected Focus module closure produced 9,464. The publication root still
  contained exactly 33,437 files after both targeted builds.
