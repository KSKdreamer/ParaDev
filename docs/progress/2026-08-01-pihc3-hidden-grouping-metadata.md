# PIHC3 Hidden Grouping Metadata

Date: 2026-08-01

## Outcome

PIHC3 no longer exposes compiler routing as user-maintained module metadata.
The 738 Focus tree links and 109 migrated Modifier output-group links moved
byte-for-byte from visible `meta.yaml` to module-local
`.paradev/meta.yaml`. The generic loader already merges this trusted system
layer before the authored layer, so compiler behavior and Registry contracts
did not gain a PIHC3-specific loading path.

The project-local Focus authoring template now declares the tree link as a
trusted `system_file`. Normal module creation, Add Focus, copy, and guarded
batch transactions therefore create/preserve it automatically. A new
standalone Modifier needs no metadata; only migrated modifiers that share a
legacy grouped output retain a hidden route.

The guarded module-duplication transaction now copies only durable
`.paradev/meta.yaml` settings. That closes the same integrity gap for all
1,424 PIHC3 modules with hidden extension semantics, including Doctrine,
Entity, Equipment Module, State Lore, and Trait. Import provenance, evidence,
diagram state, and transaction data remain excluded, and a symlinked durable
manifest fails closed.

The one remaining visible module metadata file is intentional:
`bookmark/PIHC_DIE_NEBENWELT - 新世界/meta.yaml` contains only
`inactive: true`. This matches the requested folder-based inactive model and
replaces any need for an `inactive_modules` directory.

## Verification

- Physical audit: zero forbidden component/legacy/inactive directories, zero
  untitled source units, zero visible Decision/Focus/Modifier metadata files,
  and one visible inactive Bookmark file.
- Nested-Git audit: extension descriptors plus Focus and Modifier module
  system manifests are explicitly versionable.
- Guarded-copy tests: durable hidden settings survive plan/apply; transient
  system state remains excluded; unsafe durable symlinks are rejected.
- Focus template and complete new-tree/Add-Focus workflow: passed.
- Focus family: 738 modules, 28 collections, 12,499 artifacts, zero
  diagnostics.
- Focus module partial: 83 modules in the owning tree, one collection, 11,161
  artifacts, zero diagnostics.
- Modifier family: 109 modules, 16 collections, 11,024 artifacts, zero
  diagnostics.
- Modifier module partial: 69 modules in `00_static_modifiers`, one collection,
  10,995 artifacts, zero diagnostics.
- Cached/full and clean/full: 14,617 modules, 106 collections, 35,131 artifacts,
  zero diagnostics.
- Repository fast gate: 2,278 passed and nine native-Windows cases skipped.

## Remaining

The hidden values are authoritative system routing, not duplicate authored
content. A future cross-tree Focus move should be a Registry/SDK operation that
updates this value transactionally; raw YAML editing is not the intended UX.
