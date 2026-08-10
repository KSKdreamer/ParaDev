# PIHC3 Scripted Helper Metadata Progress

Date: 2026-06-15 04:51

Linear: TAL-000

## Done

- Extended the scripted-effect and scripted-trigger importer contracts with metadata assertions for `replace_civ_with_arms_factories` and `can_ROOT_get_wargoal_on_THIS`.
- Updated `projects/PIHC3/scripts/migrate_pihc2_scripted_effects_triggers.py` to mirror shallow PDX structure into `meta.yaml`: module ids, record family, entry counts, root keys/counts, direct scalar fields, block field keys, repeated root keys, and one-level nested root keys.
- Regenerated 8,277 scripted-effect modules and 87 scripted-trigger modules.
- Updated the scripted helper migration note, design summary, and legacy inventory evidence.

## Verification

- Red: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k "scripted_effect_importer_extracts_individual_effect_contract or scripted_trigger_importer_extracts_individual_trigger_contract"` failed with missing `settings["module_id"]`.
- Green: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k "scripted_effect_importer_extracts_individual_effect_contract or scripted_trigger_importer_extracts_individual_trigger_contract"` passed: 2 passed, 168 deselected.
- Regeneration: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_scripted_effects_triggers.py --clean` wrote 8,277 scripted effects and 87 scripted triggers.
- Metadata sample: regenerated scripted effects contain 24,758 direct entries; regenerated scripted triggers contain 138 direct entries.
- Dry build: `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-scripted-helper-metadata-dry-build.json` reported 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.

## Risks Or Blockers

- This slice summarizes direct PDX structure only. It does not reconstruct higher-level helper APIs, preset recipes, decision/event/focus wiring, or gameplay balancing semantics.

## Next

- Continue improving thin non-map families, likely on-actions or path-preserving component modules with similarly shallow metadata.
