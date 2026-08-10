# PIHC3 Compact Inventory Item Source

This checkpoint removes generated authoring noise from PIHC3's project-owned
Inventory Item extension without changing its compiled contract.

## Outcome

- All 80 `inventory_item` modules now contain only `item.json`, human-authored
  `main.loc`, and `icons/` resources.
- `item.json` stores one bounded helper-quantity expression. The standard value
  is `1-100, 150-3000/50, 9999, 20000, 50000, 99999`.
- The named `PIHC3InventoryItemFamily` owns parsing, validation, guided JSON
  presentation, generated-output declarations, and compilation hooks. ParaDev's
  SDK, CLI, REST, MCP, and React renderer remain family-agnostic.
- The family generates scripted effects, scripted triggers, and deterministic
  helper localization. Authors maintain only item meaning and custom prose.
- The project-local template follows the same compact shape, so copying or
  creating an item never requires visible metadata or generated helper files.

## Guarded migration evidence

- All 80 old effect/trigger pairs matched deterministic generation before any
  source was removed.
- All generated localization values matched deterministic generation before
  they were removed from the authored files, including the corpus's conditional
  Russian coverage.
- The transaction-safe, resumable migration retired 160 generated PDX source
  files. It reports 80 already-compact modules, zero pending migrations, and no
  blocked operations.
- One representative `main.loc` shrank from 3,018 lines to 75 while preserving
  every custom localization row.
- The clean-layout audit reports 14,574 physical modules, 90 physical
  collections, 36,625 source files, one visible metadata file, and zero errors.

## Compilation evidence

- Inventory Item family plan: 80 modules, 9,618 artifacts, zero diagnostics.
- The family plan contains exactly 80 generated effect outputs, 80 generated
  trigger outputs, and 221 localization outputs.
- Clean full: 14,573 active modules, 106 collections, 33,437 artifacts, zero
  diagnostics.
- Cached full: 14,573 active modules, 106 collections, 33,437 artifacts, zero
  diagnostics.
- Inventory family partial: 80 modules, 9,618 artifacts, zero diagnostics.
- `inventory_item/1CO_C22_C07_TICKET_FINE` module partial: one module, 9,302
  artifacts, zero diagnostics.
- After both partial publications, the isolated output still contained exactly
  33,437 files, proving that the whole-project baseline remained intact.

## Verification

- Inventory migration and template/source-form contracts: 185 passed. The
  substantive run passed 184 contracts and the generated-cache hygiene check
  passed separately after removing the bytecode files created by that run.
- Standard Python gate: 2,386 passed and 9 native-Windows-only tests skipped.
- Targeted Black, Ruff, and `git diff --check` passed.
- The Heaven-style production scan passed for the Inventory extension and
  migration utility. Its heuristic reports only existing standard-library and
  PyYAML imports in broad test modules.
- The dry migration audit reports 80 already-compact modules, zero pending
  migrations, and no blocker. The source-layout preflight remains exact and
  error-free.

This is a PIHC3 authoring and compilation checkpoint, not a public release
claim.
