# PIHC3 Country And BOP Import Progress

Date: 2026-06-13 23:59 +0800

Linear: none

## Done

- Migrated all 67 PIHC2 country resources into `projects/PIHC3/src/modules/country/`.
- Migrated all 8 PIHC2 balance-of-power resources into `projects/PIHC3/src/modules/balance_of_power/`.
- Extended shared project-local slots so country modules copy `flags/**/*` to `gfx/flags/...` and BOP modules copy `icons/**/*` to `gfx/interface/bop/...`.
- Updated the country and balance-of-power migration notes plus the PIHC3 design overview counts.

## Verification

- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_countries.py --clean`
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_bops.py --clean`
- `rtk uv run paradev summary projects/PIHC3 --json`

## Risks Or Blockers

- PIHC3 currently reports zero build errors and remains unblocked, with copy-root shadow warnings expected while native outputs replace copied PIHC_dev files.
- Country history, country tags, cosmetic country definitions, OOB, portraits, map ownership, and AI setup remain copy-overlay owned or future native slices.
- BOP side decisions/events and balancing review remain future native slices.

## Next

- Continue with another compact non-map family such as idea categories, opinion modifiers, inventory items, or state lore.
- Decide when shadowed copy-root paths should be excluded after each family reaches reviewed native parity.
