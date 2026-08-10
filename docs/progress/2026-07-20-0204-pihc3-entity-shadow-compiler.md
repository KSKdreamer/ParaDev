# PIHC3 deterministic Entity shadow compiler and clean-build QA

Date: 2026-07-20 02:04 +08

## Outcome

PIHC3 now contains a deterministic, file-I/O-free compiler for all 134 portable PIHC2 Entity records. It reproduces the checked-in aggregate's nine ordered PDX trees and normalized writer bytes exactly while preserving the aggregate as the sole owner of all 182 emitted Entity artifacts.

The PIHC3 branch checkpoints are `99f2cb33c` (`feat(entities): add deterministic shadow compiler`) and `cd76db17f` (`fix(build): separate source and config roots`), both pushed to draft PR #2.

The legacy unit-assignment table is also checked in as editable strict JSON at `src/modules/entity/HOI4DEV_ENTITIES/legacy/entities.json`. Import and runtime validation share one contract, so malformed, duplicate, empty, or undeclared assignment values cannot enter through regeneration and fail later in the build.

This is the parity checkpoint before ownership cutover. Record or assignment edits intentionally block against the golden aggregate today; the next Entity slice can replace that aggregate's nine PDX snapshots with compiler-owned outputs once the GUI recovery loop is reverified.

## Portable source and compiler contract

The assignment source is exactly 37,965 bytes with SHA-256 `a4ef074d7f697e73326e7194147236417b5b79487e4f395b4ff36c589a6edb7e`. It contains 257 declared tags, 244 ordered unit types, and 605 tag memberships. The importer now includes it in the 185-file aggregate source manifest, snapshots it transactionally, and stamps the shared `pihc2.entity.assignments.v1` contract and byte provenance into aggregate metadata.

The pure compiler consumes explicit validated records, the assignment mapping, and a static-asset path inventory. It does not read files or mutate caller data. Production parity proves:

- 134 meshes;
- 264 concrete entities;
- 8,607 generated unit entities;
- six model owners;
- 173 static assets;
- nine ordered PDX outputs;
- identical output under reversed record and asset input order.

Legacy semantics covered by tests include duplicate-key order and recursive `__D` stripping, list pseudo-comments, Python float spelling, quoted names and mesh references, clone/pdxmesh tri-state behavior, texture fallback, direct animation ordering, assignment priority and tie-breaking, country handling, and reversed tag precedence.

## Build ownership and novice diagnostics

The aggregate remains the only artifact emitter. A full Entity build now compiles the portable records in memory and compares each of the nine outputs with the aggregate using both an ordered canonical tree and normalized writer bytes.

Mismatch diagnostics include the artifact path, first ordered structural difference, expected and compiled byte counts and hashes, and an edited-source candidate. A single edited record points to that module's real `record.json`; multiple edits point to the first real edited module and list every candidate instead of attaching a nonexistent `record.json` path to the aggregate. A valid assignment edit points to `legacy/entities.json`. Compiler failures such as an undeclared apply tag likewise point to the edited record.

The shadow gate cannot be disabled by changing aggregate provenance markers. A complete record corpus without `entity/HOI4DEV_ENTITIES` blocks with `entity.shadow_missing_aggregate`; a partial aggregate-plus-record build blocks with `entity.shadow_incomplete_records`. Intentionally targeted aggregate-only and small record-only inspections remain usable.

## Packaged GUI smoke state

The disposable checkout remains `/Users/magolor/Projects/ParaDev/PIHC3-GUI-Smoke`; the protected checkout was not selected or modified.

The packaged app retained the selected `PIHC3 GUI Smoke` project and previously loaded the Entity workspace with 136 objects and 457 sources. Runtime files and the assignment source were synchronized into that disposable checkout. Its intentional `VIENTO_MIRROR` scale edit from `4.0` to `4.25` produced the expected blocking `entity.shadow_mismatch` for `gfx/models/00_hoi4dev_meshes.gfx` at `root[0][3][68][3][4][3][1]`, with the expected value `4.0`, compiled value `4.25`, and `entity/VIENTO_MIRROR` attribution.

macOS locked before the packaged UI could be refreshed to verify the surfaced diagnostic and the GUI repair-to-green loop. Computer Use correctly refused further control. That UI-only acceptance remains pending; no shell or browser workaround was used.

## Full build finding

The first artifact build completed its core ParaDev plan with 18,175 modules, 37,556 artifacts, zero diagnostics, and `blocked: false`, then localization postprocessing rejected a stale, unowned output file: `localisation/english/DECISION_C01_ANGRY_EXP_l_english.yml`.

A scoped `compile.bash --clean` removed only generated PIHC3 output, the launcher descriptor, and this worktree's build cache. The clean rebuild then completed successfully:

- 18,175 modules;
- 78 collections;
- 37,556 artifacts;
- zero diagnostics and zero errors;
- `blocked: false`;
- localization dedupe scanned successfully, removed 6,088 duplicate entries, changed 1,672 files, and moved 3,338 files;
- the stale localization file is absent;
- the launcher, 30.4 MB source map, and localization postprocess manifest exist.

The source-checkout override used for that build exposed a separate wrapper defect: `PARADEV_ROOT` selected the active ParaDev code but remained exported when the CLI initialized configuration, creating a default-only `config.db` inside the ParaDev worktree. The generated database and its transient SQLite sidecars were moved to `/private/tmp/paradev-config-db-from-source-override-20260720-013003.sqlite*` for recoverability. The wrapper now consumes and unsets the source selector before launching ParaDev; an explicit `PARADEV_CONFIG_ROOT` is mapped back only when isolated configuration is intended. A cross-repository contract test pins this separation. A real summary smoke placed its 24 KB database only under `/private/tmp/paradev-build-config-smoke.dgOcUn`, left the source checkout free of configuration artifacts, and returned 18,175 modules, 37,555 summary artifacts, zero diagnostics/errors, and `blocked: false`.

## Verification gates

- Focused Entity compiler/family/importer checks: 66 passed after review fixes.
- Independent broader Entity review suite: 71 passed.
- Full PIHC3 script suite: 246 passed in 24.63 seconds.
- ParaDev PIHC3 Entity migration acceptance: one passed, one warning.
- Build-wrapper source/config separation contract plus Entity acceptance: two passed, one warning.
- Latest Entity-only plan: 135 modules, 184 planned artifacts, zero diagnostics/errors, unblocked.
- Full clean game-mod build and localization postprocessing: passed.
- Black and Flake8 across all ten changed Python files: passed.
- Independent final review: no remaining P0-P2 findings.

Heaven-style scanning reports only the migration script's pre-existing `pathlib` and direct `yaml` usage; the new compiler, runtime loader, and test utilities add no such violations.

## Next boundary

After the Mac is unlocked, rerun the packaged Entity flow: refresh, observe the precise `4.25` mismatch, restore `4.0` through the GUI, apply, and confirm a green build. Then cut the nine generated PDX paths over to compiler ownership while leaving the 173 static assets with the aggregate, so record and assignment edits generate usable game-mod output instead of intentionally stopping at parity validation.

Public distribution still separately requires Developer ID signing, notarization, stapling, and clean-machine Gatekeeper testing.
