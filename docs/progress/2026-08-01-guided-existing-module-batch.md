# Guided existing-module batch

Date: 2026-08-01

## Outcome

- `Project.plan_source_form_updates(...)` combines up to 256 Registry-owned
  JSON or PDX form updates into one no-write plan. Each source retains its
  exact size and modification-time revision for the existing crash-safe
  `Project.apply_source_draft(...)` transaction.
- Unchanged rows remain visible in the review payload but are omitted from
  `source_edits`. Duplicate canonical source paths and malformed rows fail
  before any write.
- The bounded `module_source_form_update_batch` MCP tool resolves every source
  through its module id and Registry-owned source slot. Agents can now inspect
  controls, plan several existing-module edits, review exact full-text changes,
  and apply the combined draft once without guessing control ids or paths.
- The shipped `paradev-authoring` skill and bilingual Python SDK manual now
  describe the same guided read, plan, review, and atomic-apply workflow.

## PIHC3 proof

The live MCP integration test plans simultaneous `mesh.scale` edits for
`entity/VIENTO_MIRROR` and `entity/VIENTO_AIR_AIRSHIP`. It verifies ordered
revision-guarded edits and byte-for-byte unchanged source files after planning.
The controls and compilation hooks are supplied by PIHC3's project-local
Registry extension, not a ParaDev family switch table.

The exact physical module root still contains 71 semantic families and 14,618
module folders. A fresh whole-project, case-insensitive scan found no live
`legacy`, `inactive_modules`, `_component`, or `_asset_component` directory and
no symlink below `src/modules`.

## Verification

- Synchronized source-form, MCP, PIHC3 extension, architecture, CLI, and API
  contract suite: 340 passed.
- Standard fast repository gate: 2,243 passed, with nine native-Windows tests
  skipped.
- Cached PIHC3 build: 14,617 active modules, 106 collections, 35,139 artifacts,
  zero diagnostics, zero errors, and not blocked.
- ParaDev authoring skill validation, selected import/syntax lint, outer and
  nested-project diff whitespace checks: passed.

## Follow-up boundary closed

The desktop editor now retains typed guided control intent in its app-owned
session and delegates Apply to the same canonical Python batch planner. It
preserves an unsaved Code-mode base, compares the returned exact text against
the visible draft, requires revision preconditions, merges raw and guided
source edits into one atomic apply, and fails closed on any mismatch. This
currently batches all guided source files changed within one module entity;
cross-module Apply remains a separate future workflow.
