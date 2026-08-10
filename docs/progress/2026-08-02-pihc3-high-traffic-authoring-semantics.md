# PIHC3 High-traffic Authoring Semantics

Date: 2026-08-02

## Outcome

PIHC3's nine create templates for Ideas, Events, Decisions, Focuses/focus
trees, Technologies, Characters, Countries, and Equipment now own domain help
for all 57 of their fields. These descriptions live inside the corresponding
standalone project extension descriptor and reach the SDK, GUI, REST, MCP, and
desktop AI catalog through the normal HeavenBase Registry path.

Across all 52 PIHC3 templates and 391 fields, 72 descriptions are now declared
by their extension and 319 use ParaDev's source-usage fallback. The serialized
AI catalog is 81,953 characters. ParaDev gained no family description table or
PIHC3-specific dispatch branch.

The descriptors also publish more accurate controls:

- Character gender is a reviewed choice of `female`, `male`, or `undefined`,
  matching the values present in PIHC3 sources.
- Equipment `active` and `is_archetype` are `yes`/`no` choices.
- Decision political-power cost and Equipment model year are numeric fields
  with explicit labels and explanations.
- Focus and Technology raw relationship fields explain when the tree editor or
  direct PDX source owns the value.

The eight changed extension bundles received deterministic version bumps:
Idea, Event, Decision, and Technology are 0.2.5; Focus is 0.2.6; Character,
Country, and Equipment are 0.2.4. Every version occurrence inside each hidden
descriptor agrees.

## Shared form contract fixes

`TemplateArg.advanced` is now an explicit optional Registry contract. A
declared boolean wins; omitted values retain the compatibility behavior that a
non-empty default makes a field advanced. Non-boolean declarations fail while
loading the template. This fixes Technology's empty-default prerequisite source
appearing in the primary create form; the other five existing explicit PIHC3
advanced declarations previously happened to match the default-derived result.

Template type metadata is no longer presentation-only. The shared scaffold
planner rejects blank required values, values outside declared choices,
non-finite numbers, and invalid booleans with field-specific blocking
diagnostics before any write. SDK, CLI, REST, MCP, desktop, and agent batches
therefore enforce the same contract displayed by the GUI.

## Verification

- Full all-family isolated create/strict-build plus desktop-chat and MCP gate:
  43 passed in 202.26 seconds.
- Standard Python gate: 2,291 passed; nine expected native-Windows-only tests
  skipped, with one warning.
- Desktop gate: 89 files and 1,455 tests passed.
- Strict TypeScript and Vite production build passed, with the existing
  advisory for chunks larger than 500 kB.
- Black and fatal Flake8 rules passed; all 219 checked Python files remain
  formatted.
- Clean/full and cached/full: 14,617 active modules, 106 collections, 35,131
  artifacts, zero diagnostics and errors.
- Focus family partial: 738 modules, 28 collections, 12,499 artifacts, zero
  diagnostics and errors.
- Focus module partial (`FOCUS_C01_C02_EVERFREE_FIELDTRIP`): 83 modules, one
  collection, 11,161 artifacts, zero diagnostics and errors.

The build matrix wrote only to
`/tmp/paradev-pihc3-high-traffic-help-verify`, not the user's installed mod.

The Heaven-style scanner reports only the existing utility-import debt in the
two large test modules touched for coverage. This slice added no such imports.
