# PIHC3 Operation Token Import Progress

Date: 2026-06-14 05:42 CST

Linear: N/A

## Done

- Added `projects/PIHC3/scripts/migrate_pihc2_operation_tokens.py` to split compiled PIHC_dev operation tokens into one PIHC3 module per token.
- Replaced the previous one file-level operation-token module with 5 token-level modules under `projects/PIHC3/src/modules/operation_token`.
- Restored token-owned vanilla localization rows for `name` and `desc`, plus the family-required token-id placeholder rows.
- Removed `operation_token` from the generic common-source importer so future generic imports do not overwrite the split modules.
- Updated migration docs for the operation-token importer and current PIHC3 build counts.

## Verification

- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q` -> 36 passed.
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_operation_tokens.py --clean` -> imported 5 operation token modules.
- PIHC3 emitting build -> 3,329 modules, 62 collections, 27,671 artifacts, 0 errors, `blocked: false`.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_operation_tokens.py projects/PIHC3/scripts/migrate_pihc2_common_sources.py tests/test_pihc3_migration_contracts.py` -> OK.
- `rtk bash scripts/flake.bash --ci` -> passed.

## Risks Or Blockers

- The build still reports broader copy-root/native overlap warnings; this slice targets operation-token split granularity and localization coverage.

## Next

- Continue splitting coarse non-map common families where the current file-level module hides multiple independently editable records, while leaving aggregate-shaped families such as continuous-focus palettes for a dedicated aggregate design.
