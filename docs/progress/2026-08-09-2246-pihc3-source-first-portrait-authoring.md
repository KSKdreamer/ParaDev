# PIHC3 Source-first Portrait Authoring

Date: 2026-08-09 22:46 +08:00

Status: complete stability slice

## Outcome

PIHC3's Portrait template was the last creation path that generated a visible
`meta.yaml`, used only as an empty-module placeholder. It now creates a useful
`portraits/{object_id}.txt` male/female group skeleton. The folder title still
comes from the preferred-language create field, image/GFX resources still use
the Portrait Entity's Registry slots, and no user-maintained metadata exists.

The generic desktop draft projection now renders placeholders in template file
paths before showing source tabs. The fix is not Portrait-specific: MIO,
Division, Entity, and external project templates with dynamic source paths use
the same projection. A live `PORTRAIT_UI_SMOKE` draft displayed the resolved
`PORTRAIT_UI_SMOKE` tab rather than `{object_id}`. Both smoke drafts were
discarded in memory; no PIHC3 source was written.

## Systematic authoring audit

The live PIHC3 Registry reports:

- 51 visible semantic families, each with an authoring-ready module template;
- 54 authoring-ready templates: 52 module and 2 collection templates;
- Focus and Decision collection creation;
- Focus, Technology, Doctrine, and MIO diagram providers;
- a safe `authoring_path` on every visible copy/image resource slot;
- zero template-generated visible `meta.yaml` or `meta.yml` files.

The template normalizer no longer manufactures visible metadata when removing
a redundant folder-derived title would leave an empty template. It fails with
a contextual error and requires the owning extension to declare a real source
file instead. This turns the source-first layout into a maintained invariant
rather than a one-time cleanup result.

## Verification

- The isolated all-template matrix scaffolded all 54 templates and passed the
  strict Entity/build contracts for all 51 families.
- The focused Portrait contract created the new source, emitted
  `portraits/PORTRAIT_TEMPLATE_CONTRACT.txt`, and produced no diagnostics.
- Both template-normalizer happy/failure contracts passed.
- The desktop model's 70 tests passed, including dynamic source-path rendering.
- The full Python gate passed: 2,409 tests passed and 9 native-Windows tests
  skipped on macOS.
- The full desktop gate passed: 93 files and 1,507 tests.
- TypeScript type-check and the Vite production build passed.
- The live native-web creation flow showed the compact Shared Portrait form and
  the resolved draft source tab without applying a write.
- A real PIHC3 Portrait family-partial build compiled 9 modules into 9,444
  safely scoped artifacts with zero diagnostics or errors.
- The exact source-layout audit remains green at 70 module families, 14,574
  modules, 90 collections, 36,469 source files, one visible metadata file, and
  no retired component, asset-component, legacy, or inactive-module path.
- The Heaven-style scanner and `git diff --check` passed for the touched Python
  surfaces.
