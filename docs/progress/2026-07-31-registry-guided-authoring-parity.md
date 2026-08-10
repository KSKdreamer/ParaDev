# Registry-guided PIHC3 authoring parity

Date: 2026-07-31

## Outcome

PIHC3's live source tree remains physically clean, and scripted module
authoring is now consistently Registry-owned across the SDK, desktop source
form, REST bridge, and bounded MCP runtime.

The final live-tree audit found:

- 14,618 direct module folders;
- zero `_component`, `_asset_component`, `legacy`, or `inactive_modules`
  directories;
- zero module folders outside the `id - preferred-language title` convention;
  and
- 72 standalone extension folders.

Old component paths visible through Git are deleted index/history entries, not
live compilation sources.

## Guided authoring coverage

All 51 visible PIHC3 families have an authoring-ready creation template.

Registry-owned guided source contracts now cover 48 of those 51 families. The
only exceptions are `equipment_module_category`, `texticon`, and `ui`, whose
current modules are asset/localization containers without scalar PDX sources.

The generic lossless PDX form is no longer limited to exact `def.txt` files. It
uses the same exact/glob/regex matching rules as source discovery and can
project any file owned by a `kind: pdx` resource slot, including `.txt`,
`.pdx`, `.gui`, `.gfx`, and `.asset` sources. Complexity, source-size,
exact-token, UTF-16 span, and stale-source guards remain unchanged.

The desktop no longer duplicates that decision with a filename whitelist. It
requests an optional form for the selected code-editor source and lets the
backend Registry return the authoritative form or `null`. Localization,
image, and binary-asset editors remain excluded.

This unlocks guided fields for representative PIHC3 sources such as:

- Decision, Event, Idea, Opinion Modifier, and Trait `def.txt`;
- Division history files;
- Entity `.asset`/`.gfx` files;
- MIO source trees; and
- State Lore fragments.

Focus, Technology, Doctrine, and MIO remain the four editable
Registry-provider diagram families.

## Extension ownership

Opinion Modifier and Trait no longer fall back to the central HoI4 family
registrations. Their project-local extension folders now contain:

- a concrete HeavenBase `Entity`;
- typed resource slots;
- compilation hooks;
- a project-owned build-family implementation;
- a hidden HeavenBase 0.1.2.1-compatible build-family descriptor; and
- the existing authoring template.

PIHC3 now has 71 project build-family descriptor records, up from 69. Idea,
Event, and Decision also explicitly identify their canonical definition slots
as PDX.

The two new family replacements preserve the existing artifact routes and
produce exact full-build parity.

## Agent interface

The callable authoring MCP toolkit now includes `module_source_form`.

The tool accepts a canonical module identity plus module-relative source path
and returns:

- one stable UTF-8 source snapshot;
- paired `size` and `mtime_ns` revision guards;
- whether guided editing is supported; and
- the same Registry/provider-owned `paradev.source-form.v1` controls used by
  the desktop.

Agents can therefore discover a module, inspect structured scalar fields, and
submit the resulting full-text edit through the existing crash-safe
`project_draft_apply` transaction without guessing family syntax or
overwriting a concurrent edit.

A real FastMCP call against
`trait/TRAIT_ADVANCED_MEDICAL_EXPERT/def.txt` returned four controls
(`Factor`, `Random`, `Experience loss factor`, and `Research speed factor`)
together with its stable source revision.

## Verification

- Complete Python gate: 2,373 passed, 9 native-Windows tests skipped.
- Complete desktop Vitest gate: 1,427 passed.
- Desktop TypeScript and production Vite build: passed; only the existing
  large-chunk advisory remains.
- Focused PIHC3/source-form/MCP gate: 48 passed.
- MCP/API/CLI/architecture generated-contract gate: 295 passed.
- Generated MCP and API catalog references exactly match their renderers.
- `git diff --check`: passed in the ParaDev and nested PIHC3 worktrees.
- Opinion Modifier partial: 428 modules, 0 diagnostics.
- Trait partial: 139 modules, 0 diagnostics.
- Clean/full: 14,617 active modules, 106 collections, 35,139 artifacts,
  0 diagnostics.
- Cached/full: identical.
- Focus family partial: 738 modules, 28 collections, 12,499 artifacts,
  0 diagnostics.
- Focus module partial: 129 modules, 1 collection, 11,253 artifacts,
  0 diagnostics.
- Final full publication restored: 14,617 modules, 106 collections,
  35,139 artifacts, 0 diagnostics.

## Next

The next high-value authoring gap is not another family-specific GUI branch.
It is a shared Registry-owned guided patch plan that accepts control ids and
values, produces a reviewable guarded source draft, and is reusable from
SDK/CLI/REST/MCP/desktop. Project-owned Entity `record.json` projection is now
covered by the follow-up Entity record guided-authoring slice.
