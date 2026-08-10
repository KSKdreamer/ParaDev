# PIHC3 authoring-family coverage

Date: 2026-07-29

## Outcome

PIHC3 now exposes at least one authoring-ready module template for every visible browser family. The previous gaps were:

- `focus_tree`
- `equipment_module_category`
- `special_project_reward`

The project now reports 49 authoring-ready templates spanning all 48 visible families. The extra template is the existing second Idea workflow.

## User-facing contract

- A new Focus tree needs only an object ID, display name, and country tag. Default-tree, layout, and language fields remain behind the existing default-fields disclosure.
- The scaffold writes `meta.yaml` with only `title`, a usable `def.txt`, and the canonical `main.loc` required by guarded Focus-node creation.
- New equipment-module categories need only an object ID and display name. Their optional literal `icon.png` target is exposed to the existing desktop image editor, while existing DDS/TGA sources remain supported.
- New special-project rewards need only an object ID and display name. Description, option text, effect, thresholds, one-shot behavior, and language use safe defaults and remain editable.
- All three templates use the shared SDK template, batch-preview, exact-hash apply, browser, localization, and build contracts. No family-specific React parser or write path was added.
- Inline creation now resolves SDK-style escaped braces and placeholders identically to batch creation, so Clausewitz block defaults reach both write paths byte-consistently.

## Validation

- Six focused PIHC3 migration contracts passed, including a portable temporary project that:
  - atomically created all three module types;
  - projected the new Focus tree through `Project.module_diagram`;
  - transactionally created a localized Focus node;
  - emitted all three affected families without diagnostics.
- Real PIHC3 targeted plans passed with zero diagnostics:
  - Focus trees: 28 modules, 12,499 safely scoped artifacts.
  - Equipment-module categories: 49 modules, 11,044 safely scoped artifacts.
  - Special-project rewards: 18 modules, 11,012 safely scoped artifacts.
- Python contract slices passed:
  - 38 template/authoring/browser/batch tests.
  - 13 source-backed diagram tests.
  - 6 PIHC3 template-correctness tests.
- Desktop gate passed: 84 files and 1,403 tests.
- Desktop production TypeScript/Vite build passed.
- Native-web live smoke opened the real PIHC3 project, verified all three creation dialogs and the equipment-category image tab, canceled every dialog before write, and reported no browser warnings or errors.

## Follow-up

- Doctrine now uses the same authoritative, revision-guarded source-backed
  diagram path as Focus, Technology, and MIO. Its gameplay definition remains
  in module-owned `def.txt`; ParaDev-only position, path, and mutual-exclusion
  state lives in hidden `.paradev/diagram.yaml`.
- A future shared diagram-scope action can expose whole-tree creation directly from the diagram toolbar; the current workflow is available from the Focus module page and immediately feeds the existing Focus diagram/node editor.
- Continue reducing migrated legacy payloads only where the compiler no longer consumes them; do not trade compile parity for cosmetic folder cleanup.
