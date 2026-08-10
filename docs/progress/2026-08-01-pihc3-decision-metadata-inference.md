# PIHC3 Decision Metadata Inference

Date: 2026-08-01

## Outcome

PIHC3 decision collection membership is now owned by the project-local
Decision Entity instead of 458 repeated user metadata files. Each authored
decision already contains exactly one outer category block in `def.txt`; the
registered family's `normalize` hook derives `Module.collection_id` from that
loaded PDX resource before collection aggregation.

The basic decision template no longer creates `meta.yaml`, and all 458
redundant checked-in decision metadata files were removed. The two shared
decision-support resource modules also remain metadata-free and uncollected.
Copying a decision folder, changing its folder id/title, PDX definition,
localization, and image is therefore sufficient to create a new source unit.

The family fails closed when `def.txt` has no category or declares several
categories. An explicit legacy collection value is still checked against the
source category instead of silently overriding it.

## Physical Audit

- `src/modules/decision`: 460 standalone folders, 458 authored decisions and
  two shared support/resource modules.
- Visible decision `meta.yaml`: zero.
- A same-turn follow-up moved the 738 Focus collection links and 109 Modifier
  output-group links into system-owned `.paradev/meta.yaml`. Project-wide
  visible metadata is now limited to one explicit inactive Bookmark flag.
- Project-wide forbidden `_component`, `_asset_component`, `legacy`, and
  `inactive_modules` directories remain at zero.

Focus and Modifier links were not semantically deleted: their source
definitions do not encode an unambiguous tree/output group, so the follow-up
hidden-metadata slice preserved the values behind the existing SDK-owned
system-file boundary instead of inventing filename or family-id heuristics.

## Verification

- Decision template happy/error paths: passed.
- Focused physical-layout/template contract gate: 4 passed.
- Decision-family partial: 460 modules, 62 collections, 12,044 artifacts,
  zero diagnostics.
- Decision-module partial: 12 modules in the owning category, one collection,
  11,022 artifacts, zero diagnostics.
- Cached/full and clean/full: 14,617 active modules, 106 collections, 35,131
  current artifacts, zero diagnostics.
- Project-only clean publication: the same 35,131 artifacts, zero diagnostics,
  and a non-dry result with launcher synchronization disabled.
- Standard parallel Python gate: 2,275 passed, nine native-Windows skips.
- Black, Flake8, Heaven-style scan, and `git diff --check` on the touched
  Python/test/docs slice: passed. The repository-wide formatting wrapper still
  reports 12 unrelated pre-existing files from concurrent work; this slice did
  not rewrite them.

The previous published manifest contained eight unrelated retired Interface
`*_legacy.dds` artifacts. The clean publication reconciled them: the stored
manifest now has 35,131 rows, reports no legacy rows, and none of those eight
files remains in generated output.
