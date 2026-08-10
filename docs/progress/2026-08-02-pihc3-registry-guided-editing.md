# PIHC3 Registry-owned Guided Editing

This checkpoint closes the largest remaining gap between PIHC3's semantic
creation templates and editing existing modules.

## Outcome

- Registry families may publish `source_form_field_hints` with localized
  labels and descriptions keyed by exact PDX field name. ParaDev projects
  those declarations generically and never switches on a family id.
- Every projected generic PDX scalar now has contextual path help and a
  `description_source` of `declared` or `generated`.
- Bounded PDX forms publish exact coverage counts. Files beyond 96 controls or
  32 projected sections retain Guided mode for the safe prefix and tell the
  desktop how many values remain in Code mode.
- The desktop validates and renders the shared coverage/help contract, shows a
  localized partial-coverage notice, and retains exact-token guarded updates.
- The Idea, Event, Decision, Focus, Technology, Character, Country, and
  Equipment Entity/family extensions own bilingual domain help. Entity
  protocol metadata remains deliberately unannotated because HeavenBase
  0.1.2.1 treats Entity annotations as logical fields; the paired compiler
  family exposes the typed Registry attribute.
- All 42 current event `def.txt` files now have a Guided projection. Fifteen
  are complete and 27 are explicitly partial; none fall back to Code-only
  merely because the file is large.

## Verification

- Python: 2,294 passed, 9 native-Windows skips, 2 warnings.
- Desktop: 89 files and 1,457 tests passed.
- TypeScript and Vite production build passed; the existing large-chunk
  warning remains.
- Black/flake gate: 219 files unchanged.
- Clean/full and cached/full PIHC3 builds: 14,617 modules, 106 collections,
  35,131 artifacts, zero diagnostics/errors.
- Focus-family partial: 738 modules, 28 collections, 12,499 artifacts, zero
  diagnostics/errors.
- Focus-module partial (`FOCUS_C01_C02_EVERFREE_FIELDTRIP`): 83 modules, one
  collection, 11,161 artifacts, zero diagnostics/errors.
- The canonical source-tree integration gate continues to reject `legacy/`,
  `inactive_modules/`, `_component`, and `_asset_component` directories.
