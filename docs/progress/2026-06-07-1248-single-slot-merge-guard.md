# Single Slot Merge Guard Progress

Date: 2026-06-07 12:48

Linear: TAL-294

## Done

- Added regression coverage for repeated source slot declarations that merge into a single-valued logical slot.
- Updated `match_slots(...)` so merged same-name slots still enforce `many=False` after de-duplication.
- Based source-collision diagnostics on finalized slot paths, avoiding collisions on paths dropped by single-valued slot truncation.
- Documented the deterministic single-valued merge behavior in `docs/workflows/build-flow.md`.

## Verification

- Red: `rtk bash scripts/test.bash tests/test_build_slots.py::test_slot_matching_reports_multiple_matches_after_repeated_slot_merge -q` failed because both `icon.dds` and `icon.png` were registered.
- Green: `rtk bash scripts/test.bash tests/test_build_slots.py::test_slot_matching_reports_multiple_matches_after_repeated_slot_merge -q` passed.
- Slot suite: `rtk bash scripts/test.bash tests/test_build_slots.py -q` passed, `6 passed`.
- Related compiler path: `rtk bash scripts/test.bash tests/test_build_slots.py tests/test_module_sources.py tests/test_project_build.py tests/test_simple_source_family.py -q` passed, `100 passed`.
- Style: `rtk git diff --check` passed.
- Style: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/slots.py tests/test_build_slots.py` passed, `OK: 2 file(s) - no banned imports`.
- Style: `rtk bash scripts/flake.bash --ci` passed, `46 files would be left unchanged`.
- Full: `rtk bash scripts/test.bash` passed, `291 passed`.

## Risks Or Blockers

- Linear sync is blocked by expired auth: fetching `issue:TAL-294` returned `UNAUTHORIZED; Session expired. Please re-authenticate.`

## Next

- Continue hardening generic source-slot discovery and loader diagnostics before moving on to game-specific compilers.
