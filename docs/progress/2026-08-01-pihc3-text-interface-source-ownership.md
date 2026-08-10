# PIHC3 Text and Interface Source Ownership

Date: 2026-08-01

## Outcome

The last guided-authoring audit separated one intentional exception from two
real source-contract mistakes. `equipment_module_category` contains only
localization and images, which already use the desktop's dedicated
localization and image editors. `texticon` and `ui`, however, own editable
`.gfx` and `.gui` PDX documents that their project extensions had classified
as opaque copy assets.

The Text Icon and Interface extension bundles now:

- classify their `.gfx` and `.gui` definitions as PDX resource slots;
- keep DDS resources in separate copy slots with safe authoring destinations;
- emit both source kinds to their existing game-relative output paths;
- expose guarded generic PDX forms through the Registry, SDK, desktop, REST,
  and MCP contracts;
- use the common `module_id` plus `data` HeavenBase Entity record shape;
- use one direct `build_family()` Registry target instead of duplicate
  class-level factories and one-use family subclasses; and
- present the friendlier names **Text Icons** and **Interface Resources**.

The hidden extension descriptors moved from `0.2.3` to `0.2.4`. No visible
module metadata was added.

## Guided authoring coverage

All 51 visible PIHC3 families remain creation-ready. Fifty now own a guided
JSON or PDX source contract. The one exception,
`equipment_module_category`, is intentionally localization/image-only rather
than a scripted family; its `main.loc` and icon sources remain fully editable
through the appropriate dedicated editors.

The live `PIHC_texticons.gfx` form exposes 18 guarded scalar controls, and
`alerts.gui` exposes 51. Update planning is revision-guarded and no-write until
the ordinary source-draft transaction applies it. Oversized PDX documents
continue to fail closed to the Code editor instead of exposing an incomplete
form.

## Physical cleanup status

The exact `projects/PIHC3/src/modules` tree was rechecked by the architecture
suite:

- 14,618 direct module folders and 90 direct collection folders;
- zero `_component`, `_asset_component`, `legacy`, or `inactive_modules`
  directories; and
- every direct source unit uses `id - preferred-language title` naming.

Historical deleted paths in the nested PIHC3 Git index are not physical files,
Registry inputs, or compilation sources.

## Verification

- PIHC3 extensible-layout suite: 23 passed.
- Registry, descriptor, source-form, and retired-source regression set:
  89 passed with one existing warning.
- Complete standard Python fast gate: 2,280 passed, nine native-Windows tests
  skipped, with one existing warning.
- Full Black and Flake8 repository gate: passed after canonical formatting of
  the active crash-recovery and guided-authoring changes.
- Text Icon family publication: 5 modules, 11,046 artifacts, zero diagnostics.
- Text Icon module publication (`PIHC_TEXTICONS`): 1 module, 11,001 artifacts,
  zero diagnostics.
- Interface family publication: 11 modules, 11,005 artifacts, zero diagnostics.
- Interface module publication (`alerts`): 1 module, 10,995 artifacts, zero
  diagnostics.
- Clean/full and cached/full plans: 14,617 active modules, 106 collections,
  35,131 artifacts, zero diagnostics.
- The final emitted full build has the same summary, and its generated
  `PIHC_texticons.gfx`, `PIHC_unit_categories.gfx`, and `alerts.gui` all parse
  successfully as PDX.
