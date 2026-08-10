# Shared Source Slots Progress

Date: 2026-06-07 13:36

Linear: TAL-294

## Done

- Added `Slot.shared` as an explicit opt-in for source files owned by more than one logical slot.
- Kept `slot.source_collision` when only some colliding slots opt into sharing.
- Parsed declarative `shared: true` family source-slot contracts.
- Validated Python-backed `Slot.shared` values as booleans and exposed shared slots in family inspection payloads.
- Documented shared source-slot behavior in `docs/workflows/build-flow.md`.

## Verification

- Red: `rtk bash scripts/test.bash tests/test_build_slots.py::test_slot_matching_allows_explicit_shared_source_ownership tests/test_build_slots.py::test_slot_matching_reports_source_collisions_when_only_one_slot_is_shared tests/test_project.py::test_project_families_exposes_shared_source_slot_contracts -q` failed because `Slot.shared` did not exist and declarative `shared: true` was ignored.
- Green: `rtk bash scripts/test.bash tests/test_build_slots.py::test_slot_matching_allows_explicit_shared_source_ownership tests/test_build_slots.py::test_slot_matching_reports_source_collisions_when_only_one_slot_is_shared tests/test_project.py::test_project_families_exposes_shared_source_slot_contracts -q` passed.
- Related slot/project path: `rtk bash scripts/test.bash tests/test_build_slots.py tests/test_project.py tests/test_project_build.py -q` passed, `172 passed`.
- Related source-family path: `rtk bash scripts/test.bash tests/test_module_sources.py tests/test_simple_source_family.py -q` passed, `29 passed`.
- Style: `rtk git diff --check` passed.
- Style: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/slots.py src/paradev/build/registry.py src/paradev/build/extensions.py tests/test_build_slots.py tests/test_project.py` passed, `OK: 5 file(s) - no banned imports`.
- Style: `rtk bash scripts/flake.bash --ci` passed, `46 files would be left unchanged`.
- Full: `rtk bash scripts/test.bash` passed, `304 passed`.

## Risks Or Blockers

- Linear sync is blocked by expired auth: fetching `issue:TAL-294` returned `UNAUTHORIZED; Session expired. Please re-authenticate.`

## Next

- Continue tightening the first slot compiler contracts, then reassess TAL-294 acceptance criteria before moving to the next generic compilation slice.
