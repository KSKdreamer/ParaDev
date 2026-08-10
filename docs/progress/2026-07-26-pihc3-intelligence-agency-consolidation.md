# PIHC3 Intelligence-Agency Consolidation

Date: 2026-07-26 SGT

## Summary

- Consolidated PIHC3's intelligence-agency definitions, localization,
  previews, GFX declarations, and DDS textures into nine canonical
  `intelligence_agency` modules.
- Retired the duplicate aggregate definition and the separate
  `intelligence_agency_component` and
  `intelligence_agency_asset_component` families.
- Replaced three overlapping migration scripts with one validated,
  transactional, byte-idempotent importer.
- Reduced visible metadata to type, title, and tags. Portable import
  provenance and the aggregate selector now live in `.paradev/import.yaml`.
- Kept previews editor-only and preserved the reviewed checked-in GFX/DDS
  assets without overwriting the external PIHC_dev source.

## Canonical Ownership

Each managed folder owns one quoted, aggregate-derived definition; English and
Simplified Chinese localization; an optional `icon.png` editor preview; and
the matching game-relative GFX/DDS pair. The aggregate is split by unique
`picture`, not by display name, so BOC and EOF remain distinct even though both
use `"Eyes of Fear"`.

The reviewed tree contains 61 source files. It compiles to exactly 45 runtime
artifacts:

- 9 per-agency definitions;
- 18 localization files;
- 9 GFX sprite declarations;
- 9 DDS textures.

The seven available PNG previews do not compile, and
`common/intelligence_agencies/00_intelligence_agencies.txt` is no longer
emitted.

## Import And Asset Safety

`migrate_pihc2_intelligence_agencies.py` validates the complete nine-record
aggregate, picture/module bijection, portable provenance, GFX declarations,
and complete DDS payload/header contract before publishing. It rejects
symlinked managed roots, ancestry, files, assets, and provenance before reading
content. It stages a complete replacement tree, preserves modules without
importer provenance plus non-owned files inside managed modules, rejects
portable NFC/case-folded ID collisions and divergent preserved content, and
swaps by directory rename with an external rollback backup.

The importer holds ParaDev's shared project-source mutation lock from its first
snapshot through final publication and rechecks source and destination
revisions immediately before cutover. A durable sibling marker records the
original and replacement revisions so a later run can recover an interrupted
swap without guessing which tree is authoritative.

Checked-in DDS bytes remain authoritative. All nine differ from the current
external PIHC_dev DDS data, so the importer reads PIHC_dev only for the
definition aggregate and never writes to that external mod tree. The old
checked-in component roots were moved recoverably to:

```text
/Users/magolor/.Trash/PIHC3-intelligence-agency-components-20260726/
```

After that move, a second refresh succeeded using only canonical module
definitions and assets, confirming the portable idempotent fallback.

## Verification

| Gate | Result |
| --- | --- |
| Portable fast behavior/security suite | 23 passed in 2.30 seconds |
| External aggregate parity and full family build | 2 passed in 57.10 seconds |
| Legacy family visibility contract | 1 passed; 312 deselected |
| Targeted strict dry plan | 1 module; exact 5 owned artifacts; 0 diagnostics; not blocked |
| Full strict dry plan | 18,107 modules; 78 collections; 37,500 artifacts; 0 diagnostics; not blocked |
| Full intelligence-agency ownership | 45 artifacts; 9 owners with 5 artifacts each |
| Black and Flake8 focused gate | passed |

The targeted plan includes the project-wide localization closure by design;
the selected intelligence-agency owner still contributes exactly its five
expected artifacts. The Heaven-style utility scan reports explicit
`os`/`pathlib`/`shutil` use for no-follow filesystem transactions and test-only
raw SHA-256 checks. Those are reviewed standard-library exceptions; no bespoke
utility abstraction was introduced.

## Remaining Work

- Add richer authoring fields and GUI guidance for new intelligence agencies
  without requiring users to understand imported provenance.
- Add country/focus helpers for creating and assigning agencies.
- Model intelligence-agency upgrade trees as a later dedicated authoring
  slice.
- Investigate whether MIO tree editing can reuse the focus/technology tree
  interaction model.
