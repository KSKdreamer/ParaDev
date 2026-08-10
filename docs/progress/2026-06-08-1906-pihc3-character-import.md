# PIHC3 Character Import Progress

Date: 2026-06-08 19:06

Linear: TAL-297, TAL-298

## Done

- Replaced stale `projects/PIHC3/scripts/migrate_pihc2_characters.py` with the current-layout character importer.
- Imported 250 PIHC2 `resources/characters/<TAG>` folders into `projects/PIHC3/src/modules/character`.
- Preserved compiled PIHC_dev character PDX as `def.pdx`, consolidated English/Simplified Chinese localization as `main.loc`, and recorded source evidence in `legacy/source.yaml`.
- Kept large portrait/animation binaries out of native modules; the importer lists their source paths while the copy overlay continues to own generated assets.
- Excluded reviewed character PDX/localization outputs from the PIHC_dev copy overlay.
- Updated PIHC3 user and migration docs with the new character status.

## Verification

- `rtk uv run pytest tests/test_sdk_examples.py::test_pihc3_character_importer_writes_current_module_layout -q`
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_characters.py --clean`
- `rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json`
- `Project.load("projects/PIHC3").build(emit_manifests=True)` reported 1,120 modules, 25,313 artifacts, 0 diagnostics, 0 errors, and `blocked: False`.

## Risks Or Blockers

- Portrait DDS generation and portrait sprite declarations remain copy-overlay owned.
- `resources/characters_random` remains copy-overlay owned.
- Character animation strips and role-specific authoring helpers still need later slices.

## Next

- Add a character parity reviewer against `PIHC_dev/common/characters` and localization.
- Pick the next high-value domain, likely decisions, focuses, achievements, equipment, or countries.
