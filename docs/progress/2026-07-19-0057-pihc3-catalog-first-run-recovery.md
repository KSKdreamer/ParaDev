# PIHC3 Catalog First-Run Recovery

Date: 2026-07-19 00:57 SGT

## Outcome

ParaDev now gives a novice an explicit recovery path when a project's local HeavenBase Catalog has not been prepared. An ordinary module tab still begins with the same bounded 100-row query. Only after that query fails does the UI ask the Python storage owner for a structured status; only the exact `catalog.missing` code exposes **Prepare project index**. No build or refresh starts automatically.

The recovery was exercised end to end through the real native-web GUI against a disposable copy of the minimal HOI4 project. Before the click, Catalog search was disabled, module creation remained available, and the UI explained in Chinese that PIHC3 preparation takes about 14 minutes, uses about 2.1 GiB, cannot currently be cancelled, and requires ParaDev to remain open. After the explicit click, the action became an indeterminate disabled busy state. The bridge built a 17.4 MiB Catalog, repeated one lightweight page query, hydrated the selected focus, and opened its real source editor. The final status was `present / catalog.present`, and the browser console contained no warnings or errors.

The full PIHC3 Catalog was already present and validated in the preceding checkpoint, so this block did not spend another 14 minutes rebuilding its 2.1 GiB database.

## Structured Status Contract

The Python owner now exposes both `paradev.hb.catalog_status(project, database=None)` and `Project.catalog_status(database=None)` with schema `paradev.hb.catalog-status.v1`.

| Status | Code | Meaning |
| --- | --- | --- |
| `present` | `catalog.present` | The main database path is a readable regular file. This is a filesystem status, not a full integrity claim. |
| `missing` | `catalog.missing` | The main database and its WAL/SHM sidecars are all absent. |
| `incomplete` | `catalog.incomplete` | The path is a directory or broken symlink, or a sidecar exists without the main database. |
| `unreadable` | `catalog.unreadable` | A stat/readability check failed or the file has no readable permission bits. |

Status inspection is intentionally cheap and read-only. It does not create `.paradev`, open SQLite, acquire a refresh lock, invoke `Project.build`, or run an integrity scan over a multi-gigabyte PIHC3 database. The original query remains authoritative for schema, locking, and corruption failures; those states retain the generic query error and **Retry** action instead of being misclassified as first-run setup.

## Transport and Runtime Validation

The five-field payload is carried through:

- desktop backend operation `project_catalog_status`;
- Tauri command `paradev_project_catalog_status`;
- native-web `GET /projects/catalog`;
- TypeScript `loadProjectCatalogStatus()`.

The TypeScript boundary accepts only the v1 schema, non-empty project/database strings, the exact five keys, and one of the four valid status/code pairs. A malformed payload is rejected before React can interpret it. The OpenAPI seed, REST API inventory, Catalog API inventory, generated references, and GUI-to-Python interface documentation include the new GET route.

## React Recovery Lifecycle

The Catalog hook keeps status and refresh work inside the same project/family/search/reload generation as the failed query:

- a stale status completion cannot expose recovery for a newer query;
- a stale refresh completion cannot reload a different editor scope;
- unmounting prevents status or refresh settlement from changing React state;
- an explicit refresh failure stays visible and never retries itself;
- a successful refresh starts exactly one new 100-row query and normal one-row hydration;
- diagram tabs do not query status or refresh the Catalog;
- missing-Catalog search is disabled to avoid repeated failures;
- the **New** action and locally created draft rows remain available without an index;
- there is no fake Cancel action because the synchronous bridge cannot interrupt refresh yet.

The busy label has a dedicated live status announcement. Its rotation is disabled under `prefers-reduced-motion`; visible text still communicates progress.

## Live Disposable-Project Acceptance

| Step | Result |
| --- | --- |
| Initial focus page query | expected HTTP 400 because no Catalog existed |
| Status classification | HTTP 200; `missing / catalog.missing` |
| Missing-state GUI | disabled internal-ID search; **New** enabled; warning and explicit prepare action visible |
| Before explicit click | zero refresh requests |
| Preparation | HTTP 200; indeterminate disabled action; no Cancel control |
| Persisted database | 17.4 MiB in the disposable project's `.paradev/.cache/hb/catalog.sqlite` |
| Follow-up page | HTTP 200; one focus row |
| Selected hydration | HTTP 200; real definition/localization sources opened |
| Final status | HTTP 200; `present / catalog.present` |
| Browser console | no warnings or errors |

Live testing found one additional state bug: when both the selected entity ID and hydration ID were empty, the details pane treated the two empty strings as a match and showed **Loading editor sources…** forever. Hydration loading now requires a non-empty selected ID, so the recovery screen correctly shows **Select an entity** until a row exists.

## Verification

| Gate | Result |
| --- | --- |
| Complete fast Python gate | 1,369 passed; 2 warnings |
| Core status classifications and side-effect checks | 8 passed |
| Focused status plus desktop/native-web/Tauri Python bridge gate | 15 passed; 121 deselected |
| Complete desktop Vitest gate | 843 passed across 54 files |
| Recovery/list lifecycle target | 34 passed |
| TypeScript service boundary | 52 passed |
| TypeScript check and production Vite build | passed; existing large-chunk warnings remain |
| Complete Tauri Rust gate | 41 passed across 3 suites |
| Focused bridge suites | 87 passed |
| Generated API-table/CLI/selection contracts | 34 passed; 146 deselected after GET-route synchronization |
| Repository lint and whitespace gates | passed |
| Native-web disposable-project recovery | passed |

The additional `--full` diagnostic reached 1,368 passes and exposed two pre-existing validation issues: all 314 explicitly slow PIHC3 migration contracts require the gitignored `projects/PIHC3/` fixture that is absent from this linked worktree, and one frontend-reference test contained two stale table-column snapshots. The snapshots were corrected and their CLI/manual parity checks pass (2 passed). A one-test PIHC3 probe confirmed the worktree failure occurs before assertions while opening the missing `projects/PIHC3/paradev.yaml`; the Catalog recovery diff does not touch that suite or fixture.

## Remaining Release Work

1. Catalog refresh is still one synchronous operation with no phase progress, cancellation, or restartable job status. The UI is honest about that limitation, but a production-quality background job should expose start/status/interrupt semantics.
2. Module create, rename, remove, and source writes still leave the canonical Catalog stale. The next mutation slice should atomically replace the backend-owned `hoi4-module` projection and report partial filesystem/Catalog success explicitly.
3. Lightweight rows still lack friendly localized search data; internal-ID-only search is not beginner-friendly.
4. Pinned/off-page rows and local drafts can make the displayed loaded count exceed the server's filtered page count.
5. Native Tauri visual acceptance remains blocked by the locked macOS session, and relocated packaged-sidecar/Finder-launch acceptance is still outstanding.

## Next

- Commit and push this first-run recovery checkpoint after final contract gates.
- Implement atomic module Catalog projection synchronization for create, rename, and real module removal.
- Add compact localized title/search projection for novice browsing.
- Resume native Tauri and packaged-app testing when the macOS session is available.
