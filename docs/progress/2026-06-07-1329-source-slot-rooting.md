# Source Slot Rooting Progress

Date: 2026-06-07 13:29

Linear: TAL-294

## Done

- Added regression coverage for exact source slot matches that try to escape a module root with `../`.
- Added early declarative manifest validation for escaping `source_slots` and `collection_source_slots`.
- Added Python-backed family registration validation for escaping `Slot.match` values.
- Added direct `match_slots(...)` diagnostics with `slot.invalid_match` for SDK callers.
- Documented source slot rooting behavior in `docs/workflows/build-flow.md`.

## Verification

- Red: `rtk bash scripts/test.bash tests/test_build_slots.py::test_slot_matching_reports_parent_traversal_slot_matches tests/test_project.py::test_project_manifest_rejects_escaping_source_slot_match tests/test_project.py::test_project_families_rejects_python_module_with_escaping_source_slot_match -q` failed because `../outside.pdx` was accepted.
- Green: `rtk bash scripts/test.bash tests/test_build_slots.py::test_slot_matching_reports_parent_traversal_slot_matches tests/test_project.py::test_project_manifest_rejects_escaping_source_slot_match tests/test_project.py::test_project_families_rejects_python_module_with_escaping_source_slot_match -q` passed.
- Related slot/project path: `rtk bash scripts/test.bash tests/test_build_slots.py tests/test_module_sources.py tests/test_project.py tests/test_project_build.py -q` passed, `173 passed`.
- Generic source family path: `rtk bash scripts/test.bash tests/test_simple_source_family.py -q` passed, `25 passed`.
- Style: `rtk git diff --check` passed.
- Style: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/slots.py src/paradev/build/registry.py src/paradev/build/extensions.py tests/test_build_slots.py tests/test_project.py` passed, `OK: 5 file(s) - no banned imports`.
- Style: `rtk bash scripts/flake.bash --ci` passed, `46 files would be left unchanged`.
- Full: `rtk bash scripts/test.bash` passed, `301 passed`.

## Risks Or Blockers

- Linear sync is blocked by expired auth: fetching `issue:TAL-294` returned `UNAUTHORIZED; Session expired. Please re-authenticate.`

## Next

- Continue hardening source-slot and artifact writer contracts before moving to the next generic module compilation slice.
