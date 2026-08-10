# Guided source forms

Date: 2026-07-20

Status: completed; extended with generic PDX scalars on 2026-07-28,
Registry-declared integer lists on 2026-08-02, and bounded stable-identity
search on 2026-08-09

## Problem and success criteria

PIHC3's migrated Entity records are source-editable, but changing mesh, entity, and state values still requires editing raw JSON. The first guided-form slice lets a novice change existing scalar values without moving, renaming, adding, or deleting source structure. Its PDX extension now also supports Registry-declared homogeneous integer lists such as State provinces, State victory points, and Strategic Region provinces.

The slice is successful when:

- a project family can optionally project one current source draft into a generic form;
- the desktop can request that projection for unsaved text without putting the text in a URL;
- the React editor renders the generic form without PIHC or Entity conditionals;
- each control replaces only its exact JSON scalar token;
- Save still uses the existing full-text `Project.apply_source_draft` path and family validation;
- unsupported sources remain in the advanced source editor, and invalid drafts are never discarded.

## Non-goals

- Adding, deleting, renaming, or reordering JSON members, entities, or states.
- Editing Entity `event` or `propagate_state` structures.
- A second field-level write API.
- Requiring every build family to implement a form hook.
- Putting PIHC parsing or validation in TypeScript or host code.
- Mutating the protected, dirty PIHC3 checkout during this slice.

## Placement and dependency direction

| Layer | Owner | May depend on | Must not own |
| --- | --- | --- | --- |
| Project family | PIHC3 plugin | Its strict record parser and form descriptor data | Desktop state or file writes |
| SDK | `Project.source_form` | Project containment, registry lookup, generic form validation | PIHC/Entity field knowledge |
| REST/desktop transport | Same-origin JSON request/response | SDK facade | Form interpretation or mutation |
| React editor | Generic renderer and exact-span patchers | Versioned source-form payload | Entity parsing or backend writes |
| Existing draft lifecycle | `onTextDraft` through `apply_source_draft` | Complete patched text | Field-level patch protocol |

The dependency direction remains GUI → transport → SDK → optional project family. The project plugin owns domain labels, control choices, and source parsing; core owns the stable envelope and safety checks.

## Public surface

| Symbol | Kind | Layer | Inputs | Returns | Failure behavior | Variation seam | Test anchor |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `Project.source_form` | method | SDK | source path, optional current text and query | `paradev.source-form.v1` or `None` | Contextual `ValueError`; no mutation | Optional family `source_form` hook | `tests/test_source_forms.py` |
| `read_project_source_form` | function | REST facade | project id and POST body | form payload or JSON null | 400 for invalid project, text, or provider payload | SDK dispatch | `tests/test_architecture.py` |
| `project.source_form` | frontend operation | contract | project id/root, source path, text | form payload or null | Normal REST error | Generated REST plan | frontend API contract tests |
| `readProjectSourceForm` | function | desktop client | camel-case request | typed payload or null | Reject malformed or mismatched identity | Same-origin REST adapter | `paradev.test.ts` |
| `replaceJsonScalarAtPath` | function | React model | text, typed path, scalar value | exact patched text | Reject malformed, missing, duplicate, or non-scalar targets | Closed JSON scalar operation | `jsonScalarPatch.test.ts` |
| `replacePdxScalarAtPatch` | function | React model | text, reviewed UTF-16 span, expected token, replacement | exact patched text | Reject stale length/token, malformed span, unsafe identifier, or type mismatch | Closed PDX scalar operation | `pdxSourcePatch.test.ts` |
| `replacePdxIntegerListAtPatch` | function | React model | text, reviewed block-interior span, Registry row contract, replacement text | exact patched text | Reject stale source, unsafe integers, incomplete rows, comments, or malformed layout | Closed PDX integer-list operation selected by an open Registry family | `pdxSourcePatch.test.ts` |

The family hook is deliberately optional and duck-typed:

```python
source_form(
    *,
    module_id: str,
    relative_path: str,
    text: str,
) -> dict[str, object] | None
```

`None` means that the family does not guide that source. A raised validation error means the source is recognized but its current draft is invalid.

## Form and patch contract

The SDK owns the `paradev.source-form.v1` envelope and validates recursively nested sections. Controls are `readonly`, `text`, `number`, `boolean`, or `choice`. An editable control binds to exactly one operation:

```json
{
  "op": "replace-json-scalar",
  "path": ["entities", 0, "state__D1", "animation_speed"]
}
```

Typed path segments preserve raw repeated-property identities such as `state__D1`; dotted-path parsing is not used. Labels and descriptions may be literal strings or project-owned localized text maps.

The browser parses the current draft with CodeMirror's JSON parser, finds exactly one property/array target, and replaces only that scalar token. Property order, whitespace, line endings, unknown fields, and unedited nested objects stay byte-for-byte unchanged.

### Generic PDX guided extension

