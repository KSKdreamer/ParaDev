# PIHC3 Opinion Modifier Import Progress

Date: 2026-06-14 00:08 +0800

Linear: none

## Done

- Migrated all 428 PIHC2 opinion modifier resources into `projects/PIHC3/src/modules/opinion_modifier/`.
- Preserved compiled PIHC_dev `common/opinion_modifiers/OPINION_<TAG>.txt` files as generic `def.txt` sources.
- Expanded scoped PIHC2 `@` localization into concrete `OPINION_<TAG>` keys with the shared migration localization helper.
- Updated the opinion-modifier migration note and PIHC3 design overview counts.

## Verification

- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_opinions.py --clean`
- `rtk uv run paradev summary projects/PIHC3 --json`

## Risks Or Blockers

- PIHC3 currently reports zero build errors and remains unblocked, with copy-root shadow warnings expected while native outputs replace copied PIHC_dev files.
- Trade-specific variants, trust bounds, timed decay presets, and balancing review remain future native slices.

## Next

- Continue with another compact non-map family such as idea categories, inventory items, state lore, or superevents.
- Decide when reviewed native families should gain copy-root excludes to reduce expected shadow warnings.
