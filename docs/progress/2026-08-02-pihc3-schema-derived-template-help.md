# PIHC3 Schema-derived Template Help

Date: 2026-08-02

## Outcome

Every field in PIHC3's Registry-owned create catalog now has readable help in
the SDK, desktop create dialog, MCP/REST payload, and desktop AI prompt. The
catalog contains 52 templates and 391 fields: 28 keep explicit domain guidance
declared by their owning extensions, while 363 receive a concise fallback
derived from their actual generated folder and file references.

The fallback is a schema projection, not a family-specific semantics table. It
explains concrete usage such as the readable module folder, `def.txt`, or
`main.loc`; it does not invent HoI4 meaning. An extension-provided description
always wins. Both argument and form projections expose the same text plus
`description_source: declared|generated`, so generic clients can distinguish
authoritative domain guidance from source-usage help.

Generated labels now preserve common authoring acronyms such as AI, DDS, DLC,
GFX, GUI, HoI4, ID, MIO, PDX, UI, URL, and XP while using sentence case for the
remaining words. The desktop typed model retains description provenance and
renders it on the same accessible help element as the description. The AI
catalog consumes that exact GUI-ready projection; its current serialized JSON
is 80,697 characters and has no separate ParaDev family lookup table.

## Verification

- Focused SDK/template tests: 49 passed.
- PIHC3 Registry, desktop chat, MCP, project-extension, and collection-template
  tests: 73 passed.
- Standard Python gate: 2,288 passed; nine expected native-Windows-only tests
  skipped.
- Desktop gate: 89 files and 1,455 tests passed.
- Strict TypeScript and Vite production build passed, with the existing
  advisory for chunks larger than 500 kB.
- Black and fatal Flake8 rules passed; all 219 checked Python files remain
  formatted.
- Root and nested PIHC3 diff whitespace checks passed.
- Clean/full and cached/full: 14,617 active modules, 106 collections, 35,131
  artifacts, zero diagnostics and errors.
- Focus family partial: 738 modules, 28 collections, 12,499 artifacts, zero
  diagnostics and errors.
- Focus module partial (`FOCUS_C01_C02_EVERFREE_FIELDTRIP`): 83 modules, one
  collection, 11,161 artifacts, zero diagnostics and errors.

The build matrix wrote only to
`/tmp/paradev-pihc3-template-help-verify`, not the user's installed mod.

The Heaven-style scanner reports only the existing utility-import debt in the
two large test modules touched for coverage. This slice added no utility import
and did not change PIHC3 source or extension metadata.
