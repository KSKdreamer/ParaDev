# PIHC3 MIO family consolidation

Date: 2026-07-29

## Change

Replaced PIHC3's hidden
`military_industrial_organization_component` compatibility family with the
canonical `military_industrial_organization` family. The seven modules now use
short domain-shaped folder ids, title-only visible metadata, exact nested PDX
source paths, module-local localization, and hidden portable importer state.
The old family id is retained only as a publication-ledger retirement claim.

The prior seven visible `legacy/source.yaml` files moved byte-for-byte to
`.paradev/evidence/source.yaml`. Their reconstructed original-path digest is
still
`c16a84fdd095d2530b070f87784dfaf0f63e413f644bb11066e224a690f42f72`
for 7 files and 22,732 bytes. No symlinks were introduced.

The refresh importer is now
`projects/PIHC3/scripts/migrate_pihc2_military_industrial_organizations.py`.
It accepts only the reviewed seven-file inventory, writes the consolidated
shape, and keeps the reviewed PIHC3 replacement for the removed vanilla
`rocket_artillery` technology reference. The writer also strips its internal
trailing newline before calling HeavenBase 0.1.2.1 `save_txt`, whose owned
contract appends exactly one newline; the refresh therefore reproduces all 34
canonical source-tree files byte for byte.

## Verification

- Before migration: 7 modules, 27 files, 820,982 source-tree bytes; 7 PDX
  sources and 6 localization sources.
- Before and after isolated family emission: 7 modules, 67 artifacts
  (7 PDX and 60 localization), 589,966 bytes, zero diagnostics, unblocked.
- Exact emitted path-and-byte digest:
  `62d7d8eb8f74ca70683ce9ae09ab9708ce3c0992ba403ebe4c2f41b6a21a9bf0`.
- After PIHC3's registered localization postprocessor, all 60 localization
  artifacts are routed through `localisation/replace/`, matching the current
  PIHC3 output. The published family remains 67 artifacts and 589,966 bytes;
  its exact path-and-byte digest is
  `dd2b2145c00543cc94c3cd9505c5c14d398a2a68e118bc285c5ae5de55811e2e`.
- Read-only comparison against the current generated PIHC3 mod found 0 missing
  and 0 byte-different files across all 67 published family artifacts.
- Exact canonical nested PDX source digest:
  `b871483cb075db73e37a0ee427fafdaffaa9b03ab117acbcc0eb6383a2e2cc87`
  for 7 files and 290,900 bytes.
- `rtk bash scripts/test.bash
  tests/test_pihc3_mio_family_consolidation.py -q`: 6 passed.
- `rtk bash scripts/test.bash tests/test_pihc3_migration_contracts.py -q -k
  military_industrial_organization`: passed.

The artifact check writes only to pytest temporary storage. No full PIHC3
build and no real mod-output publication ran in this slice.

## Boundary

Organization, policy, and weight roles are derived from canonical PDX content,
not folder names or metadata. MIO graph edits remain an SDK-owned exact-source
transaction; desktop code must not add another PDX parser or metadata fallback.
