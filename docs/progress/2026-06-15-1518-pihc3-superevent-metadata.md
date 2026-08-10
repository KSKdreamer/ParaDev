# PIHC3 Superevent Metadata Progress

Date: 2026-06-15 15:18

Linear: active PIHC3 migration goal

## Done

- Added a focused red/green contract for `migrate_pihc2_superevents.py` metadata extraction.
- Enriched all 14 generated `src/modules/superevent/<tag>/meta.yaml` files with compiled event-pair ids, picture sprite ids, option/effect roots, global flags, legacy `info.json` effect scopes, play-song ids, localization counts, source slot counts, and DDS header facts.
- Updated the superevent migration note, PIHC3 design summary, and legacy inventory evidence.

## Verification

- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k superevent` -> 3 passed, 209 deselected.
- `rtk uv run black --check projects/PIHC3/scripts/migrate_pihc2_superevents.py tests/test_pihc3_migration_contracts.py` -> clean.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_superevents.py tests/test_pihc3_migration_contracts.py` -> no banned imports.
- `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json` -> 16,581 modules, 37,480 artifacts, 713 diagnostics, 0 errors, `blocked: false`.

## Risks Or Blockers

- Superevent GUI/scripted-localisation close-button behavior and aggregate `SUPER.txt`/`SUPER_NEWS.txt` byte-for-byte reconstruction remain future parity work.
- Shared music files are still owned by `audio_component`; this slice only records the per-superevent play-song links.

## Next

- Continue with the remaining low-metadata non-map support families such as peace-conference, raid, MIO, and common components.
