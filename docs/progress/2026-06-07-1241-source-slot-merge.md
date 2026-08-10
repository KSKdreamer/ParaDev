# Source Slot Merge Progress

Date: 2026-06-07 12:41

Linear: TAL-294

## Done

- Added regression coverage for repeated source slot declarations with the same slot name.
- Updated `match_slots(...)` so repeated declarations merge into one deterministic, de-duplicated path list.
- Kept source-collision diagnostics scoped to different logical slot names, so repeated `loc` declarations do not report false collisions.
- Documented the merge rule in `docs/workflows/build-flow.md`.

## Verification

- Red: `rtk bash scripts/test.bash tests/test_build_slots.py::test_slot_matching_merges_repeated_slot_names_in_path_order -q` failed because `main.loc` was overwritten.
- Green: `rtk bash scripts/test.bash tests/test_build_slots.py::test_slot_matching_merges_repeated_slot_names_in_path_order -q` passed.
- Slot suite: `rtk bash scripts/test.bash tests/test_build_slots.py -q` passed, `5 passed`.
- Related compiler path: `rtk bash scripts/test.bash tests/test_build_slots.py tests/test_module_sources.py tests/test_project_build.py tests/test_simple_source_family.py -q` passed, `99 passed`.
- Style: `rtk git diff --check` passed.
- Style: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/slots.py tests/test_build_slots.py` passed, `OK: 2 file(s) - no banned imports`.
- Style: `rtk bash scripts/flake.bash --ci` passed, `46 files would be left unchanged`.
- Full: `rtk bash scripts/test.bash` passed, `290 passed`.

## Risks Or Blockers

- Linear sync is blocked by expired auth: fetching `issue:TAL-294` returned `UNAUTHORIZED; Session expired. Please re-authenticate.`

## Next

- Continue hardening source-slot and loader behavior that module families rely on before moving to game-specific compilers.
