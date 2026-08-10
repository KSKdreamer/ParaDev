# PIHC3 Registry-owned Localization Editing

Date: 2026-08-02

## Outcome

ParaDev now projects existing localization sources through the same open
Registry authoring seam as JSON and PDX sources. A `.loc` file is eligible only
when the selected project Entity declares a matching `loc` resource slot;
there is no PIHC3 family switch in the SDK or desktop.

The localization loader and Guided projector share one lossless parser for
PIHC3's bracket-section and language-header/inline forms. Each editable value
has a guarded `replace-loc-text` patch containing its canonical language, key,
duplicate occurrence, exact UTF-16 span, expected source text, newline style,
and source-length revision. Python remains write-authoritative: it validates
all replacements, applies non-overlapping spans, reparses the result, and
verifies that only the requested semantic entries changed. The desktop uses a
buffered multiline control and the same exact patch for immediate preview;
Apply still reprojects and plans through the SDK.

The form is bounded to 96 controls. All 3,968 current PIHC3 `.loc` files across
46 module families produce a valid Guided form. Of those, 3,848 are
complete and 120 explicitly report partial coverage instead of silently
dropping values. This closes the former localization-only exception for
`equipment_module_category` without adding a scripted definition file.

The companion asset audit confirmed that all image/icon authoring continues
to come from Entity-owned `copy` slots and the generic image/asset transaction.
The UI and Text Icon regression assertions now reflect their more precise
resource contracts: editable `.gui`/`.gfx` documents are PDX slots, while
their DDS destinations use separately named copy slots with safe authoring
paths. No aggregate sidecar family was restored.

The Info panel now consumes a bounded Registry-owned localization workspace
instead of parsing module text in React. `Project.localization_workspace()`
projects all active `loc` slots into one cross-language table, and
`Project.plan_localization_update()` plans closed `set`, `add`, `rename`, and
`remove` operations against unsaved drafts with revision-guarded source edits.
The native desktop bridge and Tauri commands expose the same two operations.
The former TypeScript localization parser, key resolver, and structural text
mutators have been deleted. Multiline cell edits are buffered until blur, and
localized title changes no longer also rewrite hidden metadata.

The same boundary is now part of the formal operation catalog. Read-only
`module.localization.workspace` and `module.localization.plan` bind directly
to the two `Project` methods, POST REST resources, and HeavenBase-backed MCP
tools. REST and MCP derive their draft, limit, and closed operation schemas
from one SDK-owned schema module; the planner's guarded edits still apply only
through the existing `project.draft_apply` transaction. These low-level agent
operations remain outside the generic human action palette because the Info
panel already provides the dedicated non-programmer workflow.

The desktop regression fixture now models two independent localization files.
It proves that an error from the first planner request remains actionable, a
second request succeeds without remounting the editor, and only the
Registry-owning source draft receives the recovered edit.

## Physical cleanup

- Exact live-tree scan: 71 module-family roots, 14,618 module folders, and 90
  collection folders. Every direct source folder uses
  `<object id> - <preferred-language title>`; no malformed or mislabeled folder
  remains.
- Zero `_component`, `_asset_component`, or inactive directories exist under
  `projects/PIHC3/src`. There is one author-visible `inactive: true` bookmark,
  which is correctly omitted from builds without a separate source tree.
- No directory is named `legacy`. Four live modules/collections contain
  `LEGACY` in their gameplay object id; the compiler consumes these as current
  HoI4 content contracts, not migration sources.
- The 113-test cleanup, Registry-extension, localization, focus-tree,
  technology, intelligence-agency, and MIO gate passed.
- All source remains inside the semantic module and all extension ownership
  remains project-local under `projects/PIHC3/extensions`.

## Verification

- Maintained Python fast gate: 2,309 passed, nine native-Windows skips, two
  warnings. An additional all-markers diagnostic reached 2,455 passes before
  exposing four stale slot-kind/source-form expectations; all four corrected
  assertions then passed together.
- Formal localization/architecture/CLI/MCP/native focused Python gate: 311
  passed. The smaller core, REST, MCP, and multi-file localization suite passed
  seven tests independently.
- Desktop: 90 files and 1,462 tests passed, including the multi-file
  planner-error recovery lifecycle.
- Rust/Tauri: 95 tests passed across three suites.
- TypeScript and Vite production build passed; the existing large-chunk
  advisory remains.
- Black/Flake and Rust formatting gates passed.
- Clean/full and cached/full PIHC3 builds: 14,617 modules, 106 collections,
  35,131 artifacts, zero diagnostics/errors.
- Focus-family partial: 738 modules, 28 collections, 12,499 artifacts, zero
  diagnostics/errors.
- Focus-module partial (`FOCUS_C12_SHADOWS_OF_THE_PAST`): 129 modules, one
  collection, 11,253 artifacts, zero diagnostics/errors. The owning focus-tree
  closure is intentional; unrelated non-localization families were not built.

All four builds used project-only publication; no launcher descriptor was
read or changed.

## Remaining boundary

The Registry/SDK/REST/MCP/desktop localization boundary is complete for
workspace projection, closed planning, guarded application, and multi-file
error recovery. Broader GUI interaction coverage for add, rename, and remove
can grow incrementally from the same planner contract. The next cleanup slice
returns to minimizing hidden routed metadata that can be safely derived from
Entity definitions and canonical project structure.
