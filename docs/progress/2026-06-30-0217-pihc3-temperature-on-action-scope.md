# PIHC3 Temperature On-Action Scope

## Summary

- Updated the PIHC3 state-temperature on-action source so monthly/global temperature update effects run through a scoped `random_country` effect block.
- Tightened the ParaDev migration contract to assert the scoped wrapper and reject only direct on-action-depth calls.
- Kept this separate from the desktop diagnostics bridge because it changes PIHC3 source content.

## Verification

- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k state_temperature`
- `rtk git diff --check`
- `rtk git -C projects/PIHC3 diff --check`
