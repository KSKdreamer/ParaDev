# PIHC3 Project-scoped MIO Editor

Date: 2026-08-09 22:17 +08:00

Status: complete stability slice

## Outcome

The native ParaDev GUI now opens PIHC3's complete Military Industrial
Organization projection instead of accidentally filtering it to the support
source selected by the family browser. The Registry provider declares the
closed `initial_scope="project"` capability, and the generic desktop adapter
consumes that declaration without a PIHC3 family-id switch.

The live native-web flow opened 30 PIHC3 organizations. The initial C01 tree
rendered 15 nodes and 30 links; switching to `generic_tank_organization`
rendered 13 nodes and 26 links. The scope label now says that these are
organizations in the project rather than in the incidental source module.

## Source and metadata audit

`projects/PIHC3/scripts/check_source_layout.py --json` remains green with 70
module families, 14,574 modules, 2 collection families, 90 collections,
36,469 source files, and no retired component, asset-component, legacy, or
inactive-module directory.

The exact metadata audit found 848 module/collection manifests:

- one visible manifest, the intentional inactive Bookmark flag;
- 847 hidden `.paradev/meta.yaml` files containing only collection membership;
- no repeated compiler routing, titles, localization, or resource metadata.

Those 847 pointers are the live single source of truth for 738 Focus-tree and
109 Modifier-group memberships. Templates and guarded SDK/GUI transactions
maintain them, so ordinary authors do not edit hidden metadata.

## Registry contract

`ModuleDiagramProvider.initial_scope` accepts only `selected-entity` or
`project`. The former remains the compatibility default and is omitted from
the serialized view; the latter is explicit. PIHC3 inherits the bundled MIO
provider through its project extension, so the same Registry seam works for
bundled and external entities.

The desktop parser fails safely to `selected-entity` for absent or unknown old
values. `ModuleEditor` ignores the incidental selected source only when the
active provider explicitly requests project scope. Existing selected-entity
providers retain their prior behavior and honest empty state.

## Verification

- The complete Python gate passed: 2,407 tests, with nine expected native-Windows
  skips.
- The complete desktop gate passed: 1,506 tests across 93 files.
- 40 targeted Python Registry/MIO/consolidation tests and 31 targeted desktop
  capability/session-lifecycle tests passed before the complete gates.
- TypeScript type-check and the Vite production build passed.
- A real `Project.load(...).browser(family="military_industrial_organization")`
  projection reported `initial_scope="project"` and seven physical source
  modules.
- The rendered native GUI demonstrated the complete 30-organization selector
  and two distinct usable trait graphs.
- The Heaven-style scan passed for all touched Python and Python-test files.
- `git diff --check` passed.

This slice changes diagram discovery and presentation only. It does not alter
PIHC3 compiler input, artifact ownership, or publication code, so the prior
same-day clean/full, cached, family-partial, and module-partial build matrix
remains the relevant compilation gate.
