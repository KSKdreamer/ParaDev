# PIHC3 Partial Publication And Entity Restoration

Date: 2026-07-26 SGT

## Summary

- Kept ParaDev aligned with the local HeavenBase 0.1.2.1 checkout on
  `master` at `bfd65d29021cc5ab31a83515adb719c0c27f34af`.
- Restored PIHC3's entity family as 134 ordinary, independently addressable
  record modules backed by one reviewed PIHC2 contract and one registered
  compiler.
- Replaced the compile wrapper's full-build localization workaround with a
  registered project postprocessor. A targeted module build now remains
  targeted while still producing the complete, validated localization
  closure required by Hearts of Iron IV.
- Hardened publication recovery, copy-root processing, portable path
  collision checks, replacement localization paths, invalid-byte handling,
  and project-source snapshot serialization.
- Verified clean, cached, and one-module builds against one isolated 1.3 GB
  PIHC3 output without touching the live launcher installation.

## Entity Contract

The entity family is registered through `system/entity_family.py`, with
private compiler and record helpers under `system/`. The reviewed
`scripts/data/pihc2_entity_contract.yaml` contract materializes 134 modules
under `src/modules/entity/`; each module contains only its author-facing
`meta.yaml` and `record.json`.

The aggregate `HOI4DEV_ENTITIES` source remains available as a deterministic
compatibility projection. The old declarative `families.entity` manifest
entry is gone, so family discovery and compilation have one runtime source of
truth.

## True Partial Localization

ParaDev's build extension registry now supports artifact postprocessors. The
build plan first merges selected module artifacts and active copy roots, then
runs postprocessors, artifact writers, generic validation, and final
`BuildResult` validation over that same immutable artifact set.

PIHC3 registers `system/localisation_postprocessor.py`. It:

- includes the complete localization closure with project publication scope;
- preserves language identity below `localisation/replace/<language>/`;
- records explicit publication predecessors for renamed outputs;
- validates UTF-8, BOM, localization headers, and supported languages;
- blocks malformed localization before output or ownership state changes;
- accepts both official comment-only and multi-language `languages.yml`
  reference forms.

`compile.bash` now forwards the requested selector unchanged. The old
standalone localization deduplication script and the manifest's machine-local
copy-root overlay are no longer part of the build.

## Publication And Snapshot Safety

Publication recovery separates structural blockers from ordinary stale
artifacts. Structural blockers are journaled before writers run. Ordinary
stale paths, renamed predecessors, and explicit replacements remain until all
new artifacts have been written successfully; reconciliation then deletes and
checkpoints each predecessor before publishing a complete ledger.

Copy-root artifacts participate in whole-plan postprocessing and validation,
including file-versus-descendant collision checks under portable
Unicode-normalized, case-folded paths.

Emitted builds now hold the project-source mutation lock from discovery
through publication, then the generated-root locks. SDK source mutations use
the same project lock, so a concurrent edit is queued and a build emits one
coherent old-or-new source snapshot. The public
`project_source_mutation_lock(project_root)` is re-entrant within one context,
so SDK operations can compose under one source transaction without
deadlocking. Invalid source/output-root combinations are rejected before any
project lock is acquired.

Targeted publication also distinguishes granular module/collection scope from
family-wide migration scope. A family target reconciles the active family and
its declared retired families. Module and collection targets remain granular
and leave unrelated retired rows in place until a family or full build emits
the complete replacement set.

## Initial Isolated Acceptance

Before the achievement and intelligence-agency consolidations, the acceptance
output used
`/private/tmp/paradev-pihc3-acceptance-20260726-2` and a separate temporary
ParaDev config root.

| Build | Modules | Collections | Returned artifacts | Diagnostics |
| --- | ---: | ---: | ---: | ---: |
| Clean full | 18,117 | 78 | 37,509 | 0 |
| Cached full | 18,117 | 78 | 37,509 | 0 |
| Targeted `idea/IDEA_C08_NEVER_FORGET` | 1 | 0 | 10,995 | 0 |

The full result contains 10,992 localization artifacts, 26,516 planned
non-localization artifacts, and one runtime-generated building icon strip.
The cached build retained the exact content hashes and mtimes of sampled PDX,
localization, and postprocessed outputs, and its complete ownership ledger was
byte-identical.

The targeted result contains the selected idea PDX, 10,992 project-scope
localization artifacts, and the two descriptors. It contains no unrelated
non-localization artifact. Sampled target and unrelated output hashes and
mtimes remained unchanged. The post-target ownership ledger still contains
all 37,509 full-build path keys, with no missing or extra rows and no pending
removals.

## Initial Verification Checkpoint

| Gate | Result |
| --- | --- |
| Strict full dry plan | 18,117 modules; 78 collections; 37,508 planned artifacts; 0 diagnostics |
| Entity-family regressions | 5 passed |
| Localization postprocessor regressions | 12 passed |
| Copy-root/postprocessor regressions | 13 passed |
| Publication and artifact-writer regressions | 56 passed |
| Source snapshot, mutation, security, and lock regressions | 96 passed |
| Registry, keyword, and publication focus | 31 passed |
| Family capability regressions | 25 passed |
| Isolated clean/cached/targeted publication | passed |

The remainder of this entry records the later consolidation and verification
checkpoint from the same work session.

