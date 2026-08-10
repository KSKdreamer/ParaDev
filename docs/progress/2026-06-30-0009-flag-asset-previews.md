# Flag Asset Previews Progress

Date: 2026-06-30 00:09

Linear: ongoing usability goal

## Done

- Added SDK-owned HOI4 TGA preview decoding and PNG writing helpers.
- Updated the PIHC3 flag-asset-component importer to generate one source-local `preview.png` per module from the root flag TGA variant.
- Added `preview_image_path` and `preview_image_source` metadata so the desktop module list can show browser-readable thumbnails without frontend TGA logic.
- Regenerated 1,110 PIHC3 flag asset component previews and metadata, and documented the behavior in the migration notes.

## Verification

- `rtk bash scripts/test.bash tests/test_hoi4_images.py -q`
- `rtk bash scripts/test.bash tests/test_pihc3_migration_contracts.py -k "flag_asset_component or hoi4_images" -q`
- `rtk npm run test -- src/moduleEditor/model.test.ts`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/games/hoi4/images.py tests/test_hoi4_images.py tests/test_pihc3_migration_contracts.py projects/PIHC3/scripts/migrate_pihc2_flag_asset_components.py`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 bash scripts/run.bash --tauri`

## Risks Or Blockers

- Country modules still do not expose flag previews directly; this slice makes the separate flag asset component family visually browsable first.
- Preview PNGs are source-side editor aids only and remain intentionally excluded from game output artifacts.

## Next

- Consider a separate country-facing preview slice that selects one representative country flag through Python metadata.
