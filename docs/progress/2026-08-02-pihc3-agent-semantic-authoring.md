# PIHC3 Agent-semantic Authoring

Date: 2026-08-02

## Outcome

The desktop's **Create module plan** role now receives the same user-facing
field semantics that PIHC3 templates expose to the generic GUI. Its dynamic
Registry-owned prompt catalog preserves each field's type, required state,
non-empty default, advanced status, label, description, and choices. The
prompt explicitly treats those fields—including units and examples—as
authoritative.

This closes a concrete correctness gap in the documented request “Create
ideas A, B, C, D, and E with CIC modifiers of 2%, 5%, 8%, 12%, and 16%.” The
Idea template already declared that percentages use decimal factors, but the
desktop prompt had discarded that description. The model now sees that 2% is
`0.02` before it proposes any request. The desktop still owns no write verb:
Python validates the response, plans through `Project.create_modules(...)`,
and leaves exact-hash application to the retained batch editor.

## PIHC3 field fitness

All 20 numeric fields across PIHC3's 52 project-owned templates now have both
a readable label and a semantic description. The remaining gaps were filled
for:

- Equipment Module stat values and XP cost;
- Focus cost plus X/Y tree positions;
- Special Project Reward minimum/maximum thresholds; and
- Technology research cost, start year, and X/Y grid positions.

The descriptions remain project-local extension data. No PIHC3 family name,
field unit, or conversion rule was added to ParaDev's generic desktop or MCP
code. Changed hidden extension descriptors moved to `0.2.4`; Focus moved from
`0.2.4` to `0.2.5` because it already carried the prior tree-authoring update.

## Real public-contract probe

A durable integration test now constructs an empty project with only the
PIHC3 Idea extension and drives the public HeavenBase-backed MCP toolkit:

1. set the preferred language to Chinese with a reviewed plan hash;
2. discover the one authoritative project-owned Idea template;
3. plan five modules with CIC values `0.02`, `0.05`, `0.08`, `0.12`, and
   `0.16`;
4. atomically apply that exact plan;
5. verify canonical `id - title` folders and generated PDX values; and
6. strict-build the resulting Idea family without an error.

No provider credential or mocked filesystem transaction is needed. The
desktop structured-model boundary remains covered with a fake LLM so the test
can assert the exact prompt and fail-closed proposal validation deterministically.

## Verification

- Desktop AI, MCP authoring, and PIHC3 layout contracts: 53 passed.
- All-family empty-project creation and strict-build matrix: one slow matrix
  covering 52 templates across 51 families passed.
- Standard Python gate: 2,284 passed, with nine expected native-Windows skips
  and one existing warning.
- Desktop: 89 files and 1,454 tests passed; strict TypeScript and Vite
  production build passed.
- Black and Flake8 repository gates passed. The Heaven-style scanner reported
  only the pre-existing standard-library import advisories in the touched
  large modules/tests; no new advisory remains.
- Clean/full and cached/full: 14,617 modules, 106 collections, 35,131
  artifacts, zero errors.
- Focus family partial: 738 modules, 28 collections, 12,499 artifacts, zero
  errors.
- Focus module partial (`FOCUS_C01_C02_EVERFREE_FIELDTRIP`): 83 modules, one
  collection, 11,161 artifacts, zero errors.
