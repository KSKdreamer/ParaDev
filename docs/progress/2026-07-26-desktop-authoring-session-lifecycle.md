# Desktop Authoring Session Lifecycle

Date: 2026-07-26 SGT

## Outcome

ParaDev's module and diagram editors now behave as views over one
application-owned authoring session instead of owning disposable copies of
draft state. A PIHC3 author can change rails, projects, tabs, or editor surfaces
without silently losing entity drafts, inline or batch creation state, diagram
history, or image resources. Writes are serialized across sibling views, and
browser or native app exit warns while work is dirty or in progress.

This slice changes the desktop authoring lifecycle and the SDK, desktop, Tauri,
and REST source-draft mutation boundary. Compiler planning and publication
remain unchanged. The previously verified PIHC3 clean, cached, and targeted
publications remain the current compiler acceptance checkpoint.

## Session Ownership And Identity

`ModuleEditorSessionStore` is owned by `App` and keyed by canonical project
root plus module family. It retains:

- dirty entity and source-replacement drafts;
- inline creation and batch-creation recovery state;
- diagram documents, checkpoints, viewport state, and source fingerprints;
- app-owned blob resources; and
- the shared family-session busy count.

The canonical root is part of the identity, so two checkouts with the same
project id cannot share drafts. Workspace editor keys, browser payloads, and
template payloads all use the same root/project scope checks. A stale
same-family browser response cannot hydrate the active checkout.

Empty string and `undefined` form fields remain pristine, while meaningful
`false` and `0` values create drafts. Diagram histories are bounded to 100
checkpoints.

## Tabs, Resources, And Navigation

Workspace tab entries cache their last known descriptor. This keeps a dirty or
busy family reachable even when a refreshed browser payload temporarily or
permanently stops listing it.

Clean orphan tabs use cleanup-first removal: the store disposes their retained
session and owned resources before the tab disappears. If disposal fails, the
tab remains open and a localized retry dialog is shown. Manual clean-tab close
uses the same order. This makes resource ownership explicit and avoids both
silent draft loss and unreachable blob URLs.

App navigation and close guards derive their counts from the same store. The
browser `beforeunload` handler blocks only while the shared session snapshot is
dirty or busy. Tauri menu quit, keyboard quit, and window-close events use
ParaDev's localized dialog.

The native bridge reserves an inactive lease for a renderer
session/generation, registers the frontend exit listener, and only then
activates the lease. Stale activation or release cannot affect the current
lease. Each pending exit request carries a one-use nonce bound to that lease;
confirmation requires acknowledgement of the matching lease and nonce.
Acknowledgement starts a renderer heartbeat while the dialog owns the request.
After five seconds without liveness, an acknowledged request expires without
retiring the lease. The existing error dialog can atomically rotate it to a
fresh acknowledged nonce before retrying confirmation, while a later native
close receives a fresh unacknowledged nonce. A lost retry response is
idempotently recoverable through a bounded lineage of up to eight request
nonces. Only a fresh request that also remains unacknowledged retires the dead
frontend lease. Page reload and window destruction retire the renderer
session, ordinary bridge invocations are bounded, registration retries,
asynchronous disposers are observed, and teardown is bounded.

Native confirmation has two explicit phases. ParaDev has five seconds to
acquire both lifecycle locks, verify the exact acknowledged nonce, and obtain
the renderer's begin signal; this phase performs no destructive cleanup and
can fail safely. Once cleanup begins, the request is pinned: cancel, release,
liveness expiry, renderer replacement, retry, and a second confirmation cannot
supersede it. The close dialog remains modal and the application shell,
navigation, editors, build controls, and chat remain inert until cleanup
definitively fails or the process exits. Successful cleanup atomically consumes
the pinned nonce, and the native worker owns process exit even if the
renderer-side invocation disappears. Cleanup failure reopens build admission,
refreshes the acknowledged request for retry, and reports the error only after
native cleanup has stopped.

## Mutation And Conflict Safety

Busy ownership is shared per project-family session. Starting an entity,
source, asset, create, or diagram write locks both module and diagram views;
their roots expose busy state and become inert. A second overlapping Apply is
rejected.

Successful backend mutations reconcile the app-owned session before waiting
for browser refresh. If the initiating component unmounts while a request is in
flight, the result still clears the applied drafts and refreshes project state.
For a multi-phase operation, an earlier successful phase remains committed
locally if a later phase fails; only the remaining unapplied draft is retained.