## Native Family Consolidation

### Achievements

Achievements now have one source of truth under `src/modules/achievement`.
The 49 canonical modules own their PDX and localization plus all 147 checked-in
DDS variants. The former `achievement_component` and
`achievement_asset_component` families and their parallel migration paths are
retired. A family-targeted publication can reconcile their stale aggregate and
asset outputs, while a single-achievement publication remains module-scoped.

### Intelligence Agencies

The intelligence-agency slice now consists of 9 canonical modules and one
unified importer. Their 61 source files emit 45 runtime artifacts: 9 PDX
definitions, 18 localization files, and 18 GFX/DDS files. Preview PNGs remain
non-emitting authoring inputs. The former
`intelligence_agency_component` and
`intelligence_agency_asset_component` roots, manifest entries, and three
separate importers are retired.

The isolated cutover removed exactly eight tracked stale artifacts: the former
aggregate definition and seven preview PNGs. Publication finished with a
complete 37,501-row ownership ledger and no pending removals.

### Entity And Native Unit Modifiers

The 134-record entity restoration remains independently addressable through
the registered entity family and aggregate compatibility projection described
above.

Unit modifiers now have native ownership instead of remaining in the
path-preserving unit-component import. One canonical module owns the six
current PIHC3 modifier IDs, provenance, and localization. The stale 53-ID
metadata/localization projection is gone, and the legacy unit importer no
longer claims the generated unit-modifier output path.

## Current Isolated Acceptance

After the intelligence-agency cutover, the strict full dry plan contains
18,107 modules, 78 collections, and 37,500 planned artifacts with zero
diagnostics. Runtime adds the generated building icon strip.

| Build | Modules | Collections | Returned artifacts | Diagnostics |
| --- | ---: | ---: | ---: | ---: |
| Full after native cutovers | 18,107 | 78 | 37,501 | 0 |
| Cached full | 18,107 | 78 | 37,501 | 0 |
| Targeted `intelligence_agency/INTELLIGENCE_AGENCY_BOC` | 1 | 0 | 10,997 | 0 |

The cached run preserved content hashes, mtimes, and the ownership-ledger
digest. The targeted run returned the 10,992-file project localization closure,
the selected agency's PDX/GFX/DDS files, and two descriptors. It changed no
unrelated output and left the complete ledger intact.

### Final Native-Unit Acceptance

The final isolated rerun after native unit-modifier cleanup exercised a clean
full publication, a no-clean cached publication, and a targeted publication of
`unit_component/UNIT_COMPONENT_UNITS_UNIT_MODIFIERS_UNIT_MODIFIERS`.

| Build | Modules | Collections | Returned artifacts | Diagnostics |
| --- | ---: | ---: | ---: | ---: |
| Clean full | 18,107 | 78 | 37,501 | 0 |
| Cached full | 18,107 | 78 | 37,501 | 0 |
| Targeted native unit modifiers | 1 | 0 | 10,995 | 0 |

All three runs left the same 37,501-file, 1,227,395,139-byte runtime tree:
SHA-256
`6649693b3de8b66514d5ae5a5519adf395d1e3eddf1f85319c5928d359a625a2`.
The targeted result contains the selected unit-modifier PDX artifact, the
10,992-file project localization closure, and two descriptors. It changed no
unrelated runtime content.

## Developer And Desktop Hardening

The idea and trait parity tools are portable review utilities. Both require an
explicit `--baseline-root` for the historical comparison checkout, load the
PIHC3 project through the SDK, and derive native output and source-map defaults
from the loaded project. They contain no machine-specific fallback path.

Desktop startup now lazy-loads `ModuleEditor` behind the existing localized
Suspense state. The post-split broad gate passed 64 Vitest files containing
1,161 tests, 64 Rust tests across three suites, and the production build of
3,295 modules. The main entry chunk fell from 1,200.26 kB raw / 291.84 kB gzip
to 844.15 kB raw / 197.95 kB gzip; the deferred editor chunk is 265.71 kB raw /
69.47 kB gzip.

## Test-Suite Reliability

Historical PIHC2 source contracts now resolve from
`PARADEV_PIHC2_RESOURCES_ROOT`. When that external checkout is absent, the 31
contracts that genuinely require it report explicit skips instead of blessing
empty values or machine-local paths.

The expensive PIHC3 full-plan fixture is module-scoped, and its 18 consumers
share one `xdist_group`. Parallel test execution uses `--dist=loadgroup`, so
the suite computes the 18,107-module plan once rather than once per worker.
The grouped full-build contracts passed 18/18 in 62.58 seconds.

The final migration-contract run is green with 282 passed and the 31 explicit
historical-source skips in 5:00. The repository-wide full Python gate is also
green with 1,985 passed, 34 intentional skips, and two non-failing warnings in
5:49.

| Final gate | Status |
| --- | --- |
| Repository-wide Python `--full` | Passed: 1,985 tests, 34 intentional skips, 2 non-failing warnings |
| Python formatting and lint | Passed: 168 files |
| Git diff and generated-file hygiene | Passed in both worktrees; no bytecode or transaction residue |

## Remaining Optional Investigation

Military Industrial Organization authoring remains optional follow-up work.
Its hierarchy likely needs a tree-oriented editor comparable to focus or
technology authoring, but no MIO support is claimed by this checkpoint.
