# PIHC3 Faction Metadata Progress

Date: 2026-06-15 05:16

Linear: TAL-000

## Done

- Extended the faction importer contract to assert generated `meta.yaml` structure for `faction_template_generic_dominance` and `faction_template_industrial_focus`.
- Updated `projects/PIHC3/scripts/migrate_pihc2_factions.py` to mirror shallow compiled faction-template structure into module settings: faction id, field order, scalar field keys and values, name/manifest/icon keys, leader-join flags, visible/available root keys, goal ids, and default rule ids.
- Regenerated the 4 native `faction` modules from compiled PIHC_dev `common/factions/templates/generic_factions.txt`.
- Updated the faction migration note, design summary, and legacy inventory evidence.

## Verification

- Red: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k faction_importer_extracts_individual_template_contract` failed with missing `settings["faction_id"]`.
- Green: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k faction_importer_extracts_individual_template_contract` passed: 1 passed, 169 deselected.
- Related faction contracts: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k "faction_family_uses_shared_def_and_loc_slots or faction_importer_extracts_individual_template_contract or faction_component_family_preserves_compiled_paths_with_generic_slots or faction_component_importer_extracts_compiled_system_contract or faction_uses_dedicated_importer_not_generic_common_batch"` passed: 5 passed, 165 deselected.
- Format: `rtk uv run black projects/PIHC3/scripts/migrate_pihc2_factions.py tests/test_pihc3_migration_contracts.py` reformatted the test file and left the importer unchanged.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_factions.py tests/test_pihc3_migration_contracts.py` passed.
- Regeneration: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_factions.py --clean` wrote 4 faction modules.
- Metadata sample: regenerated faction modules cover 8 goal references, 18 default-rule references, 3 explicit name loc keys, and one empty `available` block.
- Dry build: `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-faction-metadata-dry-build.json` reported 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.

## Risks Or Blockers

- This slice summarizes direct faction-template structure only. It does not reconstruct editable faction goals, manifests, rule groups, rules, upgrades, member upgrades, icon pools, AI initiative behavior, or country creation effects.

## Next

- Continue improving thin non-map gameplay families with shallow metadata and focused dry-build checks.
