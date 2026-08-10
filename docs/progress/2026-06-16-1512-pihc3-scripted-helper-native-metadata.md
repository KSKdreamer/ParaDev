# PIHC3 Scripted Helper Native Metadata

## Scope

- Continued PIHC2 scripted helper migration without changing the simple one-`def.txt` PDX slot for effects or triggers.
- Enhanced `projects/PIHC3/scripts/migrate_pihc2_scripted_effects_triggers.py` so scripted effect and trigger modules expose generic provenance metadata in both `meta.yaml` settings and `legacy/source.yaml`.
- Regenerated all ignored scripted helper modules with `--clean`: 8,277 scripted effects and 87 scripted triggers.

## Result

- Each helper module now records compiled source paths, source file extension counts, source byte/line facts, generated record text byte/line facts, compiled output path, source file stem, and `file_summaries_by_path`.
- `replace_civ_with_arms_factories` records `common/scripted_effects/00_scripted_effects.txt`, 17,105 source bytes, 587 source lines, 1,418 generated record bytes, 77 generated record lines, and output `common/scripted_effects/replace_civ_with_arms_factories.txt`.
- `can_ROOT_get_wargoal_on_THIS` records `common/scripted_triggers/00_scripted_triggers.txt`, 10,260 source bytes, 450 source lines, 124 generated record bytes, 9 generated record lines, and output `common/scripted_triggers/can_ROOT_get_wargoal_on_THIS.txt`.
- The build output contains 8,277 `scripted_effect` artifacts and 87 `scripted_trigger` artifacts under their respective `common/scripted_*` roots, with 0 copy-root-owned scripted helper artifacts.

## Verification

- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k scripted_helper_importer_extracts_generic_provenance_contract` failed before implementation on missing `compiled_source_paths`, then passed after the importer change.
- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k "scripted_effect or scripted_trigger or scripted_helper"` passed with 4 selected tests.
- `rtk uv run black --check projects/PIHC3/scripts/migrate_pihc2_scripted_effects_triggers.py tests/test_pihc3_migration_contracts.py` passed.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_scripted_effects_triggers.py tests/test_pihc3_migration_contracts.py` reported `OK: 2 file(s) - no banned imports`.
- `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-scripted-helper-native-metadata-build.json` passed with 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.

## Remaining Work

- Keep semantic helper grouping, source reconstruction, and gameplay wiring review for later scripted-helper parity slices.
- Inventory item scripted helpers remain owned by native `inventory_item` modules and are intentionally excluded from this generic helper importer.
