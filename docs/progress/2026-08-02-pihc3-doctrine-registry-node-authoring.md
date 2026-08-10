# PIHC3 Doctrine Registry Node Authoring Progress

Date: 2026-08-02 15:19

## Done

- Upgraded the project-local Doctrine bundle to `0.2.6` and kept its Entity, compiler, diagram provider, and both templates behind HeavenBase 0.1.2.1 Registry targets.
- Added the semantically separate `pihc3:doctrine/subdoctrine-basic` template. It writes only `def.txt`, preferred-language `main.loc`, and hidden `.paradev/diagram.yaml`; it does not create visible or hidden per-module metadata.
- Moved Doctrine creation onto the shared `diagram-node` capability used by the SDK, CLI, REST, MCP, and desktop. No Doctrine switch was added to React or the core SDK.
- Enriched source-backed Doctrine nodes with project localization, track, XP type, sprite key, and optional module-local `icon.png` paths.
- Made selected-node creation intuitive and source-truthful: the selected doctrine is the parent, the new standalone child owns an empty outgoing-path list, and the existing parent owns the new directed path.
- Generalized standalone diagram creation with an optional companion source plan. The SDK now installs the child, journals the parent edit, validates the combined family, and rolls both changes back when the source conflicts or the build rejects them.
- Bound creation to the reviewed definition set and selected source revisions. Exact plan-hash revalidation, family-build acceptance, Catalog refresh, and rollback remain owned by the generic Project transaction.
- Re-ran the physical PIHC3 source-layout guard: no `_component`, `_asset_component`, `legacy`, or `inactive_modules` directory remains, and direct source folders still use `id - preferred localization`.

## Verification

- `tests/test_pihc3_doctrine_consolidation.py`: 7 passed, covering live projection, child creation/apply, minimal files, localization, optional image targeting, stale-parent rejection, source-conflict rollback, build-rejection rollback, and Doctrine family compilation.
- Core Doctrine plus project-local Doctrine: 12 passed. Generic project diagram, Focus, Technology, and surface regressions: 40 passed. Desktop generic node-dialog/service regressions: 168 passed.
- Complete PIHC3 template-correctness file: 13 passed, including all 53 project templates and both Doctrine templates; the cross-file template/capability selection also passed 6/6.
- Retired-layout plus Doctrine/capability contracts: 12 passed.
- Generic desktop diagram-node form/capability tests: 15 passed.
- Isolated output at `/Users/magolor/Projects/ParaDev/pihc3-doctrine-smoke.Mq6q3M`: fresh Doctrine family, cached Doctrine family, and module-partial builds all completed with zero diagnostics or errors. Counts were 52/10,968, 52/10,968, and 1/10,909 modules/artifacts respectively.

## Risks Or Blockers

- A process-level exception rolls both the child scaffold and parent source edit back. Abrupt process death retains the durable parent-source recovery journal; extending the scaffold journal to cover the complete compound operation remains a later hard-kill refinement.
- `icon.png` remains an optional, exact module-local image target. The creation form records the HoI4 sprite key immediately; users can add or replace the source image through the normal asset editor.

## Next

- Reuse the compound diagram transaction for other parent-owned relationship formats where it reduces authoring burden.
- Continue the same project-local Entity/Registry authoring audit for the remaining tree-like and extension types, prioritizing MIO UX gaps without adding family-specific desktop dispatch.
