# PIHC3 Compact State Lore Source

Date: 2026-08-03

## Done

- Replaced 158 compiler-shaped per-module PDX fragments with one project-owned
  HeavenBase `StateLore` Entity/compiler contract.
- Renamed all 79 lore folders from lore-paragraph suffixes to the matching
  State module's preferred-language title.
- Kept `main.loc` as the only required source and retained optional
  `variants.pdx` only for states 217 and 772.
- Derived state ids only from `STATE_LORE_<positive id>`; no module metadata or
  authored aggregate registration remains.
- Added Registry-owned Guided labels, draft-time semantic validation, compact
  template behavior, migration/audit tooling, and layout/parity contracts.

## Verification

- Isolated migration: 79/79 modules compact, 81 sources, two conditional
  variants, zero generated per-module fragments.
- Aggregate payload parity:
  `823d0cf20ee03fe9ff427a90815a04ee8fa0c958b3a31579f883ceec2b4f64fa`
  and
  `08515f2d1c1bb9b3b9f022dab45dd65c8ee13523208c5e6c716c567ced2774b1`.
- Clean and cached full builds: 14,573 active modules, 106 collections,
  33,437 artifacts, zero diagnostics each.
- State Lore family/module builds: 79/1 selected modules, 9,299 artifacts,
  zero diagnostics each; the retained output still contains 33,437 files.
- Focused PIHC3 authoring/layout/template suite: 197 passed.
- Standard Python gate: 2,387 passed and 9 native-Windows tests skipped.
- Desktop gate: 90 files and 1,468 tests passed; TypeScript/Vite production
  build passed with only the existing chunk-size advisory.
- Targeted Black, Ruff, `git diff --check`, and Heaven-style production scan
  passed.

## Risks Or Blockers

- None for source migration. Gameplay behavior is preserved at the emitted
  aggregate byte level.

## Next

- Continue compacting the next high-burden semantic family after the full
  clean/cached/family/module verification matrix remains green.
