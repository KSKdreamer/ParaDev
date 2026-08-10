# PIHC3 Lazy Catalog Editor and Live GUI Audit

Date: 2026-07-19 00:24 SGT

## Outcome

ParaDev's ordinary PIHC3 module tabs now browse the canonical HeavenBase Catalog in bounded pages instead of eagerly loading and retaining an entire module family through `Project.browser`. The editor requests 100 lightweight rows, hydrates only the selected module, and appends the next page on demand. Diagram tabs retain their existing full-family path because their layouts still need the complete graph.

The change was exercised against the real 2,164 MiB PIHC3 Catalog through the native-web desktop bridge. Scripted Effects opened 100 of 8,279 modules, appended a second page to 200, searched an off-page internal ID, hydrated its real source, and preserved an unsaved source draft across search reset, paging, and a family switch. Ideas, Characters, and Focuses also opened and hydrated real PIHC3 data. No QA marker was written to disk.

This is an important scale and stability checkpoint, not the end of beginner-ready authoring. First-run Catalog preparation, Catalog synchronization after writes, and friendly localized entity titles remain release work.

## Editor Data Flow

The React service adapter now maps HeavenBase Catalog rows into the existing module editor model while retaining the SDK-owned module identity and provenance:

- ordinary family tabs request an unhydrated 100-row page;
- the selected row is requested separately with `include_data=true` and `limit=1`;
- **Load more** follows `next_offset` without replacing the current rows;
- the ID search is debounced for 180 ms and evaluated by SQLite;
- a controlled selection outside the current page is looked up and appended without loading intervening pages;
- local drafts are merged over Catalog rows and remain owned by project plus family;
- changing families no longer discards a dirty draft while the editor stays mounted;
- initial selection waits for hydration before rendering source fields;
- diagram surfaces continue to use the complete family snapshot.

The Catalog adapter validates hydrated payload identity, family, source-root, source slots, and metadata before exposing it as editable data. Malformed or cross-family payloads remain lightweight and produce a bounded editor error instead of being trusted. Source roots are inferred from the final `/modules/` path boundary, including Windows and UNC paths, and duplicate logical module rows retain their own source provenance.

## Async and Selection Hardening

Live GUI testing exposed a controlled-selection feedback defect: the workspace echoed the editor's current row back as an external selection, so a search that excluded that row immediately cleared itself. The editor now distinguishes selections it emitted from genuine incoming selection intent.

The Catalog lifecycle now assigns ownership to each request generation and each one-row lookup:

- stale page, search, reload, and hydration completions cannot mutate a newer generation;
- an old request finalizer cannot delete ownership of a newer request for the same target;
- an unresolved external selection suppresses an outbound `null` selection;
- local unsaved drafts do not trigger Catalog lookups or deselection;
- failed lookups remain failed until an explicit retry instead of entering an automatic loop;
- hydration errors are keyed by request and entity, so one row's failure does not bleed into another;
- pending debounce, page, and hydration work is ignored after unmount.

The dedicated lifecycle suite covers rapid controlled selection, old search generations, same-target stale finalizers, persistent failures, per-row errors, draft switching, unresolved external targets, and unmount settlement.

## Accessibility and Beginner-Facing Copy

The paged entity browser previously modeled rows as ARIA options while nesting selection checkboxes inside them, which is invalid interactive structure. It now uses a semantic list with a separate native row-activation button and native bulk-selection checkbox. Initial loading, an empty family, and a search with no results have distinct states; paging status and retry controls sit outside the list.

Catalog search currently supports the stable internal module ID, so its English and Chinese labels now say exactly that instead of promising name and path search. Friendly titles are shown when hydrated, but lightweight rows still expose technical IDs. A compact searchable title/localization projection remains necessary before the experience is suitable for someone who barely codes.

## Real PIHC3 Native-Web Acceptance

| Surface | Result |
| --- | --- |
| Scripted Effects | 100/8,279 loaded; selected source hydrated |
| Scripted Effects paging | 200/8,279 after one **Load more**; first page retained |
| Off-page ID search | `C04_ADD_SKY_STINGER_SUPPORT_179` found and hydrated |
| Draft preservation | `# PARADEV_QA_DRAFT` survived search reset, paging, Ideas switch, and return |
| Draft cleanup | **Discard** removed the in-memory QA edit; source file was not written |
| Ideas | 100/390 loaded; real source hydrated |
| Characters | 100/250 loaded; first hydrated title was `King Meowmeow` |
| Focuses | 28 loaded; selected Info surface exposed nine metadata text fields |
| Accessibility structure | semantic list, native row buttons, native checkboxes, truthful ID-search label |
| Browser console after clean reload | no new application errors |

The earlier hot-reload session recorded transient React hook-order errors while the hook structure was actively changing. A complete page reload after the final structure produced no new errors. Thumbnail requests produced expected cache misses followed by successful binary fetches and cache writes.

Native Tauri visual interaction is still blocked by the locked macOS session. This pass used the same React app and Python operations through the native-web bridge, so it validates the product flow and data contracts but not window chrome, native focus behavior, packaging, or Finder launch.

## Verification

| Gate | Result |
| --- | --- |
| Catalog adapter unit suite | 20 passed |
| Catalog lifecycle regression suite | 17 passed |
| Complete desktop Vitest gate | 832 passed across 54 files |
| TypeScript check and production Vite build | passed; large-chunk warnings remain |
| Repository lint gate | passed |
| Complete Tauri Rust test gate | 40 passed across 3 suites |
| Focused HeavenBase/desktop/native-web/Tauri Python gate | 121 passed in 14m 07s |
| Git whitespace check | passed |
| Real PIHC3 browser acceptance | passed through native-web bridge |

## Review Findings and Remaining Risks

Independent async review found no remaining priority-zero through priority-two defect in request ownership or controlled-selection intent after the lifecycle fixes. Adapter and accessibility findings from the same review cycle were addressed in this checkpoint.

The open product risks are:

1. A missing first-run Catalog still yields a generic error. The next contained slice will add a read-only structured Catalog status, show a manual **Prepare project index** action only for `catalog.missing`, warn that real PIHC3 preparation takes about 14 minutes and 2.1 GiB, and never start it automatically.
2. Module writes do not yet update the canonical Catalog. A frontend-only overlay is unsafe because it breaks restart behavior, paging counts, search, CLI parity, and language-server consumers. Mutation must atomically replace backend-owned projections and handle content-hash ID changes.
3. Lightweight rows lack compact friendly/localized labels, and server search supports only internal IDs. Beginners should be able to find `King Meowmeow` or a localized focus name without knowing its module ID.
4. Page counts can be cosmetically inflated when an off-page selected row or a local draft is appended to a filtered page. The server total remains authoritative, but the UI needs an explicit distinction between matching rows and pinned/discovered rows.
5. The production frontend still has large bundle warnings, and packaged-sidecar relocation/Finder-launch acceptance remains outstanding.

## Next

- Commit and push this bounded editor checkpoint.
- Add structured missing/present/incomplete/unreadable Catalog status and an explicit first-run preparation flow.
- Design backend-owned Catalog mutation around atomic entity-projection replacement rather than frontend overlays.
- Add compact localized display/search projections for novice browsing.
- Resume native Tauri accessibility and packaging acceptance when the macOS session is unlocked.
