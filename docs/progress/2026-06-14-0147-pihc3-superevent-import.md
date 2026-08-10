# 2026-06-14 01:47 +0800 - PIHC3 Superevent Import

## Summary

Imported PIHC2 superevents as native PIHC3 modules while keeping the compiler path on shared source slots.

## Changes

- Added `projects/PIHC3/scripts/migrate_pihc2_superevents.py`.
- Imported 14 `resources/superevents/<order>-<title>` folders into `src/modules/superevent/<tag>`.
- Preserved each compiled `SUPER.<tag>` hidden event and paired `SUPER_NEWS.<tag>` news event in module `def.txt`.
- Canonicalized English and Simplified Chinese legacy localization into `main.loc`.
- Copied compiled event/news DDS pictures into a shared `pictures` slot and generated `interface/PIHC3_superevents.gfx`.
- Excluded copied `SUPER.txt`, `SUPER_NEWS.txt`, `EVENT_SUPER*.dds`, `interface/events/EVENT_SUPER*.gfx`, and superevent localization files from the PIHC_dev copy root.
- Updated the superevent, copy-overlay, and overall PIHC3 migration docs.

## Verification

- Red tests first:
  - `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q`
  - Failed before the manifest/importer changes because `superevent` had no `pictures` source slot and `migrate_pihc2_superevents.py` did not exist.
- Green focused tests:
  - `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q`
  - 3 passed
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_superevents.py --clean`
  - Imported 14 modules
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_superevents.py tests/test_pihc3_migration_contracts.py`
  - OK: 2 files, no banned imports
- `rtk bash scripts/flake.bash --ci`
  - Passed
- `rtk bash scripts/test.bash`
  - 555 passed, 2 failed
  - Failures are in dirty frontend API reference work: `tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer` and `tests/test_architecture.py::test_frontend_api_binding_lookup_helpers_return_operation_ids`.
- `rtk uv run paradev summary projects/PIHC3 --json`
  - modules: 2,775
  - collections: 62
  - artifacts: 25,899
  - diagnostics: 4,183
  - errors: 0
  - blocked: false
- Clean emitted build after removing stale `projects/PIHC3/build/mod`:
  - dry_run: false
  - modules: 2,775
  - collections: 62
  - artifacts: 25,899
  - diagnostics: 4,183
  - errors: 0
  - blocked: false
- Native ownership spot checks confirmed `events/SUPEREVENT_1.txt`, both `EVENT_SUPER_1` DDS files, `EVENT_SUPER_1_l_english.yml`, and `interface/PIHC3_superevents.gfx` exist in a clean output root, while copied `events/SUPER.txt`, `events/SUPER_NEWS.txt`, and `interface/events/EVENT_SUPER_1.gfx` are absent.

## Risks Or Blockers

- Shared super-event GUI, scripted GUI, scripted-localisation selectors, close-button behavior, and music ownership remain copy-overlay owned.
- The artifact emitter is additive; cutover verification must clean `build/mod` before checking for removed copy artifacts.
- Full repository tests are currently blocked by unrelated frontend API reference drift.

## Next

- Continue with state lore, which is the next non-map custom PIHC2 system still starter-only.
