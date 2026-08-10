# PIHC3 On-Action Native Metadata

## Scope

- Continued PIHC2 on-action migration without changing the simple shared `def.txt` PDX slot.
- Enhanced `projects/PIHC3/scripts/migrate_pihc2_on_actions.py` so each hook module exposes generic provenance metadata in both `meta.yaml` settings and `legacy/source.yaml`.
- Regenerated all ignored native on-action modules with `--clean`: 115 hook modules.

## Result

- Each on-action module now records compiled source paths, source file extension counts, source byte/line facts, generated hook text byte/line facts, compiled output path, source file stem, and `file_summaries_by_path`.
- `EVENT_CECIA_1_on_actions` records `common/on_actions/EVENT_CECIA_1_on_actions.txt`, 257 source bytes, 13 source lines, 153 generated hook bytes, 13 generated hook lines, and output `common/on_actions/EVENT_CECIA_1_on_actions.txt`.
- The regenerated tree has 115 `legacy/source.yaml` manifests, 92 unique compiled source files, 115 source path references, 170,323 compiled source bytes, 5,650 compiled source lines, 48,536 generated hook bytes, and 2,844 generated hook lines.
- The build output contains 115 `module:on_action/<id>` artifacts, one separate project-owned `common/on_actions/PIHC_STATE_LORES.txt` aggregate, and 0 copy-root-owned on-action artifacts.

## Verification

- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k on_action_importer_extracts_generic_provenance_contract` failed before implementation on missing `compiled_source_paths`, then passed after the importer change.
- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k on_action` passed with 4 selected tests.
- `rtk uv run black --check projects/PIHC3/scripts/migrate_pihc2_on_actions.py tests/test_pihc3_migration_contracts.py` passed after formatting the test file.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_on_actions.py tests/test_pihc3_migration_contracts.py` reported `OK: 2 file(s) - no banned imports`.
- `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-on-action-native-metadata-build.json` passed with 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.

## Remaining Work

- Keep hook routing semantics, scenario presets, DLC gating, and gameplay parity review for later on-action slices.
- Keep `PIHC_STATE_LORES.txt` with the native state-lore aggregate family instead of importing it as a standalone on-action hook.
