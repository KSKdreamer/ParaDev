# Descriptor-owned publication migrations

Date: 2026-07-31

## Outcome

- Removed publication-retirement state from ParaDev's simple, routed, and
  collection compiler dataclasses and from project family specifications.
- Removed all 11 remaining compiler constructor declarations from PIHC3.
- Migrated 16 PIHC3 successor-family claims to the owning HeavenBase Registry
  item's hidden `meta.publication.replaces_families` metadata.
- Kept publication migration data out of the public family-authoring view.
- Preserved full-family cleanup semantics while module and collection partial
  builds retain their narrow ownership scope.

## Safety

- ParaDev inspects and validates inert Registry metadata before importing the
  extension compiler.
- The BuildRegistry rejects self replacement, active predecessors, ambiguous
  predecessor ownership, duplicate claims, and compiler-owned legacy fields.
- `scripts/migrate_extension_publication_metadata.py` is dry-run by default.
  It compares legacy descriptor and literal Python claims, refuses conflicting
  sources, then uses exact-fingerprint atomic descriptor replacement.
- The PIHC3 post-migration dry plan contains zero remaining rewrites.
- All 76 hidden extension descriptors are explicitly versionable despite the
  broader project `.paradev/` ignore rule.

## User mental model

```text
extensions/<family>/
  __init__.py             # current Entity/compiler/provider behavior
  .paradev/
    meta.yaml             # generated Registry and publication lifecycle state
```

Ordinary module authors edit neither source-family migration history nor
hidden metadata. Extension code defines only current behavior; the persisted
Registry descriptor owns system lifecycle information.

## Regression gates

- Python: 2,182 passed; nine native-Windows filesystem tests skipped.
- Desktop: 87 files and 1,415 tests passed.
- Rust/Tauri: 93 tests passed.
- TypeScript/Vite production build passed.
- Full and cached PIHC3 dry plans: 14,617 modules, 106 collections, 35,139
  artifacts, zero diagnostics.
- MIO family partial: 7 modules, 11,001 artifacts, zero diagnostics.
- MIO module partial: 1 module, 10,995 artifacts, zero diagnostics.
- Hidden-descriptor and publication migrations both report zero remaining
  PIHC3 changes.
- Main and nested repository diff checks passed.
