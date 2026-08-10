# 2026-08-01 Registry-Owned Diagram Relationship Actions

## Outcome

ParaDev no longer decides source-backed relationship editing from Focus,
Technology, Doctrine, or MIO family literals. `ModuleDiagramProvider` now
publishes declarative relationship actions through the active HeavenBase
Registry. The desktop consumes the same contract for bundled providers and
PIHC3-defined external `renderer="graph"` entities.

Each `ModuleDiagramRelationship` declares:

- the open provider planner `kind` and reader-facing label;
- the shared canvas `visual_kind`;
- which endpoint is the selected node and which endpoint owns the reviewed
  source revision;
- symmetric versus directed semantics; and
- one-versus-many cardinality.

The shared editor renders add, remove, quick-candidate, and canvas-pick
controls from those declarations. It rejects cross-scope endpoints, suppresses
directed cycle candidates, canonicalizes symmetric pairs, and replaces
single-cardinality edges in one draft. Provider planners remain the final
authority for exact source grammar and transactional writes.

## PIHC3 and MIO

The bundled providers now advertise their real source relationships:

- Technology: `dependency`, `path`;
- Focus: `prerequisite`, `mutually_exclusive`;
- Doctrine: `path`, `mutually_exclusive`;
- MIO: `relative_position`, `any_parent`, `all_parent`,
  `mutually_exclusive`.

MIO relationship editing is no longer disabled in the GUI. Desktop drafts
produce organization-scoped `MIOTraitEdgeIntent` rows using the owning target
trait's reviewed revision. Relative-position replacement emits removal and
addition in one review; unknown generic edge edits still fail closed. External
graph providers use the same UI and attach the revision from their declared
owner endpoint without a family switch.

The live PIHC3 physical module tree was also rechecked: no directory named
`*_component`, `*_asset_component`, `legacy`, or `inactive_modules` remains
under `projects/PIHC3/src/modules`.

## Verification

- Full Python repository gate: **2,425 passed**, **9 intentionally skipped**
  native-Windows tests, zero failures in 22 minutes 28 seconds.
- Full desktop gate: **1,451 passed** in 89 files.
- Strict TypeScript plus production Vite build: passed.
- Black check on touched Python files: passed.
- Flake8 with the repository's Black-compatible `E501,W503` exclusions on
  touched Python files: passed.
- Generated Build API and aggregate API Catalog manuals match their renderers.
- `git diff --check`: passed.

## Remaining Scope

This slice makes relationship editing extensible; it does not add arbitrary
extension-supplied React code. Providers select a reusable renderer protocol
and retain their source projection/planner code. Richer relationship-specific
forms may be introduced later as additional shared protocols, without adding
family-name dispatch.
