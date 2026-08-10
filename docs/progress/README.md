# ParaDev Progress Notes

Status: active log folder

Date: 2026-06-06

Purpose: store durable five-hour progress summaries for long-running agent work.

These entries are historical evidence, not current architecture authority. Older
host and tool names remain only where needed to identify an immutable checkpoint;
the current GUI authority is the Python wheel, loopback service, and macOS system
WebView described in the architecture and GUI specifications.

## Current Wrap-Up

- [2026-08-10 Tauri-free System-WebView Release Checkpoint](2026-08-10-1535-tauri-free-system-webview-release.md) removes the Rust/sidecar/installer stack, proves the Python-wheel WKWebView app lifecycle, restores clean-checkout PIHC3 reproducibility, and records exact installed-wheel plus rebuilt-sdist publication parity.
- [2026-08-10 Project API Service Boundary](2026-08-10-1413-project-api-service-boundary.md) removes Desktop-to-REST ownership, gives Desktop and FastAPI one transport-neutral project service, preserves lazy facade compatibility, and proves the rebuilt wheel through installed-App and exact four-mode PIHC3 smokes.
- [2026-08-10 PIHC3 Guided References And Owned App Host](2026-08-10-1305-pihc3-guided-references-and-owned-app-host.md) adds Registry-owned module/collection suggestions across ordinary, batch, diagram, and AI authoring; gives the installed app a dynamic nonce-authenticated server; and proves final installed-App lifecycle plus exact four-mode PIHC3 wheel parity.
- [2026-08-10 PIHC3 Safe Source Inventory](2026-08-10-1133-pihc3-safe-source-inventory.md) adds a checksummed per-file digest inventory with trusted-filesystem metadata reuse, race-safe changed-file hashing, adversarial corruption/symlink/topology tests, and an apples-to-apples pre-slice wheel performance comparison.
- [2026-08-10 Unsigned System-WebView PIHC3 Release Checkpoint](2026-08-10-1037-unsigned-system-webview-pihc3-release.md) adds first-run project-package import and collection parity to the default wheel-hosted app, proves real installed-App lifecycle plus final four-mode PIHC3 output parity, and records the seven canonical-HoI4 thin overlays.
- [2026-08-10 PIHC3 Canonical Manifest Reuse And Installed App Host](2026-08-10-0952-pihc3-canonical-manifest-reuse.md) adds checksum-validated canonical-manifest receipts, proves fixed-root determinism and exact installed-wheel four-mode PIHC3 parity, and absorbs the packaged React plus macOS system-WebView application host.
- [2026-08-10 PIHC3 Exact-copy Publication](2026-08-10-0859-pihc3-exact-copy-publication.md) adds raw-byte retained-output reuse with bounded fail-safe fallback, cuts the installed cached whole build from 38.7 to 28.5 seconds, and preserves exact 33,437-file parity across clean/cached/family/module modes.
- [2026-08-10 PIHC3 Validated Artifact-plan Cache](2026-08-10-0820-pihc3-validated-artifact-plan-cache.md) adds checksum-safe finalized-plan reuse with project-owned external-state keys, cuts the installed MIO module loop to 17.8 seconds, and proves exact 33,437-file output parity across clean/cached/family/module builds.
- [2026-08-10 PIHC3 Cached Build Throughput](2026-08-10-0737-pihc3-cached-build-throughput.md) adds exact-byte unchanged publication, compact manifests, bounded parallel source discovery, and a typed combined family compiler hook; it records a 46.0-to-26.3-second warm module-partial improvement plus clean installed-wheel and full-suite gates.
- [2026-08-10 Wheel GUI Release Gate](2026-08-10-0640-wheel-gui-release-gate.md) installs the exact wheel in a disposable runtime, launches its same-origin GUI host without checkout or `uv` access, and records checksum-bound clean/cached/family/module PIHC3 builds plus release-CI coverage.
- [2026-08-10 Installed PIHC3 GUI Builds](2026-08-10-0600-installed-pihc3-gui-builds.md) removes the installed app's `uv`/checkout dependency, fixes collection-backed Focus scopes, records rendered Focus/Technology/MIO proof plus whole/family/module builds, and adds an exact-inventory wheel builder.
- [2026-08-10 PIHC3 HeavenBase Catalog Batch Throughput](2026-08-10-0530-pihc3-heavenbase-catalog-batch-throughput.md) removes repeated owner-side configuration work, adds an explicit fresh-Catalog writer mode, and records exact 20,000-row plus 765,033-row PIHC3 parity with a 70.0% cold end-to-end improvement.
- [2026-08-10 PIHC3 Typed HeavenBase Catalog](2026-08-10-0338-pihc3-typed-heavenbase-catalog.md) replaces repeated PDX-symbol JSON with one registered typed Entity, closes partial-initial-write reads, preserves legacy query/completion payloads, and records 24.43% synthetic database reduction plus cold 765,033-row PIHC3 proof.
- [2026-08-10 PIHC3 Built-in Family Overlays](2026-08-10-0234-pihc3-builtin-family-overlays.md) removes the redundant Idea/Event Entity contributions, retains thin PIHC3 compiler overlays, and records cold HeavenBase Catalog plus exact build-output parity.
- [2026-08-10 Desktop Build Lifecycle](2026-08-10-0204-desktop-build-lifecycle.md) records app-shell-owned build presentation, native-process recovery and shutdown, project-scoped concurrency, cross-process publication locking, and the complete then-current desktop lifecycle gates.
- [2026-08-10 PIHC3 Fast Cached Publication](2026-08-10-0155-pihc3-fast-cached-publication.md) records single-projection crash-safe ledger checkpoints, unchanged-manifest suppression, compact desktop results, profiled staging-path cleanup, exact four-mode PIHC3 parity, and the cached improvement from 66.33 to 52.89 seconds.
- [2026-08-10 PIHC3 Cached Publication](2026-08-10-0110-pihc3-cached-publication.md) records bounded batch staging, percent-coalesced desktop progress, exact full/cached/partial output parity, and the published-wheel cached-build improvement from 81.28 to 66.33 seconds.
- [2026-08-10 HeavenBase 0.1.2.2 And PIHC3 Stability Closure](2026-08-10-0020-heavenbase-0122-pihc3-stability.md) records the published-wheel migration, exact full/cached/partial PIHC3 parity, zero-retired-folder re-audit, bounded Guided search, cache fault recovery, and native FastMCP 4 structured results.
- [2026-08-09 PIHC3 Source-first Portrait Authoring](2026-08-09-2246-pihc3-source-first-portrait-authoring.md) removes the last template-generated visible metadata file, replaces it with a real Portrait source skeleton, resolves dynamic draft source names generically, and records all-54-template plus live GUI proof.
- [2026-08-09 PIHC3 Project-scoped MIO Editor](2026-08-09-2217-pihc3-project-scoped-mio-editor.md) moves initial diagram scope into the Registry capability contract, fixes the real support-source empty-canvas bug, records rendered 30-organization PIHC3 proof, and re-audits the minimal hidden collection metadata.
- [2026-08-09 PIHC3 Build Lifecycle And Layout Verification](2026-08-09-2159-pihc3-build-lifecycle-and-layout-verification.md) re-verifies the exact zero-component/legacy/inactive source tree, proves all four GUI build scopes, adds artifact-ledger-safe clean/full recovery, fixes Focus Registry routing and scoped inventory merging, and records the 2,405-test Python plus 1,506-test desktop gates.
- [2026-08-09 PIHC3 Large-family Progressive Disclosure](2026-08-09-2045-pihc3-large-family-disclosure.md) bounds no-Catalog rendering to 100-row batches, starts with only the active family group expanded, preserves complete-family search/selection and deliberate group expansion, and records live 8,279-object Scripted Effects proof plus the 1,502-test desktop gate.
- [2026-08-09 PIHC3 Guided AI Authoring](2026-08-09-2020-pihc3-guided-ai-authoring.md) adds Registry-owned natural-language edits for selected existing sources, retains exact revision-guarded review/apply semantics, and reaffirms the physically canonical PIHC3 tree.
- [2026-08-09 PIHC3 Live Layout Closure](2026-08-09-1831-pihc3-live-layout-closure.md) verifies the physical zero-component/legacy/inactive tree, closes the inactive-collection preflight gap, repairs remount-safe publication ownership, adds built-in AI collection planning, and records green full/cached/partial builds plus the 2,398-test Python gate.
- [2026-08-03 PIHC3 Compact State Lore Source](2026-08-03-pihc3-compact-state-lore-source.md) replaces 158 generated per-module fragments with optional compact variants, canonicalizes all 79 folders to their State titles, and preserves both aggregate payloads byte-for-byte.
- [2026-08-03 PIHC3 Compact Inventory Item Source](2026-08-03-pihc3-compact-inventory-item-source.md) replaces 80 expanded helper-source modules with one compact Registry-owned JSON definition each, generates PDX/localization deterministically, and records exact pre-retirement parity plus four-mode build verification.
- [2026-08-03 PIHC3 Registry-guided Semantic Family Batch](2026-08-03-pihc3-registry-guided-semantic-family-batch.md) adds extension-owned existing-source guidance for Achievement, Division, Doctrine, Modifier, Inventory Item, State Lore, and Superevent, with guarded real-source probes and no frontend family switches.
- [2026-08-03 PIHC3 MIO Guided Authoring And Honest Module Counts](2026-08-03-pihc3-mio-guided-authoring-and-module-counts.md) adds Registry-owned bilingual MIO source guidance, truthful filtered/paged module totals, live 51-family readiness evidence, and complete Python/desktop verification.
- [2026-08-02 PIHC3 Source-layout Preflight](2026-08-02-pihc3-source-layout-preflight.md) reconciles the clean live tree with component-heavy nested-Git history, removes one unreferenced copy-marked Texticon duplicate, adds a build-time JSON cleanliness guard, retires stale component-layout guidance, and proves clean/cached/family/module publication with zero retired output paths.
- [2026-08-02 PIHC3 Module-activity Authoring](2026-08-02-pihc3-module-activity-authoring.md) adds generic active/inactive authoring across SDK/CLI/REST/MCP/native GUI, proves inactive modules remain editable but never compile, re-audits the exact zero-component/legacy tree, and passes all four PIHC3 build modes plus complete then-current Python and desktop gates.
- [2026-08-02 PIHC3 Guided Script Bodies](2026-08-02-pihc3-guided-script-bodies.md) adds Registry-declared exact PDX block-body editing, project-owned script-container templates, exhaustive 8,593-module coverage, and native PIHC3 proof with no family-specific GUI logic.
- [2026-08-02 PIHC3 Guided Map Lists](2026-08-02-pihc3-guided-map-lists.md) adds Registry-owned State/Strategic Region province and victory-point editing, exact guarded multiline patches, exhaustive live-source projection, and rendered native PIHC3 proof without family-specific GUI logic.
- [2026-08-02 PIHC3 Localization Single-source Cleanup](2026-08-02-pihc3-localization-single-source-cleanup.md) removes country/Focus/State/Strategic Region mirrors and orphan region placeholders, co-locates victory-point ownership with States, restores preferred-language naming, adds apostrophe-key compatibility, and proves clean/cached/family/module publication.
- [2026-08-02 PIHC3 Doctrine Compound Child Authoring](2026-08-02-pihc3-doctrine-compound-child-authoring.md) makes selected-node creation produce an intuitive standalone child, atomically journals the parent-owned path, and proves rollback plus fresh/cached/module-partial compilation without family-specific UI logic.
- [2026-08-02 PIHC3 Doctrine Registry Node Authoring](2026-08-02-pihc3-doctrine-registry-node-authoring.md) adds minimal standalone subdoctrine creation, localized/image-aware Doctrine projection, exact stale-source rollback, and fresh/cached/module-partial compile proof without a Doctrine-specific GUI path.
- [2026-08-02 PIHC3 Doctrine Single-source Consolidation](2026-08-02-pihc3-doctrine-single-source-consolidation.md) removes 43 non-compiling pre-1.17 nodes and stale land/air aggregates, folds shared support into the Doctrine Entity, and proves clean/cached/family/module compile parity.
- [2026-08-02 PIHC3 Technology Registry Node Authoring](2026-08-02-pihc3-technology-registry-node-authoring.md) fixes the real shared-support diagram crash, moves Technology creation to project-owned generic diagram-node authoring, and proves exact-hash rollback plus full/cached/partial compile parity.
- [2026-08-02 PIHC3 Generic Diagram-node Authoring](2026-08-02-pihc3-generic-diagram-node-authoring.md) removes the parallel Focus-only surface, moves project-specific creation into the PIHC3 Registry provider, and proves exact-hash build rollback plus unchanged four-mode compile parity.
- [2026-08-02 PIHC3 Component And Legacy Path Closure](2026-08-02-pihc3-component-legacy-path-closure.md) records the exact whole-tree zero-component/legacy-path audit, live-ID normalization, guarded collection removal, and complete compile/test parity.
- [2026-08-02 PIHC3 Atomic Collection Rename](2026-08-02-pihc3-atomic-collection-rename.md) records the v4 Registry-container recovery journal, atomic member-pointer rewrites, exact zero-retired-folder re-audit, and unchanged four-mode compilation parity.
- [2026-08-02 PIHC3 Collection-membership Authoring](2026-08-02-pihc3-collection-membership-authoring.md) records the exact zero-retired-folder re-audit, the 847 genuine collection-only manifests, one guarded SDK/CLI/REST/MCP/GUI picker, and unchanged four-mode compilation parity.
- [2026-08-02 PIHC3 Source-derived Metadata Cleanup](2026-08-02-pihc3-source-derived-metadata-cleanup.md) removes all 577 repeated per-module compiler settings, adds Registry-owned default routing, and preserves full/cached/partial compile parity.
- [2026-08-02 PIHC3 Registry-owned Localization Editing](2026-08-02-pihc3-registry-localization-editing.md) records exact guarded Guided editing for all 3,968 current localization files, Registry-derived image/asset ownership, the zero-retired-directory audit, and unchanged four-mode compilation output.
- [2026-08-02 PIHC3 Registry-owned Guided Editing](2026-08-02-pihc3-registry-guided-editing.md) records family-owned existing-module help, bounded partial forms for every current event source, HeavenBase 0.1.2.1 Entity metadata compatibility, and unchanged four-mode compilation output.
- [2026-08-02 PIHC3 High-traffic Authoring Semantics](2026-08-02-pihc3-high-traffic-authoring-semantics.md) records complete extension-owned help for 57 fields across nine core templates, real advanced-field ownership, shared backend type validation, and unchanged full/cached/partial compilation output.
- [2026-08-02 PIHC3 Schema-derived Template Help](2026-08-02-pihc3-schema-derived-template-help.md) records 391/391 GUI/SDK/agent field descriptions, transparent declared/generated provenance, acronym-safe labels, rendered desktop coverage, and unchanged full/cached/partial compilation output.
- [2026-08-02 PIHC3 Authoring Capability Closure](2026-08-02-pihc3-authoring-capability-closure.md) records complete 51-family/52-template authoring coverage, shared GUI/agent form projection with 391 readable labels, explicit localization slot typing, and unchanged full/cached/partial compilation output.
- [2026-08-02 PIHC3 Runtime Entity Parity](2026-08-02-pihc3-runtime-entity-parity.md) records removal of 13 shadow Entity schemas, real HeavenBase Registry parity across all 71 project module-family bundles, the exact clean physical audit, and unchanged four-mode compilation output.
- [2026-08-02 PIHC3 Agent-semantic Authoring](2026-08-02-pihc3-agent-semantic-authoring.md) records the Registry-complete desktop AI template catalog, complete numeric field semantics, real five-Idea MCP plan/apply/strict-build proof, and unchanged four-mode PIHC3 compile parity.
- [2026-08-01 PIHC3 All-family Template Fitness](2026-08-01-pihc3-all-family-template-fitness.md) records the empty-project 52-template creation matrix, corrected Entity localization contracts, first-use collection safety, shadowed fallback cleanup, exact zero-component physical audit, and clean/cached/partial compile parity.
- [2026-08-01 PIHC3 Text and Interface Source Ownership](2026-08-01-pihc3-text-interface-source-ownership.md) records the corrected PDX/image resource slots, compact project-local Entity bundles, 50/51 guided scripted-family coverage, intentional localization/image-only exception, and complete clean/cached/partial compile parity.
- [2026-08-01 PIHC3 Rendered Authoring Hardening](2026-08-01-pihc3-rendered-authoring-hardening.md) records the scalar-template renderer crash fix, retained source-root recovery, exact zero-component live-tree audit, rendered Idea create/apply proof, and complete clean/cached/partial gates.
- [2026-08-01 PIHC3 Hidden Grouping Metadata](2026-08-01-pihc3-hidden-grouping-metadata.md) records migration of 847 Focus/Modifier routing files to system-owned `.paradev` metadata, automatic Focus template maintenance, the single visible inactive flag, and clean/cached/partial parity.
- [2026-08-01 PIHC3 Decision Metadata Inference](2026-08-01-pihc3-decision-metadata-inference.md) records removal of 458 redundant visible metadata files, project-local Entity normalization, actionable ambiguous-category failures, and clean/cached/partial compile parity.
- [2026-08-01 Registry Diagram Relationship Actions](2026-08-01-registry-diagram-relationship-actions.md) records provider-owned edge semantics, shared bundled/external editing controls, MIO relationship writeback, the live zero-component audit, and the complete Python/desktop gates.
- [2026-08-01 Registry Diagram Renderer Adapters](2026-08-01-registry-diagram-renderer-adapters.md) records the renderer-owned desktop seam, shared external graph protocol, fail-closed validation, and rendered provider parity test.
- [2026-08-01 PIHC3 Code-owned Extension Families](2026-08-01-pihc3-code-owned-extension-families.md) records the zero-component 14,618-folder layout, 71 project-local compiler targets, Entity-owned resource slots, and Registry-derived aggregate asset destinations.
- [2026-08-01 PIHC3 Project-language Single Source](2026-08-01-pihc3-project-language-single-source.md) records the one-field Chinese authoring preference, shared SDK/desktop/REST/MCP behavior, exact zero-component filesystem audit, and clean/cached/partial compile parity.
- [2026-08-01 Guided Existing-module Batch](2026-08-01-guided-existing-module-batch.md) records one atomic Registry-owned plan/apply workflow for several existing modules, the agent authoring contract, live PIHC3 no-write proof, and fresh repository/build verification.
- [2026-08-01 PIHC3 Physical Layout Reverification](2026-08-01-pihc3-physical-layout-reverification.md) records the exact-path zero-component audit, project-wide case-insensitive guard, nested-Git-index explanation, consolidated asset ownership, and fresh clean/cached/partial build matrix.
- [2026-07-31 PIHC3 Entity Record Guided Authoring](2026-07-31-pihc3-entity-record-guided-authoring.md) records project-owned portable Entity JSON forms, exact duplicate-key patches, 134/134 live coverage, bounded code fallback, and SDK/MCP/build verification.
- [2026-07-31 Registry-guided PIHC3 Authoring Parity](2026-07-31-registry-guided-authoring-parity.md) records the zero-retired-folder live audit, 48/51 guided family coverage, project-owned Trait/Opinion Modifier compilers, bounded MCP source forms, and exact four-mode compile parity.
- [2026-07-31 Compatible Project Startup Recovery](2026-07-31-compatible-project-startup-recovery.md) records automatic recovery from obsolete saved PIHC3 checkouts, strict manual selection behavior, path self-repair, and rendered native-web verification.
- [2026-07-31 Agent-safe Existing-module Editing](2026-07-31-agent-safe-existing-module-editing.md) records live Registry/template/diagram coverage, bounded MCP browse/source reads, stable revision-guarded agent edits, and the refreshed ParaDev authoring skill.
- [2026-07-31 Source-draft Crash Recovery](2026-07-31-source-draft-crash-recovery.md) records the durable hidden write-ahead journal, automatic pre-build/apply recovery, external-edit preservation, and abrupt-write/folder-rename regression coverage.
- [2026-07-31 PIHC3 Semantic-Owner Cleanup](2026-07-31-pihc3-semantic-owner-cleanup.md) records removal of the four transitional support families and all retired component tombstones, owner-Entity resource slots, exact 35,139-artifact parity, and clean/cached/partial verification.
- [2026-07-31 Transactional Module Title Apply](2026-07-31-transactional-module-title-apply.md) records the single SDK-owned source/localization/folder-title transaction, callable MCP surface, rollback tests, and complete PIHC3 compile matrix.
- [2026-07-31 Registry-Owned Module Title Authoring](2026-07-31-registry-owned-title-authoring.md) records localization-owned Name editing, same-id folder-title synchronization, the zero-component PIHC3 physical audit, and the complete compile/test matrix.
- [2026-07-31 Registry-Owned Module Identity Copy](2026-07-31-registry-owned-identity-copy.md) records extension-owned independent duplication, the live zero-component PIHC3 audit, and the full compile/test matrix.
- [2026-07-31 PIHC3 Canonical Folder Titles](2026-07-31-pihc3-canonical-folder-titles.md) records the complete preferred-title naming gate, cleanup of dynamic script expressions from 17 folder suffixes, portable scaffold projection, and Registry-owned family title-localization keys.
- [2026-07-31 Registry-Owned Family Presentation](2026-07-31-registry-owned-family-presentation.md) records the extension-owned family identity contract, desktop compatibility-table removal, concurrent HeavenBase catalog read fix, PIHC3 compile parity, and the distinction between deleted source folders and hidden migration tombstones.
- [2026-07-31 PIHC3 Live-Tree Cleanup Audit](2026-07-31-pihc3-live-tree-cleanup-audit.md) records the whole-project forbidden-folder scan, staged-edit preservation audit, direct partial-build UX, and clean/cached/focus build matrix.
- [2026-07-31 PIHC3 Registry Family Handoff](2026-07-31-pihc3-registry-family-handoff.md) records the clean 14,618-folder PIHC3 audit, Registry/browser/template family identity handoff, provider-owned diagram source paths, and complete build/test matrix.
- [2026-06-21 Stable Wrap Summary](2026-06-21-0031-stable-wrap-summary.md) summarizes the current stable checkpoint: the API catalog/manual reference contracts are clean, the desktop focus-tree editor remains intentionally evolving, and the only included GUI change is the PIHC3-backed smoke fixture plus its local Vite file access.
- [2026-06-21 Focus Preview Icons](2026-06-21-0032-focus-preview-icons.md) records the PIHC3 preview PNG path that backs the focus-tree smoke fixture.
- [2026-06-21 Project Inspection Selector](2026-06-21-0040-project-inspection-selector.md) completes the shared selector-helper coverage for the generated project inspection reference.
- [2026-06-21 Focus Source Layout Preservation](2026-06-21-0045-focus-source-layout-preservation.md) records the compact focus tile and PIHC `cx`/`cy` source-layout preservation checkpoint.
- [2026-06-21 Inspection CLI Selectors](2026-06-21-0049-inspection-cli-selectors.md) records the final CLI adapter, generated API reference, and targeted verification sync for project inspection selectors.
- [2026-06-21 Stable Version Final Sync](2026-06-21-0054-stable-version-final-sync.md) records the final whole-repo wrap-up scope, legacy-artifact cleanup decision, and verification gate list.
- [2026-06-21 Focus Compact Image Canvas](2026-06-21-0057-focus-compact-image-canvas.md) records the 2 x 2 focus icon canvas and live smoke verification.
- [2026-06-21 Focus Preview Preference](2026-06-21-0101-focus-preview-preference.md) records migrated `preview.png` preference for source-backed focus diagram images.
- [2026-06-21 Focus Source Backed Fixture](2026-06-21-0105-focus-source-backed-fixture.md) records the larger C08_MAIN source-backed adapter fixture for migrated preview icons.
- [2026-06-21 Focus Source Backed Smoke](2026-06-21-0114-focus-source-backed-smoke.md) records the browser smoke that proves migrated PIHC3 focus preview images hydrate into compact canvas icons.
- [2026-06-21 Focus Image Hydration Size](2026-06-21-0132-focus-image-hydration-size.md) records the per-node thumbnail sizing pass for compact source-backed focus preview icons.
- [2026-06-21 Boot Progress Animation](2026-06-21-0135-boot-progress-animation.md) records the active boot-progress track animation and PIHC3 loading smoke fixture.
- [2026-06-21 Diagram Fit ViewBox](2026-06-21-0146-diagram-fit-viewbox.md) records the normal-window canvas fit pass for large focus/technology diagrams.
- [2026-06-21 C08 Main Source Layout Fields](2026-06-21-0157-c08-main-source-layout-fields.md) records the C08_MAIN PIHC3 fixture regeneration and regression test for source-focus layout fields.
- [2026-06-21 Focus Source Info Drafts](2026-06-21-0210-focus-source-info-drafts.md) records source-backed `legacy/<focus>/info.json` layout drafts for migrated PIHC focus edits.
- [2026-06-21 Focus Source Relationship Drafts](2026-06-21-0214-focus-source-relationship-drafts.md) records source-backed dependency and mutual-exclusion JSON drafts for migrated PIHC focus edits.
- [2026-06-21 Focus Source Apply Review](2026-06-21-0223-focus-source-apply-review.md) records apply-review rows for migrated focus source `info.json` files alongside module `meta.yaml`.
- [2026-06-21 Diagram Preview Tab Isolation](2026-06-21-0228-diagram-preview-tab-isolation.md) records separate preview-tab replacement behavior for diagram tabs versus normal module tabs.
- [2026-06-21 Diagram Tab Smoke](2026-06-21-0236-diagram-tab-smoke.md) records rendered shell coverage for opening a normal focus module tab and its separate focus-tree diagram tab.
- [2026-06-21 Focus Slot Grid](2026-06-21-0248-focus-slot-grid.md) records the 48 px HOI4 focus-slot grid fix so adjacent PIHC source rows no longer overlap.
- [2026-06-21 Focus Move Smoke](2026-06-21-0259-focus-move-smoke.md) records rendered apply-review image scaling and branch movement coverage for HOI4-style focus trees.
- [2026-06-21 Focus Move Footprint](2026-06-21-0306-focus-move-footprint.md) records selected-node movement footprint feedback for branch, node-only, and descendant-relayout focus moves.
- [2026-06-21 Focus Footprint Centering](2026-06-21-0314-focus-footprint-centering.md) records the inspector action for centering the active move footprint in large PIHC focus trees.
- [2026-06-21 PIHC3 Cache Cleanup](2026-06-21-0325-pihc3-cache-cleanup.md) records removal and verification of generated PIHC3 bytecode caches from the project tree.
- [2026-06-21 Module Local Diagram Images](2026-06-21-0333-module-local-diagram-images.md) records module-local migrated image resolution for PIHC3 diagram nodes plus the focus preview smoke recheck.
- [2026-06-21 Technology Icon Grid](2026-06-21-0345-technology-icon-grid.md) records compact 48 px technology icon nodes, PIHC3 module-local image smoke coverage, and one-slot metadata expectation sync.
- [2026-06-21 Focus Inspectable Zoom](2026-06-21-0422-focus-inspectable-zoom.md) records image-backed focus/technology diagram initial zoom so migrated PIHC3 icons open at an inspectable normal-window scale.
- [2026-06-21 PIHC3 Clean Build](2026-06-21-0428-pihc3-clean-build.md) records the `compile.bash --clean` wrapper, generated-cache cleanup, and PIHC3 clean plan verification.
- [2026-06-21 PIHC3 Summary Wrapper](2026-06-21-0434-pihc3-summary-wrapper.md) records the compact `compile.bash --summary` health-check mode for PIHC3.
- [2026-06-21 Module Batch Request](2026-06-21-0448-module-batch-request.md) records the SDK/CLI request generator for rerunnable PIHC3 module update batches.
- [2026-06-21 Batch Request Schema Export](2026-06-21-0454-batch-request-schema-export.md) records the public SDK facade export and generated reference sync for the batch request schema.
- [2026-06-21 Focus Image Size Contract](2026-06-21-0459-focus-image-size-contract.md) records the shared canvas/smoke sizing helper and browser-verified PIHC3 focus preview image footprint.
- [2026-06-21 Focus Layout Control Isolation](2026-06-21-0505-focus-layout-control-isolation.md) records the guard that keeps PIHC focus layout-hint controls out of technology diagrams.
- [2026-06-21 Focus Layout Alias Cleanup](2026-06-21-0510-focus-layout-alias-cleanup.md) records canonical PIHC source focus layout-hint writeback for alias-heavy migrated metadata.
- [2026-06-21 Diagram Draft Availability](2026-06-21-0516-diagram-draft-availability.md) records apply-review skip handling for PIHC3 changed rows whose source path has no generated draft text.
- [2026-06-21 Unavailable Draft Apply Block](2026-06-21-0519-unavailable-draft-apply-block.md) records the apply guard that prevents partial writes when a PIHC3 source-backed diagram draft cannot be generated.
- [2026-06-21 Source-Only Draft Row](2026-06-21-0522-source-only-draft-row.md) records removal of unchanged meta rows when PIHC3 diagram review generates only source-info drafts.
- [2026-06-21 Diagram Apply Plan Guard](2026-06-21-0530-diagram-apply-plan-guard.md) records the apply-time draft reconciliation guard that blocks partial PIHC3 diagram writes when any changed row has no generated text.
- [2026-06-21 Empty Draft Unavailable](2026-06-21-0532-empty-draft-unavailable.md) records immediate unavailable-row marking when PIHC3 diagram draft generation returns no text for path-backed rows.
- [2026-06-21 Batch Request Target Validation](2026-06-21-0536-batch-request-target-validation.md) records SDK/CLI batch request generation rejecting unknown PIHC3 module targets before emitting canonical JSON.
- [2026-06-21 Batch Request File Validation](2026-06-21-0541-batch-request-file-validation.md) records SDK/CLI batch request generation rejecting missing file targets unless creation is explicit.
- [2026-06-21 Diagram Image Partial Hydration](2026-06-21-0545-diagram-image-partial-hydration.md) records per-node image hydration failure handling so one bad PIHC3 icon does not blank the canvas images.
- [2026-06-21 Diagram Image Progress](2026-06-21-0552-diagram-image-progress.md) records the source-backed diagram toolbar progress chip for local PIHC3 image hydration.
- [2026-06-21 Focus Image Canvas QA](2026-06-21-0607-focus-image-canvas-qa.md) records fresh verification that migrated PIHC3 focus preview images render as compact canvas icons.
- [2026-06-21 Boot Progress Payload Summary](2026-06-21-0611-boot-progress-payload-summary.md) records payload-aware desktop refresh progress text for large PIHC3 project loads.
- [2026-06-21 PIHC3 Recursive Cache Clean](2026-06-21-0618-pihc3-recursive-cache-clean.md) records recursive bytecode cleanup in the single PIHC3 build wrapper and a fresh clean-summary smoke check.
- [2026-06-21 Diagram Pinned Sibling Packing](2026-06-21-0624-diagram-pinned-sibling-packing.md) records the focus-tree layout pass that keeps auto children from overlapping absolute or relative siblings on the same grid row.
- [2026-06-21 Source Null Parent Roots](2026-06-21-0628-source-null-parent-roots.md) records source-backed `parent: null` focus records staying canonical roots while prerequisites remain dependency edges.
- [2026-06-21 Source Backed C08 Part IV Images](2026-06-21-0637-source-backed-c08-partiv-images.md) records the source-backed C08_PARTIV smoke model and rendered browser check for nine migrated PIHC3 focus preview images.
- [2026-06-21 Source Info Root Parent](2026-06-21-0642-source-info-root-parent.md) records source-info JSON writeback preserving `parent: null` when a migrated PIHC focus becomes a root.
- [2026-06-21 Focus Actual Image Canvas](2026-06-21-0655-focus-actual-image-canvas.md) records browser verification that migrated PIHC3 focus preview images render as actual compact canvas images, plus the source-backed root-position apply fix.
- [2026-06-21 Module Tab Diagram Entry](2026-06-21-0704-module-tab-diagram-entry.md) records the normal module-tab `Open diagram` action that opens the existing separate focus/technology diagram tab.
- [2026-06-21 Diagram Tab Source-Backed Images](2026-06-21-0715-diagram-tab-source-backed-images.md) records source-backed PIHC3 focus preview hydration through the normal shell diagram-tab smoke.
- [2026-06-21 Legacy Desktop-host Relative Source Images](2026-06-21-0722-tauri-relative-source-images.md) records project-relative text and binary source resolution through the then-current desktop bridge for PIHC-style image paths.
- [2026-06-21 Source Backed Apply Images](2026-06-21-0729-source-backed-apply-images.md) records project-relative focus image hydration in React and the source-backed apply-review smoke fixture.
- [2026-06-21 Focus Compact Auto Rows](2026-06-21-0745-focus-compact-auto-rows.md) records compact HOI4-style auto-row spacing for source-backed PIHC focus trees.
- [2026-06-21 Focus Source Slot Images](2026-06-21-0804-focus-source-slot-images.md) records HOI4DEV-style source slot positioning plus browser-verified migrated PIHC3 focus preview images in the canvas.
- [2026-06-21 Source Backed Move Images](2026-06-21-0812-source-backed-move-images.md) records source-backed PIHC3 focus preview images plus rendered subtree/node-only/relayout movement checks in the browser smoke.
- [2026-06-21 Source Layout Hint Smoke](2026-06-21-0817-source-layout-hint-smoke.md) records rendered inspector editing for PIHC source layout hints `priority`, `w`, `dw`, and `dc` in the source-backed focus tree smoke.
- [2026-06-21 Layout Hint Apply Draft](2026-06-21-0822-layout-hint-apply-draft.md) records the rendered apply-review smoke proving PIHC layout hint edits create the expected source-info JSON draft.
- [2026-06-21 Focus Image Canvas Recheck](2026-06-21-0942-focus-image-canvas-recheck.md) records the migrated preview coverage audit and browser proof that source-backed focus icons render as actual 34 x 34 SVG images.
- [2026-06-21 Project API Reference Sync](2026-06-21-0945-project-api-reference-sync.md) records the generated Project API reference sync for the SDK/CLI module-batch request surface.
- [2026-06-21 PIHC3 Clean-Only Wrapper](2026-06-21-0950-pihc3-clean-only-wrapper.md) records the `compile.bash --clean-only` cleanup mode and contract test for generated PIHC3 runtime files.
- [2026-06-21 Focus Image Browser Contract](2026-06-21-0957-focus-image-browser-contract.md) records the normal-browser source-backed smoke proof for actual PIHC3 preview images in 48 px focus slots.
- [2026-06-21 Diagram Toolbar Command Lane](2026-06-21-1004-diagram-toolbar-command-lane.md) records the compact selected-node command lane and rendered normal-window toolbar checks.
- [2026-06-21 Diagram Narrow Global Actions](2026-06-21-1009-diagram-narrow-global-actions.md) records the narrow-window icon-only global diagram actions and apply-review smoke proof.
- [2026-06-21 Diagram Unlock Edit](2026-06-21-1023-diagram-unlock-edit.md) records the source-side unlock relationship editor and rendered technology apply-review smoke proof.
- [2026-06-21 Focus Relationship Smoke](2026-06-21-1031-focus-relationship-smoke.md) records the source-backed PIHC focus prerequisite/reference editor smoke and apply-review proof.
- [2026-06-21 Focus Preview URL Canvas](2026-06-21-1052-focus-preview-url-canvas.md) records migrated `preview_url` metadata, actual PNG-backed focus image rendering, and compact canvas verification.
- [2026-06-21 PIHC3 Projectwide Bytecode Clean](2026-06-21-1101-pihc3-projectwide-bytecode-clean.md) records projectwide PIHC3 bytecode cleanup through the single `compile.bash` wrapper.
- [2026-06-21 Batch Request Change Counts](2026-06-21-1105-batch-request-change-counts.md) records SDK/CLI preflight changed/unchanged counts for generated module batch requests.
- [2026-06-21 Diagram Selected Focus Scope](2026-06-21-1121-diagram-selected-focus-scope.md) records selected-focus-tree diagram scoping plus fresh migrated image-canvas verification.
- [2026-06-21 Focus Diagram Scope Selector](2026-06-21-1130-focus-diagram-scope-selector.md) records the in-tab focus-tree selector and full AppShell smoke proof for switching scoped PIHC focus trees.
- [2026-06-21 Focus C01 Grid DPI](2026-06-21-1152-focus-c01-grid-dpi.md) records the 96 px focus coordinate grid, 72 px high-DPI icons, simplified focus canvas chrome, and full C01_MAIN browser smoke coverage.
- [2026-06-21 Focus C01 Simplified Canvas](2026-06-21-1213-focus-c01-simplified-canvas.md) records the fitted C01_MAIN viewport, hidden focus-tree inspector/advanced toolbar groups, hover panels, and selected-node mode switch smoke.
- [2026-06-21 C01 Mode Apply Source](2026-06-21-1226-c01-mode-apply-source.md) records source-backed C01 mode-switch apply coverage from selected-node relative mode into migrated `legacy/<focus>/info.json`.
- [2026-06-21 Focus Node Info Popup](2026-06-21-1240-focus-node-info-popup.md) records double-click focus-node info popups, source-info path display, and the SVG hitbox fix needed for compact icon nodes.
- [2026-06-21 Diagram Popup Smoke Contract](2026-06-21-1246-diagram-popup-smoke-contract.md) records machine-readable diagram-tab smoke fields for the opened C01 focus-node info popup.
- [2026-06-21 C01 Mode Switch Smoke Contract](2026-06-21-1251-c01-mode-switch-smoke-contract.md) records machine-readable diagram-tab smoke fields for selected focus-node mode and the upper-right three-way mode switch.
- [2026-06-21 Focus C01 Interaction QA](2026-06-21-1311-focus-c01-interaction-qa.md) records the final browser QA pass for C01_MAIN grid density, high-DPI focus icons, simplified chrome, mode-switch apply, and double-click popup behavior.
- [2026-06-21 Diagram Ctrl Wheel Zoom](2026-06-21-1316-diagram-ctrl-wheel-zoom.md) records Ctrl + mouse wheel zoom handling for the diagram canvas and the rendered C01 smoke health check.
- [2026-06-21 Diagram Cursor Wheel Zoom](2026-06-21-1323-diagram-cursor-wheel-zoom.md) records cursor-anchored Ctrl + mouse wheel zoom for the focus-tree diagram viewport.
- [2026-06-21 Focus Popup Module Jump](2026-06-21-1334-focus-popup-module-jump.md) records the opened focus-node popup action that jumps from the diagram tab back to the normal module editor tab.
- [2026-06-21 Focus Popup Source Handoff](2026-06-21-1346-focus-popup-source-handoff.md) records source-backed PIHC focus info tabs and the popup jump landing on the selected focus `info.json` editor.
- [2026-06-21 Diagram Canvas Wheel Capture](2026-06-21-1357-diagram-canvas-wheel-capture.md) records canvas-level native Ctrl/Command + mouse wheel zoom capture for the diagram editor.
- [2026-06-21 Technology Popup Meta Handoff](2026-06-21-1404-technology-popup-meta-handoff.md) records technology node popup `meta.yaml` source paths and normal module editor source-tab handoff.
- [2026-06-21 Metadata Source Code Tabs](2026-06-21-1407-metadata-source-code-tabs.md) records `meta.yaml` source tabs opening as code sources instead of localization sources.
- [2026-06-21 Source Tab Picker](2026-06-21-1411-source-tab-picker.md) records the compact source-file selector for source-backed modules with many editable source tabs.
- [2026-06-21 Source Picker Path Readout](2026-06-21-1414-source-picker-path-readout.md) records the selected relative-path readout beside the compact source selector.
- [2026-06-21 Source Picker Smoke Contract](2026-06-21-1425-source-picker-smoke-contract.md) records machine-readable diagram-tab smoke fields for the compact source picker, selected source path, and rendered module editor verification.
- [2026-06-21 Diagram Node Hit Targets](2026-06-21-1430-diagram-node-hit-targets.md) records stable per-node SVG hit targets and browser-verified C01 focus popup opening.
- [2026-06-21 Diagram Wheel Zoom Clamp](2026-06-21-1443-diagram-wheel-zoom-clamp.md) records Ctrl/Command wheel zoom boundary clamping for the shared diagram canvas.
- [2026-06-21 Diagram Search Centering](2026-06-21-1450-diagram-search-centering.md) records first-match search centering for large C01 focus trees plus fresh rendered smoke verification.
- [2026-06-21 Diagram Minimap Drag](2026-06-21-1500-diagram-minimap-drag.md) records continuous minimap drag panning for large C01 focus trees plus Browser CUA smoke verification.
- [2026-06-21 Diagram Viewport History](2026-06-21-1506-diagram-viewport-history.md) records viewport-only pan/zoom saves staying out of diagram undo history while keeping C01 view restore behavior.
- [2026-06-21 Diagram Panel Wheel Zoom](2026-06-21-1516-diagram-panel-wheel-zoom.md) records panel-wide Ctrl/Command + mouse wheel zoom, SVG-bound cursor anchoring, and rendered C01 interaction proof.
- [2026-06-21 Diagram Wheel Pan](2026-06-21-1523-diagram-wheel-pan.md) records SVG-only normal wheel panning, Shift-wheel horizontal panning, and Ctrl-wheel zoom regression proof.
- [2026-06-21 Batch Request Target Preview](2026-06-21-1629-batch-request-target-preview.md) records per-edit target preview rows for SDK/CLI module batch requests plus real PIHC3 verification.
- [2026-06-21 Desktop Batch Preview Bridge](2026-06-21-1634-desktop-batch-preview-bridge.md) records the then-current desktop TypeScript bridge for SDK-owned module batch request target previews.
- [2026-06-21 Focus Coordinate Centering](2026-06-21-1645-focus-coordinate-centering.md) records focus icons, hit targets, and viewport navigation treating PIHC focus `x,y` as the center of the 1.5-slot visible footprint.
- [2026-06-21 Focus Wrap Verification](2026-06-21-1909-focus-wrap-verification.md) records the final wrap-up verification set, generated API reference repairs, and push-ready checkpoint.
- [2026-06-20 Stable API And Desktop Wrap-Up](2026-06-20-2312-stable-api-desktop-wrap.md) is the previous broader wrap-up for the generated API table/reference work and desktop focus-tree checkpoint.

## Naming

Use one note per checkpoint:

```text
docs/progress/YYYY-MM-DD-HHMM-<short-topic>.md
```

Example:

```text
docs/progress/2026-06-06-1700-pdx-core.md
```

## Template

```markdown
# <Topic> Progress

Date: YYYY-MM-DD HH:MM

Linear: TAL-000

## Done

-

## Verification

-

## Risks Or Blockers

-

## Next

-
```

Keep notes short. Link to changed docs, issues, and important commands instead of copying long logs.
