# Technology authoring and catalog readiness

Date: 2026-07-29 11:22

## Outcome

The desktop no longer sends an expected failing catalog query when a project's
optional HeavenBase catalog is absent. It loads catalog readiness once,
coalesces concurrent checks, and uses the source browser directly for the
ordinary not-configured state. Incomplete or unreadable catalogs remain visible
repair states instead of being mislabeled as an ordinary source fallback.

PIHC3's Technology tree now opens a focused single-module creation dialog. The
dialog renders the existing `pihc3:technology/basic` template, previews the
exact source files and plan hash, and applies only through the existing guarded
`Project.create_modules(...)` transaction. No parallel desktop, REST, MCP, or
compiler authoring implementation was added.

The minimal Technology template creates only title metadata, PDX definition,
and localization with a description. Its optional image target is the
module-local `icon.png`, which the Image tab can create after the module exists.

## Verification

- Live PIHC3 browser smoke: Technology family and tree loaded through the
  source browser with no failed catalog query or console warning; a three-file
  module preview produced an exact plan hash, cancel wrote no source folder.
- Desktop: 84 Vitest files / 1,402 tests passed; production TypeScript and Vite
  build passed.
- Python: 2,534 tests passed and 33 expected platform/source-fixture skips.
- Python style: Black left 216 files unchanged; Flake8 passed.
- PIHC3 clean/full and cached: 17,063 modules, 78 collections, 37,501
  artifacts, zero diagnostics/errors, unblocked. Their structured results were
  byte-identical.
- PIHC3 Technology family partial: 300 modules and 11,899 affected artifacts.
- PIHC3 `technology/TECHNOLOGY_FIREARM_I` module partial: one module and 10,997
  affected artifacts including the safe localization publication closure.
- Both partial modes retained all 37,501 published files. The v3 ownership
  ledger remains `complete` with `whole_project_baseline: true`.

## Risk

The full Python gate took 32 minutes 8 seconds while remaining CPU-bound. This
does not block correctness, but it is substantially slower than the previous
baseline and should be profiled before adding more corpus-wide test passes.

## Next

Continue the canonical PIHC3 authoring plan by applying the same
template-driven, exact-transaction flow to the next highest-friction family,
without adding family-specific desktop parsers or visible system metadata.