Modified and removal-draft entities that disappear from the next backend
payload become explicit `missing` source conflicts. They remain visible and
recoverable, but Apply and source replacement are blocked. If the row
reappears, normal merge clears the conflict automatically. Newly created local
drafts are not misclassified as missing backend rows. Only complete,
unfiltered family payloads are authoritative for absence; paged and searched
Catalog results cannot fabricate a missing conflict.

The first edit to an existing source retains its size and nanosecond
modification time. Text edits, existing replacements, and guarded removals send
that revision through TypeScript, Tauri, the desktop facade, REST, and the SDK.
New image and asset targets send `expected_absent=true`. Unknown nested fields
are rejected instead of silently disabling a guard. The canonical source-text
read returns text, size, and modification time from one descriptor-stable
snapshot, and a source drafted again after partial Apply captures the refreshed
revision.

One source-draft request is a bounded filesystem transaction. It supports at
most 256 targets and 256 MiB of streamed recovery backups. Guarded installs and
removals use same-directory quarantine and no-replace links, close the final
name-binding race, and preserve a concurrently appearing file. If a later
target fails, rollback restores earlier targets only while they still match
ParaDev's exact inode, size, modification time, and content digest. A newer
external edit is preserved and incomplete recovery reports the retained path.
Every successful request attempts Catalog projection synchronization for each
touched canonical module and reports the aggregate status.

Diagram sessions record a fingerprint of their base browser document. Clean
history rebases automatically after backend refresh while preserving only the
viewport. Dirty history remains available when its base changes, but Apply is
blocked with a localized source-conflict message so retained history cannot
overwrite external edits.

Failed or unverified Catalog synchronization is now retained in the
application-owned family session. It survives module/diagram remounts, blocks a
queued identity change, keeps repair available, and cannot be cleared by a
later stale success. Source and diagram results are committed before owned
image/blob cleanup, so cleanup failure cannot undo authoritative mutation
reconciliation.

## Verification

| Gate | Result |
| --- | --- |
| Desktop Vitest | Passed: 69 files, 1,225 tests |
| Desktop production build | Passed: TypeScript and Vite, 3,299 modules |
| Rust formatting | Passed |
| Native Rust tests | Passed: 86 tests across three suites |
| Repository-wide Python gate | Passed: 2,006 tests; 34 intentional environment-dependent skips |
| Fresh strict PIHC3 dry plan | Passed: 18,107 modules, 78 collections, 37,500 planned artifacts, zero diagnostics |
| Git diff whitespace check | Passed |

### Current re-verification (2026-08-10)

- Focused renderer session/exit/conflict gate: 225 tests passed across eight
  files.
- SDK project and desktop mutation gate: 487 tests passed.
- Complete desktop suite: 93 files and 1,510 tests passed.
- Complete Tauri suite: 96 tests passed; Rust formatting remained clean.
- Production TypeScript/Vite build passed.

The earlier compiler and repository-wide Python checkpoint is recorded in
[`2026-07-26-pihc3-partial-publication-entity.md`](2026-07-26-pihc3-partial-publication-entity.md):
PIHC3 clean, cached, and targeted builds produced the same 37,501-file runtime
tree, and the repository-wide Python gate passed 1,985 tests with 34 intentional
skips.

## Known Boundaries And Next Work

- Authoring sessions are process-local. They protect ordinary navigation,
  unmount, and graceful exit, but do not yet provide crash or process-restart
  draft recovery.
- Session comparison and cloning still traverse structured draft payloads,
  including image data. The diagram history cap bounds one growth path, but
  larger drafts should move to a more incremental or persistent representation.
- If the native bridge is permanently unavailable before a listener can
  activate, normal quit deliberately remains fail-closed to protect possible
  dirty work; operating-system force-quit is the escape hatch.
- Missing-source conflicts currently require source restoration or explicit
  draft discard; there is no merge assistant yet.
- A non-linkable concurrent target such as a directory is never destroyed; if
  it cannot be restored to the canonical name without overwriting something
  newer, ParaDev reports the retained same-directory quarantine path for manual
  recovery.
- The next PIHC3 modularization candidate is the technology family, where the
  audited legacy-to-native mapping is complete. MIO authoring remains an
  optional follow-up; its first safe GUI increment should be a read-only native
  tree before any writeback contract is added.
