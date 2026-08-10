# PIHC3 Scripted GUI Metadata Progress

Date: 2026-06-15 04:43

Linear: TAL-000

## Done

- Extended the scripted-GUI importer contract with metadata assertions for `pihc_inventory_toggle`.
- Updated `projects/PIHC3/scripts/migrate_pihc2_scripted_guis.py` to mirror compiled GUI ids, wrapper names, field order, direct scalar fields, visible-root keys, effect ids/root keys, trigger ids/root keys, and property ids/root keys.
- Regenerated all 109 scripted GUI modules.
- Updated the scripted GUI migration note, design summary, and legacy inventory evidence.

## Verification

- Red: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k scripted_gui_importer_extracts_individual_gui_contract` failed with missing `settings["gui_id"]`.
- Green: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k scripted_gui_importer_extracts_individual_gui_contract` passed: 1 passed, 169 deselected.
- Regeneration: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_scripted_guis.py --clean` wrote 109 modules.
- Metadata sample: regenerated scripted GUIs include 104 visible blocks, 81 GUIs with effects, 69 with triggers, 10 with properties, and 84 split records from `PIHC_inventory.txt`.
- Dry build: `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-scripted-gui-metadata-dry-build.json` reported 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.

## Risks Or Blockers

- This slice summarizes compiled script-side GUI records only. Interface `.gui` layout files, scripted-localisation behavior, dynamic-list semantics, button behavior, and full UI workflow parity remain future work.

## Next

- Continue enhancing thin non-map families, with scripted effects/triggers or path-preserving component metadata likely next.
