# PIHC3 Atomic Catalog Mutations

Date: 2026-07-19 04:55 SGT

## Outcome

ParaDev now keeps canonical module-folder mutations and the persisted HeavenBase `hoi4-module` projection consistent across module create, rename, and remove. The Python SDK remains authoritative for the source operation and reports Catalog synchronization as an independent, typed result. The desktop accepts a validated source success even when that secondary result fails or is missing, preserves the source-backed local row, pauses Catalog reads for that editor scope, and offers an explicit repair action instead of inviting the novice to repeat an irreversible operation.

This block also replaces path-based scaffold, rename, and removal writes with lexical, descriptor-anchored, no-follow operations. Multi-file scaffold creation and forced replacement now stage the full rendered set before installation, retain originals until every install and final identity check succeeds, and roll back ordinary failures. If rollback itself cannot restore an original, ParaDev preserves the transaction as recovery data and returns its path instead of deleting the last copy.

The mutation work is a major reliability checkpoint, not a packaging-ready declaration. Native Tauri visual acceptance remains blocked by the locked macOS session, the linked worktree still lacks the gitignored PIHC3 project fixture, and Windows does not yet provide an implemented safe equivalent for the required descriptor operations.

## Source and Catalog Transaction Contract

Written create, rename, and remove payloads use the private closed schema `paradev.hb.catalog-mutation.v1`:

| Status | Code | Source result | Desktop behavior |
| --- | --- | --- | --- |
| `applied` | `catalog.mutation.applied` | successful | reload Catalog once when the scope was already clean |
| `not_configured` | `catalog.mutation.not_configured` | successful | preserve the source-backed local view and offer index repair |
| `failed` | `catalog.mutation.failed` | successful | preserve the source-backed local view, latch Catalog bypass, and show repair |
| adapter-only `unverified` | `catalog.mutation.unverified` | validated successful response with missing/malformed secondary result | preserve success, latch bypass, and show repair |

Dry runs, blocked operations, and non-written removals omit the result. Create nests it in the scaffold plan; rename and remove return it at the response top level. A source success is never converted into a retryable source failure merely because the derived projection could not be verified.

Canonical module create, rename, and remove acquire the same per-project writer lock used by initial Catalog writes and full refresh. The source change and one mixed delete/upsert provider call remain inside that lock, so a refresh snapshot cannot overtake a newer delta. The projection planner constructs detached HeavenBase objects without polluting global/default/live tracking, then applies the physical table metadata to the live backend. SQLite delete/upsert work executes in one provider transaction.

Cleanup after a committed provider write is non-authoritative: workspace-drop or engine-disposal failures are logged without changing an already-applied result. Refresh-lock rollback and close failures are independently logged, the connection is always closed when possible, and cleanup cannot mask either a completed result or the active primary exception.

This is operation-order atomicity for ordinary runtime execution, not process-crash atomicity across the filesystem and SQLite. A durable mutation-intent journal and startup reconciliation remain future work.

## Filesystem Safety and Recovery

Module authoring targets remain lexical from project configuration through build views and scaffold planning. Create, rename, and removal reject symlinked or unreadable path components and use directory descriptors plus no-follow opens for the actual mutation. Concurrent family/module swaps are detected by inode identity checks and rolled back against the already-open trusted directories.

Scaffold writes now use this sequence:

1. render and validate every target without following links;
2. stage every file below `source_root/.paradev/module-transactions`;
3. open or create all destination parents through anchored descriptors and prevalidate every target;
4. move existing forced-replacement targets into per-transaction backups;
5. install staged files and recheck the canonical family/module identities;
6. remove backups only after complete success, or restore them in reverse order after failure.

A newly created module is removed when staging, descriptor opening, installation, or identity validation fails. Existing modules retain their original files after ordinary staging/install failures. A double failure during install and backup restoration returns `scaffold.rollback_incomplete` with a structured `recovery_path`, logs that retained transaction, and deliberately skips transaction cleanup so the original remains recoverable.

Removal uses a complementary quarantine protocol. The canonical module folder is atomically moved to `source_root/.paradev/module-trash`, the Catalog delta is applied, and quarantine cleanup runs last. A cleanup failure does not resurrect the canonical path or misreport source failure; it returns `removed=true` plus typed `paradev.module.remove-cleanup.v1` pending cleanup metadata and a matching warning. If cleanup actually completed before raising, descriptor-relative inspection recognizes that absence and suppresses a false pending warning.

