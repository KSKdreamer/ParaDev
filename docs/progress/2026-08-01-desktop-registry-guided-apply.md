# Desktop Registry-guided apply

Date: 2026-08-01

## Outcome

- Guided JSON and PDX controls no longer become write-authoritative React
  patches. React still produces an immediate lossless preview, but it retains
  the control id, typed scalar value, and first unsaved source base as session
  intent.
- `Project.plan_source_form_update(..., text=...)` can plan against that
  unsaved base while preserving the stable disk snapshot's size and
  modification-time revision. The bounded batch method accepts the same
  optional text per source.
- Strict Tauri, Python desktop-helper, and native-web adapters expose that one
  SDK batch contract. The TypeScript service validates schema, project/source
  identity, project containment, counts, control values, exact source edits,
  and revision fields before the editor can use the response.
- Apply reconciles every Registry-planned source against the visible module
  draft and then combines guided and raw source edits in the existing
  crash-safe transaction. Any missing, stale, revision-free, or text-mismatched
  plan leaves the draft untouched and shows an actionable error.
- Code-to-Guided editing preserves the unsaved Code base. A later raw Code edit
  explicitly clears guided intent for that source, preventing two competing
  patch authorities.

## Verification

- Standard Python repository gate: 2,248 passed, with nine native-Windows
  tests skipped.
- Desktop test gate: 1,435 passed; production TypeScript/Vite build passed.
- Native Tauri gate: 95 Rust tests passed; `cargo check` and formatting passed.
- Cached PIHC3 build: 14,617 active modules, 106 collections, 35,139
  artifacts, zero diagnostics, zero errors, and not blocked.
- SDK source-form, desktop-helper, native-web bridge, Tauri bridge,
  architecture, service/model/rendered lifecycle, selected import lint, and
  diff-whitespace checks passed.

## Scope

One module entity may include several guided source files and they are planned
together. A future multi-module review/apply surface can reuse the same SDK
batch contract without adding family-specific desktop logic.
