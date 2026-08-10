# PIHC3 Registry family handoff

Date: 2026-07-31

## Outcome

- Re-audited `projects/PIHC3/src/modules` after the component consolidation:
  zero `_component`, `_asset_component`, `legacy`, or `inactive_modules`
  directories remain.
- All 14,618 physical module folders use `id - preferred-language title`.
- The only 1,306 visible `meta.yaml` files are minimal author inputs:
  1,305 contain only `collection`, and the bookmark contains only
  `inactive`. System routing and diagram state remain hidden under
  `.paradev/`.
- Removed the remaining user-visible “legacy Entity authoring” label from the
  PIHC3 Entity extension.

## Registry-driven desktop handoff

- Template rows now expose `family_id`, the exact browser/workspace identity
  associated with their Registry family. The template index exposes the same
  field, and `Project.templates(family=...)` accepts either the Registry family
  or stable browser identity.
- Desktop family discovery resolves browser ids, Registry families, template
  family ids, and registered diagram aliases as one runtime identity.
- Project-exclusive families therefore appear and scaffold without a new
  desktop family mapping. A regression fixture proves an unknown
  `weather_magic` extension reaches the workspace as `weather-magic`.
- Existing plural tab/session ids remain behind a compatibility adapter so
  saved workspaces and translations do not churn. The adapter is not required
  for new external families.
- AI batch review, Catalog paging, scoped refreshes, and module template
  selection now use the same runtime family handoff.

## Diagram source integrity

- Diagram node source handoff now accepts only a provider-declared,
  project-relative `source_path`/`sourcePath`.
- Removed GUI synthesis of `legacy/<focus>/info.json`.
- Removed GUI synthesis of visible technology `meta.yaml`; current technology
  nodes open their authoritative module `def.txt`.
- The generic handoff permits project-exclusive source formats while retaining
  traversal and URL rejection.

## Verification

- PIHC3 runtime identity audit: 75 browser families, 53 authoring-ready
  templates, zero family-id mismatches.
- Python: 2,331 passed; nine native-Windows tests skipped.
- Desktop: 87 files and 1,416 tests passed.
- Rust/Tauri: 93 tests passed.
- TypeScript/Vite production build passed.
- Full and cached PIHC3 plans: 14,617 modules, 106 collections, 35,139
  artifacts, zero diagnostics.
- Technology family partial: 300 modules, 11,899 artifacts, zero diagnostics.
- `technology/TECHNOLOGY_FIREARM_I` module partial: one module, 10,997
  artifacts, zero diagnostics.
- Source cleanup audit and repository diff check passed.

## Next

- Move the remaining stable workspace compatibility aliases into a
  Registry-owned presentation contract before removing the adapter.
- Continue retiring browser-only legacy focus metadata editing code now that
  PIHC3 focus, technology, doctrine, and MIO diagrams all expose authoritative
  provider source paths.