## Desktop Mutation Lifecycle

The Tauri bridge now exposes canonical module removal, while native-web reuses the generated `module.remove` contract and existing write-enabled REST route. The TypeScript boundary validates request authority and the full parent/source identity before interpreting the secondary Catalog result, including:

- exact write/force outcomes and canonical draft IDs;
- scalar template values, typed scaffold file actions, and blocked plans;
- normalized relative, external, Windows-drive, and UNC source roots;
- canonical module roots and rename old/new root pairing;
- successful-removal gating and exact pending-cleanup path/diagnostic correspondence.

The React editor removes whole canonical folders through `removeModule`; it no longer approximates that operation by deleting only known files. Duplicate module identities block folder rename/removal but still allow source-only edits. Permanent deletion copy names the exact folder, known file count, unindexed-file risk, and irreversibility.

Catalog bypass is per editor scope and dirty state is latched. Once a failed or unverified delta occurs, a later successful delta cannot silently clear the state or reload stale rows. Create, rename, and whole-folder removal remain disabled until explicit repair, while source-only editing stays available. Successful clean-scope mutations reload exactly once.

## Verification

| Gate | Result |
| --- | --- |
| Complete fast Python gate | 1,425 passed; 2 warnings |
| Complete desktop Vitest gate | 900 passed across 54 files |
| TypeScript service boundary | 92 passed |
| Desktop production build | passed; existing large-chunk advisory remains |
| Complete Tauri Rust gate | 42 passed across 3 suites |
| Desktop/native-web/Tauri Python bridge suites | 96 passed; 1 warning |
| Complete project SDK module | 218 passed |
| Scaffold/create/template focus after transaction additions | 25 passed; 193 deselected |
| Module removal focus | 12 passed |
| Catalog removal plus deterministic rename/remove ordering | 2 passed |
| Catalog lock cleanup/non-masking outcomes | 5 passed; 63 deselected |
| Architecture API focus | 39 passed; 52 deselected |
| Repository lint and whitespace gates | passed |

Three independent reviews covered GUI mutation state, TypeScript trust boundaries, and Python storage ordering. Their P1 findings were fixed with regressions: dirty-state relatching, malformed/missing Catalog-result handling, blocked scaffold actions, UNC normalization, multi-file force-update staging/rollback, cleanup-safe refresh locks, and preservation of the only original backup after a double I/O failure. The final storage re-review found no remaining P0/P1 issue in the implemented ordinary-failure paths.

## Live Acceptance Limits

- No native Tauri GUI session was available in this block because the macOS desktop remained locked. Prior native-web Catalog recovery acceptance still passes, but it is not a substitute for packaged native acceptance.
- The linked worktree does not contain the gitignored `projects/PIHC3/` fixture, so this block could not run the real PIHC3 source tree through create/rename/remove interactions or a full mod compile.
- The already-validated PIHC3 Catalog was not rebuilt again; the mutation work used deterministic disposable-project and provider tests.
- The existing Vite chunk-size advisory remains and should be addressed before release packaging.

## Remaining Release Work

1. Add a durable mutation-intent journal and startup reconciliation for process death between filesystem and Catalog commits.
2. Implement a safe Windows mutation backend instead of the current fail-closed behavior, then run packaged Windows acceptance.
3. Extend Catalog delta parity to direct source-file writes/removals and other entity mutation surfaces.
4. Restore the PIHC3 fixture in this worktree and run a complete real-project entity inventory, GUI edit/create/rename/remove matrix, and actual mod compile.
5. Resume native Tauri, Finder-launch, relocated-sidecar, signing, and packaged-app acceptance after the macOS session is available.
6. Continue novice UX work: friendly localized Catalog search, progress/cancellation for long index repair, and clearer cleanup/recovery assistance.

## Next

- Commit and push this atomic Catalog mutation checkpoint to the existing draft PR.
- Restore or link the PIHC3 fixture and verify every migrated entity family against the real compiler.
- Implement source-file mutation deltas and crash reconciliation before declaring the editor stable for non-coders.
