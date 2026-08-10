# PIHC3 Entity record guided authoring

Date: 2026-07-31

## Outcome

PIHC3's project-local Entity extension now owns a bounded guided editor for
portable `record.json` sources. ParaDev remains family-agnostic: it resolves the
active build family through the HeavenBase Registry, validates the returned
`paradev.source-form.v1` payload, and carries exact JSON patch paths to the
desktop, REST, and MCP surfaces.

This closes the remaining raw-JSON-only gap for PIHC3 model records without
adding an Entity family table or record schema to the ParaDev SDK.

## Project-owned contract

`projects/PIHC3/extensions/entity/records.py` now projects the already validated
`pihc2.entity.record.v1` value into:

- text, number, and boolean controls for existing scalar values;
- user-facing nested section labels such as
  `Entities › Item 1 › State › Event (2)`;
- friendlier domain labels such as `PDX mesh` and `Sound effect`; and
- exact `replace-json-scalar` paths that retain list indexes and portable
  duplicate keys such as `event__D1`.

The extension returns no guided form when a record exceeds 192 controls,
64 scalar-bearing sections, or 12 levels of nesting. The desktop then keeps
the safe code editor available instead of attempting a partial or ambiguous
projection.

The ParaDev SDK does not write while projecting a form. Existing source text is
validated as strict UTF-8 JSON through the Entity extension's own loader, and
the normal guarded source-draft transaction remains the only write path.

## Live PIHC3 coverage

All 134 current Entity `record.json` files project successfully:

- smallest form: 13 controls;
- largest form: 184 controls;
- every editable control has a non-empty exact JSON path; and
- duplicate-key records preserve their source keys while presenting ordinal
  labels to non-programmer users.

The representative `entity/VIENTO_MIRROR` record is available through both
`Project.source_form(...)` and the callable `module_source_form` MCP tool. Its
13 controls include model scale, animation state, event timing, particle, and
boolean fields paired with a stable source snapshot and revision.

## Guided update planning

`Project.plan_source_form_update(...)` now closes the agent-side token-editing
gap without creating another write path. It:

- rereads one stable source snapshot;
- recomputes the active Registry-owned form against that exact text;
- accepts only editable control ids with same-kind scalar replacements;
- validates JSON paths or exact PDX UTF-16 spans and stale tokens;
- preserves PDX comments, whitespace, newline style, and untouched tokens; and
- returns one full-text `source_edit` with paired size/mtime revision guards.

The new read-only MCP tool `module_source_form_update` exposes that plan to LLM
agents. An agent can now call `module_source_form`, submit selected control ids
and values, review the returned changes, and pass the unchanged `source_edit`
to `project_draft_apply`. Project writes still occur only inside the existing
crash-recoverable transaction.

A live plan for `entity/VIENTO_MIRROR` changes only the project-owned Scale
control from `4.0` to `4.5`; the project file remains untouched and the plan's
revision exactly matches the preceding MCP source snapshot.

## MCP process reliability

The real-stdio MCP regression now supplies the repository `src` directory
explicitly to its child process. It therefore tests a source checkout
deterministically instead of passing only when ParaDev happens to be installed
in the invoking interpreter.

## Verification

- Every live Entity record projection: passed (134/134).
- Representative SDK and real MCP form tests: passed.
- Focused PIHC3 layout gate: 15 passed.
- Source-form and MCP gate: 37 passed after the stdio environment fix.
- Final source-form/MCP/PIHC planner gate: 61 passed.
- Project/MCP/API generated-contract selectors: 20 passed.
- Final standard fast repository gate: 2,236 passed, 9 native-Windows tests
  skipped.
- Entity migration-contract gate: 4 passed.
- Import/undefined-name lint on touched extension/tests: passed.
- Entity-family partial build: 135 modules, 11,176 artifacts, 0 diagnostics.
- Cached full build: 14,617 modules, 106 collections, 35,139 artifacts,
  0 diagnostics.
- ParaDev and nested PIHC3 `git diff --check`: passed.

## Next

The next shared authoring step is multi-module guided batching: combine several
reviewed `module_source_form_update` plans into one atomic source-draft request,
with collision checks and a single review surface. REST/frontend exposure can
reuse the same SDK planner if the desktop later needs server-side control
intents instead of its current local exact-patch implementation.
