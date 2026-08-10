# PIHC3 On-Action Metadata Progress

Date: 2026-06-15 05:02

Linear: TAL-000

## Done

- Extended the on-action importer contract to assert generated `meta.yaml` wrapper/action/hook ids and shallow PDX body summaries for `EVENT_CECIA_1_on_actions` and `PIHC_C03_MUFFIN__on_monthly_C03`.
- Updated `projects/PIHC3/scripts/migrate_pihc2_on_actions.py` to mirror shallow compiled hook structure into module settings: module ids, action ids, hook ids, entry counts, root keys/counts, direct scalar fields, block field keys, repeated root keys, and one-level nested root keys.
- Regenerated 115 native `on_action` modules from compiled PIHC_dev `common/on_actions/*.txt`, still skipping the `PIHC_STATE_LORES.txt` aggregate owned by `state_lore`.
- Updated the on-action migration note, design summary, and legacy inventory evidence.

## Verification

- Red: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k on_action_importer_extracts_individual_hook_contract` failed with missing `settings["legacy_wrapper"]`.
- Green: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k on_action_importer_extracts_individual_hook_contract` passed: 1 passed, 169 deselected.
- Related on-action contracts: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k "on_action_family_uses_shared_def_slot or on_action_importer_extracts_individual_hook_contract or on_action_uses_dedicated_importer_not_generic_common_batch"` passed: 3 passed, 167 deselected.
- Format: `rtk uv run black projects/PIHC3/scripts/migrate_pihc2_on_actions.py tests/test_pihc3_migration_contracts.py` left both files unchanged.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_on_actions.py tests/test_pihc3_migration_contracts.py` passed.
- Regeneration: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_on_actions.py --clean` wrote 115 on-action modules.
- Metadata sample: regenerated modules use the `on_actions` wrapper, cover 25 distinct hook ids, and 114 modules expose `effect` as the top-level root key.
- Dry build: `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-on-action-metadata-dry-build.json` reported 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.

## Risks Or Blockers

- This slice summarizes direct PDX structure only. It does not reconstruct semantic event/random-event routing, scope-specific presets, DLC gating, or gameplay balance review.

## Next

- Continue improving thin non-map families with shallow metadata and focused dry-build checks.
