# PIHC3 Runtime Entity Parity

Date: 2026-08-02

## Outcome

All PIHC3 module-family bundles now have a verified single Entity schema source.
ParaDev installs the project through the HeavenBase 0.1.2.1 `ModuleService`,
resolves each path-backed `hb.Entity` and build-family target from the Registry,
and checks their runtime contract instead of trusting descriptor text or Python
source inspection.

The audit covers all 71 module-family bundles. Every resolved Entity has:

- the descriptor's Entity identifier and a non-empty runtime record schema;
- a semantic family matching its standalone extension folder;
- non-empty Entity-owned `resource_slots` equal to the registered compiler
  slots;
- normalize, check, and emit compilation hooks; and
- a co-located Registry-loaded family target that constructs the same compiler
  type from those slots.

The 72nd `localisation` bundle is intentionally not a module family. It owns the
whole-project localisation writer and postprocessor and therefore declares no
Entity.

## Removed shadow schemas

Thirteen older path-backed Entity records still carried a duplicate
`meta.definition` left from their declarative phase: Achievement, Character,
Country, Decision, Division, Doctrine, Event, Idea, Idea Category, Military
Industrial Organization, Modifier, State, and Technology. Several had already
diverged from their live Python Entity fields—for example, Idea advertised
generic `module_id`/`data` fields while its runtime class declared `title`.

Those duplicate definitions are removed. The Python `hb.Entity` class is now
the only owner of record fields, resource slots, and hooks. The existing
`materialize_project_extension_entities.py` migration also removes stale
definitions when it encounters an already path-backed Entity, so rerunning the
safe system-metadata utility cannot recreate the split source of truth.

Inline definitions remain only where HeavenBase expects inert declarative data,
such as Extension registration and authoring templates. ParaDev gained no
family switch, duplicated schema table, or PIHC3-specific Registry bypass.

## Physical source audit

The exact `projects/PIHC3/src` tree contains 14,618 direct module folders and
90 direct collection folders. All 14,708 source units use the
`id - preferred-language title` convention. The live project contains zero
directories named `legacy` or `inactive_modules`, ending in `_component`, or
containing `_asset_component`. The one disabled bookmark stays in the normal
`bookmark` family with `inactive: true`.

## Verification

- Registry/extension/template/MCP focused gate: 85 passed.
- Standard Python gate: 2,286 passed; nine expected native-Windows-only tests
  skipped, with one existing warning.
- Desktop final gate: 89 files and 1,454 tests passed; strict TypeScript and
  Vite production build passed. An initial concurrent run hit one bounded
  event-loop settle timeout; its 33-test file and the complete suite both
  passed immediately when rerun without the concurrent Python load.
- Black and fatal Flake8 rules passed. The Heaven-style scanner reported only
  the existing utility-layer advisories in the two previously large touched
  files; this change added no such import.
- Root and nested PIHC3 diff whitespace checks passed.
- Clean/full and cached/full: 14,617 active modules, 106 collections, 35,131
  artifacts, zero diagnostics and errors.
- Focus family partial: 738 modules, 28 collections, 12,499 artifacts, zero
  diagnostics and errors.
- Focus module partial (`FOCUS_C01_C02_EVERFREE_FIELDTRIP`): 83 modules, one
  collection, 11,161 artifacts, zero diagnostics and errors.

The four compilation modes wrote only to an isolated temporary mod root, not
the user's installed Hearts of Iron IV mod directory.
