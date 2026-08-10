# 2026-06-20 13:58 - PIHC3 cwd-independent build wrapper

## Slice

Made the PIHC3 one-line build wrapper independent of the caller's current directory.

## Changes

- Added a PIHC3 migration contract assertion that `compile.bash` enters the ParaDev repo root before sourcing `scripts/_env.bash`.
- Updated `projects/PIHC3/compile.bash` to `cd "${ROOT}"` after computing the absolute PIHC3 project root and ParaDev repo root.
- Synced the PIHC3 README and user manual wording so the wrapper contract is explicit for users.

## Verification

- Red check: `rtk bash scripts/test.bash tests/test_pihc3_migration_contracts.py::test_pihc3_project_build_wrappers_use_current_paradev_surfaces -q` failed because `cd "${ROOT}"` was absent.
- Green check: `rtk bash scripts/test.bash tests/test_pihc3_migration_contracts.py::test_pihc3_project_build_wrappers_use_current_paradev_surfaces -q` passed with `1 passed`.
- Style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_pihc3_migration_contracts.py` reported `OK: 1 file(s) - no banned imports`.
- Shell syntax: `rtk bash -n projects/PIHC3/compile.bash` exited successfully.
- Smoke: from `/tmp`, `/bin/bash /Users/magolor/Utils/ParaDev-3/projects/PIHC3/compile.bash --plan-only --json` exited successfully and produced an 81,895,686-byte JSON plan.

## Notes

- A broader `rtk bash scripts/test.bash tests/test_pihc3_migration_contracts.py -q` run was interrupted after about 26 minutes because the wrapper launched a much larger CPU-bound test run than intended for this small shell-wrapper slice.
