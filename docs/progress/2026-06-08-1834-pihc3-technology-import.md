# 2026-06-08 18:34 PIHC3 Technology Import

Linear: TAL-297, TAL-298

## Done

- Ported `projects/PIHC3/scripts/migrate_pihc2_technologies.py` from the older `src/general/technologies` shape to current `src/modules/technology`.
- Added a regression test proving the importer writes current module files, YAML localization, legacy source evidence, and buildable technology artifacts.
- Imported all 300 PIHC2 `resources/technologies` folders into native PIHC3 technology modules.
- Excluded native technology PDX and English/Chinese localization outputs from the `PIHC_dev` copy overlay.
- Updated the PIHC3 user manual and migration notes.

## Evidence

- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_technologies.py --clean`: imported 300 technology modules.
- `rtk uv run paradev build projects/PIHC3 --emit-manifests --json`: 829 modules, 26,892 artifacts, 0 diagnostics, 0 errors, `blocked: false`.
- `rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json`: 0 diagnostics after the overlay exclusions.

## Limits

- The native technology slice covers PDX and localization parity through compiled PIHC_dev blocks plus PIHC2 source evidence.
- Technology icons, interface sprite files, root technology GUI fragments, doctrine integration, and equipment/module technology side effects remain copy-overlay or future native work.

## Next

- Add parity review tooling for technology PDX/localization against `PIHC_dev`.
- Decide whether equipment, doctrines, or characters should be the next native import domain.