For a registered family whose canonical non-regex PDX source slot is exactly
`def.txt`, the SDK projects existing `=` scalar assignments without a
family-specific form provider. The generic projection exposes:

- `yes`/`no` booleans;
- finite decimal numbers;
- quoted strings; and
- conservative bare identifiers that cannot inject comments, braces, or
  operators.

A Registry family may additionally declare an exact field as
`control: integer-list`, with a row width and minimum value. ParaDev then
projects a multiline text control over the interior of that keyed block. The
`replace-pdx-integer-list` patch preserves the existing braces, line endings,
indentation, and surrounding source while requiring safe decimal integers and
complete rows. This is the shared mechanism used by PIHC3 State province
lists, State victory-point pairs, and Strategic Region province lists; the
desktop has no family-name switch.

Undeclared blocks and lists, commented or mixed-shape lists, variables, colors,
comparisons, ambiguous tokens, and documents over the bounded
depth/section/control limits remain available only in **Code** mode. Repeated
keys carry a zero-based occurrence at every path segment, while the actual edit
is pinned to an exact reviewed token span and expected source length. Spans use
UTF-16 code units so Python and JavaScript refer to the same position even when
earlier comments contain emoji.

The desktop never searches for a similar key or token. It verifies the source
length, span, expected token, and scalar kind, then replaces only that token in
the existing full-text draft. Comments, whitespace, quoting outside the edited
string, and line endings remain untouched. PDX text and identifier controls
buffer locally and commit once on blur or Enter; Escape restores the projected
value. After every committed PDX edit, the desktop reparses the full draft and
keeps the previous controls disabled until fresh exact spans arrive. A stale or
malformed projection fails closed into Code mode without writing a file.

### Bounded search

The same projection accepts an optional query of at most 200 characters.
Providers filter their already parsed controls, then return complete matching
sections inside the ordinary section/control bounds. Control and section ids
remain their global full-source identities rather than being renumbered by
the query, so a reviewed update always targets the same source span. An empty
match is a valid form with no sections and zero shown controls; it is not an
unsupported-source fallback. SDK, REST, desktop bridge, MCP, generated
frontend contract, and React all carry the same query value.

## Data and control flow

```text
open Guided / return from Advanced
  → POST current source text
  → Project resolves contained module and registered raw family
  → optional family parser returns declarative sections
  → SDK validates and wraps the payload
  → generic React controls read values from the current source text
  → one control replaces one reviewed scalar token or list interior
  → onTextDraft receives the complete new text
  → existing Save applies the full text through apply_source_draft
  → existing family validate_source_text runs before mutation
```

## Implementation slices and feedback gates

1. SDK and transport contract.
   - Verify focused Project, REST/OpenAPI, backend, loopback-host, and service tests.
   - Stop if a draft body would be routed through GET or a temporary file.
2. Generic JSON scalar renderer.
   - Verify exact CRLF/unknown-field preservation and malformed/duplicate-path failures.
   - Stop if the renderer needs an Entity field name.
3. Editor lifecycle integration.
   - Verify loading, unsupported, stale response, Guided/Advanced, invalid retry, Save, and Restore behavior in both locales.
4. PIHC3 disposable-project provider and GUI smoke.
   - Reuse the strict PIHC2 record parser.
   - Expose mesh scale; existing entity scale/default state; state name plus existing animation/speed/blend/chance/looping/next-state fields.
   - Keep names read-only and omit absent optional fields.
5. Package and end-to-end regression.
   - Rebuild the wheel-hosted app, install its macOS system-WebView bundle, open the disposable PIHC3 project, edit a record through Guided mode, save, build the exact Entity family, relaunch, and record results.

## Risks and waivers

- The first provider is exercised in the disposable PIHC3 GUI project because the user's protected PIHC3 checkout has unrelated dirty changes. Porting the provider into that checkout requires a safe project branch/worktree or explicit user direction.
- Number controls preserve a valid user-entered JSON number lexeme; strings may normalize only the edited token's JSON escapes.
- JSON family forms are reprojected when entering Guided mode. Generic PDX
  forms are reprojected after each committed field edit because any token
  length change invalidates later exact spans; buffered PDX text fields avoid
  per-keystroke bridge traffic.
- Windows safe source-draft mutation remains a separate packaging boundary already recorded in the Entity authoring report.

## Completion evidence

The signed-ad-hoc packaged app completed the planned Chinese-language regression on the disposable PIHC3 project. It loaded the remembered project without preparing the optional full index, projected `VIENTO_AIR_AIRSHIP_C40/record.json`, changed only mesh scale from `3.0` to `3.25`, saved the exact scalar-token patch, rebuilt the complete Entity family successfully, restored `3.0`, and rebuilt again. The final source matched its original 3,465-byte content and SHA-256 exactly. The final family build covered 136 modules and emitted 189 artifacts with zero diagnostics, zero errors, and `blocked: false`.
